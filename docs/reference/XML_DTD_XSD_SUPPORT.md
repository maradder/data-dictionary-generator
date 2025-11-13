# XML Schema Support (DTD & XSD)

The Data Dictionary Generator now supports **DTD (Document Type Definition)** and **XSD (XML Schema Definition)** for enhanced XML parsing and validation.

## 📋 Features

### DTD Support
- **Automatic Detection**: Detects embedded or external DTDs
- **Element Definitions**: Extracts element content models and hierarchies
- **Attribute Metadata**: Captures attribute types, defaults, and constraints
- **Cardinality**: Identifies required, optional, repeating elements
- **Entity Declarations**: Extracts entity definitions

### XSD Support
- **Schema Parsing**: Reads and parses XSD schema files
- **Validation**: Validates XML against XSD schema
- **Type Information**: Extracts complex and simple type definitions
- **Constraints**: Captures minOccurs, maxOccurs, restrictions
- **Data Types**: Identifies xs:string, xs:integer, xs:decimal, etc.
- **Enumerations**: Extracts allowed values from enumerations

## 🎯 What Gets Extracted

### From DTD

```xml
<!DOCTYPE bookstore [
  <!ELEMENT book (title, author+, price, isbn?)>
  <!ATTLIST book
    id ID #REQUIRED
    lang (en|es|fr) "en">
]>
```

**Extracted Metadata:**
- `title`: REQUIRED (appears once)
- `author`: ONE_OR_MORE (+ symbol)
- `price`: REQUIRED
- `isbn`: OPTIONAL (? symbol)
- `id` attribute: REQUIRED, type ID
- `lang` attribute: OPTIONAL, enumeration (en|es|fr), default "en"

### From XSD

```xml
<xs:element name="price" type="PriceType"/>

<xs:simpleType name="PriceType">
  <xs:restriction base="xs:decimal">
    <xs:minInclusive value="0.01"/>
    <xs:maxInclusive value="9999.99"/>
  </xs:restriction>
</xs:simpleType>
```

**Extracted Metadata:**
- Element: `price`
- Type: `PriceType` (xs:decimal)
- Min value: 0.01
- Max value: 9999.99
- Required: Based on minOccurs (default 1)

## 📂 Sample Files

### Sample XML with DTD
**File**: `sample-xml-with-dtd.xml`
- Embedded DTD definition
- 4 book records
- Demonstrates required/optional elements
- Shows attribute enumerations

### Sample XML with XSD
**Files**: `sample-xml-with-xsd.xml` + `sample-books.xsd`
- External XSD schema
- 5 book records
- Complex types with sequences
- Simple types with restrictions
- Attribute definitions
- Enumeration values

## 🔧 Usage

### Basic XML Parsing (Auto DTD Detection)
```python
from pathlib import Path
from src.processors.xml_parser import XMLParser

parser = XMLParser()
result = parser.parse_file(Path("sample-xml-with-dtd.xml"))

# Access DTD metadata
if 'dtd_metadata' in result:
    dtd = result['dtd_metadata']
    print(f"Elements: {list(dtd['elements'].keys())}")
    print(f"Attributes: {dtd['attributes']}")

# Fields now include DTD metadata
for field in result['fields']:
    if 'dtd_metadata' in field:
        print(f"{field['field_name']}: {field['dtd_metadata']}")
```

### XML with External XSD Schema
```python
parser = XMLParser()
result = parser.parse_file(
    file_path=Path("sample-xml-with-xsd.xml"),
    xsd_path=Path("sample-books.xsd")
)

# Check validation results
if 'xsd_metadata' in result:
    xsd = result['xsd_metadata']
    validation = xsd['validation']

    if validation['is_valid']:
        print("✓ XML is valid")
    else:
        print("✗ Validation errors:")
        for error in validation['errors']:
            print(f"  Line {error['line']}: {error['message']}")

# Fields include XSD metadata
for field in result['fields']:
    if 'xsd_metadata' in field:
        meta = field['xsd_metadata']
        if 'element' in meta:
            elem = meta['element']
            print(f"{field['field_name']}:")
            print(f"  Type: {elem['type']}")
            print(f"  Required: {elem['required']}")
            print(f"  Repeating: {elem['repeating']}")
```

## 📊 Field Metadata Enhancements

Each field in the parsed results can now include:

### DTD Metadata
```python
{
    'field_name': 'author',
    'dtd_metadata': {
        'element': {
            'content_type': 'PCDATA',
            'content_model': '(#PCDATA)',
            'children': []
        }
    }
}
```

### XSD Metadata
```python
{
    'field_name': 'price',
    'xsd_metadata': {
        'element': {
            'type': 'PriceType',
            'min_occurs': '1',
            'max_occurs': '1',
            'required': True,
            'repeating': False,
            'nillable': False
        }
    }
}
```

