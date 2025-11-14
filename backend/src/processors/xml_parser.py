"""
XML Parser for streaming analysis of XML files.

This module provides the XMLParser class for parsing large XML files
using streaming techniques with lxml, extracting field structure and
sample values with proper memory management.
"""

import logging
from pathlib import Path
from typing import Any
from collections import defaultdict

from lxml import etree

from ..core.config import settings
from ..core.exceptions import XMLParseError, ValidationError, DTDParseError
from .xml_schema_parser import DTDParser, XSDParser, XMLSchemaEnhancer
from .timeout_utils import with_timeout, TimeoutError

logger = logging.getLogger(__name__)


class XMLParser:
    """
    Streaming XML parser for large files.
    Extracts field structure, attributes, and sample values.
    Uses lxml.iterparse() with proper memory management.
    """

    def __init__(self, max_samples: int = 1000, max_depth: int = None):
        """
        Initialize XMLParser.

        Args:
            max_samples: Maximum number of records to sample
            max_depth: Maximum nesting depth to analyze (defaults to settings.XML_MAX_DEPTH)
        """
        self.max_samples = max_samples
        self.max_depth = max_depth or settings.XML_MAX_DEPTH
        self.strip_namespaces = settings.XML_STRIP_NAMESPACES
        self.attribute_prefix = settings.XML_ATTRIBUTE_PREFIX
        self.dtd_parser = DTDParser()
        self.xsd_parser = XSDParser()
        self.schema_enhancer = XMLSchemaEnhancer()

    def parse_file(self, file_path: Path, xsd_path: Path | None = None) -> dict[str, Any]:
        """
        Parse XML file and extract field metadata with optional DTD/XSD schema information.

        Args:
            file_path: Path to XML file
            xsd_path: Optional path to XSD schema file

        Returns:
            {
                'fields': [...],  # List of field metadata
                'total_records': int,
                'is_array': bool,  # Whether root contains multiple records
                'dtd_metadata': {...} | None,  # DTD schema info if present
                'xsd_metadata': {...} | None  # XSD schema info if provided
            }

        Raises:
            ValidationError: If file is too large or invalid
            XMLParseError: If XML is malformed
            TimeoutError: If parsing exceeds timeout
        """
        # Validate file size
        file_size_mb = file_path.stat().st_size / (1024 * 1024)
        max_size_mb = settings.XML_MAX_FILE_SIZE_MB

        if file_size_mb > max_size_mb:
            logger.error(
                f"XML file too large: {file_size_mb:.2f}MB exceeds limit of {max_size_mb}MB",
                extra={'file_path': str(file_path), 'file_size_mb': file_size_mb}
            )
            raise ValidationError(
                f"XML file too large: {file_size_mb:.2f}MB exceeds maximum allowed size of {max_size_mb}MB",
                details={'file_size_mb': file_size_mb, 'max_size_mb': max_size_mb}
            )

        logger.info(f"Parsing XML file: {file_path.name} ({file_size_mb:.2f}MB)")

        try:
            # Extract DTD information if present
            dtd_info = self._extract_dtd(file_path)

            # Extract XSD information if schema provided
            xsd_info = None
            if xsd_path and xsd_path.exists():
                xsd_info = self.xsd_parser.parse_xsd(xsd_path)
                # Validate XML against XSD
                validation_result = self.xsd_parser.validate_xml(file_path, xsd_path)
                if xsd_info:
                    xsd_info['validation'] = validation_result

            # Detect if XML represents a collection or single record
            is_array, root_element = self._detect_structure(file_path)

            if is_array:
                result = self._parse_collection(file_path, root_element)
            else:
                result = self._parse_single_record(file_path)

            # Enhance fields with schema information
            if dtd_info or xsd_info:
                result['fields'] = self.schema_enhancer.enhance_fields(
                    result['fields'],
                    dtd_info,
                    xsd_info
                )

            # Add schema metadata to result
            if dtd_info:
                result['dtd_metadata'] = dtd_info
            if xsd_info:
                result['xsd_metadata'] = xsd_info

            logger.info(
                f"Successfully parsed XML file with {len(result['fields'])} fields",
                extra={'total_records': result['total_records'], 'is_array': result['is_array']}
            )

            return result

        except TimeoutError as e:
            logger.error(
                f"XML parsing timeout: {e}",
                extra={'file_path': str(file_path), 'timeout_seconds': settings.XML_PARSE_TIMEOUT}
            )
            raise XMLParseError(
                f"XML parsing timed out after {settings.XML_PARSE_TIMEOUT} seconds. File may be too large or complex.",
                details={'file_path': str(file_path), 'timeout': settings.XML_PARSE_TIMEOUT}
            )
        except etree.XMLSyntaxError as e:
            logger.error(
                f"XML syntax error: {e}",
                extra={'file_path': str(file_path), 'line': e.lineno, 'error': str(e)}
            )
            raise XMLParseError(
                f"Malformed XML file: {str(e)}",
                details={'file_path': str(file_path), 'line': getattr(e, 'lineno', None)}
            )
        except Exception as e:
            logger.error(
                f"Unexpected error parsing XML: {e}",
                extra={'file_path': str(file_path), 'error_type': type(e).__name__}
            )
            raise XMLParseError(
                f"Failed to parse XML file: {str(e)}",
                details={'file_path': str(file_path)}
            )

    @with_timeout(30)  # 30 second timeout for structure detection
    def _detect_structure(self, file_path: Path) -> tuple[bool, str | None]:
        """
        Detect if XML is a collection of records or single record.

        Returns:
            (is_array, repeating_element_name)
        """
        # Parse first few elements to detect structure
        # Security: Disable network access and external entities
        context = etree.iterparse(
            str(file_path),
            events=('end',),
            encoding='utf-8',
            recover=True,
            no_network=not settings.XML_ALLOW_NETWORK_ACCESS,
            load_dtd=False  # Don't load DTD during structure detection
        )

        element_counts = defaultdict(int)
        parent_map = {}
        depth_map = {}
        checked_elements = 0
        root = None

        try:
            for event, elem in context:
                if root is None:
                    root = elem.getroottree().getroot()

                tag = self._clean_tag(elem.tag)
                parent = elem.getparent()

                if parent is not None:
                    parent_tag = self._clean_tag(parent.tag)
                    key = (parent_tag, tag)
                    element_counts[key] += 1
                    parent_map[tag] = parent_tag

                    # Track depth
                    depth = self._get_element_depth(elem)
                    depth_map[tag] = depth

                checked_elements += 1
                if checked_elements > 100:  # Check first 100 elements
                    break

                # Clear memory
                elem.clear()
                # Safely delete previous siblings if parent exists
                if elem.getparent() is not None:
                    while elem.getprevious() is not None:
                        del elem.getparent()[0]

            del context

            # Detect if there's a repeating element pattern
            for (parent_tag, child_tag), count in element_counts.items():
                # If a child element repeats more than once under the same parent at depth 1-2
                if count > 1 and depth_map.get(child_tag, 0) <= 2:
                    return True, child_tag

            return False, None

        except etree.XMLSyntaxError as e:
            raise XMLParseError(
                f"Malformed XML file during structure detection: {e}",
                details={'file_path': str(file_path)}
            )

    @with_timeout(None)  # Timeout will be handled by parent parse_file timeout
    def _parse_collection(self, file_path: Path, record_element: str) -> dict[str, Any]:
        """Parse XML collection (multiple records)"""
        fields_map = {}
        records_processed = 0

        # Security: Disable network access and external entities
        context = etree.iterparse(
            str(file_path),
            events=('end',),
            tag=record_element,
            encoding='utf-8',
            recover=True,
            no_network=not settings.XML_ALLOW_NETWORK_ACCESS,
            load_dtd=False  # Don't load DTD during parsing
        )

        try:
            for event, elem in context:
                if records_processed >= self.max_samples:
                    break

                # Extract fields from this record
                self._extract_fields(
                    elem,
                    parent_path='',
                    fields_map=fields_map,
                    depth=0
                )
                records_processed += 1

                # CRITICAL: Clear memory to prevent buildup
                elem.clear()
                # Safely delete previous siblings if parent exists
                if elem.getparent() is not None:
                    while elem.getprevious() is not None:
                        del elem.getparent()[0]

            del context

            return {
                'fields': [field.to_dict() for field in fields_map.values()],
                'total_records': records_processed,
                'is_array': True
            }

        except etree.XMLSyntaxError as e:
            raise XMLParseError(
                f"Malformed XML file during collection parsing: {e}",
                details={'file_path': str(file_path), 'record_element': record_element}
            )

    @with_timeout(None)  # Timeout will be handled by parent parse_file timeout
    def _parse_single_record(self, file_path: Path) -> dict[str, Any]:
        """Parse single XML record"""
        fields_map = {}

        try:
            # Security: Disable network access and external entities
            parser = etree.XMLParser(
                no_network=not settings.XML_ALLOW_NETWORK_ACCESS,
                resolve_entities=settings.XML_ALLOW_EXTERNAL_ENTITIES
            )
            tree = etree.parse(str(file_path), parser)
            root = tree.getroot()

            self._extract_fields(
                root,
                parent_path='',
                fields_map=fields_map,
                depth=0
            )

            return {
                'fields': [field.to_dict() for field in fields_map.values()],
                'total_records': 1,
                'is_array': False
            }

        except etree.XMLSyntaxError as e:
            raise XMLParseError(
                f"Malformed XML file during single record parsing: {e}",
                details={'file_path': str(file_path)}
            )

    def _extract_fields(
        self,
        elem: etree._Element,
        parent_path: str,
        fields_map: dict[str, 'XMLFieldMetadata'],
        depth: int
    ):
        """
        Recursively extract fields from XML element.

        Handles:
        - Element tags as fields
        - Attributes as separate fields with @ prefix
        - Nested elements
        - Repeating elements (arrays)
        """
        if depth > self.max_depth:
            return

        tag = self._clean_tag(elem.tag)
        field_path = f"{parent_path}.{tag}" if parent_path else tag

        # Extract attributes as separate fields
        if elem.attrib:
            for attr_name, attr_value in elem.attrib.items():
                attr_clean = self._clean_tag(attr_name)
                attr_path = f"{field_path}.{self.attribute_prefix}{attr_clean}"

                if attr_path not in fields_map:
                    fields_map[attr_path] = XMLFieldMetadata(
                        field_path=attr_path,
                        field_name=f"{self.attribute_prefix}{attr_clean}",
                        parent_path=field_path,
                        nesting_level=depth,
                        is_attribute=True
                    )

                fields_map[attr_path].observe_value(attr_value)

        # Handle element content
        if field_path not in fields_map:
            fields_map[field_path] = XMLFieldMetadata(
                field_path=field_path,
                field_name=tag,
                parent_path=parent_path,
                nesting_level=depth,
                is_attribute=False
            )

        field_meta = fields_map[field_path]

        # Get element text content (excluding children's text)
        text = elem.text.strip() if elem.text else ""

        # Check if element has children
        children = list(elem)

        if children:
            # Element has nested structure
            field_meta.observe_value(None)  # No direct text value

            # Track repeating child elements for array detection
            child_tags = {}
            for child in children:
                child_tag = self._clean_tag(child.tag)
                child_tags[child_tag] = child_tags.get(child_tag, 0) + 1

            # Process children
            for child in children:
                child_tag = self._clean_tag(child.tag)

                # Mark as array if repeating
                child_path = f"{field_path}.{child_tag}"
                if child_tags[child_tag] > 1:
                    if child_path not in fields_map:
                        fields_map[child_path] = XMLFieldMetadata(
                            field_path=child_path,
                            field_name=child_tag,
                            parent_path=field_path,
                            nesting_level=depth + 1,
                            is_attribute=False
                        )
                    fields_map[child_path].is_array = True

                # Recurse
                self._extract_fields(child, field_path, fields_map, depth + 1)

        elif text:
            # Leaf node with text content
            field_meta.observe_value(text)
        else:
            # Empty element
            field_meta.observe_value(None)

    def _clean_tag(self, tag: str) -> str:
        """
        Clean XML tag by removing namespace if configured.

        Example: {http://example.com}element -> element
        """
        if self.strip_namespaces and tag.startswith('{'):
            return tag.split('}', 1)[1] if '}' in tag else tag
        return tag

    def _get_element_depth(self, elem: etree._Element) -> int:
        """Calculate depth of element in tree"""
        depth = 0
        parent = elem.getparent()
        while parent is not None:
            depth += 1
            parent = parent.getparent()
        return depth

    @with_timeout(30)  # 30 second timeout for DTD extraction
    def _extract_dtd(self, file_path: Path) -> dict[str, Any] | None:
        """
        Extract DTD information from XML file if present.

        Args:
            file_path: Path to XML file

        Returns:
            DTD metadata dictionary or None if no DTD

        Raises:
            DTDParseError: If DTD is present but cannot be parsed
        """
        try:
            # Security: Control DTD loading behavior
            # load_dtd=True allows reading the DTD for schema info
            # but no_network prevents fetching external DTDs via HTTP
            parser = etree.XMLParser(
                dtd_validation=False,
                load_dtd=True,
                no_network=not settings.XML_ALLOW_NETWORK_ACCESS,
                resolve_entities=settings.XML_ALLOW_EXTERNAL_ENTITIES
            )
            tree = etree.parse(str(file_path), parser)
            dtd = tree.docinfo.internalDTD or tree.docinfo.externalDTD

            if dtd is not None:
                logger.debug(f"Extracting DTD from {file_path.name}")
                dtd_info = self.dtd_parser.parse_dtd(dtd)
                if dtd_info:
                    logger.info(
                        f"Extracted DTD with {len(dtd_info.get('elements', {}))} elements",
                        extra={'file_path': str(file_path)}
                    )
                return dtd_info

            return None

        except etree.XMLSyntaxError as e:
            # DTD syntax errors are non-fatal - log and continue without DTD
            logger.warning(
                f"DTD syntax error in {file_path.name}: {e}",
                extra={'file_path': str(file_path), 'error': str(e)}
            )
            return None
        except Exception as e:
            # Other DTD errors are also non-fatal but should be logged
            logger.warning(
                f"Error extracting DTD from {file_path.name}: {e}",
                extra={'file_path': str(file_path), 'error_type': type(e).__name__}
            )
            return None


