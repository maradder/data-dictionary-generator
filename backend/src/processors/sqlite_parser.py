"""
SQLite Parser for extracting database schema and metadata.

This module provides the SQLiteParser class for parsing SQLite database files,
extracting complete schema information including tables, columns, data types,
constraints, and sample values.
"""

import sqlite3
from pathlib import Path
from typing import Any
from collections import defaultdict


class SQLiteParser:
    """
    SQLite database parser for schema extraction.
    Extracts table structures, columns, constraints, and sample values.
    """

    def __init__(self, max_samples: int = 1000):
        """
        Initialize SQLiteParser.

        Args:
            max_samples: Maximum number of rows to sample per table
        """
        self.max_samples = max_samples

    def parse_file(self, file_path: Path) -> dict[str, Any]:
        """
        Parse SQLite database file and extract schema metadata.

        Args:
            file_path: Path to SQLite database file

        Returns:
            {
                'fields': [...],  # List of field metadata (tables and columns)
                'total_records': int,  # Total rows across all tables
                'is_array': bool  # Always True for database tables
            }

        Raises:
            sqlite3.Error: If database cannot be opened or queried
        """
        # Open database in read-only mode for security
        uri = f"file:{file_path}?mode=ro"
        try:
            conn = sqlite3.connect(uri, uri=True, timeout=10.0)
            conn.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            raise ValueError(f"Cannot open SQLite database: {e}")

        try:
            fields_map = {}
            total_records = 0

            # Get list of all tables (excluding system tables)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table'
                AND name NOT LIKE 'sqlite_%'
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]

            # Process each table
            for table_name in tables:
                table_records = self._process_table(
                    conn, table_name, fields_map
                )
                total_records += table_records

            return {
                'fields': [field.to_dict() for field in fields_map.values()],
                'total_records': total_records,
                'is_array': True  # Database has multiple tables
            }

        finally:
            conn.close()

    def _process_table(
        self,
        conn: sqlite3.Connection,
        table_name: str,
        fields_map: dict[str, 'SQLiteFieldMetadata']
    ) -> int:
        """
        Process a single table and extract all column metadata.

        Args:
            conn: Database connection
            table_name: Name of table to process
            fields_map: Dictionary to accumulate field metadata

        Returns:
            Number of records in the table
        """
        cursor = conn.cursor()

        # Get table row count
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {self._quote_identifier(table_name)}")
            table_row_count = cursor.fetchone()[0]
        except sqlite3.Error:
            table_row_count = 0

        # Get column information via PRAGMA
        cursor.execute(f"PRAGMA table_info({self._quote_identifier(table_name)})")
        columns = cursor.fetchall()

        # Get primary keys
        cursor.execute(f"PRAGMA table_info({self._quote_identifier(table_name)})")
        primary_keys = {row['name'] for row in cursor.fetchall() if row['pk'] > 0}

        # Get foreign keys
        cursor.execute(f"PRAGMA foreign_key_list({self._quote_identifier(table_name)})")
        foreign_keys = {}
        for row in cursor.fetchall():
            col_name = row['from']
            ref_table = row['table']
            ref_col = row['to']
            foreign_keys[col_name] = f"{ref_table}({ref_col})"

        # Get indexes
        cursor.execute(f"PRAGMA index_list({self._quote_identifier(table_name)})")
        indexes = cursor.fetchall()
        indexed_columns = set()
        unique_columns = set()

        for index in indexes:
            index_name = index['name']
            is_unique = index['unique']

            # Get columns in this index
            cursor.execute(f"PRAGMA index_info({self._quote_identifier(index_name)})")
            for idx_col in cursor.fetchall():
                col_name = idx_col['name']
                indexed_columns.add(col_name)
                if is_unique:
                    unique_columns.add(col_name)

        # Process each column
        for column in columns:
            col_name = column['name']
            col_type = column['type']
            not_null = column['notnull']
            default_value = column['dflt_value']
            is_pk = column['pk'] > 0

            field_path = f"{table_name}.{col_name}"

            # Create field metadata
            field_meta = SQLiteFieldMetadata(
                field_path=field_path,
                field_name=col_name,
                parent_path=table_name,
                nesting_level=1,  # Tables at 0, columns at 1
                table_name=table_name,
                column_type=col_type,
                is_primary_key=is_pk,
                is_foreign_key=col_name in foreign_keys,
                foreign_key_ref=foreign_keys.get(col_name),
                is_unique=col_name in unique_columns,
                is_indexed=col_name in indexed_columns,
                is_not_null=not_null,
                default_value=default_value
            )

            # Sample column data
            if table_row_count > 0:
                self._sample_column_data(
                    conn, table_name, col_name, field_meta, table_row_count
                )

            fields_map[field_path] = field_meta

        return table_row_count

    def _sample_column_data(
        self,
        conn: sqlite3.Connection,
        table_name: str,
        column_name: str,
        field_meta: 'SQLiteFieldMetadata',
        total_count: int
    ):
        """
        Sample data from a column and update field metadata.

        Args:
            conn: Database connection
            table_name: Name of table
            column_name: Name of column
            field_meta: Field metadata object to update
            total_count: Total rows in table
        """
        cursor = conn.cursor()
        quoted_table = self._quote_identifier(table_name)
        quoted_column = self._quote_identifier(column_name)

        try:
            # Get null count
            cursor.execute(f"""
                SELECT COUNT(*) FROM {quoted_table}
                WHERE {quoted_column} IS NULL
            """)
            null_count = cursor.fetchone()[0]
            field_meta.null_count = null_count
            field_meta.total_count = total_count

            # Sample distinct values (up to max_samples)
            sample_limit = min(self.max_samples, total_count)
            cursor.execute(f"""
                SELECT DISTINCT {quoted_column}
                FROM {quoted_table}
                WHERE {quoted_column} IS NOT NULL
                LIMIT {sample_limit}
            """)

            for row in cursor.fetchall():
                value = row[0]
                field_meta.observe_value(value)

        except sqlite3.Error:
            # If sampling fails, just set counts to what we know
            field_meta.total_count = total_count
            field_meta.null_count = 0

    def _quote_identifier(self, identifier: str) -> str:
        """
        Quote SQL identifier to prevent SQL injection and handle special characters.

        Args:
            identifier: Table or column name

        Returns:
            Quoted identifier safe for SQL
        """
        # SQLite uses double quotes for identifiers
        escaped = identifier.replace('"', '""')
        return f'"{escaped}"'


