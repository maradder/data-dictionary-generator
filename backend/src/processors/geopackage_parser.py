"""
GeoPackage Parser for extracting geospatial database schema and metadata.

GeoPackage is an open, standards-based, platform-independent, portable,
self-describing format for transferring geospatial information. It is built
on top of SQLite and adds geospatial capabilities.

This parser extends SQLiteParser to add:
- Geometry column detection and type identification
- Coordinate Reference System (CRS) information
- Spatial extent (bounding boxes)
- Layer metadata from gpkg_contents
- Spatial index detection
"""

import sqlite3
from pathlib import Path
from typing import Any

from .sqlite_parser import SQLiteParser, SQLiteFieldMetadata


class GeoPackageParser(SQLiteParser):
    """
    GeoPackage database parser for geospatial schema extraction.
    Extends SQLiteParser with spatial awareness.
    """

    def __init__(self, max_samples: int = 1000):
        """
        Initialize GeoPackageParser.

        Args:
            max_samples: Maximum number of rows to sample per table
        """
        super().__init__(max_samples)
        self.geometry_columns = {}  # table_name.column_name -> geometry info
        self.spatial_ref_systems = {}  # srs_id -> SRS info
        self.contents_metadata = {}  # table_name -> contents info

    def parse_file(self, file_path: Path) -> dict[str, Any]:
        """
        Parse GeoPackage file and extract schema with spatial metadata.

        Args:
            file_path: Path to GeoPackage (.gpkg) file

        Returns:
            {
                'fields': [...],  # List of field metadata with spatial info
                'total_records': int,
                'is_array': bool,
                'geopackage_metadata': {
                    'is_valid_geopackage': bool,
                    'geometry_columns': [...],
                    'spatial_ref_systems': [...],
                    'layers': [...]
                }
            }

        Raises:
            ValueError: If file is not a valid SQLite/GeoPackage database
        """
        # Open database in read-only mode
        uri = f"file:{file_path}?mode=ro"
        try:
            conn = sqlite3.connect(uri, uri=True, timeout=10.0)
            conn.row_factory = sqlite3.Row
        except sqlite3.Error as e:
            raise ValueError(f"Cannot open GeoPackage database: {e}")

        try:
            # Check if this is a valid GeoPackage
            is_valid_gpkg = self._validate_geopackage(conn)

            if is_valid_gpkg:
                # Extract GeoPackage-specific metadata
                self._extract_spatial_ref_systems(conn)
                self._extract_contents_metadata(conn)
                self._extract_geometry_columns(conn)

            # Use parent SQLiteParser to extract basic schema
            fields_map = {}
            total_records = 0

            # Get list of user tables (excluding GeoPackage metadata tables)
            cursor = conn.cursor()
            cursor.execute("""
                SELECT name FROM sqlite_master
                WHERE type='table'
                AND name NOT LIKE 'sqlite_%'
                AND name NOT LIKE 'gpkg_%'
                AND name NOT LIKE 'rtree_%'
                ORDER BY name
            """)
            tables = [row[0] for row in cursor.fetchall()]

            # Process each table
            for table_name in tables:
                table_records = self._process_table(
                    conn, table_name, fields_map
                )
                total_records += table_records

            # Enhance fields with GeoPackage metadata
            if is_valid_gpkg:
                self._enhance_fields_with_spatial_info(fields_map)

            result = {
                'fields': [field.to_dict() for field in fields_map.values()],
                'total_records': total_records,
                'is_array': True
            }

            # Add GeoPackage-specific metadata
            if is_valid_gpkg:
                result['geopackage_metadata'] = {
                    'is_valid_geopackage': True,
                    'geometry_columns': self._format_geometry_columns(),
                    'spatial_ref_systems': self._format_spatial_ref_systems(),
                    'layers': self._format_contents_metadata()
                }

            return result

        finally:
            conn.close()

    def _validate_geopackage(self, conn: sqlite3.Connection) -> bool:
        """
        Check if database is a valid GeoPackage.

        A valid GeoPackage must have:
        - gpkg_contents table
        - gpkg_geometry_columns table
        - gpkg_spatial_ref_sys table

        Args:
            conn: Database connection

        Returns:
            True if valid GeoPackage, False otherwise
        """
        cursor = conn.cursor()

        required_tables = [
            'gpkg_contents',
            'gpkg_geometry_columns',
            'gpkg_spatial_ref_sys'
        ]

        try:
            for table in required_tables:
                cursor.execute("""
                    SELECT COUNT(*) FROM sqlite_master
                    WHERE type='table' AND name=?
                """, (table,))

                if cursor.fetchone()[0] == 0:
                    return False

            return True
        except sqlite3.Error:
            return False

    def _extract_spatial_ref_systems(self, conn: sqlite3.Connection):
        """
        Extract Spatial Reference System information.

        Args:
            conn: Database connection
        """
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT srs_name, srs_id, organization, organization_coordsys_id,
                       definition, description
                FROM gpkg_spatial_ref_sys
            """)

            for row in cursor.fetchall():
                srs_id = row['srs_id']
                self.spatial_ref_systems[srs_id] = {
                    'srs_name': row['srs_name'],
                    'srs_id': srs_id,
                    'organization': row['organization'],
                    'organization_coordsys_id': row['organization_coordsys_id'],
                    'definition': row['definition'],
                    'description': row['description']
                }
        except sqlite3.Error:
            pass  # Table might not exist or be readable

    def _extract_contents_metadata(self, conn: sqlite3.Connection):
        """
        Extract layer metadata from gpkg_contents table.

        Args:
            conn: Database connection
        """
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT table_name, data_type, identifier, description,
                       last_change, min_x, min_y, max_x, max_y, srs_id
                FROM gpkg_contents
            """)

            for row in cursor.fetchall():
                table_name = row['table_name']
                self.contents_metadata[table_name] = {
                    'data_type': row['data_type'],
                    'identifier': row['identifier'],
                    'description': row['description'],
                    'last_change': row['last_change'],
                    'bbox': {
                        'min_x': row['min_x'],
                        'min_y': row['min_y'],
                        'max_x': row['max_x'],
                        'max_y': row['max_y']
                    } if row['min_x'] is not None else None,
                    'srs_id': row['srs_id']
                }
        except sqlite3.Error:
            pass

    def _extract_geometry_columns(self, conn: sqlite3.Connection):
        """
        Extract geometry column information.

        Args:
            conn: Database connection
        """
        cursor = conn.cursor()

        try:
            cursor.execute("""
                SELECT table_name, column_name, geometry_type_name,
                       srs_id, z, m
                FROM gpkg_geometry_columns
            """)

            for row in cursor.fetchall():
                table_name = row['table_name']
                column_name = row['column_name']
                key = f"{table_name}.{column_name}"

                self.geometry_columns[key] = {
                    'geometry_type': row['geometry_type_name'],
                    'srs_id': row['srs_id'],
                    'has_z': row['z'] == 1 or row['z'] == 2,  # 1=mandatory, 2=optional
                    'has_m': row['m'] == 1 or row['m'] == 2,
                    'dimensions': self._get_dimension_string(row['z'], row['m'])
                }
        except sqlite3.Error:
            pass

    def _get_dimension_string(self, z: int, m: int) -> str:
        """
        Get dimension string for geometry.

        Args:
            z: Z coordinate flag (0=prohibited, 1=mandatory, 2=optional)
            m: M coordinate flag (0=prohibited, 1=mandatory, 2=optional)

        Returns:
            Dimension string (e.g., "XY", "XYZ", "XYM", "XYZM")
        """
        dims = "XY"
        if z in (1, 2):
            dims += "Z"
        if m in (1, 2):
            dims += "M"
        return dims

    def _enhance_fields_with_spatial_info(
        self,
        fields_map: dict[str, SQLiteFieldMetadata]
    ):
        """
        Enhance field metadata with GeoPackage spatial information.

        Args:
            fields_map: Dictionary of field metadata objects
        """
        for field_path, field_meta in fields_map.items():
            # Check if this field is a geometry column
            if field_path in self.geometry_columns:
                geom_info = self.geometry_columns[field_path]
                srs_id = geom_info['srs_id']

                # Add geometry information to field metadata
                if not hasattr(field_meta, 'geopackage_metadata'):
                    field_meta.geopackage_metadata = {}

                field_meta.geopackage_metadata = {
                    'is_geometry': True,
                    'geometry_type': geom_info['geometry_type'],
                    'dimensions': geom_info['dimensions'],
                    'has_z': geom_info['has_z'],
                    'has_m': geom_info['has_m'],
                    'srs_id': srs_id,
                    'coordinate_system': self.spatial_ref_systems.get(srs_id, {}).get('srs_name'),
                    'epsg_code': self.spatial_ref_systems.get(srs_id, {}).get('organization_coordsys_id')
                }

            # Add layer metadata if table has it
            table_name = field_meta.table_name
            if table_name in self.contents_metadata:
                content_info = self.contents_metadata[table_name]

                if not hasattr(field_meta, 'geopackage_metadata'):
                    field_meta.geopackage_metadata = {}

                field_meta.geopackage_metadata['layer_info'] = {
                    'data_type': content_info['data_type'],
                    'identifier': content_info['identifier'],
                    'description': content_info['description'],
                    'bbox': content_info['bbox']
                }

    def _format_geometry_columns(self) -> list[dict[str, Any]]:
        """Format geometry columns metadata for output"""
        return [
            {
                'field_path': key,
                'geometry_type': info['geometry_type'],
                'dimensions': info['dimensions'],
                'srs_id': info['srs_id'],
                'coordinate_system': self.spatial_ref_systems.get(info['srs_id'], {}).get('srs_name')
            }
            for key, info in self.geometry_columns.items()
        ]

    def _format_spatial_ref_systems(self) -> list[dict[str, Any]]:
        """Format spatial reference systems for output"""
        return [
            {
                'srs_id': srs_id,
                'srs_name': info['srs_name'],
                'organization': info['organization'],
                'epsg_code': info['organization_coordsys_id'],
                'description': info['description']
            }
            for srs_id, info in self.spatial_ref_systems.items()
        ]

    def _format_contents_metadata(self) -> list[dict[str, Any]]:
        """Format contents metadata for output"""
        return [
            {
                'table_name': table_name,
                'data_type': info['data_type'],
                'identifier': info['identifier'],
                'description': info['description'],
                'last_change': info['last_change'],
                'bbox': info['bbox'],
                'srs_id': info['srs_id']
            }
            for table_name, info in self.contents_metadata.items()
        ]


class GeoPackageFieldMetadata(SQLiteFieldMetadata):
    """
    Extended field metadata for GeoPackage columns.
    Adds spatial information to base SQLite metadata.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.geopackage_metadata = {}

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary with GeoPackage metadata"""
        result = super().to_dict()

        # Add GeoPackage-specific metadata if present
        if hasattr(self, 'geopackage_metadata') and self.geopackage_metadata:
            result['geopackage_metadata'] = self.geopackage_metadata

        return result
