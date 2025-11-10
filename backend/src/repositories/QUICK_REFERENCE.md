# Repository Layer Quick Reference

## Import Pattern
```python
from repositories import (
    BaseRepository,
    DictionaryRepository,
    VersionRepository,
    FieldRepository,
    AnnotationRepository
)
from core.database import get_db
```

## Initialization
```python
db = next(get_db())  # Get database session

dict_repo = DictionaryRepository(db)
version_repo = VersionRepository(db)
field_repo = FieldRepository(db)
annotation_repo = AnnotationRepository(db)
```

## Common Operations (Available on All Repositories)

### Basic CRUD
```python
# Get by ID
entity = repo.get_by_id(entity_id)

# Create
entity = repo.create(name="example", **kwargs)

# Update
entity = repo.update(entity_id, name="new_name")

# Delete
success = repo.delete(entity_id)

# Check existence
exists = repo.exists(entity_id)
```

### Listing & Pagination
```python
# Get all with pagination
entities = repo.get_all(skip=0, limit=20, order_by="created_at", order_dir="desc")

# Paginate with total count
items, total = repo.paginate(page=1, page_size=20, order_by="created_at")

# Count
total = repo.count(filters={"is_active": True})

# Filter
entities = repo.filter(
    filters={"status": "active"},
    skip=0,
    limit=100,
    order_by="name"
)
```

## DictionaryRepository Specific

```python
# By name
dictionary = dict_repo.get_by_name("customer_data")

# With versions loaded
dictionary = dict_repo.get_by_id_with_versions(dict_id)

# List with latest version
dictionaries = dict_repo.list_with_latest_version(limit=20)

# Search
results = dict_repo.search_by_name("customer")

# Check name exists
exists = dict_repo.exists_by_name("name", exclude_id=dict_id)

# Recent dictionaries
recent = dict_repo.get_recent(limit=10)

# Update metadata
dictionary = dict_repo.update_metadata(dict_id, {"key": "value"})
```

## VersionRepository Specific

```python
# All versions for dictionary
versions = version_repo.get_by_dictionary(dict_id)

# Latest version
latest = version_repo.get_latest_version(dict_id)

# Latest with fields loaded
latest = version_repo.get_latest_version_with_fields(dict_id)

# Create new version (auto-increments version number)
version = version_repo.create_new_version(
    dictionary_id=dict_id,
    schema_hash="abc123...",
    created_by="user@example.com"
)

# Find by schema hash
version = version_repo.get_by_schema_hash(dict_id, schema_hash)

# Check if schema exists
exists = version_repo.schema_exists(dict_id, schema_hash)

# Get specific version number
version = version_repo.get_by_version_number(dict_id, 5)

# Version range
versions = version_repo.get_version_range(dict_id, start=1, end=10)

# Update stats
version = version_repo.update_processing_stats(version_id, stats_dict)

# Cleanup old versions
deleted = version_repo.delete_old_versions(dict_id, keep_latest=10)
```

## FieldRepository Specific

```python
# All fields for version
fields = field_repo.get_by_version(version_id)

# With annotations loaded (prevents N+1)
fields = field_repo.get_fields_with_annotations(version_id)

# Bulk insert
fields = field_repo.bulk_insert_fields(field_data_list)

# Filter by type
string_fields = field_repo.get_by_type(version_id, "string")

# Filter by semantic type
email_fields = field_repo.get_by_semantic_type(version_id, "email")

# PII fields
pii_fields = field_repo.get_pii_fields(version_id)
ssn_fields = field_repo.get_by_pii_type(version_id, "ssn")

# Nullable/array fields
nullable = field_repo.get_nullable_fields(version_id)
arrays = field_repo.get_array_fields(version_id)

# By nesting level
top_level = field_repo.get_by_nesting_level(version_id, 0)

# By exact path
field = field_repo.get_by_field_path(version_id, "user.email")

# Search by name
results = field_repo.search_by_name(version_id, "email")

# High cardinality (potential unique IDs)
unique_fields = field_repo.get_high_cardinality_fields(version_id, threshold=0.9)

# Bulk update PII
count = field_repo.bulk_update_pii_status([id1, id2], is_pii=True, pii_type="email")

# Count
total = field_repo.count_by_version(version_id)
```

## AnnotationRepository Specific

```python
# All annotations for field
annotations = annotation_repo.get_by_field(field_id)

# Latest annotation for field
latest = annotation_repo.get_latest_by_field(field_id)

# Bulk create
annotations = annotation_repo.bulk_create_annotations(annotation_data_list)

# Update
annotation = annotation_repo.update_annotation(
    annotation_id,
    description="New description",
    business_name="New Name",
    updated_by="user@example.com"
)

# Filter by source
ai_annotations = annotation_repo.get_ai_generated()
user_annotations = annotation_repo.get_user_generated()
gpt4_annotations = annotation_repo.get_by_model_version("gpt-4")

# Search
results = annotation_repo.search_by_description("email")
results = annotation_repo.search_by_business_name("customer")

# By business owner
annotations = annotation_repo.get_by_business_owner("Data Team")

# Tags
tagged = annotation_repo.get_with_tags("category", "pii")
annotation = annotation_repo.update_tags(annotation_id, {"key": "value"})

# Bulk delete
count = annotation_repo.delete_by_field(field_id)

# Counts
total = annotation_repo.count_by_field(field_id)
ai_count = annotation_repo.count_ai_generated()
user_count = annotation_repo.count_user_generated()
```

## Performance Tips

### Avoid N+1 Queries
```python
# BAD - Will cause N+1 queries
fields = field_repo.get_by_version(version_id)
for field in fields:
    for annotation in field.annotations:  # Triggers separate query per field!
        print(annotation.description)

# GOOD - Eager loading
fields = field_repo.get_fields_with_annotations(version_id)
for field in fields:
    for annotation in field.annotations:  # Already loaded!
        print(annotation.description)
```

### Use Bulk Operations
```python
# BAD - Multiple individual inserts
for field_data in field_data_list:
    field_repo.create(**field_data)

# GOOD - Single bulk insert
fields = field_repo.bulk_insert_fields(field_data_list)
```

### Pagination for Large Results
```python
# BAD - Loading everything
all_fields = field_repo.get_by_version(version_id)  # Could be thousands!

# GOOD - Paginate
items, total = field_repo.paginate(page=1, page_size=100)
```

## Transaction Management

Repositories use the session's transaction. Commit/rollback at the service layer:

```python
try:
    # Multiple repository operations
    dictionary = dict_repo.create(name="test")
    version = version_repo.create_new_version(dictionary.id, "hash123")
    
    # Commit transaction
    db.commit()
except Exception as e:
    # Rollback on error
    db.rollback()
    raise
finally:
    db.close()
```

## Testing Pattern

```python
from unittest.mock import Mock, MagicMock
import pytest

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def dict_repo(mock_db):
    return DictionaryRepository(mock_db)

def test_get_by_name(dict_repo, mock_db):
    # Setup
    mock_result = Mock()
    mock_result.scalar_one_or_none.return_value = Mock(name="test_dict")
    mock_db.execute.return_value = mock_result
    
    # Execute
    result = dict_repo.get_by_name("test_dict")
    
    # Assert
    assert result.name == "test_dict"
    mock_db.execute.assert_called_once()
```
