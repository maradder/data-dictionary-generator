"""
Protobuf Parser for .proto and .desc files
Supports both human-readable .proto files and compiled FileDescriptorSet (.desc) files
"""

import logging
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional
from google.protobuf.descriptor_pb2 import FileDescriptorSet, FieldDescriptorProto

logger = logging.getLogger(__name__)


class ProtobufParser:
    """Parser for Protocol Buffer schema files (.proto and .desc)"""

    # Map protobuf types to human-readable names
    TYPE_MAP = {
        FieldDescriptorProto.TYPE_DOUBLE: "double",
        FieldDescriptorProto.TYPE_FLOAT: "float",
        FieldDescriptorProto.TYPE_INT64: "int64",
        FieldDescriptorProto.TYPE_UINT64: "uint64",
        FieldDescriptorProto.TYPE_INT32: "int32",
        FieldDescriptorProto.TYPE_FIXED64: "fixed64",
        FieldDescriptorProto.TYPE_FIXED32: "fixed32",
        FieldDescriptorProto.TYPE_BOOL: "bool",
        FieldDescriptorProto.TYPE_STRING: "string",
        FieldDescriptorProto.TYPE_BYTES: "bytes",
        FieldDescriptorProto.TYPE_UINT32: "uint32",
        FieldDescriptorProto.TYPE_SFIXED32: "sfixed32",
        FieldDescriptorProto.TYPE_SFIXED64: "sfixed64",
        FieldDescriptorProto.TYPE_SINT32: "sint32",
        FieldDescriptorProto.TYPE_SINT64: "sint64",
        FieldDescriptorProto.TYPE_MESSAGE: "message",
        FieldDescriptorProto.TYPE_ENUM: "enum",
        FieldDescriptorProto.TYPE_GROUP: "group",
    }

    # Map label to cardinality
    LABEL_MAP = {
        FieldDescriptorProto.LABEL_OPTIONAL: "optional",
        FieldDescriptorProto.LABEL_REQUIRED: "required",
        FieldDescriptorProto.LABEL_REPEATED: "repeated",
    }

    def __init__(self, file_path: str):
        """
        Initialize parser with file path

        Args:
            file_path: Path to .proto or .desc file
        """
        self.file_path = Path(file_path)
        self.file_extension = self.file_path.suffix.lower()

    def parse(self) -> Dict[str, Any]:
        """
        Parse the protobuf schema file

        Returns:
            Dictionary containing parsed schema information
        """
        logger.info(f"Parsing protobuf file: {self.file_path}")

        # Load FileDescriptorSet
        if self.file_extension == '.desc':
            fds = self._parse_descriptor_set()
        elif self.file_extension == '.proto':
            fds = self._compile_proto_to_descriptor()
        else:
            raise ValueError(f"Unsupported file extension: {self.file_extension}. Expected .proto or .desc")

        # Extract schema information
        schema = self._extract_schema(fds)

        logger.info(f"Successfully parsed {len(schema['messages'])} messages and {len(schema['enums'])} enums")
        return schema

    def _parse_descriptor_set(self) -> FileDescriptorSet:
        """
        Parse a .desc FileDescriptorSet file

        Returns:
            FileDescriptorSet object
        """
        logger.debug(f"Reading descriptor set from {self.file_path}")
        with open(self.file_path, 'rb') as f:
            data = f.read()

        fds = FileDescriptorSet()
        fds.ParseFromString(data)
        return fds

    def _compile_proto_to_descriptor(self) -> FileDescriptorSet:
        """
        Compile a .proto file to FileDescriptorSet using protoc
        Tries grpcio-tools first (pure Python), falls back to system protoc

        Returns:
            FileDescriptorSet object
        """
        logger.debug(f"Compiling .proto file to descriptor: {self.file_path}")

        # Create temporary file for descriptor output
        with tempfile.NamedTemporaryFile(suffix='.desc', delete=False) as tmp_file:
            tmp_path = tmp_file.name

        try:
            proto_dir = self.file_path.parent
            proto_name = self.file_path.name

            # Try grpcio-tools first (pure Python, no binary dependency)
            try:
                from grpc_tools import protoc as grpc_protoc
                import pkg_resources

                # Get grpc_tools proto include path
                proto_include = pkg_resources.resource_filename('grpc_tools', '_proto')

                # Build arguments for grpc_tools.protoc
                args = [
                    'grpc_tools.protoc',  # argv[0]
                    f'--proto_path={proto_dir}',
                    f'--proto_path={proto_include}',  # Include well-known types
                    f'--descriptor_set_out={tmp_path}',
                    '--include_imports',
                    str(self.file_path)
                ]

                logger.debug(f"Using grpcio-tools protoc: {' '.join(args)}")
                result = grpc_protoc.main(args)

                if result != 0:
                    raise RuntimeError(f"grpcio-tools protoc failed with code {result}")

            except ImportError:
                # Fall back to system protoc
                logger.debug("grpcio-tools not available, trying system protoc")

                try:
                    result = subprocess.run(['protoc', '--version'],
                                          capture_output=True,
                                          text=True,
                                          check=True)
                    logger.debug(f"Using {result.stdout.strip()}")
                except (subprocess.CalledProcessError, FileNotFoundError):
                    raise RuntimeError(
                        "Neither grpcio-tools nor system protoc compiler found.\n"
                        "Install grpcio-tools: pip install grpcio-tools\n"
                        "Or install protoc: https://grpc.io/docs/protoc-installation/"
                    )

                cmd = [
                    'protoc',
                    f'--proto_path={proto_dir}',
                    f'--descriptor_set_out={tmp_path}',
                    '--include_imports',
                    proto_name
                ]

                logger.debug(f"Running command: {' '.join(cmd)}")
                result = subprocess.run(
                    cmd,
                    cwd=proto_dir,
                    capture_output=True,
                    text=True,
                    check=True
                )

            # Read the generated descriptor
            with open(tmp_path, 'rb') as f:
                data = f.read()

            fds = FileDescriptorSet()
            fds.ParseFromString(data)
            return fds

        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to compile .proto file: {e.stderr}")
            raise RuntimeError(f"Failed to compile .proto file: {e.stderr}")
        finally:
            # Clean up temporary file
            Path(tmp_path).unlink(missing_ok=True)

    def _extract_schema(self, fds: FileDescriptorSet) -> Dict[str, Any]:
        """
        Extract schema information from FileDescriptorSet

        Args:
            fds: FileDescriptorSet object

        Returns:
            Dictionary with schema information
        """
        schema = {
            'format': 'protobuf',
            'files': [],
            'messages': [],
            'enums': [],
            'services': []
        }

        # Process each file in the descriptor set
        for file_descriptor in fds.file:
            file_info = {
                'name': file_descriptor.name,
                'package': file_descriptor.package,
                'syntax': file_descriptor.syntax or 'proto2'
            }
            schema['files'].append(file_info)

            # Extract messages
            for message in file_descriptor.message_type:
                schema['messages'].append(
                    self._extract_message(message, file_descriptor.package)
                )

            # Extract enums
            for enum in file_descriptor.enum_type:
                schema['enums'].append(
                    self._extract_enum(enum, file_descriptor.package)
                )

            # Extract services
            for service in file_descriptor.service:
                schema['services'].append(
                    self._extract_service(service, file_descriptor.package)
                )

        return schema

    def _extract_message(self, message, package: str, parent_path: str = "") -> Dict[str, Any]:
        """
        Extract message type information

        Args:
            message: MessageDescriptor
            package: Package name
            parent_path: Parent message path for nested messages

        Returns:
            Dictionary with message information
        """
        full_name = f"{package}.{parent_path}.{message.name}" if parent_path else f"{package}.{message.name}"
        full_name = full_name.lstrip('.')

        message_info = {
            'name': message.name,
            'full_name': full_name,
            'fields': [],
            'nested_messages': [],
            'nested_enums': []
        }

        # Extract fields
        for field in message.field:
            message_info['fields'].append(self._extract_field(field))

        # Extract nested messages
        for nested in message.nested_type:
            # Skip map entry types (auto-generated)
            if nested.options.map_entry:
                continue
            message_info['nested_messages'].append(
                self._extract_message(nested, package, f"{parent_path}.{message.name}" if parent_path else message.name)
            )

        # Extract nested enums
        for nested_enum in message.enum_type:
            message_info['nested_enums'].append(
                self._extract_enum(nested_enum, package, f"{parent_path}.{message.name}" if parent_path else message.name)
            )

        return message_info

    def _extract_field(self, field) -> Dict[str, Any]:
        """
        Extract field information

        Args:
            field: FieldDescriptor

        Returns:
            Dictionary with field information
        """
        field_type = self.TYPE_MAP.get(field.type, 'unknown')

        # For message and enum types, use the type_name
        if field.type in (FieldDescriptorProto.TYPE_MESSAGE, FieldDescriptorProto.TYPE_ENUM):
            # Remove leading dot and use the simple name
            type_name = field.type_name.lstrip('.')
            field_type = f"{field_type}<{type_name}>"

        field_info = {
            'name': field.name,
            'number': field.number,
            'type': field_type,
            'label': self.LABEL_MAP.get(field.label, 'optional'),
        }

        # Add default value if present
        if field.HasField('default_value'):
            field_info['default'] = field.default_value

        return field_info

    def _extract_enum(self, enum, package: str, parent_path: str = "") -> Dict[str, Any]:
        """
        Extract enum type information

        Args:
            enum: EnumDescriptor
            package: Package name
            parent_path: Parent message path for nested enums

        Returns:
            Dictionary with enum information
        """
        full_name = f"{package}.{parent_path}.{enum.name}" if parent_path else f"{package}.{enum.name}"
        full_name = full_name.lstrip('.')

        enum_info = {
            'name': enum.name,
            'full_name': full_name,
            'values': []
        }

        for value in enum.value:
            enum_info['values'].append({
                'name': value.name,
                'number': value.number
            })

        return enum_info

    def _extract_service(self, service, package: str) -> Dict[str, Any]:
        """
        Extract service information

        Args:
            service: ServiceDescriptor
            package: Package name

        Returns:
            Dictionary with service information
        """
        full_name = f"{package}.{service.name}".lstrip('.')

        service_info = {
            'name': service.name,
            'full_name': full_name,
            'methods': []
        }

        for method in service.method:
            service_info['methods'].append({
                'name': method.name,
                'input_type': method.input_type.lstrip('.'),
                'output_type': method.output_type.lstrip('.'),
                'client_streaming': method.client_streaming,
                'server_streaming': method.server_streaming
            })

        return service_info

    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse protobuf file and extract field metadata in the format expected by dictionary_service.

        Args:
            file_path: Path to .proto or .desc file (unused, uses self.file_path)

        Returns:
            {
                'fields': [...],  # List of field metadata
                'total_records': int,  # Number of messages defined
                'is_array': bool  # Always True for protobuf (multiple message types)
            }
        """
        schema = self.parse()
        fields = []

        # Convert messages to fields
        for message in schema['messages']:
            # Add the message itself as a container field
            message_path = message['full_name']

            # Process each field in the message
            for field in message['fields']:
                field_path = f"{message_path}.{field['name']}"

                # Map protobuf type to types_seen
                proto_type = field['type']
                types_seen = self._map_protobuf_type_to_standard(proto_type)

                # Determine if it's an array (repeated field)
                is_array = field['label'] == 'repeated'

                # Determine if nullable (optional in proto3, or not required in proto2)
                is_nullable = field['label'] == 'optional'

                field_metadata = {
                    'field_path': field_path,
                    'field_name': field['name'],
                    'parent_path': message_path,
                    'nesting_level': 1,  # Fields are at level 1 under message
                    'types_seen': types_seen,
                    'is_array': is_array,
                    'array_item_types': types_seen if is_array else [],
                    'sample_values': [],  # No sample data in schema files
                    'null_count': 0,
                    'total_count': 0,
                    'null_percentage': 0.0,
                    # Protobuf-specific metadata
                    'protobuf_metadata': {
                        'message_type': message['full_name'],
                        'field_number': field['number'],
                        'field_type': proto_type,
                        'label': field['label'],
                        'default': field.get('default'),
                    }
                }

                fields.append(field_metadata)

        # Add enum types as fields
        for enum in schema['enums']:
            enum_path = enum['full_name']

            for value in enum['values']:
                field_path = f"{enum_path}.{value['name']}"

                field_metadata = {
                    'field_path': field_path,
                    'field_name': value['name'],
                    'parent_path': enum_path,
                    'nesting_level': 1,
                    'types_seen': ['integer'],  # Enum values are integers
                    'is_array': False,
                    'array_item_types': [],
                    'sample_values': [value['number']],
                    'null_count': 0,
                    'total_count': 1,
                    'null_percentage': 0.0,
                    # Protobuf-specific metadata
                    'protobuf_metadata': {
                        'enum_type': enum['full_name'],
                        'enum_number': value['number'],
                    }
                }

                fields.append(field_metadata)

        # Add service methods as fields
        for service in schema['services']:
            service_path = service['full_name']

            for method in service['methods']:
                field_path = f"{service_path}.{method['name']}"

                streaming_info = []
                if method['client_streaming']:
                    streaming_info.append('client_streaming')
                if method['server_streaming']:
                    streaming_info.append('server_streaming')
                streaming = ', '.join(streaming_info) if streaming_info else 'unary'

                field_metadata = {
                    'field_path': field_path,
                    'field_name': method['name'],
                    'parent_path': service_path,
                    'nesting_level': 1,
                    'types_seen': ['string'],  # Methods are string-like
                    'is_array': False,
                    'array_item_types': [],
                    'sample_values': [],
                    'null_count': 0,
                    'total_count': 0,
                    'null_percentage': 0.0,
                    # Protobuf-specific metadata
                    'protobuf_metadata': {
                        'service_type': service['full_name'],
                        'input_type': method['input_type'],
                        'output_type': method['output_type'],
                        'streaming': streaming,
                    }
                }

                fields.append(field_metadata)

        # Calculate total_records as the number of messages (since each message is like a table/record type)
        total_records = len(schema['messages'])

        return {
            'fields': fields,
            'total_records': total_records,
            'is_array': True  # Protobuf files define multiple message types
        }

    def _map_protobuf_type_to_standard(self, proto_type: str) -> List[str]:
        """
        Map protobuf type to standard types_seen format.

        Args:
            proto_type: Protobuf type string (e.g., "int32", "string", "message<...>")

        Returns:
            List of standard type names
        """
        # Handle message and enum types (e.g., "message<package.MessageName>")
        if proto_type.startswith('message<'):
            return ['object']
        elif proto_type.startswith('enum<'):
            return ['integer']

        # Map primitive types
        type_mapping = {
            'double': ['float'],
            'float': ['float'],
            'int32': ['integer'],
            'int64': ['integer'],
            'uint32': ['integer'],
            'uint64': ['integer'],
            'sint32': ['integer'],
            'sint64': ['integer'],
            'fixed32': ['integer'],
            'fixed64': ['integer'],
            'sfixed32': ['integer'],
            'sfixed64': ['integer'],
            'bool': ['boolean'],
            'string': ['string'],
            'bytes': ['binary'],
        }

        return type_mapping.get(proto_type, ['string'])

    def get_tables(self) -> List[Dict[str, Any]]:
        """
        Convert protobuf messages to table-like structures for data dictionary

        Returns:
            List of table dictionaries
        """
        schema = self.parse()
        tables = []

        # Convert each message to a table
        for message in schema['messages']:
            table = {
                'name': message['full_name'],
                'type': 'message',
                'columns': []
            }

            for field in message['fields']:
                column = {
                    'name': field['name'],
                    'data_type': field['type'],
                    'required': field['label'] == 'required',
                    'repeated': field['label'] == 'repeated',
                    'field_number': field['number'],
                }

                if 'default' in field:
                    column['default'] = field['default']

                table['columns'].append(column)

            tables.append(table)

        # Add enums as separate tables
        for enum in schema['enums']:
            table = {
                'name': enum['full_name'],
                'type': 'enum',
                'columns': []
            }

            for value in enum['values']:
                column = {
                    'name': value['name'],
                    'data_type': 'enum_value',
                    'enum_number': value['number']
                }
                table['columns'].append(column)

            tables.append(table)

        # Add services as separate tables
        for service in schema['services']:
            table = {
                'name': service['full_name'],
                'type': 'service',
                'columns': []
            }

            for method in service['methods']:
                streaming_info = []
                if method['client_streaming']:
                    streaming_info.append('client_streaming')
                if method['server_streaming']:
                    streaming_info.append('server_streaming')

                streaming = ', '.join(streaming_info) if streaming_info else 'unary'

                column = {
                    'name': method['name'],
                    'data_type': 'rpc_method',
                    'input_type': method['input_type'],
                    'output_type': method['output_type'],
                    'streaming': streaming
                }
                table['columns'].append(column)

            tables.append(table)

        return tables
