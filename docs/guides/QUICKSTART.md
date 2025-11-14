# Data Dictionary Generator - Quickstart Tutorial

**Get from zero to your first data dictionary in 10 minutes.**

This hands-on tutorial will walk you through installing, running, and using the Data Dictionary Generator to analyze a sample dataset. By the end, you'll understand how the tool works and be ready to use it with your own data.

## What You'll Learn

- How to install and run the application (2 minutes)
- How to upload and analyze a JSON file (3 minutes)
- How to explore the generated data dictionary (3 minutes)
- How to export results to Excel (1 minute)
- What to try next (1 minute)

## Prerequisites

Before starting, ensure you have:

- **Docker and Docker Compose** installed ([Get Docker](https://docs.docker.com/get-docker/))
  - OR **Python 3.11+** for local development
- **5 GB** of free disk space
- **Internet connection** (for Docker images and optional AI features)

Optional but recommended:
- **OpenAI API key** for AI-powered field descriptions ([Get API key](https://platform.openai.com/api-keys))

---

## Part 1: Installation and Setup (2 minutes)

### Option A: Docker (Recommended - Fastest Setup)

This is the quickest way to get started with zero configuration.

**Step 1: Clone the repository**

```bash
git clone https://github.com/your-org/data-dictionary-gen.git
cd data-dictionary-gen
```

**Step 2: Start the application**

```bash
# Start the SQLite-based application (single container, lightweight)
docker-compose up -d app
```

Expected output:
```
[+] Running 2/2
 ✔ Network ddgen_network  Created
 ✔ Container ddgen_app    Started
```

**Step 3: Verify it's running**

```bash
# Check the application health
curl http://localhost:8000/health
```

Expected output:
```json
{"status":"healthy","database":"connected"}
```

That's it! The application is now running at **http://localhost:8000**

### Option B: Local Development (Without Docker)

Choose this if you prefer running Python directly or want to modify the code.

**Step 1: Clone and navigate to backend**

```bash
git clone https://github.com/your-org/data-dictionary-gen.git
cd data-dictionary-gen/backend
```

**Step 2: Create virtual environment and install dependencies**

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

**Step 3: Set up the database**

```bash
# Create environment file
cat > .env <<EOF
DATABASE_URL=sqlite:///./data/app.db
DATABASE_TYPE=sqlite
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=INFO
EOF

# Create data directory
mkdir -p data

# Run database migrations
alembic upgrade head
```

**Step 4: Start the backend server**

```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Expected output:
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Application startup complete.
```

**Step 5: Open your browser**

Navigate to **http://localhost:8000/api/docs** to see the API documentation.

---

## Part 2: Upload Your First File (3 minutes)

Now let's analyze a sample dataset to see the tool in action.

**Step 1: Open the API documentation**

Visit **http://localhost:8000/api/docs** in your browser. This is FastAPI's interactive API documentation where we can test the application.

**Step 2: Create a test file**

We'll use the provided sample data. First, let's examine what's in it:

```bash
# View the first few lines of the sample data
head -n 20 samples/sample-data.json
```

This sample contains user records with:
- Basic information (email, name, age)
- PII data (phone numbers, SSN)
- Nested structures (profile, preferences)
- Arrays (addresses, orders)

**Step 3: Upload the file via API**

In the API docs at http://localhost:8000/api/docs:

1. Find the **POST /api/v1/dictionaries/** endpoint
2. Click "Try it out"
3. Fill in the request body:

```json
{
  "name": "User Analytics Data",
  "description": "Sample customer data with PII and nested structures",
  "file_type": "json",
  "generate_descriptions": false
}
```

4. Click "Choose File" and select `samples/sample-data.json`
5. Click "Execute"

OR use curl from the command line:

```bash
curl -X POST "http://localhost:8000/api/v1/dictionaries/" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@samples/sample-data.json" \
  -F "name=User Analytics Data" \
  -F "description=Sample customer data with PII and nested structures" \
  -F "generate_descriptions=false"
```

**Step 4: Watch the processing**

The application will:
- Parse the JSON file (streaming for memory efficiency)
- Detect data types (string, number, boolean, etc.)
- Calculate statistics (min, max, mean, median for numeric fields)
- Identify PII (emails, phone numbers, SSNs)
- Flatten nested structures
- Analyze arrays

This takes about 10-30 seconds depending on your system.

**Expected response:**

```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "name": "User Analytics Data",
  "description": "Sample customer data with PII and nested structures",
  "file_name": "sample-data.json",
  "file_size": 13000,
  "record_count": 10,
  "field_count": 42,
  "created_at": "2024-01-15T10:30:00Z",
  "status": "completed"
}
```

Copy the `id` value - you'll need it for the next steps.

---

## Part 3: Explore the Data Dictionary (3 minutes)

Now let's explore what the tool discovered about your data.

**Step 1: Get the dictionary details**

Replace `{dictionary_id}` with the ID from the previous step:

```bash
curl http://localhost:8000/api/v1/dictionaries/{dictionary_id}
```

You'll see a summary including:
- File metadata (name, size, record count)
- Number of fields detected
- Creation timestamp
- Version information

**Step 2: List all fields**

```bash
curl http://localhost:8000/api/v1/dictionaries/{dictionary_id}/fields
```

This returns all detected fields. Let's look at what you'll see:

**Root-level fields:**
- `user_id` - String, unique identifier
- `email` - String, PII detected (email pattern)
- `first_name` - String
- `last_name` - String
- `age` - Number, statistics calculated
- `phone` - String, PII detected (phone pattern)
- `ssn` - String, PII detected (SSN pattern)
- `is_active` - Boolean
- `account_balance` - Number, statistics calculated

**Nested fields (automatically flattened):**
- `profile.bio` - String
- `profile.avatar_url` - String (URL pattern detected)
- `profile.preferences.theme` - String
- `profile.preferences.notifications_enabled` - Boolean
- `profile.preferences.language` - String

**Array item fields:**
- `addresses[].type` - String, low cardinality (home, work)
- `addresses[].street` - String
- `addresses[].city` - String
- `addresses[].state` - String
- `addresses[].zip_code` - String
- `orders[].order_id` - String
- `orders[].total` - Number, statistics calculated
- `orders[].status` - String, low cardinality (pending, delivered)

**Step 3: Examine a specific field**

Let's look at the `email` field in detail:

```bash
curl http://localhost:8000/api/v1/dictionaries/{dictionary_id}/fields?field_name=email
```

Response shows:

```json
{
  "field_name": "email",
  "field_path": "email",
  "data_type": "string",
  "semantic_type": "email",
  "is_pii": true,
  "null_percentage": 0.0,
  "distinct_count": 10,
  "cardinality_ratio": 1.0,
  "sample_values": [
    "john.doe@example.com",
    "jane.smith@example.com",
    "bob.wilson@example.com"
  ],
  "statistics": null,
  "description": "Email address field - contains PII"
}
```

Key insights:
- **is_pii: true** - Automatically detected as personally identifiable
- **semantic_type: email** - Pattern recognition identified email format
- **null_percentage: 0.0** - No missing values
- **cardinality_ratio: 1.0** - All unique values (good for identifier)

**Step 4: View statistics for a numeric field**

```bash
curl http://localhost:8000/api/v1/dictionaries/{dictionary_id}/fields?field_name=age
```

Response includes statistical analysis:

```json
{
  "field_name": "age",
  "data_type": "number",
  "null_percentage": 20.0,
  "distinct_count": 8,
  "statistics": {
    "min": 26,
    "max": 51,
    "mean": 35.75,
    "median": 34.5,
    "std_dev": 8.24,
    "percentiles": {
      "25": 29.0,
      "50": 34.5,
      "75": 42.0
    }
  },
  "sample_values": [26, 28, 31, 34, 37, 42, 45, 51]
}
```

This tells you:
- Age range: 26-51 years
- Average age: ~36 years
- 20% of records have missing age data
- Data distribution via percentiles

---

## Part 4: Export to Excel (1 minute)

Now let's export the data dictionary to a professional Excel report.

**Step 1: Download the Excel export**

```bash
curl -o user_data_dictionary.xlsx \
  "http://localhost:8000/api/v1/dictionaries/{dictionary_id}/export"
```

OR visit this URL in your browser:
```
http://localhost:8000/api/v1/dictionaries/{dictionary_id}/export
```

**Step 2: Open the Excel file**

The generated Excel file contains:

**Metadata Sheet:**
- Dictionary name and description
- File information (name, size, records)
- Generation timestamp
- Field summary

**Fields Sheet:**
- Field Name
- Field Path (showing nesting)
- Data Type
- Semantic Type
- PII Flag (highlighted in red)
- Null Percentage (color-coded by severity)
- Cardinality
- Statistics (min, max, mean for numeric fields)
- Sample Values
- Description

**Color Coding:**
- Red: PII fields (requires data protection)
- Orange: High null percentage (>20% missing data)
- Green: Complete data (0% nulls)
- Blue: Numeric fields with statistics

This Excel file is ready to share with your team, attach to documentation, or use for data governance.

---

## Part 5: Next Steps (1 minute)

Congratulations! You've successfully:
- Installed the Data Dictionary Generator
- Uploaded and analyzed a JSON file
- Explored the generated metadata
- Exported a professional Excel report

### Try These Next:

**1. Test with your own data**

Upload your own JSON files (up to 500MB):

```bash
curl -X POST "http://localhost:8000/api/v1/dictionaries/" \
  -F "file=@your-data.json" \
  -F "name=My Dataset" \
  -F "description=Production data from Q4 2024"
```

**2. Enable AI-powered descriptions**

Add your OpenAI API key to get intelligent field descriptions:

```bash
# For Docker users
docker-compose down
export OPENAI_API_KEY="sk-your-api-key-here"
docker-compose up -d app

# For local development
echo "OPENAI_API_KEY=sk-your-api-key-here" >> .env
# Restart the server
```

Then upload with AI enabled:

```bash
curl -X POST "http://localhost:8000/api/v1/dictionaries/" \
  -F "file=@samples/sample-data.json" \
  -F "name=User Data (with AI)" \
  -F "generate_descriptions=true"
```

**3. Try other file formats**

The tool supports multiple formats:

```bash
# XML file
curl -X POST "http://localhost:8000/api/v1/dictionaries/" \
  -F "file=@samples/sample-data-simple.xml" \
  -F "name=XML Dataset"

# SQLite database
curl -X POST "http://localhost:8000/api/v1/dictionaries/" \
  -F "file=@samples/sample-database.db" \
  -F "name=SQLite Database"

# GeoPackage (geospatial data)
curl -X POST "http://localhost:8000/api/v1/dictionaries/" \
  -F "file=@samples/sample-geopackage.gpkg" \
  -F "name=Geographic Data"

# Protocol Buffers
curl -X POST "http://localhost:8000/api/v1/dictionaries/" \
  -F "file=@samples/sample-addressbook.proto" \
  -F "name=Protobuf Schema"
```

**4. Track schema versions**

Upload modified data to track changes over time:

```bash
# Modify your JSON file (add/remove fields)
# Then upload as a new version
curl -X POST "http://localhost:8000/api/v1/dictionaries/{dictionary_id}/versions" \
  -F "file=@samples/sample-data-modified.json"

# Compare versions
curl "http://localhost:8000/api/v1/dictionaries/{dictionary_id}/versions/compare?version1=1&version2=2"
```

**5. Search across all dictionaries**

```bash
# Search for fields containing "email"
curl "http://localhost:8000/api/v1/search?query=email"

# Search for PII fields across all datasets
curl "http://localhost:8000/api/v1/search?is_pii=true"
```

---

## Understanding Your Output

### Data Types Detected

The tool automatically identifies:

- **String**: Text data (names, IDs, descriptions)
- **Number**: Numeric data (integers, decimals)
- **Boolean**: True/false values
- **Date**: Timestamps in ISO 8601 format
- **Array**: Lists of values
- **Object**: Nested structures

### Semantic Types Identified

Beyond basic types, the tool recognizes:

- **email**: Email addresses
- **phone**: Phone numbers (various formats)
- **ssn**: Social Security Numbers
- **url**: Web URLs
- **currency**: Monetary values
- **postal_code**: ZIP codes
- **credit_card**: Credit card numbers (last 4 digits)

### PII Detection

The following are automatically flagged as Personally Identifiable Information:

- Email addresses
- Phone numbers
- Social Security Numbers
- Credit card numbers
- Full names (when detected as names)

Use these flags to ensure proper data handling and compliance.

### Quality Metrics

**Null Percentage:**
- 0%: Complete data
- 1-10%: Excellent quality
- 11-20%: Good quality
- 21-50%: Fair quality (investigate)
- 50%+: Poor quality (requires attention)

**Cardinality Ratio:**
- 1.0: Unique values (good for IDs)
- 0.5-0.9: High variety (names, descriptions)
- 0.1-0.4: Medium variety (categories, states)
- <0.1: Low variety (boolean, small enums)

---

## Troubleshooting

### Application won't start

**Check if port 8000 is already in use:**

```bash
# Find what's using port 8000
lsof -i :8000

# Use a different port
docker run -p 8080:8000 -v $(pwd)/data:/app/data ddgen_app
```

**Check Docker is running:**

```bash
docker ps
# Should show running containers
```

### Upload fails

**File too large:**
- Maximum file size: 500MB
- For larger files, use sampling or chunking

**Invalid JSON:**

```bash
# Validate your JSON first
python3 -m json.tool < your-file.json
```

**Connection refused:**

```bash
# Verify the backend is running
curl http://localhost:8000/health

# Check logs
docker-compose logs app
# or for local development:
tail -f logs/app.log
```

### No statistics for numeric fields

- Ensure the field contains actual numbers, not strings
- Check if there are enough non-null values (minimum 2 required)

### PII not detected

- Email detection requires valid email format (contains @)
- Phone numbers must match common patterns (+1-XXX-XXX-XXXX, etc.)
- SSN must follow XXX-XX-XXXX format

---

## Key Commands Reference

### Docker Operations

```bash
# Start
docker-compose up -d app

# Stop
docker-compose down

# View logs
docker-compose logs -f app

# Restart
docker-compose restart app

# Rebuild after code changes
docker-compose build app
docker-compose up -d app
```

### Database Operations

```bash
# Backup SQLite database
cp data/app.db backups/app-$(date +%Y%m%d).db

# View database stats
curl http://localhost:8000/api/v1/database/stats

# Check database health
curl http://localhost:8000/api/v1/database/health
```

### API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# List all dictionaries
curl http://localhost:8000/api/v1/dictionaries/

# Get specific dictionary
curl http://localhost:8000/api/v1/dictionaries/{id}

# List fields
curl http://localhost:8000/api/v1/dictionaries/{id}/fields

# Export to Excel
curl -o output.xlsx http://localhost:8000/api/v1/dictionaries/{id}/export

# Search across all data
curl "http://localhost:8000/api/v1/search?query=email"
```

---

## What You've Learned

In just 10 minutes, you've learned how to:

1. Install and run the Data Dictionary Generator using Docker or Python
2. Upload and parse JSON files to extract metadata
3. View automatically detected fields, types, and statistics
4. Identify PII and assess data quality metrics
5. Export professional Excel reports for documentation
6. Understand the tool's capabilities across different file formats

The Data Dictionary Generator helps data engineers, analysts, and scientists understand their data structures quickly and comprehensively - turning raw data into documented, analyzable information.

---

## Learn More

- **Full Documentation**: See [README.md](README.md) for complete feature list
- **API Documentation**: Visit http://localhost:8000/api/docs when running
- **Sample Data Guide**: See [docs/samples/SAMPLE_DATA_README.md](docs/samples/SAMPLE_DATA_README.md)
- **Deployment Guide**: See [docs/deployment/DOCKER_DEPLOYMENT.md](docs/deployment/DOCKER_DEPLOYMENT.md)
- **Technical Architecture**: See [docs/reference/SOFTWARE_DESIGN.md](docs/reference/SOFTWARE_DESIGN.md)

---

## Support

Found a bug or have a question?

- **GitHub Issues**: Report bugs and request features
- **API Docs**: Interactive documentation at `/api/docs`
- **Health Endpoint**: Check system status at `/health`

Happy data cataloging!