class SQLiteFieldMetadata:
    """Accumulates metadata for a single SQLite column"""

    def __init__(
        self,
        field_path: str,
        field_name: str,
        parent_path: str,
        nesting_level: int,
        table_name: str,
        column_type: str,
        is_primary_key: bool = False,
        is_foreign_key: bool = False,
        foreign_key_ref: str | None = None,
        is_unique: bool = False,
        is_indexed: bool = False,
        is_not_null: bool = False,
        default_value: Any = None
    ):
        """
        Initialize SQLiteFieldMetadata.

        Args:
            field_path: Full path to field (table.column)
            field_name: Name of the column
            parent_path: Table name
            nesting_level: Depth in hierarchy (1 for columns)
            table_name: Name of the table
            column_type: SQLite column type
            is_primary_key: Whether column is a primary key
            is_foreign_key: Whether column is a foreign key
            foreign_key_ref: Foreign key reference (e.g., "users(id)")
            is_unique: Whether column has unique constraint
            is_indexed: Whether column is indexed
            is_not_null: Whether column has NOT NULL constraint
            default_value: Default value for column
        """
        self.field_path = field_path
        self.field_name = field_name
        self.parent_path = parent_path
        self.nesting_level = nesting_level
        self.table_name = table_name
        self.column_type = column_type.upper() if column_type else ""
        self.is_primary_key = is_primary_key
        self.is_foreign_key = is_foreign_key
        self.foreign_key_ref = foreign_key_ref
        self.is_unique = is_unique
        self.is_indexed = is_indexed
        self.is_not_null = is_not_null
        self.default_value = default_value

        self.values = []  # Sample values
        self.types_seen = set()
        self.null_count = 0
        self.total_count = 0

    def observe_value(self, value: Any):
        """
        Record observation of a value.

        Args:
            value: Value observed in the column
        """
        if value is None:
            self.types_seen.add('null')
        elif isinstance(value, bool):
            self.types_seen.add('boolean')
            self._add_sample(value)
        elif isinstance(value, int):
            self.types_seen.add('integer')
            self._add_sample(value)
        elif isinstance(value, float):
            self.types_seen.add('float')
            self._add_sample(value)
        elif isinstance(value, str):
            self.types_seen.add('string')
            self._add_sample(value)
        elif isinstance(value, bytes):
            self.types_seen.add('binary')
            # Don't sample binary data, just note its presence
        else:
            self.types_seen.add('string')
            self._add_sample(str(value))

    def _add_sample(self, value: Any):
        """Add sample value (up to 10 unique)"""
        if len(self.values) < 10 and value not in self.values:
            self.values.append(value)

    def _map_sqlite_type(self) -> str:
        """
        Map SQLite type to standard type.

        SQLite type affinity rules:
        - INTEGER, INT, TINYINT, SMALLINT, MEDIUMINT, BIGINT -> integer
        - REAL, DOUBLE, FLOAT -> float
        - TEXT, VARCHAR, CHAR, CLOB -> string
        - BLOB -> binary
        - NUMERIC, DECIMAL -> float
        - BOOLEAN, BOOL -> boolean
        - DATE, DATETIME, TIMESTAMP -> string (will be detected as date by semantic analyzer)
        """
        col_type_upper = self.column_type.upper()

        if not col_type_upper:
            # No type specified - SQLite allows this
            # Infer from observed values
            if 'integer' in self.types_seen:
                return 'integer'
            elif 'float' in self.types_seen:
                return 'float'
            elif 'boolean' in self.types_seen:
                return 'boolean'
            elif 'binary' in self.types_seen:
                return 'binary'
            else:
                return 'string'

        # Check for integer types
        if any(t in col_type_upper for t in ['INT', 'TINYINT', 'SMALLINT', 'MEDIUMINT', 'BIGINT']):
            return 'integer'

        # Check for float types
        if any(t in col_type_upper for t in ['REAL', 'DOUBLE', 'FLOAT', 'NUMERIC', 'DECIMAL']):
            return 'float'

        # Check for text types
        if any(t in col_type_upper for t in ['TEXT', 'VARCHAR', 'CHAR', 'CLOB', 'STRING']):
            return 'string'

        # Check for binary types
        if 'BLOB' in col_type_upper:
            return 'binary'

        # Check for boolean types
        if any(t in col_type_upper for t in ['BOOL', 'BOOLEAN']):
            return 'boolean'

        # Check for date/time types (stored as string or integer in SQLite)
        if any(t in col_type_upper for t in ['DATE', 'TIME', 'DATETIME', 'TIMESTAMP']):
            return 'string'

        # Default to string for unknown types
        return 'string'

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary matching JSONParser/XMLParser output format"""
        # Determine primary type
        primary_type = self._map_sqlite_type()

        # Build types_seen list
        types_list = list(self.types_seen) if self.types_seen else [primary_type]
        if 'null' not in types_list and self.null_count > 0:
            types_list.append('null')

        return {
            'field_path': self.field_path,
            'field_name': self.field_name,
            'parent_path': self.parent_path,
            'nesting_level': self.nesting_level,
            'types_seen': types_list,
            'is_array': False,  # SQL columns are not arrays
            'array_item_types': [],
            'sample_values': self.values,
            'null_count': self.null_count,
            'total_count': self.total_count,
            'null_percentage': (self.null_count / self.total_count * 100) if self.total_count > 0 else 0,
            # SQLite-specific metadata
            'sqlite_metadata': {
                'table_name': self.table_name,
                'column_type': self.column_type,
                'is_primary_key': self.is_primary_key,
                'is_foreign_key': self.is_foreign_key,
                'foreign_key_ref': self.foreign_key_ref,
                'is_unique': self.is_unique,
                'is_indexed': self.is_indexed,
                'is_not_null': self.is_not_null,
                'default_value': self.default_value,
            }
        }
