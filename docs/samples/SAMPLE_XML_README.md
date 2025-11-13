# Sample XML Files Documentation

This directory contains three sample XML files demonstrating the XML ingestion capabilities of the Data Dictionary Generator. Each file showcases different levels of complexity to help you understand and test the system.

---

## Files Overview

### 1. `sample-data-simple.xml` - Simple Flat Structure

**Complexity Level:** ⭐ Basic
**Use Case:** Getting started, basic testing
**File Size:** ~1KB
**Records:** 5 users

#### Structure:
- **Flat hierarchy** with minimal nesting
- **Basic data types** (string, integer, boolean)
- **No attributes** - element values only
- **Simple field names** - straightforward naming

#### What it demonstrates:
- ✅ Basic XML parsing
- ✅ Repeating elements (multiple `<user>` tags)
- ✅ Type inference from string values
- ✅ Simple field extraction

#### Example field paths:
```
userId
firstName
lastName
email
age
active
country
```

#### Best for:
- First-time users learning the system
- Quick validation tests
- Understanding basic XML → data dictionary mapping

---

### 2. `sample-data-medium.xml` - Nested with Attributes

**Complexity Level:** ⭐⭐⭐ Intermediate
**File Size:** ~3KB
**Records:** 5 user analytics profiles

#### Structure:
- **Moderate nesting** (2-3 levels deep)
- **Attributes on elements** (id, status, tier, etc.)
- **Nested objects** (profile, subscription, activity, preferences)
- **ISO date formats** and timestamps
- **Mixed empty and populated values**
- **Namespace declarations** (automatically stripped)

#### What it demonstrates:
- ✅ XML attributes → fields with `@` prefix
- ✅ Nested element structures
- ✅ Namespace handling (stripped by default)
- ✅ Date/timestamp parsing
- ✅ Boolean attributes
- ✅ Empty element handling
- ✅ PII detection (email, phone)

#### Example field paths:
```
user.@id                          # Attribute
user.@status                      # Attribute
user.profile.username
user.profile.email                # PII detected
user.profile.phone                # PII detected
user.subscription.@tier
user.subscription.monthlyPrice
user.activity.loginCount
user.preferences.language
```

#### Best for:
- Understanding attribute handling
- Testing nested structures
- Real-world data patterns
- PII detection validation

---

### 3. `sample-data-complex.xml` - Enterprise E-Commerce

**Complexity Level:** ⭐⭐⭐⭐⭐ Advanced
**Use Case:** Production-like testing, comprehensive validation
**File Size:** ~15KB
**Records:** 3 customers with full order history

#### Structure:
- **Deep nesting** (up to 7-8 levels)
- **Heavy use of attributes** on most elements
- **Repeating nested elements** (items in orders)
- **Multiple data types**: strings, numbers, decimals, dates, booleans, coordinates
- **PII-rich content**: SSN, credit cards, emails, phones, addresses
- **Complex hierarchies**: customers → orders → items → pricing breakdown
- **Real-world patterns**: e-commerce transactions, analytics, preferences

#### What it demonstrates:
- ✅ Deep nesting (7+ levels)
- ✅ Arrays within arrays (orders with items)
- ✅ Comprehensive PII detection
  - Social Security Numbers (SSN)
  - Credit card numbers (masked)
  - Email addresses
  - Phone numbers
  - Physical addresses
- ✅ Geographic coordinates
- ✅ Complex attributes (multiple per element)
- ✅ Mixed content (some empty, some populated)
- ✅ Currency and financial data
- ✅ Date/timestamp formats
- ✅ Semantic type detection (URLs, IDs, percentages)
- ✅ Namespace with schema URL

#### Example field paths:
```
customer.@customerId                                    # Attribute
customer.personalInfo.name.@prefix                     # Nested attribute
customer.personalInfo.name.firstName
customer.personalInfo.ssn                               # PII: SSN
customer.personalInfo.contact.email.@type              # Email with attribute
customer.personalInfo.contact.email                     # PII: Email
customer.personalInfo.contact.phone                     # PII: Phone
customer.personalInfo.addresses.address.@addressId     # Address attribute
customer.personalInfo.addresses.address.zipCode
customer.personalInfo.addresses.address.coordinates.latitude
customer.accountDetails.creditCard.cardNumber           # PII: Credit Card
customer.purchaseHistory.order.@orderId                # Order attribute
customer.purchaseHistory.order.items.item.@sku         # Item SKU
customer.purchaseHistory.order.items.item.productName
customer.purchaseHistory.order.items.item.unitPrice.@currency
customer.purchaseHistory.order.totals.grandTotal
customer.analytics.churnRisk.@score                    # Risk score attribute
```

