# Data Dictionary Generator - Backend

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Technology Stack](#technology-stack)
- [Directory Structure](#directory-structure)
- [Getting Started](#getting-started)
- [Configuration](#configuration)
- [API Documentation](#api-documentation)
- [Development Workflow](#development-workflow)
- [Core Components](#core-components)
- [Design Patterns](#design-patterns)
- [Known Limitations](#known-limitations)
- [Troubleshooting](#troubleshooting)

## Overview

The Data Dictionary Generator backend is a FastAPI-based REST API that automatically generates comprehensive data dictionaries from JSON files. It performs intelligent type inference, semantic analysis, statistical computation, PII detection, and optional AI-powered field descriptions.

**Key Capabilities:**
- Parse large JSON files (up to 500MB) using streaming architecture
- Infer data types (string, int, float, boolean, array, object) and semantic types (email, URL, phone, date, currency, SSN)
- Compute statistical measures (min, max, mean, median, percentiles, standard deviation)
- Detect PII with confidence scoring
- Generate AI-powered field descriptions using GPT-4
- Track schema versions with automatic change detection
- Export formatted Excel files with professional styling
- Global search across dictionaries and fields

## Architecture

### High-Level Design

```
┌─────────────┐
│   Client    │
│  (React)    │
└─────┬───────┘
      │ HTTP/REST
      ▼
┌─────────────────────────────────────────────┐
│           FastAPI Application               │
│  ┌────────────────────────────────────┐     │
│  │      API Layer (v1)                │     │
│  │  - Dictionaries                    │     │
│  │  - Versions                        │     │
│  │  - Exports                         │     │
│  │  - Search                          │     │
│  └────────┬───────────────────────────┘     │
│           │                                 │
│  ┌────────▼────────────────────────────┐    │
│  │      Service Layer                  │    │
│  │  - DictionaryService                │    │
│  │  - VersionService                   │    │
│  │  - AnalysisService                  │    │
│  │  - ExportService                    │    │
│  └────────┬────────────────────────────┘    │
│           │                                 │
│  ┌────────▼────────────────────────────┐    │
│  │     Repository Layer (DAL)          │    │
│  │  - DictionaryRepo                   │    │
│  │  - VersionRepo                      │    │
│  │  - FieldRepo                        │    │
│  │  - AnnotationRepo                   │    │
│  └────────┬────────────────────────────┘    │
│           │                                 │
│  ┌────────▼────────────────────────────┐    │
│  │      Processors                     │    │
│  │  - JSONParser (streaming)           │    │
│  │  - TypeInferrer                     │    │
│  │  - SemanticDetector                 │    │
│  │  - QualityAnalyzer                  │    │
│  │  - PIIDetector                      │    │
│  │  - AIGenerator                      │    │
│  └─────────────────────────────────────┘    │
└─────────────┬───────────────────────────────┘
              │
    ┌─────────┴─────────┐
    ▼                   ▼
┌──────────┐      ┌──────────┐
│PostgreSQL│      │  OpenAI  │
│  (JSONB) │      │  GPT-4   │
└──────────┘      └──────────┘
```

### Request Flow

1. **Upload Flow:**
   ```
   Client → POST /api/v1/dictionaries/upload
     → DictionaryService.create_from_file()
       → JSONParser.parse_streaming() [ijson]
         → TypeInferrer.infer_type()
         → SemanticDetector.detect_semantic_type()
         → QualityAnalyzer.analyze_field()
         → PIIDetector.detect_pii()
         → AIGenerator.generate_description() [optional]
       → DictionaryRepo.create()
       → VersionRepo.create()
       → FieldRepo.bulk_insert()
     → Response with dictionary metadata
   ```

2. **Export Flow:**
   ```
   Client → GET /api/v1/exports/{id}/excel
     → ExportService.export_to_excel()
       → VersionRepo.get_with_fields()
       → ExcelExporter.export()
         → Create workbook with openpyxl
         → Apply professional formatting
         → Write field data with statistics
       → Stream file response
   ```

### Layered Architecture

**1. API Layer** (`/src/api/v1/`)
- FastAPI routers and endpoints
- Request validation (Pydantic)
- Response serialization
- Error handling

**2. Service Layer** (`/src/services/`)
- Business logic orchestration
- Multi-step workflows
- Transaction management
- Cross-repository operations

**3. Repository Layer** (`/src/repositories/`)
- Data access abstraction
- SQLAlchemy ORM operations
- Query optimization
- Relationship loading

**4. Processing Layer** (`/src/processors/`)
- Stateless computation modules
- Type inference algorithms
- Statistical analysis
- External API integration (OpenAI)

**5. Data Layer**
- PostgreSQL with JSONB storage
- SQLAlchemy 2.0 models
- Alembic migrations

## Technology Stack

### Core Framework
- **FastAPI** 0.104+ - Modern async web framework
- **Python** 3.11+ - Language runtime
- **Uvicorn** - ASGI server with hot reload

### Database & ORM
- **PostgreSQL** 15+ - Primary data store with JSONB support
- **SQLAlchemy** 2.0 - ORM with declarative `Mapped[]` types
- **Alembic** - Database migration management
- **psycopg2-binary** - PostgreSQL adapter

### Data Validation
- **Pydantic** 2.5+ - Runtime type validation and settings
- **pydantic-settings** - Environment configuration

### Data Processing
- **pandas** 2.1+ - Statistical analysis and data manipulation
- **NumPy** 1.26+ - Numerical computations
- **ijson** 3.2+ - Streaming JSON parser for large files

### Excel Generation
- **openpyxl** 3.1+ - Excel file creation and formatting

### AI Integration
- **openai** 1.3+ - GPT-4 API client
- **tiktoken** 0.5+ - Token counting for API limits

### Caching & Queue (Phase 2)
- **Redis** 7+ - In-memory cache and job queue backend

### Testing & Quality
- **pytest** 7.4+ - Test framework with async support
- **pytest-cov** - Code coverage reporting
- **pytest-asyncio** - Async test support
- **httpx** - HTTP client for API testing

### Code Quality
- **ruff** - Fast Python linter and formatter (replaces black, isort, flake8)
- **mypy** - Static type checker
- **pre-commit** - Git hooks for quality gates

### Utilities
- **python-json-logger** - Structured JSON logging
- **tenacity** - Retry logic with exponential backoff
- **python-dotenv** - Environment variable management

## Directory Structure

```
backend/
├── src/                        # Application source code
│   ├── api/                    # API layer
│   │   ├── v1/                 # API version 1
│   │   │   ├── dictionaries.py # Dictionary endpoints (upload, list, get, update, delete)
│   │   │   ├── versions.py     # Version endpoints (get, list)
│   │   │   ├── exports.py      # Export endpoints (Excel generation)
│   │   │   └── search.py       # Search endpoints (global search)
│   │   ├── middlewares.py      # Request logging middleware
│   │   └── dependencies.py     # Dependency injection (DB session, services)
│   │
│   ├── core/                   # Core infrastructure
│   │   ├── config.py           # Pydantic settings (env vars)
│   │   ├── database.py         # SQLAlchemy engine and session
│   │   ├── logging.py          # Structured logging configuration
│   │   ├── exceptions.py       # Custom exception classes
│   │   └── security.py         # Auth utilities (placeholder for Phase 2)
│   │
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── base.py             # Base model with common fields
│   │   ├── dictionary.py       # Dictionary model
│   │   ├── version.py          # Version model (schema snapshots)
│   │   ├── field.py            # Field model (column metadata)
│   │   └── annotation.py       # Annotation model (user notes)
│   │
│   ├── schemas/                # Pydantic DTOs (request/response)
│   │   ├── common.py           # Pagination, error responses
│   │   ├── dictionary.py       # Dictionary schemas
│   │   ├── version.py          # Version schemas
│   │   ├── field.py            # Field schemas
│   │   └── export.py           # Export configuration schemas
│   │
│   ├── services/               # Business logic orchestration
│   │   ├── dictionary_service.py  # Dictionary CRUD and upload processing
│   │   ├── version_service.py     # Version management and comparison
│   │   ├── analysis_service.py    # Field analysis coordination
│   │   └── export_service.py      # Export orchestration
│   │
│   ├── processors/             # Stateless computation modules
│   │   ├── json_parser.py         # Streaming JSON parser (ijson)
│   │   ├── type_inferrer.py       # Type inference (string, int, float, etc.)
│   │   ├── semantic_detector.py   # Semantic type detection (email, URL, etc.)
│   │   ├── quality_analyzer.py    # Statistical analysis (min, max, mean, etc.)
│   │   ├── pii_detector.py        # PII detection with confidence scoring
│   │   └── ai_generator.py        # GPT-4 description generation
│   │
│   ├── repositories/           # Data access layer
│   │   ├── base.py                # Base repository with common operations
│   │   ├── dictionary_repo.py     # Dictionary data access
│   │   ├── version_repo.py        # Version data access
│   │   ├── field_repo.py          # Field data access
│   │   └── annotation_repo.py     # Annotation data access
│   │
│   ├── exporters/              # Export format handlers
│   │   ├── base.py                # Base exporter interface
│   │   └── excel_exporter.py      # Excel export with formatting
│   │
│   └── main.py                 # Application entry point (FastAPI app)
│
├── alembic/                    # Database migrations
│   ├── versions/               # Migration files
│   │   └── 2025_11_09_0944_*.py  # Initial schema
│   └── env.py                  # Alembic configuration
│
├── tests/                      # Test suite
│   ├── unit/                   # Unit tests (processors, utilities)
│   ├── integration/            # Integration tests (API, database)
│   ├── fixtures/               # Test data fixtures
│   ├── conftest.py             # Pytest configuration and fixtures
│   └── test_health.py          # Basic health check test
│
├── scripts/                    # Utility scripts
│   └── setup_db.py             # Database initialization script
│
├── logs/                       # Application logs (gitignored)
│
├── .env                        # Environment variables (gitignored)
├── .env.example                # Example environment configuration
├── .gitignore                  # Git ignore rules
├── alembic.ini                 # Alembic configuration
├── pyproject.toml              # Project metadata and tool configuration
├── pytest.ini                  # Pytest configuration
├── requirements.txt            # Production dependencies
├── requirements-dev.txt        # Development dependencies
├── validate_processors.py      # Processor validation script
└── README.md                   # This file
```

## Getting Started

### Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.11+** - [Download](https://www.python.org/downloads/)
- **PostgreSQL 15+** - [Download](https://www.postgresql.org/download/)
- **Redis 7+** (optional for Phase 2) - [Download](https://redis.io/download)
- **Git** - [Download](https://git-scm.com/downloads)

### Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/marcusradder/data-dictionary-gen.git
   cd data-dictionary-gen/backend
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate on macOS/Linux
   source venv/bin/activate

   # Activate on Windows
   venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   # Install production dependencies
   pip install -r requirements.txt

   # Install development dependencies (includes testing, linting, etc.)
   pip install -r requirements-dev.txt
   ```

4. **Set up PostgreSQL database:**
   ```bash
   # Create database and user
   psql -U postgres
   CREATE DATABASE data_dictionary_db;
   CREATE USER ddgen_user WITH PASSWORD 'ddgen_password';
   GRANT ALL PRIVILEGES ON DATABASE data_dictionary_db TO ddgen_user;
   \q
   ```

5. **Configure environment variables:**
   ```bash
   # Copy example environment file
   cp .env.example .env

   # Edit .env with your settings (see Configuration section)
   nano .env  # or use your preferred editor
   ```

   **Required changes:**
   - Set `DATABASE_URL` to match your PostgreSQL configuration
   - Set `OPENAI_API_KEY` if using AI descriptions (optional)
   - Set `OPENAI_ENABLED=false` to disable AI features

6. **Run database migrations:**
   ```bash
   alembic upgrade head
   ```

7. **Start the development server:**
   ```bash
   # Option 1: Using uvicorn directly
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

   # Option 2: Using the main module
   python -m src.main
   ```

8. **Verify installation:**
   ```bash
   # Check health endpoint
   curl http://localhost:8000/health

   # Expected response:
   # {"status":"healthy","app_name":"Data Dictionary Generator","version":"1.0.0","environment":"development"}
   ```

9. **Access API documentation:**
   - **Swagger UI:** http://localhost:8000/api/docs
   - **ReDoc:** http://localhost:8000/api/redoc
   - **OpenAPI JSON:** http://localhost:8000/api/openapi.json

### Quick Start Example

Once the server is running, you can test the API:

```bash
# Upload a JSON file
curl -X POST "http://localhost:8000/api/v1/dictionaries/upload" \
  -F "file=@sample_data.json" \
  -F "name=My First Dictionary" \
  -F "description=Sample data dictionary"

# List all dictionaries
curl "http://localhost:8000/api/v1/dictionaries?limit=10&offset=0"

# Get dictionary details
curl "http://localhost:8000/api/v1/dictionaries/{dictionary_id}"

# Export to Excel
curl "http://localhost:8000/api/v1/exports/{version_id}/excel" \
  -o data_dictionary.xlsx
```

## Configuration

The application uses **Pydantic Settings** to load configuration from environment variables or a `.env` file. All settings are defined in `/src/core/config.py`.

### Environment Variables

#### Application Settings

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `APP_NAME` | str | "Data Dictionary Generator" | Application name |
| `APP_VERSION` | str | "1.0.0" | Application version |
| `ENVIRONMENT` | str | "development" | Environment (development, staging, production) |
| `DEBUG` | bool | false | Enable debug mode |
| `LOG_LEVEL` | str | "INFO" | Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL) |

#### Server Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `HOST` | str | "0.0.0.0" | Server bind address |
| `PORT` | int | 8000 | Server port |
| `RELOAD` | bool | false | Enable auto-reload on code changes |

#### Database Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `DATABASE_URL` | str | "postgresql://..." | PostgreSQL connection string |
| `DB_POOL_SIZE` | int | 10 | Connection pool size |
| `DB_MAX_OVERFLOW` | int | 20 | Max overflow connections |
| `DB_ECHO` | bool | false | Log SQL queries |

**Database URL Format:**
```
postgresql://[user]:[password]@[host]:[port]/[database]
```

#### Security Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `SECRET_KEY` | str | "your-secret-key..." | Secret key for JWT/sessions |
| `API_KEY_ENABLED` | bool | false | Enable API key authentication |
| `ALLOWED_ORIGINS` | list[str] | ["http://localhost:3000",...] | CORS allowed origins |

#### OpenAI Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `OPENAI_API_KEY` | str | "" | OpenAI API key for GPT-4 |
| `OPENAI_MODEL` | str | "gpt-4" | Model to use (gpt-4, gpt-3.5-turbo) |
| `OPENAI_MAX_TOKENS` | int | 500 | Max tokens per description |
| `OPENAI_TEMPERATURE` | float | 0.7 | Creativity/randomness (0.0-1.0) |
| `OPENAI_ENABLED` | bool | true | Enable/disable AI descriptions |

**Cost Considerations:**
- GPT-4 costs approximately $0.03-0.06 per 1K tokens
- A typical field description uses 50-150 tokens
- For a 1000-field dictionary: ~$3-9 in API costs
- Set `OPENAI_ENABLED=false` to disable AI generation

#### File Processing Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `MAX_FILE_SIZE_MB` | int | 500 | Maximum JSON file size (MB) |
| `MAX_RECORDS_TO_ANALYZE` | int | 10000 | Limit for initial analysis |
| `SAMPLE_SIZE` | int | 100 | Number of sample values per field |
| `STREAMING_CHUNK_SIZE` | int | 65536 | Chunk size for streaming parser |

#### Export Configuration

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `EXCEL_MAX_ROWS` | int | 1048576 | Excel row limit |
| `EXPORT_TEMP_DIR` | str | "/tmp/data-dict-exports" | Temporary export directory |

#### Redis Configuration (Phase 2)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `REDIS_URL` | str | "redis://localhost:6380/0" | Redis connection string |
| `REDIS_CACHE_TTL` | int | 3600 | Cache TTL in seconds |

### Configuration Examples

**Development (.env):**
```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
RELOAD=true
DB_ECHO=true
OPENAI_ENABLED=false
MAX_FILE_SIZE_MB=500
```

**Production (.env):**
```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
RELOAD=false
DB_ECHO=false
DATABASE_URL=postgresql://user:pass@prod-db:5432/ddgen_prod
SECRET_KEY=<strong-random-key>
OPENAI_ENABLED=true
OPENAI_API_KEY=<your-api-key>
SENTRY_DSN=<your-sentry-dsn>
```

## API Documentation

### Base URL
```
http://localhost:8000/api/v1
```

### Authentication
**Status:** Not implemented in Phase 1
- API key authentication is disabled (`API_KEY_ENABLED=false`)
- All endpoints are publicly accessible
- Phase 2 will add JWT-based authentication

### Endpoints

#### 1. Dictionaries

**Upload JSON File**
```http
POST /api/v1/dictionaries/upload
Content-Type: multipart/form-data

Parameters:
  file: <binary>          # JSON file to upload
  name: string            # Dictionary name
  description?: string    # Optional description
  generate_ai_descriptions?: boolean  # Enable AI descriptions (default: false)

Response: 201 Created
{
  "id": "uuid",
  "name": "string",
  "description": "string",
  "created_at": "datetime",
  "created_by": "string",
  "version_count": 1,
  "latest_version_number": 1,
  "field_count": 150
}
```

**List Dictionaries**
```http
GET /api/v1/dictionaries?limit=20&offset=0

Query Parameters:
  limit: int (1-100)      # Items per page
  offset: int (>=0)       # Number of items to skip

Response: 200 OK
{
  "data": [
    {
      "id": "uuid",
      "name": "string",
      "description": "string",
      "created_at": "datetime",
      "created_by": "string",
      "version_count": 2,
      "latest_version_number": 2,
      "field_count": 150
    }
  ],
  "meta": {
    "total": 100,
    "limit": 20,
    "offset": 0,
    "has_more": true
  }
}
```

**Get Dictionary Details**
```http
GET /api/v1/dictionaries/{dictionary_id}

Response: 200 OK
{
  "id": "uuid",
  "name": "string",
  "description": "string",
  "created_at": "datetime",
  "created_by": "string",
  "versions": [
    {
      "id": "uuid",
      "version_number": 1,
      "created_at": "datetime",
      "field_count": 150,
      "schema_hash": "string"
    }
  ]
}
```

**Get Dictionary Fields**
```http
GET /api/v1/dictionaries/{dictionary_id}/fields?limit=50&offset=0&search=user&field_type=string

Query Parameters:
  limit: int (1-100)      # Items per page
  offset: int (>=0)       # Items to skip
  search?: string         # Search in field_name and field_path
  field_type?: string     # Filter by type (string, integer, float, etc.)
  semantic_type?: string  # Filter by semantic type (email, url, etc.)
  has_pii?: boolean       # Filter PII fields

Response: 200 OK
{
  "data": [
    {
      "id": "uuid",
      "field_name": "user_email",
      "field_path": "$.user.email",
      "field_type": "string",
      "semantic_type": "email",
      "is_nullable": false,
      "is_unique": true,
      "sample_values": ["user@example.com", "admin@test.com"],
      "statistics": {
        "min_length": 10,
        "max_length": 50,
        "avg_length": 25.5
      },
      "pii_detected": true,
      "pii_types": ["email"],
      "pii_confidence": 0.99,
      "ai_generated_description": "Email address of the user",
      "quality_score": 0.95
    }
  ],
  "meta": {
    "total": 150,
    "limit": 50,
    "offset": 0,
    "has_more": true
  }
}
```

**Update Dictionary**
```http
PATCH /api/v1/dictionaries/{dictionary_id}
Content-Type: application/json

Request Body:
{
  "name": "string",
  "description": "string"
}

Response: 200 OK
{
  "id": "uuid",
  "name": "string",
  "description": "string",
  "updated_at": "datetime"
}
```

**Delete Dictionary**
```http
DELETE /api/v1/dictionaries/{dictionary_id}

Response: 204 No Content
```

#### 2. Versions

**Get Version Details**
```http
GET /api/v1/versions/{version_id}

Response: 200 OK
{
  "id": "uuid",
  "dictionary_id": "uuid",
  "version_number": 1,
  "created_at": "datetime",
  "schema_hash": "string",
  "field_count": 150,
  "fields": [
    {
      "id": "uuid",
      "field_name": "user_id",
      "field_path": "$.user.id",
      "field_type": "integer",
      // ... additional field details
    }
  ]
}
```

**List Versions for Dictionary**
```http
GET /api/v1/dictionaries/{dictionary_id}/versions

Response: 200 OK
{
  "data": [
    {
      "id": "uuid",
      "version_number": 2,
      "created_at": "datetime",
      "field_count": 155,
      "changes": {
        "added": 5,
        "removed": 0,
        "modified": 2
      }
    }
  ]
}
```

#### 3. Exports

**Export to Excel**
```http
GET /api/v1/exports/{version_id}/excel

Response: 200 OK
Content-Type: application/vnd.openxmlformats-officedocument.spreadsheetml.sheet
Content-Disposition: attachment; filename="data_dictionary_v1.xlsx"

<binary Excel file>
```

**Excel Export Format:**
- **Sheet 1: Overview** - Dictionary metadata and summary statistics
- **Sheet 2: Fields** - Complete field listing with:
  - Field Name, Path, Type, Semantic Type
  - Nullable, Unique flags
  - Sample values
  - Statistics (min, max, avg, etc.)
  - PII detection results
  - AI descriptions
  - Quality scores
- **Sheet 3: Statistics** - Aggregated statistics and type distribution
- **Professional formatting:** Headers, colors, column widths, freeze panes

#### 4. Search

**Global Search**
```http
GET /api/v1/search?query=email&limit=20

Query Parameters:
  query: string           # Search term
  limit: int (1-100)      # Results per page
  offset: int (>=0)       # Items to skip
  dictionary_id?: uuid    # Filter by dictionary
  field_type?: string     # Filter by type
  has_pii?: boolean       # Filter PII fields

Response: 200 OK
{
  "data": [
    {
      "field_id": "uuid",
      "field_name": "user_email",
      "field_path": "$.user.email",
      "field_type": "string",
      "semantic_type": "email",
      "dictionary_id": "uuid",
      "dictionary_name": "User Data",
      "version_id": "uuid",
      "version_number": 1,
      "match_score": 0.95
    }
  ],
  "meta": {
    "total": 15,
    "limit": 20,
    "offset": 0,
    "has_more": false
  }
}
```

### Error Responses

All error responses follow this structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context"
    }
  }
}
```

**Error Codes:**
- `400` - `VALIDATION_ERROR` - Invalid request data
- `404` - `NOT_FOUND` - Resource not found
- `422` - `PROCESSING_ERROR` - File processing failed
- `500` - `EXPORT_ERROR` - Export generation failed
- `503` - `EXTERNAL_SERVICE_ERROR` - OpenAI API failure

### Rate Limiting
**Status:** Not implemented in Phase 1
- No rate limiting currently enforced
- Phase 2 will add Redis-based rate limiting

### Interactive Documentation

The API includes auto-generated interactive documentation:

**Swagger UI** (http://localhost:8000/api/docs):
- Interactive API explorer
- Try endpoints directly from browser
- View request/response schemas
- Authentication testing (when enabled)

**ReDoc** (http://localhost:8000/api/redoc):
- Beautiful, responsive documentation
- Three-column layout
- Code samples in multiple languages
- Download OpenAPI spec

## Development Workflow

### Testing

The project uses **pytest** with async support and coverage reporting.

**Run all tests:**
```bash
pytest
```

**Run with coverage:**
```bash
pytest --cov=src --cov-report=html
```

**Run specific test file:**
```bash
pytest tests/test_health.py
```

**Run specific test function:**
```bash
pytest tests/test_health.py::test_health_check
```

**Run with verbose output:**
```bash
pytest -v
```

**Run integration tests only:**
```bash
pytest tests/integration/
```

**Run unit tests only:**
```bash
pytest tests/unit/
```

**View coverage report:**
```bash
# Generate HTML coverage report
pytest --cov=src --cov-report=html

# Open in browser
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
start htmlcov/index.html  # Windows
```

**Test Configuration:**
- Configuration: `pytest.ini` and `pyproject.toml`
- Fixtures: `tests/conftest.py`
- Minimum coverage: Not enforced (intentionally low coverage in Phase 1)

### Code Quality

**Linting with Ruff:**
```bash
# Check for issues
ruff check src/

# Check specific file
ruff check src/api/v1/dictionaries.py

# Auto-fix issues
ruff check --fix src/

# Show all violations
ruff check --show-files src/
```

**Formatting with Ruff:**
```bash
# Format code
ruff format src/

# Check formatting without changes
ruff format --check src/
```

**Type Checking with MyPy:**
```bash
# Type check entire project
mypy src/

# Type check specific module
mypy src/services/dictionary_service.py

# Show error codes
mypy --show-error-codes src/
```

**Pre-commit Hooks:**
```bash
# Install pre-commit hooks
pre-commit install

# Run manually on all files
pre-commit run --all-files

# Run on specific files
pre-commit run --files src/main.py
```

**Tool Configuration:**
- **Ruff:** `pyproject.toml` - Line length 100, Python 3.11+
- **MyPy:** `pyproject.toml` - Strict type checking enabled
- **Pytest:** `pytest.ini` and `pyproject.toml`

### Database Migrations

**Create a new migration:**
```bash
alembic revision --autogenerate -m "Add new field to table"
```

**Apply migrations:**
```bash
# Upgrade to latest
alembic upgrade head

# Upgrade to specific revision
alembic upgrade <revision_id>

# Upgrade one version
alembic upgrade +1
```

**Downgrade migrations:**
```bash
# Downgrade one version
alembic downgrade -1

# Downgrade to specific revision
alembic downgrade <revision_id>

# Downgrade to base (caution!)
alembic downgrade base
```

**View migration history:**
```bash
# Show current version
alembic current

# Show migration history
alembic history

# Show pending migrations
alembic history --verbose
```

**Migration Best Practices:**
- Always review auto-generated migrations
- Test migrations on a copy of production data
- Include both upgrade and downgrade logic
- Use descriptive migration messages
- Never edit applied migrations

### Running the Server

**Development mode (auto-reload):**
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

**Production mode:**
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

**With custom log level:**
```bash
uvicorn src.main:app --reload --log-level debug
```

**Using Gunicorn (production):**
```bash
gunicorn src.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --access-logfile - \
  --error-logfile -
```

### Logging

The application uses structured JSON logging with `python-json-logger`.

**Log Levels:**
- `DEBUG` - Detailed diagnostic information
- `INFO` - General informational messages
- `WARNING` - Warning messages for non-critical issues
- `ERROR` - Error messages for failures
- `CRITICAL` - Critical failures requiring immediate attention

**Log Output:**
```json
{
  "timestamp": "2025-11-09T12:00:00.000Z",
  "level": "INFO",
  "logger": "src.services.dictionary_service",
  "message": "Processing JSON file",
  "filename": "sample.json",
  "file_size_mb": 45.2,
  "environment": "development"
}
```

**Logs Location:**
- Development: `logs/app.log`
- Production: stdout/stderr (captured by logging infrastructure)

### Development Tools

**Interactive Python shell:**
```bash
# Start iPython with application context
ipython
>>> from src.core.database import get_db
>>> from src.models import Dictionary, Version, Field
>>> # Explore models and database
```

**Database shell:**
```bash
# Connect to PostgreSQL
psql -U ddgen_user -d data_dictionary_db
```

**Validate processors:**
```bash
# Run processor validation script
python validate_processors.py
```

## Core Components

### 1. Processors

**JSONParser** (`src/processors/json_parser.py`)
- Streaming JSON parser using `ijson`
- Handles files up to 500MB without loading into memory
- Extracts field paths and sample values
- Supports nested objects and arrays

**TypeInferrer** (`src/processors/type_inferrer.py`)
- Infers basic types: `string`, `integer`, `float`, `boolean`, `array`, `object`
- Handles mixed-type fields with majority voting
- Detects nullable fields

**SemanticDetector** (`src/processors/semantic_detector.py`)
- Detects semantic types: `email`, `url`, `phone`, `date`, `time`, `datetime`, `currency`, `ssn`, `zipcode`, `ipv4`, `ipv6`, `uuid`, `credit_card`
- Uses regex patterns and heuristics
- Returns confidence scores

**QualityAnalyzer** (`src/processors/quality_analyzer.py`)
- Computes statistics: min, max, mean, median, percentiles (25th, 50th, 75th, 95th), standard deviation
- Calculates quality scores based on completeness and consistency
- Identifies unique and nullable fields

**PIIDetector** (`src/processors/pii_detector.py`)
- Detects PII types: email, phone, SSN, credit card, address, name patterns
- Returns confidence scores (0.0-1.0)
- Configurable sensitivity thresholds

**AIGenerator** (`src/processors/ai_generator.py`)
- Generates field descriptions using GPT-4
- Includes context: field name, type, sample values, statistics
- Implements retry logic with exponential backoff
- Respects token limits and rate limits
- Can be disabled via `OPENAI_ENABLED=false`

### 2. Services

**DictionaryService** (`src/services/dictionary_service.py`)
- Orchestrates dictionary creation from uploaded files
- Coordinates parsing, analysis, and storage
- Manages transactions across repositories
- Handles version creation

**VersionService** (`src/services/version_service.py`)
- Manages schema versions
- Computes schema hashes for change detection
- Compares versions to identify changes

**AnalysisService** (`src/services/analysis_service.py`)
- Coordinates field analysis across processors
- Manages parallel processing of fields
- Aggregates results from multiple analyzers

**ExportService** (`src/services/export_service.py`)
- Orchestrates export generation
- Manages temporary file creation
- Streams export responses

### 3. Repositories

**Base Repository Pattern** (`src/repositories/base.py`)
- Generic CRUD operations: `create()`, `get()`, `list()`, `update()`, `delete()`
- Pagination support
- Transaction management
- Relationship loading

**DictionaryRepo** (`src/repositories/dictionary_repo.py`)
- Dictionary-specific queries
- Version relationship loading
- Search functionality

**VersionRepo** (`src/repositories/version_repo.py`)
- Version queries with field loading
- Schema hash lookup
- Version comparison

**FieldRepo** (`src/repositories/field_repo.py`)
- Bulk insert optimization
- Advanced filtering (type, semantic type, PII)
- Search across name and path
- Statistics retrieval

**AnnotationRepo** (`src/repositories/annotation_repo.py`)
- User annotation CRUD
- Field association management

### 4. Models

**SQLAlchemy 2.0 Models** with declarative `Mapped[]` types:

**Dictionary** (`src/models/dictionary.py`)
```python
class Dictionary(Base):
    id: Mapped[UUID]
    name: Mapped[str]
    description: Mapped[str | None]
    created_at: Mapped[datetime]
    created_by: Mapped[str]
    versions: Mapped[list["Version"]] = relationship(back_populates="dictionary")
```

**Version** (`src/models/version.py`)
```python
class Version(Base):
    id: Mapped[UUID]
    dictionary_id: Mapped[UUID]
    version_number: Mapped[int]
    schema_hash: Mapped[str]
    created_at: Mapped[datetime]
    fields: Mapped[list["Field"]] = relationship(back_populates="version")
```

**Field** (`src/models/field.py`)
```python
class Field(Base):
    id: Mapped[UUID]
    version_id: Mapped[UUID]
    field_name: Mapped[str]
    field_path: Mapped[str]
    field_type: Mapped[str]
    semantic_type: Mapped[str | None]
    is_nullable: Mapped[bool]
    is_unique: Mapped[bool]
    sample_values: Mapped[list[Any]]  # JSONB
    statistics: Mapped[dict[str, Any] | None]  # JSONB
    pii_detected: Mapped[bool]
    pii_types: Mapped[list[str] | None]  # JSONB
    pii_confidence: Mapped[float | None]
    ai_generated_description: Mapped[str | None]
    quality_score: Mapped[float | None]
```

**Annotation** (`src/models/annotation.py`)
```python
class Annotation(Base):
    id: Mapped[UUID]
    field_id: Mapped[UUID]
    user_id: Mapped[str]
    annotation_text: Mapped[str]
    created_at: Mapped[datetime]
    updated_at: Mapped[datetime]
```

## Design Patterns

### 1. Layered Architecture

The application follows a strict layered architecture:
- **API Layer:** Request handling and validation
- **Service Layer:** Business logic orchestration
- **Repository Layer:** Data access abstraction
- **Model Layer:** Database schema definition

**Benefits:**
- Clear separation of concerns
- Testability through dependency injection
- Easy to swap implementations (e.g., mock repositories for testing)

### 2. Repository Pattern

Repositories abstract database access:
```python
class BaseRepository(Generic[ModelType]):
    def create(self, obj: ModelType) -> ModelType: ...
    def get(self, id: UUID) -> ModelType | None: ...
    def list(self, limit: int, offset: int) -> tuple[list[ModelType], int]: ...
    def update(self, id: UUID, updates: dict) -> ModelType: ...
    def delete(self, id: UUID) -> None: ...
```

**Benefits:**
- Single source of truth for data access
- Easy to optimize queries
- Simplified testing with mock repositories

### 3. Dependency Injection

FastAPI's dependency injection system provides services and database sessions:
```python
def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_dictionary_service(db: Session = Depends(get_db)) -> DictionaryService:
    return DictionaryService(db)
```

**Benefits:**
- Loose coupling
- Easy testing
- Resource lifecycle management

### 4. Service Orchestration

Services coordinate multi-step workflows:
```python
class DictionaryService:
    def create_from_file(self, file: UploadFile, name: str) -> Dictionary:
        # 1. Parse JSON
        fields = self.json_parser.parse(file)

        # 2. Analyze fields
        analyzed_fields = self.analysis_service.analyze(fields)

        # 3. Create dictionary and version
        dictionary = self.dictionary_repo.create(...)
        version = self.version_repo.create(...)

        # 4. Bulk insert fields
        self.field_repo.bulk_insert(analyzed_fields)

        return dictionary
```

**Benefits:**
- Complex workflows broken into steps
- Transaction management
- Error handling and rollback

### 5. Streaming Processing

Large file processing uses streaming to avoid memory issues:
```python
def parse_streaming(file: BinaryIO) -> Iterator[FieldData]:
    parser = ijson.items(file, 'item')
    for item in parser:
        yield process_item(item)
```

**Benefits:**
- Constant memory usage
- Handles files larger than RAM
- Incremental processing

### 6. Exception Hierarchy

Custom exceptions provide structured error handling:
```python
class DataDictException(Exception): ...
class ValidationError(DataDictException): ...
class NotFoundError(DataDictException): ...
class ProcessingError(DataDictException): ...
```

**Benefits:**
- Consistent error responses
- Easy to add exception handlers
- Clear error semantics

## Known Limitations

The following features are intentionally **not implemented** in Phase 1:

### 1. Authentication & Authorization
- **Status:** Placeholder only (`API_KEY_ENABLED=false`)
- **Impact:** All endpoints are publicly accessible
- **Rationale:** Focus on core functionality first
- **Roadmap:** Phase 2 will add JWT-based authentication with role-based access control (RBAC)

### 2. Rate Limiting
- **Status:** Not implemented (`RATE_LIMIT_ENABLED=false`)
- **Impact:** No protection against abuse or DDoS
- **Rationale:** Not critical for internal/prototype deployments
- **Roadmap:** Phase 2 will add Redis-based rate limiting (requests per minute)

### 3. Background Job Processing
- **Status:** All processing is synchronous
- **Impact:** Large file uploads block the request thread
- **Rationale:** Simpler implementation, acceptable for files <500MB
- **Roadmap:** Phase 2 will add Celery for async processing with job status tracking

### 4. Monitoring & Observability
- **Status:** Basic logging only
- **Impact:** Limited visibility into production issues
- **Rationale:** Not needed for development/testing
- **Roadmap:** Phase 2 will add:
  - Sentry for error tracking
  - Prometheus metrics
  - Structured logging aggregation
  - Performance monitoring (APM)

### 5. Comprehensive Test Coverage
- **Status:** Minimal tests (~5% coverage)
- **Impact:** Increased risk of regressions
- **Rationale:** Rapid prototyping phase
- **Roadmap:** Ongoing improvement, target 80% coverage

### 6. API Versioning Strategy
- **Status:** Single version (v1) with no deprecation plan
- **Impact:** Breaking changes will affect all clients
- **Rationale:** MVP stage, no external clients yet
- **Roadmap:** Implement versioning strategy before public release

### 7. Data Retention & Archival
- **Status:** No automatic cleanup of old versions or exports
- **Impact:** Database/storage growth over time
- **Rationale:** Not critical for small-scale deployments
- **Roadmap:** Phase 2 will add configurable retention policies

### 8. Multi-Tenancy
- **Status:** Single-tenant architecture
- **Impact:** Cannot isolate data for multiple organizations
- **Rationale:** Designed for single-organization use
- **Roadmap:** Consider for SaaS deployment

### 9. Advanced Search
- **Status:** Basic SQL LIKE search only
- **Impact:** No fuzzy matching, relevance scoring, or faceted search
- **Rationale:** Full-text search adds complexity
- **Roadmap:** Phase 3 may add PostgreSQL full-text search or Elasticsearch

### 10. Export Formats
- **Status:** Excel only
- **Impact:** No CSV, Parquet, or JSON export options
- **Rationale:** Excel is primary requirement
- **Roadmap:** Additional formats can be added easily (see `src/exporters/`)

## Troubleshooting

### Common Issues

#### 1. Database Connection Errors

**Error:** `sqlalchemy.exc.OperationalError: could not connect to server`

**Solutions:**
- Verify PostgreSQL is running: `pg_isready`
- Check `DATABASE_URL` in `.env` matches your PostgreSQL configuration
- Ensure database exists: `psql -l | grep data_dictionary_db`
- Check PostgreSQL logs: `tail -f /usr/local/var/log/postgresql.log` (macOS)

#### 2. Migration Errors

**Error:** `alembic.util.exc.CommandError: Can't locate revision identified by 'xyz'`

**Solutions:**
```bash
# Reset migrations (WARNING: deletes all data)
alembic downgrade base
alembic upgrade head

# Or recreate database
dropdb data_dictionary_db
createdb data_dictionary_db
alembic upgrade head
```

#### 3. Import Errors

**Error:** `ModuleNotFoundError: No module named 'src'`

**Solutions:**
- Ensure you're in the `backend/` directory
- Activate virtual environment: `source venv/bin/activate`
- Reinstall dependencies: `pip install -r requirements.txt`
- Check PYTHONPATH: `export PYTHONPATH="${PYTHONPATH}:$(pwd)"`

#### 4. OpenAI API Errors

**Error:** `openai.error.AuthenticationError: Invalid API key`

**Solutions:**
- Verify `OPENAI_API_KEY` in `.env`
- Check API key at https://platform.openai.com/api-keys
- Disable AI features: Set `OPENAI_ENABLED=false` in `.env`
- Check account credits: https://platform.openai.com/usage

**Error:** `openai.error.RateLimitError: Rate limit exceeded`

**Solutions:**
- Reduce concurrent requests
- Increase retry delays in `src/processors/ai_generator.py`
- Upgrade OpenAI plan for higher limits
- Process files in smaller batches

#### 5. File Upload Errors

**Error:** `413 Request Entity Too Large`

**Solutions:**
- Check `MAX_FILE_SIZE_MB` in `.env`
- Increase Nginx/reverse proxy limits (if applicable)
- Split large files into smaller chunks

**Error:** `422 Unprocessable Entity: Invalid JSON`

**Solutions:**
- Validate JSON syntax: `python -m json.tool < file.json`
- Check for trailing commas, missing quotes
- Ensure UTF-8 encoding: `file -I file.json`

#### 6. Excel Export Errors

**Error:** `ExportError: Excel row limit exceeded`

**Solutions:**
- Reduce fields in export (filter or paginate)
- Excel has 1,048,576 row limit (hardcoded)
- Consider CSV export for larger datasets (not yet implemented)

#### 7. Memory Issues

**Error:** `MemoryError` during large file processing

**Solutions:**
- Reduce `MAX_RECORDS_TO_ANALYZE` in `.env`
- Reduce `SAMPLE_SIZE` in `.env`
- Increase system memory/swap
- Ensure streaming parser is used (ijson)

### Debug Mode

Enable debug mode for detailed error messages:

**.env:**
```env
DEBUG=true
LOG_LEVEL=DEBUG
DB_ECHO=true
```

**Run with debugger:**
```bash
# Use pdb
python -m pdb src/main.py

# Use ipdb (better)
pip install ipdb
ipdb src/main.py
```

### Logging

Check application logs:
```bash
# View real-time logs
tail -f logs/app.log

# Search logs for errors
grep ERROR logs/app.log

# View last 100 lines
tail -n 100 logs/app.log
```

### Database Inspection

```bash
# Connect to database
psql -U ddgen_user -d data_dictionary_db

# List tables
\dt

# Describe table
\d dictionaries

# Count records
SELECT COUNT(*) FROM dictionaries;

# View recent dictionaries
SELECT id, name, created_at FROM dictionaries ORDER BY created_at DESC LIMIT 10;
```

### Performance Issues

**Slow API responses:**
- Enable SQL query logging: `DB_ECHO=true`
- Check for missing indexes
- Review slow query log
- Use `EXPLAIN ANALYZE` on queries
- Consider pagination for large result sets

**High memory usage:**
- Check for memory leaks in long-running processes
- Monitor with `htop` or `ps aux`
- Review streaming parser implementation
- Reduce `SAMPLE_SIZE` and `MAX_RECORDS_TO_ANALYZE`

### Getting Help

1. **Check logs:** Review `logs/app.log` for detailed error messages
2. **Enable debug mode:** Set `DEBUG=true` and `LOG_LEVEL=DEBUG`
3. **Search issues:** Check GitHub issues for similar problems
4. **Reproduce:** Create minimal reproducible example
5. **Report:** Open GitHub issue with:
   - Environment details (Python version, OS)
   - Error message and stack trace
   - Steps to reproduce
   - Configuration (redact secrets)

---

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure `ruff check` and `mypy` pass
5. Submit a pull request

## Contact

For questions or support, please open a GitHub issue.
