# Core Processing Components

This directory contains the core processing components for JSON analysis and data dictionary generation.

## Modules

### 1. json_parser.py
**Purpose:** Parse JSON files and extract field structure using streaming techniques.

**Classes:**
- `JSONParser`: Streaming JSON parser for large files
  - `parse_file()`: Main entry point for parsing JSON files
  - `_parse_array_root()`: Handle JSON arrays
  - `_parse_object_root()`: Handle JSON objects
  - `_extract_fields()`: Recursively extract fields from objects
  
- `FieldMetadata`: Accumulates metadata for a single field
  - `observe_value()`: Record observation of a value
  - `to_dict()`: Convert to dictionary

**Features:**
- Streaming parsing with ijson for memory efficiency
- Handles nested objects up to 10 levels deep
- Uses dot notation for field paths
- Samples up to 1000 records by default
- Tracks type occurrences and null counts

### 2. type_inferrer.py
**Purpose:** Infer data types with confidence scores from observed values.

**Classes:**
- `TypeInferrer`: Infers data types from observed values
  - `infer_type()`: Infer primary type and confidence score
  - `infer_array_item_type()`: Infer array item type

**Features:**
- Type hierarchy handling (integer + float = float)
- Confidence percentage calculation
- Null value handling

### 3. semantic_detector.py
**Purpose:** Detect semantic types (email, phone, URL, UUID, dates, etc.).

**Classes:**
- `SemanticTypeDetector`: Detects semantic types from field values
  - `detect()`: Main detection method

**Features:**
- Regex patterns for email, phone, URL, UUID, zip codes
- Multiple date format detection
- Currency detection
- Field name-based hints
- 70% threshold for pattern matching

### 4. pii_detector.py
**Purpose:** Identify potential PII (Personally Identifiable Information) fields.

**Classes:**
- `PIIDetector`: Detects potential PII in fields
  - `detect_pii()`: Main PII detection method
  - `_is_credit_card()`: Luhn algorithm validation

**Features:**
- SSN pattern detection
- Credit card detection with Luhn algorithm
- Field name-based detection
- Value-based detection
- Semantic type integration

### 5. quality_analyzer.py
**Purpose:** Calculate data quality metrics using pandas.

**Classes:**
- `QualityAnalyzer`: Analyzes data quality metrics for fields
  - `analyze_field()`: Calculate quality metrics
  - `get_sample_values()`: Get unique sample values

**Features:**
- Null percentage calculation
- Cardinality analysis
- Statistical metrics for numeric fields (min, max, mean, median, std, percentiles)
- Distinct count and cardinality ratio

### 6. ai_generator.py
**Purpose:** Generate field descriptions using OpenAI API.

**Classes:**
- `AIDescriptionGenerator`: Generates field descriptions using OpenAI
  - `generate_description()`: Generate description and business name
  - `generate_batch()`: Batch processing support

**Features:**
- OpenAI integration (gpt-3.5-turbo)
- Retry logic with tenacity (3 attempts, exponential backoff)
- In-memory caching mechanism
- Fallback descriptions when API fails
- Configurable model and API key

## Usage Example

```python
from processors import (
    JSONParser,
    TypeInferrer,
    SemanticTypeDetector,
    PIIDetector,
    QualityAnalyzer,
    AIDescriptionGenerator
)
from pathlib import Path

# Parse JSON file
parser = JSONParser(max_samples=1000, max_depth=10)
result = parser.parse_file(Path("data.json"))

# Analyze each field
type_inferrer = TypeInferrer()
semantic_detector = SemanticTypeDetector()
pii_detector = PIIDetector()
quality_analyzer = QualityAnalyzer()
ai_generator = AIDescriptionGenerator()

for field in result['fields']:
    # Infer type
    data_type, confidence = type_inferrer.infer_type(field['types_seen'])
    
    # Detect semantic type
    semantic_type = semantic_detector.detect(
        field['field_name'],
        field['sample_values'],
        data_type
    )
    
    # Detect PII
    is_pii, pii_type = pii_detector.detect_pii(
        field['field_path'],
        field['field_name'],
        semantic_type,
        field['sample_values']
    )
    
    # Analyze quality
    quality_metrics = quality_analyzer.analyze_field(
        field['sample_values'],
        data_type
    )
    
    # Generate description (if API key available)
    description, business_name = ai_generator.generate_description(
        field['field_path'],
        field['field_name'],
        data_type,
        semantic_type,
        field['sample_values']
    )
```

## Dependencies

- ijson: Streaming JSON parser
- pandas: Data analysis and quality metrics
- numpy: Numerical operations
- openai: OpenAI API client
- tenacity: Retry logic

## Design Principles

1. **Memory Efficiency**: Use streaming parsing for large files
2. **Type Safety**: Comprehensive type hints throughout
3. **Error Handling**: Graceful fallbacks and retry logic
4. **Extensibility**: Easy to add new semantic types or PII patterns
5. **Performance**: Optimized for large-scale JSON analysis
6. **Modularity**: Each processor has a single, well-defined responsibility

## Testing

Each processor module should have corresponding unit tests in `/backend/tests/processors/`:
- `test_json_parser.py`
- `test_type_inferrer.py`
- `test_semantic_detector.py`
- `test_pii_detector.py`
- `test_quality_analyzer.py`
- `test_ai_generator.py`