#### Best for:
- Stress testing the parser
- Validating PII detection across multiple types
- Understanding complex hierarchies
- Production readiness testing
- Demonstrating full feature set
- Performance benchmarking

---

## How to Use These Files

### 1. Via Web UI

1. Start the application:
   ```bash
   # Terminal 1 - Backend
   cd backend
   uvicorn src.main:app --reload

   # Terminal 2 - Frontend
   cd frontend
   npm run dev
   ```

2. Open http://localhost:5173

3. Click **"Upload New"** button

4. Select one of the XML files

5. Fill in the form:
   - **Name**: e.g., "Simple User Data" / "User Analytics" / "E-Commerce Platform"
   - **Description**: Describe the dataset
   - **AI Descriptions**: Toggle on/off (requires OpenAI API key)

6. Click **"Create Dictionary"**

7. Explore the results:
   - Field hierarchy with nesting levels
   - Attributes marked with `@` prefix
   - PII fields highlighted
   - Type inference results
   - Sample values
   - Statistics and quality metrics

### 2. Via API (cURL)

```bash
# Simple XML
curl -X POST "http://localhost:8000/api/v1/dictionaries/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample-data-simple.xml" \
  -F "name=Simple User Data" \
  -F "description=Basic user information" \
  -F "generate_ai_descriptions=false"

# Medium complexity XML
curl -X POST "http://localhost:8000/api/v1/dictionaries/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample-data-medium.xml" \
  -F "name=User Analytics" \
  -F "description=User analytics with subscriptions and preferences" \
  -F "generate_ai_descriptions=true"

# Complex XML
curl -X POST "http://localhost:8000/api/v1/dictionaries/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@sample-data-complex.xml" \
  -F "name=E-Commerce Platform" \
  -F "description=Complete e-commerce customer and order data" \
  -F "generate_ai_descriptions=true"
```

### 3. Via Python API Client

```python
import requests

# Upload complex XML
with open('sample-data-complex.xml', 'rb') as f:
    files = {'file': ('sample-data-complex.xml', f, 'application/xml')}
    data = {
        'name': 'E-Commerce Platform',
        'description': 'Complex e-commerce data with deep nesting',
        'generate_ai_descriptions': True
    }

    response = requests.post(
        'http://localhost:8000/api/v1/dictionaries/',
        files=files,
        data=data
    )

    dictionary = response.json()
    print(f"Dictionary ID: {dictionary['id']}")
    print(f"Total fields: {dictionary['latest_version']['field_count']}")
```

---

## Expected Results by File

### Simple XML
- **~7 fields** extracted
- **Field types**: string, integer, boolean
- **Nesting depth**: 1-2 levels
- **PII detected**: Email addresses
- **Processing time**: < 1 second

### Medium XML
- **~25-30 fields** extracted
- **Attributes**: ~10-15 attribute fields with `@` prefix
- **Field types**: string, integer, float, boolean, timestamp
- **Nesting depth**: 3-4 levels
- **PII detected**: Email addresses, phone numbers
- **Semantic types**: Dates, currencies, timezones, languages
- **Processing time**: 1-2 seconds

### Complex XML
- **~100+ fields** extracted
- **Attributes**: ~30-40 attribute fields
- **Field types**: All types including decimal, coordinates
- **Nesting depth**: 7-8 levels
- **PII detected**:
  - SSN (Social Security Numbers)
  - Credit card numbers
  - Email addresses (multiple)
  - Phone numbers (multiple)
  - Physical addresses
- **Semantic types**:
  - Dates and timestamps
  - Currencies with symbols
  - Percentages
  - Geographic coordinates
  - URLs
  - UUIDs/IDs
- **Processing time**: 3-5 seconds

---

## XML-Specific Features Demonstrated

