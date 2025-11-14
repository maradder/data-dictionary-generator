"""
XML Schema (DTD and XSD) Parser

Extracts schema information from XML files including:
- DTD (Document Type Definition) validation and metadata
- XSD (XML Schema Definition) validation and metadata
- Element constraints (required, optional, cardinality)
- Attribute definitions and types
- Data type information
"""

import logging
import re
from pathlib import Path
from typing import Any
from lxml import etree

from ..core.config import settings
from ..core.exceptions import SchemaValidationError
from .timeout_utils import with_timeout

logger = logging.getLogger(__name__)


class DTDParser:
    """
    Parser for XML Document Type Definitions (DTD).
    Extracts element definitions, attributes, and cardinality constraints.
    """

    def __init__(self):
        self.elements = {}  # element_name -> definition
        self.attributes = {}  # element_name -> {attr_name -> definition}
        self.entities = {}  # entity_name -> value

    def parse_dtd(self, dtd: etree.DTD) -> dict[str, Any]:
        """
        Parse DTD and extract schema information.

        Args:
            dtd: lxml DTD object

        Returns:
            Dictionary with DTD metadata
        """
        result = {
            'has_dtd': True,
            'elements': {},
            'attributes': {},
            'entities': {}
        }

        # Parse element definitions
        for element in dtd.iterelements():
            element_name = element.name
            content_model = element.content

            result['elements'][element_name] = {
                'name': element_name,
                'content_type': self._parse_content_type(content_model),
                'content_model': str(content_model) if content_model else 'EMPTY',
                'children': self._extract_children(content_model),
                'cardinality': {}
            }

        # Parse attribute definitions
        for element in dtd.iterelements():
            element_name = element.name
            if element_name not in result['attributes']:
                result['attributes'][element_name] = {}

            for attr in element.iterattributes():
                attr_name = attr.name
                result['attributes'][element_name][attr_name] = {
                    'name': attr_name,
                    'type': attr.type,
                    'default_type': attr.default,  # REQUIRED, IMPLIED, FIXED, or None
                    'default_value': attr.default_value,
                    'allowed_values': list(attr.itervalues()) if attr.type == 'enumeration' else None
                }

        # Parse entities
        for entity in dtd.iterentities():
            result['entities'][entity.name] = {
                'name': entity.name,
                'content': entity.content
            }

        return result

    def _parse_content_type(self, content_model) -> str:
        """Determine content type from content model"""
        if content_model is None:
            return 'EMPTY'

        content_str = str(content_model)

        if content_str == '(#PCDATA)':
            return 'PCDATA'
        elif '#PCDATA' in content_str:
            return 'MIXED'
        elif content_str in ('EMPTY', 'ANY'):
            return content_str
        else:
            return 'ELEMENT'

    def _extract_children(self, content_model) -> list[dict[str, Any]]:
        """Extract child elements from content model"""
        if content_model is None:
            return []

        children = []
        content_str = str(content_model)

        # Remove PCDATA and special characters
        content_str = content_str.replace('#PCDATA', '').replace('|', ',')
        content_str = re.sub(r'[()]', '', content_str)

        # Extract element names and their cardinality
        for part in content_str.split(','):
            part = part.strip()
            if not part:
                continue

            cardinality = 'REQUIRED'
            name = part

            if part.endswith('?'):
                cardinality = 'OPTIONAL'
                name = part[:-1]
            elif part.endswith('*'):
                cardinality = 'ZERO_OR_MORE'
                name = part[:-1]
            elif part.endswith('+'):
                cardinality = 'ONE_OR_MORE'
                name = part[:-1]

            if name:
                children.append({
                    'name': name,
                    'cardinality': cardinality
                })

        return children