### Attribute Metadata (DTD)
```python
{
    'field_name': '@lang',
    'dtd_metadata': {
        'attribute': {
            'type': 'enumeration',
            'required': False,
            'default_value': 'en',
            'allowed_values': ['en', 'es', 'fr', 'de']
        }
    }
}
```

## 🧪 Testing

### Run DTD Tests
```bash
cd backend
python -c "
from pathlib import Path
from src.processors.xml_parser import XMLParser

parser = XMLParser()
result = parser.parse_file(Path('../sample-xml-with-dtd.xml'))

print('DTD Detection:', 'dtd_metadata' in result)
if 'dtd_metadata' in result:
    dtd = result['dtd_metadata']
    print('Elements found:', len(dtd['elements']))
    print('Attributes found:', sum(len(attrs) for attrs in dtd['attributes'].values()))
"
```

### Run XSD Tests
```bash
cd backend
python -c "
from pathlib import Path
from src.processors.xml_parser import XMLParser

parser = XMLParser()
result = parser.parse_file(
    Path('../sample-xml-with-xsd.xml'),
    Path('../sample-books.xsd')
)

print('XSD Detection:', 'xsd_metadata' in result)
if 'xsd_metadata' in result:
    xsd = result['xsd_metadata']
    print('Validation:', xsd['validation']['is_valid'])
    print('Elements found:', len(xsd['elements']))
    print('Complex types:', len(xsd['complex_types']))
    print('Simple types:', len(xsd['simple_types']))
"
```

## 📖 DTD Cardinality Symbols

| Symbol | Meaning | Example |
|--------|---------|---------|
| (none) | Required once | `<!ELEMENT book (title)>` |
| `?` | Optional (0 or 1) | `<!ELEMENT book (isbn?)>` |
| `+` | One or more | `<!ELEMENT book (author+)>` |
| `*` | Zero or more | `<!ELEMENT book (review*)>` |

## 📖 XSD Data Types

Common XSD types automatically detected:

| XSD Type | Description |
|----------|-------------|
| `xs:string` | Text string |
| `xs:integer` | Whole number |
| `xs:decimal` | Decimal number |
| `xs:boolean` | true/false |
| `xs:date` | Date (YYYY-MM-DD) |
| `xs:dateTime` | Date and time |
| `xs:time` | Time only |
| `xs:anyURI` | URI/URL |

## 🎨 Benefits for Data Dictionaries

1. **Required vs Optional**: Know which fields must be present
2. **Cardinality**: Understand repeating elements (arrays)
3. **Data Types**: More accurate type inference from schema
4. **Validation**: Ensure XML conforms to schema
5. **Constraints**: Document min/max values, patterns, enumerations
6. **Enumerations**: List all allowed values
7. **Default Values**: Know what happens when field is missing

## 🔄 Comparison: Vanilla XML vs DTD vs XSD

| Feature | Vanilla XML | DTD | XSD |
|---------|-------------|-----|-----|
| Structure extraction | ✓ | ✓ | ✓ |
| Type information | Inferred | Limited | Rich |
| Required fields | No | Yes | Yes |
| Cardinality | No | Yes | Yes |
| Data validation | No | Basic | Advanced |
| Namespaces | Yes | No | Yes |
| Complex types | No | No | Yes |
| Restrictions | No | No | Yes (pattern, range, etc.) |
| Enumerations | No | Yes | Yes |

## 💡 Use Cases

### When to Use DTD
- Legacy XML systems
- Simple structure definitions
- Embedded schema requirements
- SGML compatibility

### When to Use XSD
- Modern XML applications
- Complex data types
- Strict validation requirements
- Namespace support needed
- Rich constraint definitions

### When to Use Vanilla XML
- No schema available
- Exploratory data analysis
- Schema-less data sources
- Quick prototyping

## 🚀 Upload to UI

Both DTD and XSD metadata will be captured automatically when you upload XML files through the web interface:

1. Upload `sample-xml-with-dtd.xml` - DTD will be auto-detected
2. Upload `sample-xml-with-xsd.xml` - XSD validation requires backend support for schema upload (future enhancement)

The data dictionary will show:
- Required vs optional fields
- Allowed values for enumerations
- Data type constraints
- Cardinality information

## 📝 Notes

- **DTD**: Automatically detected from `<!DOCTYPE>` declarations
- **XSD**: Requires explicit schema file path (programmatic use)
- **Performance**: Schema parsing adds minimal overhead
- **Validation**: XSD validation is optional and can be enabled/disabled
- **Compatibility**: Works with existing XML parser, backward compatible

## 🔮 Future Enhancements

- UI upload for XSD schema files
- RelaxNG schema support
- Schematron validation rules
- Schema visualization in UI
- Schema-driven form generation
