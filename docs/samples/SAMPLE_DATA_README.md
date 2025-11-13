# Sample Data for Testing

## File: `sample-data.json`

This sample JSON file contains 10 user records designed to demonstrate all the features of the Data Dictionary Generator frontend.

## What This Data Tests

### 📊 Data Types
- **Strings**: user_id, email, names, addresses, bios
- **Numbers**: age, account_balance, order totals, login_count, revenue
- **Booleans**: is_active, is_primary, notifications_enabled
- **Dates**: created_at, last_login, order_date (ISO 8601 format)
- **Nulls**: Various fields have null values to test null percentage calculations
- **Arrays**: addresses, orders, tags

### 🏗️ Nested Structures (3 levels deep)
```
root
├── user_id, email, name, etc. (level 0)
├── profile (level 1)
│   ├── bio, avatar_url
│   └── preferences (level 2)
│       ├── theme
│       ├── notifications_enabled
│       └── language
├── addresses[] (level 1, array)
│   ├── type, street, city, etc.
│   └── is_primary
└── orders[] (level 1, array)
    ├── order_id, total
    └── status, order_date
```

### 🔒 PII (Personally Identifiable Information)
The data includes fields that should be detected as PII:
- **Email addresses**: `email` field
- **Phone numbers**: `phone` field (US format)
- **SSN**: `ssn` field (US Social Security Numbers)
- **Credit card**: `credit_card_last4` field

### 📈 Statistical Variety

**Age Distribution:**
- Min: 26, Max: 51
- Mix of values with 2 nulls
- Good for testing statistical analysis

**Account Balance:**
- Range: $0.00 to $8,500.00
- Tests currency/decimal handling
- Various precision levels

**Login Counts:**
- Range: 8 to 567
- Tests integer statistics
- Shows user engagement patterns

### 🎯 Data Quality Features

**Null Values (to test null % calculation):**
- Some users have no `age`
- Some have no `phone`
- Some have null `bio` or `avatar_url`
- Some have null `credit_card_last4`
- One user has empty arrays (no addresses/orders)

**Cardinality Testing:**
- `subscription_tier`: Low cardinality (3 values: basic, premium, enterprise)
- `user_id`: High cardinality (all unique)
- `is_active`: Binary (true/false)
- `tags`: Variable array length

**Array Fields:**
- Empty arrays: usr_004 has no addresses or orders
- Single items: Most users have 1-2 addresses
- Multiple items: Enterprise users have more orders

### 🏷️ Semantic Types
Fields that should be auto-detected:
- `email` → email type
- `phone` → phone type
- `ssn` → SSN type
- `*_url` → URL type
- `*_at`, `*_date` → date/timestamp type
- `zip_code` → postal code type

## How to Use

### 1. Upload via Frontend

1. Start the backend: `cd backend && uvicorn main:app --reload`
2. Start the frontend: `cd frontend && npm run dev`
3. Navigate to `http://localhost:5173`
4. Click "Upload New" button
5. Drag and drop `sample-data.json`
6. Fill in:
   - **Name**: "User Analytics Data"
   - **Description**: "Sample customer data for testing with nested profiles, orders, and PII"
   - ✅ Check "Generate AI-powered field descriptions"
7. Click "Create Dictionary"

### 2. What You'll See

After processing (may take 1-2 minutes with AI descriptions):

**Overview Tab:**
- 10 records analyzed
- 40+ fields detected (including nested fields)
- File size: ~8 KB
- Multiple versions (if you upload again)

**Fields Tab:**
- Search through all fields
- Sort by name, type, null %, etc.
- Filter by PII status
- Click any field to see details:
  - Type information
  - PII warnings (email, phone, SSN)
  - Null percentages
  - Statistics (for numeric fields)
  - Sample values
  - AI-generated descriptions

**Versions Tab:**
- Version 1 with creation timestamp
- Upload a modified version to test version comparison

### 3. Test Scenarios

**For Data Engineers:**
- ✅ Upload the file
- ✅ View all detected fields
- ✅ Check PII detection accuracy
- ✅ Export to Excel

**For Data Analysts:**
- ✅ Search for specific fields (e.g., "email", "order")
- ✅ Filter by null percentage > 10%
- ✅ View data quality metrics
- ✅ Read AI descriptions

**For Data Scientists:**
- ✅ Check statistical summaries (age, balance, revenue)
- ✅ View percentiles and distributions
- ✅ Analyze cardinality ratios
- ✅ Inspect sample values

### 4. Testing Version Comparison

1. Modify the JSON file (add a field, change values)
2. Upload as a new version
3. Navigate to dictionary detail → Versions tab
4. Click "Compare Versions"
5. See added/removed/modified fields
6. Breaking changes highlighted

## Expected Field Count

When you upload this file, you should see approximately:

- **Root level fields**: ~15 (user_id, email, age, etc.)
- **Nested fields (profile)**: ~5
- **Nested fields (preferences)**: ~3
- **Array item fields (addresses)**: ~7
- **Array item fields (orders)**: ~5
- **Total unique field paths**: **35-40 fields**

## File Statistics

- **Size**: ~8 KB
- **Records**: 10
- **Nesting levels**: 3 (root → profile → preferences)
- **Arrays**: 3 (addresses, orders, tags)
- **PII fields**: 4 (email, phone, SSN, credit_card)
- **Null values**: Present in ~15% of fields
- **Data types**: 5 (string, number, boolean, null, array)

## Tips for Testing

1. **PII Detection**: Check that email, phone, and SSN fields are flagged as PII
2. **Statistics**: Numeric fields should show min/max/mean/median
3. **Null %**: Fields with nulls should show accurate percentages
4. **Cardinality**: High for IDs, low for subscription_tier
5. **Nested Paths**: Should see fields like "profile.preferences.theme"
6. **Arrays**: Should detect both array fields and item types
7. **AI Descriptions**: Should generate meaningful descriptions for each field

## Troubleshooting

**If upload fails:**
- Check backend is running on port 8000
- Check file is valid JSON (use a JSON validator)
- Check backend logs for errors

**If PII not detected:**
- Email should be detected (contains @ symbol)
- Phone should be detected (matches +1-XXX-XXX-XXXX pattern)
- SSN should be detected (matches XXX-XX-XXXX pattern)

**If statistics missing:**
- Only numeric fields get statistical analysis
- Check field is actually a number, not a string

## Next Steps

After testing with this sample:
1. Try uploading your own JSON data
2. Test with larger files (100+ records)
3. Test with deeply nested structures (5+ levels)
4. Test version comparison features
5. Test Excel export functionality

Enjoy testing the Data Dictionary Generator! 🎉
