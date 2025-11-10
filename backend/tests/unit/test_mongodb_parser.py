"""
Unit tests for MongoDB Extended JSON Parser.

Tests MongoDB type detection including ObjectId, ISODate, NumberLong,
NumberDecimal, and Binary types in various formats.
"""

import json
import tempfile
from pathlib import Path

import pytest

from src.processors.mongodb_parser import MongoDBFieldMetadata, MongoDBParser


class TestMongoDBFieldMetadata:
    """Test MongoDB field metadata detection"""

    def test_objectid_detection(self):
        """Test ObjectId detection: {"$oid": "..."}"""
        field_meta = MongoDBFieldMetadata(
            field_path="_id",
            field_name="_id",
            parent_path="",
            nesting_level=0
        )

        # Valid ObjectId
        field_meta.observe_value({"$oid": "507f1f77bcf86cd799439011"})

        assert 'mongodb_objectid' in field_meta.types_seen
        assert len(field_meta.values) == 1
        assert field_meta.values[0] == "507f1f77bcf86cd799439011"

    def test_objectid_case_insensitive(self):
        """Test ObjectId detection with uppercase hex"""
        field_meta = MongoDBFieldMetadata(
            field_path="_id",
            field_name="_id",
            parent_path="",
            nesting_level=0
        )

        # ObjectId with uppercase letters
        field_meta.observe_value({"$oid": "507F1F77BCF86CD799439011"})

        assert 'mongodb_objectid' in field_meta.types_seen
        assert field_meta.values[0] == "507F1F77BCF86CD799439011"

    def test_date_iso_string_format(self):
        """Test ISODate string format: {"$date": "2023-01-15T10:30:00.000Z"}"""
        field_meta = MongoDBFieldMetadata(
            field_path="createdAt",
            field_name="createdAt",
            parent_path="",
            nesting_level=0
        )

        # ISO date string format
        field_meta.observe_value({"$date": "2023-01-15T10:30:00.000Z"})

        assert 'mongodb_date' in field_meta.types_seen
        assert len(field_meta.values) == 1
        assert field_meta.values[0] == "2023-01-15T10:30:00.000Z"

    def test_date_iso_string_without_milliseconds(self):
        """Test ISODate without milliseconds: {"$date": "2023-01-15T10:30:00Z"}"""
        field_meta = MongoDBFieldMetadata(
            field_path="createdAt",
            field_name="createdAt",
            parent_path="",
            nesting_level=0
        )

        field_meta.observe_value({"$date": "2023-01-15T10:30:00Z"})

        assert 'mongodb_date' in field_meta.types_seen
        assert field_meta.values[0] == "2023-01-15T10:30:00Z"

    def test_date_numberlong_format(self):
        """Test Date with NumberLong: {"$date": {"$numberLong": "1673777400000"}}"""
        field_meta = MongoDBFieldMetadata(
            field_path="timestamp",
            field_name="timestamp",
            parent_path="",
            nesting_level=0
        )

        # Date with NumberLong format
        field_meta.observe_value({"$date": {"$numberLong": "1673777400000"}})

        assert 'mongodb_date' in field_meta.types_seen
        assert len(field_meta.values) == 1
        assert field_meta.values[0] == "1673777400000"

    def test_numberlong_detection(self):
        """Test NumberLong: {"$numberLong": "9223372036854775807"}"""
        field_meta = MongoDBFieldMetadata(
            field_path="bigNumber",
            field_name="bigNumber",
            parent_path="",
            nesting_level=0
        )

        field_meta.observe_value({"$numberLong": "9223372036854775807"})

        assert 'mongodb_long' in field_meta.types_seen
        assert field_meta.values[0] == "9223372036854775807"

    def test_numberdecimal_detection(self):
        """Test NumberDecimal: {"$numberDecimal": "123.45"}"""
        field_meta = MongoDBFieldMetadata(
            field_path="price",
            field_name="price",
            parent_path="",
            nesting_level=0
        )

        field_meta.observe_value({"$numberDecimal": "123.45"})

        assert 'mongodb_decimal' in field_meta.types_seen
        assert field_meta.values[0] == "123.45"

    def test_binary_detection(self):
        """Test Binary: {"$binary": {"base64": "...", "subType": "0"}}"""
        field_meta = MongoDBFieldMetadata(
            field_path="data",
            field_name="data",
            parent_path="",
            nesting_level=0
        )

        field_meta.observe_value({
            "$binary": {
                "base64": "SGVsbG8gV29ybGQ=",
                "subType": "0"
            }
        })

        assert 'mongodb_binary' in field_meta.types_seen
        assert field_meta.values[0] == "<binary>"

    def test_fallback_to_standard_json(self):
        """Test fallback to standard JSON types for non-MongoDB values"""
        field_meta = MongoDBFieldMetadata(
            field_path="name",
            field_name="name",
            parent_path="",
            nesting_level=0
        )

        # Standard JSON types should still work
        field_meta.observe_value("John Doe")
        field_meta.observe_value(42)
        field_meta.observe_value(3.14)
        field_meta.observe_value(True)
        field_meta.observe_value(None)

        assert 'string' in field_meta.types_seen
        assert 'integer' in field_meta.types_seen
        assert 'float' in field_meta.types_seen
        assert 'boolean' in field_meta.types_seen
        assert 'null' in field_meta.types_seen

    def test_mixed_mongodb_and_standard_types(self):
        """Test field with both MongoDB and standard types"""
        field_meta = MongoDBFieldMetadata(
            field_path="mixed",
            field_name="mixed",
            parent_path="",
            nesting_level=0
        )

        field_meta.observe_value({"$oid": "507f1f77bcf86cd799439011"})
        field_meta.observe_value("regular string")
        field_meta.observe_value(None)

        assert 'mongodb_objectid' in field_meta.types_seen
        assert 'string' in field_meta.types_seen
        assert 'null' in field_meta.types_seen