class XSDParser:
    """
    Parser for XML Schema Definition (XSD).
    Extracts schema information including types, elements, and constraints.
    """

    def __init__(self):
        self.namespaces = {
            'xs': 'http://www.w3.org/2001/XMLSchema',
            'xsd': 'http://www.w3.org/2001/XMLSchema'
        }

    @with_timeout(30)  # 30 second timeout for XSD parsing
    def parse_xsd(self, xsd_path: Path) -> dict[str, Any]:
        """
        Parse XSD schema file.

        Args:
            xsd_path: Path to XSD file

        Returns:
            Dictionary with XSD metadata
        """
        try:
            logger.debug(f"Parsing XSD schema: {xsd_path.name}")

            # Security: Disable network access when parsing schema
            parser = etree.XMLParser(
                no_network=not settings.XML_ALLOW_NETWORK_ACCESS,
                resolve_entities=settings.XML_ALLOW_EXTERNAL_ENTITIES
            )
            tree = etree.parse(str(xsd_path), parser)
            root = tree.getroot()

            # Update namespaces from document
            if root.nsmap:
                self.namespaces.update(root.nsmap)

            result = {
                'has_xsd': True,
                'target_namespace': root.get('targetNamespace'),
                'elements': {},
                'complex_types': {},
                'simple_types': {},
                'attributes': {}
            }

            # Parse top-level elements
            for elem in root.xpath('.//xs:element | .//xsd:element', namespaces=self.namespaces):
                elem_name = elem.get('name')
                if elem_name:
                    result['elements'][elem_name] = self._parse_element(elem)

            # Parse complex types
            for complex_type in root.xpath('.//xs:complexType | .//xsd:complexType', namespaces=self.namespaces):
                type_name = complex_type.get('name')
                if type_name:
                    result['complex_types'][type_name] = self._parse_complex_type(complex_type)

            # Parse simple types
            for simple_type in root.xpath('.//xs:simpleType | .//xsd:simpleType', namespaces=self.namespaces):
                type_name = simple_type.get('name')
                if type_name:
                    result['simple_types'][type_name] = self._parse_simple_type(simple_type)

            logger.info(
                f"Parsed XSD schema with {len(result['elements'])} elements, "
                f"{len(result['complex_types'])} complex types, {len(result['simple_types'])} simple types",
                extra={'xsd_path': str(xsd_path)}
            )

            return result

        except etree.XMLSyntaxError as e:
            logger.error(
                f"XSD syntax error in {xsd_path.name}: {e}",
                extra={'xsd_path': str(xsd_path), 'error': str(e)}
            )
            return {
                'has_xsd': True,
                'error': f"XSD syntax error: {str(e)}",
                'elements': {},
                'complex_types': {},
                'simple_types': {}
            }
        except Exception as e:
            logger.error(
                f"Error parsing XSD {xsd_path.name}: {e}",
                extra={'xsd_path': str(xsd_path), 'error_type': type(e).__name__}
            )
            return {
                'has_xsd': True,
                'error': str(e),
                'elements': {},
                'complex_types': {},
                'simple_types': {}
            }

    def _parse_element(self, elem) -> dict[str, Any]:
        """Parse XSD element definition"""
        return {
            'name': elem.get('name'),
            'type': elem.get('type'),
            'min_occurs': elem.get('minOccurs', '1'),
            'max_occurs': elem.get('maxOccurs', '1'),
            'nillable': elem.get('nillable', 'false') == 'true',
            'default': elem.get('default'),
            'fixed': elem.get('fixed')
        }

    def _parse_complex_type(self, complex_type) -> dict[str, Any]:
        """Parse XSD complex type definition"""
        result = {
            'name': complex_type.get('name'),
            'elements': [],
            'attributes': [],
            'compositor': None  # sequence, choice, all
        }

        # Find compositor (sequence, choice, all)
        for compositor_name in ['sequence', 'choice', 'all']:
            compositor = complex_type.find(f'.//xs:{compositor_name}', namespaces=self.namespaces)
            if compositor is None:
                compositor = complex_type.find(f'.//xsd:{compositor_name}', namespaces=self.namespaces)

            if compositor is not None:
                result['compositor'] = compositor_name

                # Parse child elements
                for elem in compositor.xpath('.//xs:element | .//xsd:element', namespaces=self.namespaces):
                    result['elements'].append(self._parse_element(elem))
                break

        # Parse attributes
        for attr in complex_type.xpath('.//xs:attribute | .//xsd:attribute', namespaces=self.namespaces):
            result['attributes'].append({
                'name': attr.get('name'),
                'type': attr.get('type'),
                'use': attr.get('use', 'optional'),  # required, optional, prohibited
                'default': attr.get('default'),
                'fixed': attr.get('fixed')
            })

        return result

    def _parse_simple_type(self, simple_type) -> dict[str, Any]:
        """Parse XSD simple type definition"""
        result = {
            'name': simple_type.get('name'),
            'base_type': None,
            'restrictions': []
        }

        # Find restriction
        restriction = simple_type.find('.//xs:restriction | .//xsd:restriction', namespaces=self.namespaces)
        if restriction is not None:
            result['base_type'] = restriction.get('base')

            # Parse restriction facets
            for facet in restriction:
                facet_name = etree.QName(facet.tag).localname
                facet_value = facet.get('value')
                result['restrictions'].append({
                    'type': facet_name,
                    'value': facet_value
                })

        # Find enumeration values
        enums = simple_type.xpath('.//xs:enumeration/@value | .//xsd:enumeration/@value', namespaces=self.namespaces)
        if enums:
            result['enumeration'] = enums

        return result

    @with_timeout(30)  # Use XML_VALIDATION_TIMEOUT config
    def validate_xml(self, xml_path: Path, xsd_path: Path) -> dict[str, Any]:
        """
        Validate XML file against XSD schema.

        Args:
            xml_path: Path to XML file
            xsd_path: Path to XSD schema file

        Returns:
            Validation result with errors if any
        """
        try:
            logger.debug(f"Validating {xml_path.name} against {xsd_path.name}")

            # Security: Disable network access when parsing schema and XML
            parser = etree.XMLParser(
                no_network=not settings.XML_ALLOW_NETWORK_ACCESS,
                resolve_entities=settings.XML_ALLOW_EXTERNAL_ENTITIES
            )

            # Parse schema
            schema_doc = etree.parse(str(xsd_path), parser)
            schema = etree.XMLSchema(schema_doc)

            # Parse XML
            xml_doc = etree.parse(str(xml_path), parser)

            # Validate
            is_valid = schema.validate(xml_doc)

            result = {
                'is_valid': is_valid,
                'errors': [
                    {
                        'line': error.line,
                        'column': error.column,
                        'message': error.message,
                        'type': error.type_name
                    }
                    for error in schema.error_log
                ]
            }

            if is_valid:
                logger.info(
                    f"XML validation successful: {xml_path.name}",
                    extra={'xml_path': str(xml_path), 'xsd_path': str(xsd_path)}
                )
            else:
                logger.warning(
                    f"XML validation failed: {xml_path.name} has {len(result['errors'])} error(s)",
                    extra={'xml_path': str(xml_path), 'xsd_path': str(xsd_path), 'errors': len(result['errors'])}
                )

            return result

        except etree.XMLSchemaParseError as e:
            logger.error(
                f"XSD schema parsing error: {e}",
                extra={'xsd_path': str(xsd_path), 'error': str(e)}
            )
            return {
                'is_valid': False,
                'errors': [{'message': f"Schema parsing error: {str(e)}", 'type': 'schema_error'}]
            }
        except etree.XMLSyntaxError as e:
            logger.error(
                f"XML syntax error during validation: {e}",
                extra={'xml_path': str(xml_path), 'error': str(e)}
            )
            return {
                'is_valid': False,
                'errors': [{'message': f"XML syntax error: {str(e)}", 'type': 'syntax_error', 'line': getattr(e, 'lineno', None)}]
            }
        except Exception as e:
            logger.error(
                f"Unexpected error during validation: {e}",
                extra={'xml_path': str(xml_path), 'xsd_path': str(xsd_path), 'error_type': type(e).__name__}
            )
            return {
                'is_valid': False,
                'errors': [{'message': str(e), 'type': 'exception'}]
            }