### 1. Attribute Handling
Attributes are extracted as separate fields with the `@` prefix:
```xml
<user id="123" status="active">
```
Creates fields:
- `user.@id` (value: "123")
- `user.@status` (value: "active")

### 2. Namespace Stripping
```xml
<ns:element xmlns:ns="http://example.com">
```
Becomes:
- `element` (namespace stripped by default)

### 3. Array Detection
Repeating elements are automatically detected:
```xml
<users>
    <user>...</user>
    <user>...</user>
</users>
```
- Field `user` marked as `is_array: true`
- Multiple sample values collected

### 4. Empty Element Handling
```xml
<middleName></middleName>
<nickname/>
```
- Tracked as null values
- Null percentage calculated

### 5. Nested Structures
Full path preservation:
```xml
<customer>
    <address>
        <city>New York</city>
    </address>
</customer>
```
Creates: `customer.address.city`

---

## Testing Recommendations

### Progressive Testing Strategy

1. **Start Simple** (`sample-data-simple.xml`)
   - Verify basic parsing works
   - Understand field extraction
   - Check type inference

2. **Add Complexity** (`sample-data-medium.xml`)
   - Test attribute handling
   - Validate nested structures
   - Verify PII detection

3. **Full Validation** (`sample-data-complex.xml`)
   - Stress test the parser
   - Validate all features
   - Check performance
   - Verify memory management

### What to Look For

✅ **Field Extraction**
- All fields discovered
- Correct nesting levels
- Attributes marked with `@`

✅ **Type Inference**
- Strings, integers, floats correctly identified
- Dates/timestamps recognized
- Booleans detected

✅ **PII Detection**
- Emails flagged
- Phone numbers flagged
- SSN flagged (complex only)
- Credit cards flagged (complex only)

✅ **Quality Metrics**
- Sample values collected
- Null counts accurate
- Statistics calculated (for numeric fields)

✅ **Performance**
- Processing completes in reasonable time
- Memory usage stays bounded
- No errors or warnings

---

## Configuration Options

You can customize XML parsing behavior in `backend/src/core/config.py`:

```python
# XML Processing
XML_MAX_DEPTH: int = 10              # Maximum nesting depth
XML_STRIP_NAMESPACES: bool = True    # Strip namespace prefixes
XML_ATTRIBUTE_PREFIX: str = "@"      # Prefix for attributes
```

To change these:
1. Edit `backend/.env` file
2. Add environment variables:
   ```bash
   XML_MAX_DEPTH=15
   XML_STRIP_NAMESPACES=false
   XML_ATTRIBUTE_PREFIX="_attr_"
   ```
3. Restart the backend server

---

## Troubleshooting

### File Upload Fails
- **Check file size**: Must be < 500MB (configurable)
- **Verify XML syntax**: Use an XML validator
- **Check file extension**: Must be `.xml`

### Fields Missing
- **Check nesting depth**: May exceed `XML_MAX_DEPTH` (default: 10)
- **Verify XML structure**: Malformed XML will error
- **Check for namespaces**: May need to disable stripping

### PII Not Detected
- **Check patterns**: PII detection uses regex patterns
- **Verify field names**: Some detection is name-based
- **Enable AI enhancement**: More accurate detection (requires API key)

### Performance Issues
- **Large files**: XML parsing is memory-efficient but takes time
- **Deep nesting**: Increases processing time
- **Many attributes**: Each attribute is a separate field

---

## Next Steps

After testing with these samples:

1. **Try your own XML files**
   - Export from your systems
   - Test various formats
   - Validate field extraction

2. **Explore generated dictionaries**
   - Export to Excel
   - Compare versions
   - Add manual annotations

3. **Integrate into workflows**
   - API automation
   - Scheduled imports
   - Data catalog integration

4. **Provide feedback**
   - Report issues on GitHub
   - Suggest improvements
   - Share use cases

---

## Related Documentation

- **[README.md](README.md)** - Main project documentation
- **[QUICK_START.md](QUICK_START.md)** - Getting started guide
- **[backend/README.md](backend/README.md)** - Backend API documentation
- **[docs/SOFTWARE_DESIGN.md](docs/SOFTWARE_DESIGN.md)** - Technical architecture

---

**Happy data dictionary generation! 🚀**
