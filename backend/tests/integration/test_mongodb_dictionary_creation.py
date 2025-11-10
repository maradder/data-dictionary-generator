"""
Integration tests for MongoDB Extended JSON dictionary creation.

Tests end-to-end flow from MongoDB JSON file to complete dictionary with
correct type mapping and semantic type assignment.
"""

import json
import tempfile
from pathlib import Path

import pytest

from src.services.dictionary_service import DictionaryService


class TestMongoDBDictionaryCreation:
    """Integration tests for MongoDB dictionary creation"""

    @pytest.fixture
    def dictionary_service(self, test_db):
        """Create dictionary service instance"""
        return DictionaryService(db=test_db)

    @pytest.fixture
    def mongodb_sample_file(self):
        """Create sample MongoDB Extended JSON file"""
        test_data = [
            {
                "_id": {"$oid": "507f1f77bcf86cd799439011"},
                "userId": {"$oid": "507f1f77bcf86cd799439012"},
                "username": "john_doe",
                "email": "john@example.com",
                "age": 30,
                "balance": {"$numberDecimal": "1234.56"},
                "loginCount": {"$numberLong": "9999999999"},
                "createdAt": {"$date": "2023-01-15T10:30:00.000Z"},
                "lastLogin": {"$date": {"$numberLong": "1673777400000"}},
                "active": True,
                "profile": {
                    "bio": "Software developer",
                    "location": "New York",
                    "memberSince": {"$date": "2020-05-01T00:00:00.000Z"}
                },
                "tags": ["developer", "python", "mongodb"],
                "avatar": {
                    "$binary": {
                        "base64": "SGVsbG8gV29ybGQ=",
                        "subType": "0"
                    }
                }
            },
            {
                "_id": {"$oid": "507f1f77bcf86cd799439013"},
                "userId": {"$oid": "507f1f77bcf86cd799439014"},
                "username": "jane_smith",
                "email": "jane@example.com",
                "age": 28,
                "balance": {"$numberDecimal": "5678.90"},
                "loginCount": {"$numberLong": "5555555555"},
                "createdAt": {"$date": "2023-02-20T14:15:00.000Z"},
                "lastLogin": {"$date": {"$numberLong": "1676900100000"}},
                "active": False,
                "profile": {
                    "bio": "Data scientist",
                    "location": "San Francisco",
                    "memberSince": {"$date": "2021-03-15T00:00:00.000Z"}
                },
                "tags": ["data-science", "python", "ml"],
                "avatar": {
                    "$binary": {
                        "base64": "RGF0YSBTY2llbmNl",
                        "subType": "0"
                    }
                }
            },
            {
                "_id": {"$oid": "507f1f77bcf86cd799439015"},
                "userId": {"$oid": "507f1f77bcf86cd799439016"},
                "username": "bob_johnson",
                "email": "bob@example.com",
                "age": 35,
                "balance": {"$numberDecimal": "999.99"},
                "loginCount": {"$numberLong": "1234567890"},
                "createdAt": {"$date": "2023-03-10T08:00:00.000Z"},
                "lastLogin": {"$date": {"$numberLong": "1678435200000"}},
                "active": True,
                "profile": {
                    "bio": "DevOps engineer",
                    "location": "Austin",
                    "memberSince": {"$date": "2019-11-20T00:00:00.000Z"}
                },
                "tags": ["devops", "kubernetes", "docker"],
                "avatar": {
                    "$binary": {
                        "base64": "RGV2T3Bz",
                        "subType": "0"
                    }
                }
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(test_data, f)
            temp_path = Path(f.name)

        yield temp_path

        # Cleanup
        temp_path.unlink()

    def test_mongodb_format_detection(self, dictionary_service, mongodb_sample_file):
        """Test that MongoDB format is correctly detected"""
        is_mongodb = dictionary_service._detect_mongodb_format(mongodb_sample_file)
        assert is_mongodb is True

    def test_standard_json_not_detected_as_mongodb(self, dictionary_service):
        """Test that standard JSON is not detected as MongoDB format"""
        standard_json = [
            {"id": 1, "name": "John", "age": 30},
            {"id": 2, "name": "Jane", "age": 28}
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(standard_json, f)
            temp_path = Path(f.name)

        try:
            is_mongodb = dictionary_service._detect_mongodb_format(temp_path)
            assert is_mongodb is False
        finally:
            temp_path.unlink()

    def test_create_mongodb_dictionary(self, dictionary_service, mongodb_sample_file):
        """Test complete dictionary creation from MongoDB Extended JSON"""
        # Create dictionary
        dictionary = dictionary_service.create_dictionary(
            file_path=mongodb_sample_file,
            name="MongoDB User Collection",
            description="Test MongoDB Extended JSON import",
            created_by="test_user",
            generate_ai_descriptions=False
        )

        # Verify dictionary created
        assert dictionary is not None
        assert dictionary.name == "MongoDB User Collection"
        assert dictionary.total_records_analyzed == 3

        # Get the latest version
        version = dictionary.versions[0]
        assert version is not None
        assert version.version_number == 1

        # Get all fields
        fields = version.fields
        assert len(fields) > 0

        # Create field lookup by name
        fields_by_name = {field.field_name: field for field in fields}

        # Test ObjectId fields
        assert '_id' in fields_by_name
        _id_field = fields_by_name['_id']
        assert _id_field.data_type == 'objectid'
        assert _id_field.semantic_type == 'identifier'
        assert _id_field.confidence_score == 95.0

        assert 'userId' in fields_by_name
        user_id_field = fields_by_name['userId']
        assert user_id_field.data_type == 'objectid'
        assert user_id_field.semantic_type == 'identifier'

        # Test Date fields
        assert 'createdAt' in fields_by_name
        created_field = fields_by_name['createdAt']
        assert created_field.data_type == 'datetime'
        assert created_field.semantic_type == 'timestamp'
        assert created_field.confidence_score == 95.0

        assert 'lastLogin' in fields_by_name
        last_login_field = fields_by_name['lastLogin']
        assert last_login_field.data_type == 'datetime'
        assert last_login_field.semantic_type == 'timestamp'

        # Test NumberDecimal fields
        assert 'balance' in fields_by_name
        balance_field = fields_by_name['balance']
        assert balance_field.data_type == 'decimal'
        assert balance_field.confidence_score == 95.0

        # Test NumberLong fields
        assert 'loginCount' in fields_by_name
        login_count_field = fields_by_name['loginCount']
        assert login_count_field.data_type == 'integer'
        assert login_count_field.confidence_score == 95.0

        # Test Binary fields
        assert 'avatar' in fields_by_name
        avatar_field = fields_by_name['avatar']
        assert avatar_field.data_type == 'binary'
        assert avatar_field.confidence_score == 95.0

        # Test standard JSON fields still work
        assert 'username' in fields_by_name
        username_field = fields_by_name['username']
        assert username_field.data_type == 'string'

        assert 'email' in fields_by_name
        email_field = fields_by_name['email']
        assert email_field.data_type == 'string'
        assert email_field.semantic_type == 'email'

        assert 'age' in fields_by_name
        age_field = fields_by_name['age']
        assert age_field.data_type == 'integer'

        assert 'active' in fields_by_name
        active_field = fields_by_name['active']
        assert active_field.data_type == 'boolean'

        # Test nested fields
        assert 'profile.bio' in [f.field_path for f in fields]
        assert 'profile.memberSince' in [f.field_path for f in fields]

        # Find nested memberSince field
        member_since_field = next(
            (f for f in fields if f.field_path == 'profile.memberSince'),
            None
        )
        assert member_since_field is not None
        assert member_since_field.data_type == 'datetime'
        assert member_since_field.semantic_type == 'timestamp'

        # Test array field
        tags_field = next(
            (f for f in fields if f.field_name == 'tags'),
            None
        )
        assert tags_field is not None
        assert tags_field.is_array is True

    def test_mongodb_dictionary_with_mixed_data(self, dictionary_service):
        """Test dictionary creation with mixed MongoDB and standard JSON"""
        mixed_data = [
            {
                "_id": {"$oid": "507f1f77bcf86cd799439011"},
                "name": "Product 1",
                "price": 29.99,  # Standard float
                "stock": 100,  # Standard integer
                "lastUpdated": {"$date": "2023-01-15T10:30:00.000Z"}
            },
            {
                "_id": {"$oid": "507f1f77bcf86cd799439012"},
                "name": "Product 2",
                "price": 49.99,
                "stock": 50,
                "lastUpdated": {"$date": "2023-01-16T11:45:00.000Z"}
            }
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(mixed_data, f)
            temp_path = Path(f.name)

        try:
            dictionary = dictionary_service.create_dictionary(
                file_path=temp_path,
                name="Mixed Format Test",
                description="Test mixed MongoDB and standard JSON",
                created_by="test_user"
            )

            version = dictionary.versions[0]
            fields = version.fields
            fields_by_name = {field.field_name: field for field in fields}

            # MongoDB types
            assert fields_by_name['_id'].data_type == 'objectid'
            assert fields_by_name['lastUpdated'].data_type == 'datetime'

            # Standard JSON types
            assert fields_by_name['name'].data_type == 'string'
            assert fields_by_name['price'].data_type == 'float'
            assert fields_by_name['stock'].data_type == 'integer'

        finally:
            temp_path.unlink()

    def test_mongodb_dictionary_backward_compatibility(self, dictionary_service):
        """Test that standard JSON files still work (backward compatibility)"""
        standard_json = [
            {"id": 1, "name": "John", "age": 30, "email": "john@example.com"},
            {"id": 2, "name": "Jane", "age": 28, "email": "jane@example.com"}
        ]

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(standard_json, f)
            temp_path = Path(f.name)

        try:
            dictionary = dictionary_service.create_dictionary(
                file_path=temp_path,
                name="Standard JSON Test",
                description="Test backward compatibility with standard JSON",
                created_by="test_user"
            )

            assert dictionary is not None
            assert dictionary.total_records_analyzed == 2

            version = dictionary.versions[0]
            fields = version.fields
            fields_by_name = {field.field_name: field for field in fields}

            # All should be standard types
            assert fields_by_name['id'].data_type == 'integer'
            assert fields_by_name['name'].data_type == 'string'
            assert fields_by_name['age'].data_type == 'integer'
            assert fields_by_name['email'].data_type == 'string'
            assert fields_by_name['email'].semantic_type == 'email'

        finally:
            temp_path.unlink()

    def test_mongodb_sample_values(self, dictionary_service, mongodb_sample_file):
        """Test that sample values are correctly extracted from MongoDB types"""
        dictionary = dictionary_service.create_dictionary(
            file_path=mongodb_sample_file,
            name="Sample Values Test",
            description="Test sample value extraction",
            created_by="test_user"
        )

        version = dictionary.versions[0]
        fields = version.fields
        fields_by_name = {field.field_name: field for field in fields}

        # Check that ObjectId sample values contain the hex string, not the wrapper
        _id_field = fields_by_name['_id']
        sample_values = _id_field.sample_values.get('values', [])
        assert len(sample_values) > 0
        # Sample should be the ObjectId hex string, not the entire object
        assert all(isinstance(v, str) and len(v) == 24 for v in sample_values)

        # Check date sample values
        created_field = fields_by_name['createdAt']
        date_samples = created_field.sample_values.get('values', [])
        assert len(date_samples) > 0
        # Should contain ISO date strings
        assert all(isinstance(v, str) for v in date_samples)
