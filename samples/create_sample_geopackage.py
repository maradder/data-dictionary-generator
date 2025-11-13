"""
Script to create a sample GeoPackage file for testing the Data Dictionary Generator.

This GeoPackage includes:
- Multiple feature layers (vector data)
- Various geometry types (POINT, LINESTRING, POLYGON)
- Coordinate reference systems (CRS)
- Spatial metadata and bounding boxes
- Realistic GIS data
"""

import sqlite3
import struct
from datetime import datetime


def create_wkb_point(x, y):
    """Create Well-Known Binary for a 2D POINT"""
    # WKB format: byte order (1=little endian) + geometry type (1=POINT) + coordinates
    return struct.pack('<BId d', 1, 1, x, y)


def create_sample_geopackage(gpkg_path='sample-geopackage.gpkg'):
    """Create a sample GeoPackage with multiple layers and geometry types"""

    # Remove existing file if present
    import os
    if os.path.exists(gpkg_path):
        os.remove(gpkg_path)

    # Connect to database
    conn = sqlite3.connect(gpkg_path)
    cursor = conn.cursor()

    print("Creating GeoPackage structure...")

    # Create required GeoPackage tables
    cursor.executescript("""
    -- ====================
    -- REQUIRED GEOPACKAGE TABLES
    -- ====================

    -- Spatial Reference Systems
    CREATE TABLE gpkg_spatial_ref_sys (
        srs_name TEXT NOT NULL,
        srs_id INTEGER NOT NULL PRIMARY KEY,
        organization TEXT NOT NULL,
        organization_coordsys_id INTEGER NOT NULL,
        definition TEXT NOT NULL,
        description TEXT
    );

    -- Insert common spatial reference systems
    INSERT INTO gpkg_spatial_ref_sys VALUES
        ('WGS 84', 4326, 'EPSG', 4326,
         'GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]]',
         'WGS 84 geographic coordinate system'),
        ('WGS 84 / Pseudo-Mercator', 3857, 'EPSG', 3857,
         'PROJCS["WGS 84 / Pseudo-Mercator",GEOGCS["WGS 84",DATUM["WGS_1984",SPHEROID["WGS 84",6378137,298.257223563]],PRIMEM["Greenwich",0],UNIT["degree",0.0174532925199433]],PROJECTION["Mercator_1SP"],PARAMETER["central_meridian",0],PARAMETER["scale_factor",1],PARAMETER["false_easting",0],PARAMETER["false_northing",0],UNIT["metre",1]]',
         'Web Mercator projection used by Google Maps, OpenStreetMap');

    -- Contents table
    CREATE TABLE gpkg_contents (
        table_name TEXT NOT NULL PRIMARY KEY,
        data_type TEXT NOT NULL,
        identifier TEXT UNIQUE,
        description TEXT DEFAULT '',
        last_change DATETIME NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ','now')),
        min_x DOUBLE,
        min_y DOUBLE,
        max_x DOUBLE,
        max_y DOUBLE,
        srs_id INTEGER,
        CONSTRAINT fk_gc_r_srs_id FOREIGN KEY (srs_id) REFERENCES gpkg_spatial_ref_sys(srs_id)
    );

    -- Geometry Columns table
    CREATE TABLE gpkg_geometry_columns (
        table_name TEXT NOT NULL,
        column_name TEXT NOT NULL,
        geometry_type_name TEXT NOT NULL,
        srs_id INTEGER NOT NULL,
        z TINYINT NOT NULL,
        m TINYINT NOT NULL,
        CONSTRAINT pk_geom_cols PRIMARY KEY (table_name, column_name),
        CONSTRAINT fk_gc_tn FOREIGN KEY (table_name) REFERENCES gpkg_contents(table_name),
        CONSTRAINT fk_gc_srs FOREIGN KEY (srs_id) REFERENCES gpkg_spatial_ref_sys(srs_id)
    );

    -- ====================
    -- USER FEATURE TABLES
    -- ====================

    -- Cities (POINT geometry)
    CREATE TABLE cities (
        fid INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        country TEXT NOT NULL,
        population INTEGER,
        capital BOOLEAN DEFAULT 0,
        area_km2 REAL,
        founded_year INTEGER,
        timezone TEXT,
        elevation_m INTEGER,
        geom BLOB
    );

    -- Parks (POLYGON geometry)
    CREATE TABLE parks (
        fid INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        park_type TEXT,
        area_hectares REAL,
        established_date DATE,
        visitors_annual INTEGER,
        has_camping BOOLEAN DEFAULT 0,
        facilities TEXT,
        geom BLOB
    );

    -- Roads (LINESTRING geometry)
    CREATE TABLE roads (
        fid INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        road_type TEXT,
        surface TEXT,
        lanes INTEGER,
        max_speed_kph INTEGER,
        length_km REAL,
        one_way BOOLEAN DEFAULT 0,
        last_maintained DATE,
        geom BLOB
    );

    -- Points of Interest (POINT geometry)
    CREATE TABLE poi (
        fid INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        category TEXT NOT NULL,
        subcategory TEXT,
        rating REAL,
        num_reviews INTEGER,
        price_level TEXT,
        phone TEXT,
        website TEXT,
        opening_hours TEXT,
        wheelchair_accessible BOOLEAN,
        geom BLOB
    );
    """)

    print("✓ GeoPackage structure created")

    # Register feature tables in gpkg_contents
    cursor.executemany("""
        INSERT INTO gpkg_contents (table_name, data_type, identifier, description, last_change, min_x, min_y, max_x, max_y, srs_id)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, [
        ('cities', 'features', 'cities', 'Major world cities with population data',
         datetime.now().isoformat(), -180.0, -90.0, 180.0, 90.0, 4326),
        ('parks', 'features', 'parks', 'National and regional parks',
         datetime.now().isoformat(), -180.0, -90.0, 180.0, 90.0, 4326),
        ('roads', 'features', 'roads', 'Road network including highways and streets',
         datetime.now().isoformat(), -180.0, -90.0, 180.0, 90.0, 4326),
        ('poi', 'features', 'poi', 'Points of interest including restaurants, hotels, attractions',
         datetime.now().isoformat(), -180.0, -90.0, 180.0, 90.0, 4326),
    ])

    # Register geometry columns
    cursor.executemany("""
        INSERT INTO gpkg_geometry_columns (table_name, column_name, geometry_type_name, srs_id, z, m)
        VALUES (?, ?, ?, ?, ?, ?)
    """, [
        ('cities', 'geom', 'POINT', 4326, 0, 0),
        ('parks', 'geom', 'POLYGON', 4326, 0, 0),
        ('roads', 'geom', 'LINESTRING', 4326, 0, 0),
        ('poi', 'geom', 'POINT', 4326, 0, 0),
    ])

    print("✓ Feature layers registered")

    # Insert sample cities
    cities_data = [
        ('New York City', 'United States', 8336817, 0, 783.8, 1624, 'America/New_York', 10, create_wkb_point(-74.0060, 40.7128)),
        ('London', 'United Kingdom', 8982000, 1, 1572.0, 47, 'Europe/London', 11, create_wkb_point(-0.1276, 51.5074)),
        ('Tokyo', 'Japan', 13960000, 1, 2191.0, 1457, 'Asia/Tokyo', 40, create_wkb_point(139.6917, 35.6895)),
        ('Paris', 'France', 2161000, 1, 105.4, 259, 'Europe/Paris', 35, create_wkb_point(2.3522, 48.8566)),
        ('Sydney', 'Australia', 5312000, 0, 12368.0, 1788, 'Australia/Sydney', 58, create_wkb_point(151.2093, -33.8688)),
        ('São Paulo', 'Brazil', 12330000, 0, 1521.0, 1554, 'America/Sao_Paulo', 760, create_wkb_point(-46.6333, -23.5505)),
        ('Mumbai', 'India', 12442373, 0, 603.4, None, 'Asia/Kolkata', 14, create_wkb_point(72.8777, 19.0760)),
        ('Cairo', 'Egypt', 9500000, 1, 528.0, 969, 'Africa/Cairo', 23, create_wkb_point(31.2357, 30.0444)),
        ('Moscow', 'Russia', 12500000, 1, 2511.0, 1147, 'Europe/Moscow', 156, create_wkb_point(37.6173, 55.7558)),
        ('Beijing', 'China', 21540000, 1, 16410.0, 1045, 'Asia/Shanghai', 43, create_wkb_point(116.4074, 39.9042)),
    ]

    cursor.executemany("""
        INSERT INTO cities (name, country, population, capital, area_km2, founded_year, timezone, elevation_m, geom)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, cities_data)

    print(f"✓ Inserted {len(cities_data)} cities")

    # Insert sample parks (using simplified WKB for demonstration)
    parks_data = [
        ('Yellowstone National Park', 'National Park', 898317.0, '1872-03-01', 4000000, 1, 'Camping, Hiking, Fishing'),
        ('Central Park', 'Urban Park', 341.0, '1857-07-21', 42000000, 0, 'Playgrounds, Ice Skating, Boating'),
        ('Yosemite National Park', 'National Park', 308074.0, '1890-10-01', 5000000, 1, 'Rock Climbing, Hiking, Camping'),
        ('Hyde Park', 'Urban Park', 142.0, '1637-01-01', 10000000, 0, 'Boating, Swimming, Events'),
    ]

    cursor.executemany("""
        INSERT INTO parks (name, park_type, area_hectares, established_date, visitors_annual, has_camping, facilities)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, parks_data)

    print(f"✓ Inserted {len(parks_data)} parks")

    # Insert sample roads
    roads_data = [
        ('Interstate 5', 'Highway', 'Asphalt', 4, 120, 2256.0, 0, '2023-06-15'),
        ('Route 66', 'Highway', 'Asphalt', 2, 90, 3940.0, 0, '2022-08-20'),
        ('Broadway', 'Avenue', 'Asphalt', 6, 40, 21.0, 0, '2024-01-10'),
        ('Pacific Coast Highway', 'Scenic Route', 'Asphalt', 2, 90, 1055.0, 0, '2023-11-05'),
        ('Fifth Avenue', 'Avenue', 'Asphalt', 4, 40, 10.0, 0, '2024-02-28'),
    ]

    cursor.executemany("""
        INSERT INTO roads (name, road_type, surface, lanes, max_speed_kph, length_km, one_way, last_maintained)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, roads_data)

    print(f"✓ Inserted {len(roads_data)} roads")

    # Insert sample POIs
    poi_data = [
        ('Statue of Liberty', 'Attraction', 'Monument', 4.7, 54231, None, '+1-212-363-3200', 'nps.gov/stli', '9:00-17:00', 1, create_wkb_point(-74.0445, 40.6892)),
        ('Eiffel Tower', 'Attraction', 'Monument', 4.6, 127548, '€€€', '+33-892-70-12-39', 'toureiffel.paris', '9:30-23:45', 1, create_wkb_point(2.2945, 48.8584)),
        ('The Louvre', 'Museum', 'Art Museum', 4.7, 96847, '€€', '+33-1-40-20-50-50', 'louvre.fr', '9:00-18:00', 1, create_wkb_point(2.3376, 48.8606)),
        ('Times Square', 'Attraction', 'Public Space', 4.5, 73294, None, None, 'timessquarenyc.org', '24/7', 1, create_wkb_point(-73.9855, 40.7580)),
        ('Sydney Opera House', 'Attraction', 'Performing Arts', 4.8, 64823, '€€€', '+61-2-9250-7111', 'sydneyoperahouse.com', '9:00-20:30', 1, create_wkb_point(151.2153, -33.8568)),
        ('Grand Canyon Visitor Center', 'Attraction', 'Nature', 4.9, 89234, '€', '+1-928-638-7888', 'nps.gov/grca', '8:00-17:00', 1, create_wkb_point(-112.1401, 36.0544)),
        ('Tokyo Skytree', 'Attraction', 'Observation Tower', 4.6, 45678, '€€', '+81-3-5302-3456', 'tokyo-skytree.jp', '8:00-22:00', 1, create_wkb_point(139.8107, 35.7101)),
    ]

    cursor.executemany("""
        INSERT INTO poi (name, category, subcategory, rating, num_reviews, price_level, phone, website, opening_hours, wheelchair_accessible, geom)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, poi_data)

    print(f"✓ Inserted {len(poi_data)} points of interest")

    # Commit and close
    conn.commit()
    conn.close()

    print(f"\n✅ Sample GeoPackage created successfully: {gpkg_path}")
    print(f"\nGeoPackage Statistics:")
    print(f"  - 4 feature layers (cities, parks, roads, poi)")
    print(f"  - 3 geometry types (POINT, LINESTRING, POLYGON)")
    print(f"  - 2 coordinate reference systems (WGS 84, Web Mercator)")
    print(f"  - {len(cities_data)} cities")
    print(f"  - {len(parks_data)} parks")
    print(f"  - {len(roads_data)} roads")
    print(f"  - {len(poi_data)} points of interest")
    print(f"  - Complete spatial metadata (bounding boxes, SRS definitions)")
    print(f"\nYou can now upload this file to test the GeoPackage parser!")


if __name__ == '__main__':
    create_sample_geopackage()