class XMLFieldMetadata:
    """Accumulates metadata for a single XML field"""

    def __init__(
        self,
        field_path: str,
        field_name: str,
        parent_path: str,
        nesting_level: int,
        is_attribute: bool = False
    ):
        """
        Initialize XMLFieldMetadata.

        Args:
            field_path: Full dot-notation path to field
            field_name: Name of the field
            parent_path: Path to parent element
            nesting_level: Depth in XML hierarchy
            is_attribute: Whether this field is an XML attribute
        """
        self.field_path = field_path
        self.field_name = field_name
        self.parent_path = parent_path
        self.nesting_level = nesting_level
        self.is_attribute = is_attribute
        self.values = []  # Sample values
        self.types_seen = set()
        self.null_count = 0
        self.total_count = 0
        self.is_array = False

    def observe_value(self, value: Any):
        """Record observation of a value"""
        self.total_count += 1

        if value is None or value == "":
            self.null_count += 1
            self.types_seen.add('null')
        else:
            # XML values are strings, but we detect type patterns
            self.types_seen.add('string')
            self._add_sample(value)

    def _add_sample(self, value: Any):
        """Add sample value (up to 10 unique)"""
        if len(self.values) < 10 and value not in self.values:
            self.values.append(value)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary matching JSONParser output format"""
        return {
            'field_path': self.field_path,
            'field_name': self.field_name,
            'parent_path': self.parent_path,
            'nesting_level': self.nesting_level,
            'types_seen': list(self.types_seen),
            'is_array': self.is_array,
            'is_attribute': self.is_attribute,  # XML-specific
            'array_item_types': [],  # Empty for XML
            'sample_values': self.values,
            'null_count': self.null_count,
            'total_count': self.total_count,
            'null_percentage': (self.null_count / self.total_count * 100) if self.total_count > 0 else 0
        }