class TestMongoDBParser:
    """Test MongoDB parser integration"""

    def test_parse_mongodb_document(self):
        """Test parsing a complete MongoDB document"""
        # Create test file with MongoDB Extended JSON
        test_data = {
            "_id": {"$oid": "507f1f77bcf86cd799439011"},
            "name": "John Doe",
            "age": 30,
            "createdAt": {"$date": "2023-01-15T10:30:00.000Z"},
            "balance": {"$numberDecimal": "1234.56"},
            "visitCount": {"$numberLong": "9999999999"}
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = Path(f.name)

        try:
            parser = MongoDBParser()
            result = parser.parse_file(temp_path)

            assert result['is_array'] is False
            assert result['total_records'] == 1
            assert len(result['fields']) == 6

            # Check field types
            fields_by_name = {f['field_name']: f for f in result['fields']}

            # _id should be detected as mongodb_objectid
            assert 'mongodb_objectid' in fields_by_name['_id']['types_seen']

            # name should be standard string
            assert 'string' in fields_by_name['name']['types_seen']

            # age should be standard integer
            assert 'integer' in fields_by_name['age']['types_seen']

            # createdAt should be mongodb_date
            assert 'mongodb_date' in fields_by_name['createdAt']['types_seen']

            # balance should be mongodb_decimal
            assert 'mongodb_decimal' in fields_by_name['balance']['types_seen']

            # visitCount should be mongodb_long
            assert 'mongodb_long' in fields_by_name['visitCount']['types_seen']

        finally:
            temp_path.unlink()

    def test_parse_mongodb_array(self):
        """Test parsing array of MongoDB documents"""
        test_data = [
            {
                "_id": {"$oid": "507f1f77bcf86cd799439011"},
                "name": "User 1",
                "createdAt": {"$date": "2023-01-15T10:30:00.000Z"}
            },
            {
                "_id": {"$oid": "507f1f77bcf86cd799439012"},
                "name": "User 2",
                "createdAt": {"$date": "2023-01-16T11:45:00.000Z"}
            },
            {
                "_id": {"$oid": "507f1f77bcf86cd799439013"},
                "name": "User 3",
                "createdAt": {"$date": "2023-01-17T09:20:00.000Z"}
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = Path(f.name)

        try:
            parser = MongoDBParser()
            result = parser.parse_file(temp_path)

            assert result['is_array'] is True
            assert result['total_records'] == 3
            assert len(result['fields']) == 3

            fields_by_name = {f['field_name']: f for f in result['fields']}

            # All _id values should be detected as mongodb_objectid
            assert 'mongodb_objectid' in fields_by_name['_id']['types_seen']
            assert fields_by_name['_id']['total_count'] == 3

            # All createdAt values should be mongodb_date
            assert 'mongodb_date' in fields_by_name['createdAt']['types_seen']
            assert fields_by_name['createdAt']['total_count'] == 3

        finally:
            temp_path.unlink()

    def test_parse_nested_mongodb_document(self):
        """Test parsing nested MongoDB structures"""
        test_data = {
            "_id": {"$oid": "507f1f77bcf86cd799439011"},
            "user": {
                "userId": {"$oid": "507f1f77bcf86cd799439012"},
                "joinedAt": {"$date": "2023-01-15T10:30:00.000Z"},
                "profile": {
                    "name": "John Doe",
                    "age": 30
                }
            }
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = Path(f.name)

        try:
            parser = MongoDBParser()
            result = parser.parse_file(temp_path)

            fields_by_path = {f['field_path']: f for f in result['fields']}

            # Root _id
            assert 'mongodb_objectid' in fields_by_path['_id']['types_seen']

            # Nested userId
            assert 'user.userId' in fields_by_path
            assert 'mongodb_objectid' in fields_by_path['user.userId']['types_seen']

            # Nested date
            assert 'user.joinedAt' in fields_by_path
            assert 'mongodb_date' in fields_by_path['user.joinedAt']['types_seen']

            # Deep nested standard fields
            assert 'user.profile.name' in fields_by_path
            assert 'string' in fields_by_path['user.profile.name']['types_seen']

        finally:
            temp_path.unlink()

    def test_mongodb_type_wrappers_not_treated_as_nested_objects(self):
        """Test that MongoDB type wrappers don't create nested object fields"""
        test_data = {
            "_id": {"$oid": "507f1f77bcf86cd799439011"},
            "timestamp": {"$date": {"$numberLong": "1673777400000"}}
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = Path(f.name)

        try:
            parser = MongoDBParser()
            result = parser.parse_file(temp_path)

            fields_by_path = {f['field_path']: f for f in result['fields']}

            # Should only have _id and timestamp fields
            assert len(result['fields']) == 2
            assert '_id' in fields_by_path
            assert 'timestamp' in fields_by_path

            # Should NOT have nested fields like _id.$oid or timestamp.$date
            assert '_id.$oid' not in fields_by_path
            assert 'timestamp.$date' not in fields_by_path
            assert 'timestamp.$date.$numberLong' not in fields_by_path

        finally:
            temp_path.unlink()

    def test_all_mongodb_types_together(self):
        """Test document with all MongoDB Extended JSON types"""
        test_data = {
            "_id": {"$oid": "507f1f77bcf86cd799439011"},
            "created": {"$date": "2023-01-15T10:30:00.000Z"},
            "modified": {"$date": {"$numberLong": "1673777400000"}},
            "counter": {"$numberLong": "9223372036854775807"},
            "price": {"$numberDecimal": "99.99"},
            "data": {
                "$binary": {
                    "base64": "SGVsbG8gV29ybGQ=",
                    "subType": "0"
                }
            },
            "name": "Test Product",
            "active": True,
            "quantity": 10
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = Path(f.name)

        try:
            parser = MongoDBParser()
            result = parser.parse_file(temp_path)

            fields_by_name = {f['field_name']: f for f in result['fields']}

            # Verify all MongoDB types detected correctly
            assert 'mongodb_objectid' in fields_by_name['_id']['types_seen']
            assert 'mongodb_date' in fields_by_name['created']['types_seen']
            assert 'mongodb_date' in fields_by_name['modified']['types_seen']
            assert 'mongodb_long' in fields_by_name['counter']['types_seen']
            assert 'mongodb_decimal' in fields_by_name['price']['types_seen']
            assert 'mongodb_binary' in fields_by_name['data']['types_seen']

            # Verify standard types still work
            assert 'string' in fields_by_name['name']['types_seen']
            assert 'boolean' in fields_by_name['active']['types_seen']
            assert 'integer' in fields_by_name['quantity']['types_seen']

        finally:
            temp_path.unlink()