class XMLSchemaEnhancer:
    """
    Enhances XML field metadata with DTD/XSD schema information.
    """

    def __init__(self):
        self.dtd_parser = DTDParser()
        self.xsd_parser = XSDParser()

    def enhance_fields(
        self,
        fields: list[dict[str, Any]],
        dtd_info: dict[str, Any] | None,
        xsd_info: dict[str, Any] | None
    ) -> list[dict[str, Any]]:
        """
        Enhance field metadata with schema information.

        Args:
            fields: List of field dictionaries
            dtd_info: DTD metadata (if available)
            xsd_info: XSD metadata (if available)

        Returns:
            Enhanced field list
        """
        for field in fields:
            field_name = field['field_name']
            parent_path = field.get('parent_path', '')

            # Add DTD information
            if dtd_info and dtd_info.get('has_dtd'):
                field['dtd_metadata'] = self._get_dtd_metadata(
                    field_name, parent_path, dtd_info
                )

            # Add XSD information
            if xsd_info and xsd_info.get('has_xsd'):
                field['xsd_metadata'] = self._get_xsd_metadata(
                    field_name, parent_path, xsd_info
                )

        return fields

    def _get_dtd_metadata(
        self,
        field_name: str,
        parent_path: str,
        dtd_info: dict[str, Any]
    ) -> dict[str, Any]:
        """Extract DTD metadata for a specific field"""
        metadata = {}

        # Check if field is an element
        if field_name in dtd_info['elements']:
            elem_def = dtd_info['elements'][field_name]
            metadata['element'] = {
                'content_type': elem_def['content_type'],
                'content_model': elem_def['content_model'],
                'children': elem_def['children']
            }

        # Check if field is an attribute
        if field_name.startswith('@'):
            attr_name = field_name[1:]  # Remove @ prefix
            parent_element = parent_path.split('.')[-1] if parent_path else None

            if parent_element and parent_element in dtd_info['attributes']:
                if attr_name in dtd_info['attributes'][parent_element]:
                    attr_def = dtd_info['attributes'][parent_element][attr_name]
                    metadata['attribute'] = {
                        'type': attr_def['type'],
                        'required': attr_def['default_type'] == 'REQUIRED',
                        'default_value': attr_def['default_value'],
                        'allowed_values': attr_def['allowed_values']
                    }

        return metadata if metadata else None

    def _get_xsd_metadata(
        self,
        field_name: str,
        parent_path: str,
        xsd_info: dict[str, Any]
    ) -> dict[str, Any]:
        """Extract XSD metadata for a specific field"""
        metadata = {}

        # Check if field is a top-level element
        if field_name in xsd_info['elements']:
            elem_def = xsd_info['elements'][field_name]
            metadata['element'] = {
                'type': elem_def['type'],
                'min_occurs': elem_def['min_occurs'],
                'max_occurs': elem_def['max_occurs'],
                'required': elem_def['min_occurs'] != '0',
                'repeating': elem_def['max_occurs'] not in ('1', '0'),
                'nillable': elem_def['nillable'],
                'default': elem_def['default']
            }

        return metadata if metadata else None
