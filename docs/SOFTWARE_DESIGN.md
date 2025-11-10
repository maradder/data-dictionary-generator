# Software Design Document
## Data Dictionary Generator - Backend System

**Version:** 1.0
**Date:** 2025-11-08
**Status:** Draft
**Related Documents:**
- [CONOPS.md](./CONOPS.md)
- [REQUIREMENTS.md](./REQUIREMENTS.md)

---

## Table of Contents
1. [Introduction](#1-introduction)
2. [System Architecture](#2-system-architecture)
3. [Database Design](#3-database-design)
4. [API Design](#4-api-design)
5. [Core Processing Components](#5-core-processing-components)
6. [Service Layer Design](#6-service-layer-design)
7. [Data Flow & Algorithms](#7-data-flow--algorithms)
8. [Security Design](#8-security-design)
9. [Error Handling & Logging](#9-error-handling--logging)
10. [Performance Optimization](#10-performance-optimization)
11. [Testing Strategy](#11-testing-strategy)
12. [Deployment Architecture](#12-deployment-architecture)

---

## 1. Introduction

### 1.1 Purpose
This document describes the detailed software design for the Data Dictionary Generator backend system. It provides the technical blueprint for implementation, focusing on API-first design principles to enable both direct API consumption and frontend integration.

### 1.2 Design Goals
1. **API-First**: Design a comprehensive REST API that can be used independently
2. **Modularity**: Clear separation of concerns with layered architecture
3. **Extensibility**: Easy to add new analyzers, exporters, and integrations
4. **Performance**: Handle large JSON files efficiently with streaming and async processing
5. **Testability**: Dependency injection and interface-based design for comprehensive testing
6. **Maintainability**: Clean code, well-documented, following Python best practices

### 1.3 Technology Stack Summary

**Core Framework:**
- Python 3.11+
- FastAPI 0.104+
- SQLAlchemy 2.0+
- Pydantic 2.5+

**Database:**
- PostgreSQL 15+ (primary data store)
- Redis 7+ (caching, job queues - Phase 2)

**Processing:**
- Pandas 2.1+ (data analysis)
- ijson (streaming JSON parsing)
- NumPy (statistical calculations)

**Excel Generation:**
- openpyxl 3.1+ (Excel creation)

**AI Integration:**
- OpenAI Python SDK (GPT-4/3.5-turbo)
- tiktoken (token counting)

**Testing:**
- pytest 7.4+
- pytest-asyncio
- pytest-cov
- httpx (async test client)

**Development:**
- ruff (linting/formatting)
- mypy (type checking)
- pre-commit (git hooks)
- Alembic (database migrations)

---

## 2. System Architecture

### 2.1 Layered Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Layer (FastAPI)                       │
│  ┌────────────┬──────────────┬──────────────┬─────────────────┐ │
│  │ Dictionary │   Version    │   Export     │   Search        │ │
│  │ Endpoints  │  Endpoints   │  Endpoints   │   Endpoints     │ │
│  └────────────┴──────────────┴──────────────┴─────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │ DTOs (Pydantic Models)
┌────────────────────────────▼────────────────────────────────────┐
│                        Service Layer                             │
│  ┌────────────┬──────────────┬──────────────┬─────────────────┐ │
│  │ Dictionary │   Version    │   Export     │   Analysis      │ │
│  │  Service   │   Service    │   Service    │   Service       │ │
│  └────────────┴──────────────┴──────────────┴─────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │ Domain Models
┌────────────────────────────▼────────────────────────────────────┐
│                     Processing Layer                             │
│  ┌────────────┬──────────────┬──────────────┬─────────────────┐ │
│  │   JSON     │    Type      │   Quality    │   AI            │ │
│  │  Parser    │   Inferrer   │   Analyzer   │   Generator     │ │
│  └────────────┴──────────────┴──────────────┴─────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    Repository Layer                              │
│  ┌────────────┬──────────────┬──────────────┬─────────────────┐ │
│  │ Dictionary │   Field      │   Version    │   Annotation    │ │
│  │    Repo    │    Repo      │    Repo      │     Repo        │ │
│  └────────────┴──────────────┴──────────────┴─────────────────┘ │
└────────────────────────────┬────────────────────────────────────┘
                             │ SQLAlchemy ORM
┌────────────────────────────▼────────────────────────────────────┐
│                    Database (PostgreSQL)                         │
│     dictionaries  │  fields  │  versions  │  annotations        │
└──────────────────────────────────────────────────────────────────┘
```

### 2.2 Package Structure

```
data-dictionary-gen/
├── backend/
│   ├── alembic/                    # Database migrations
│   │   ├── versions/
│   │   └── env.py
│   ├── src/
│   │   ├── api/                    # API Layer
│   │   │   ├── __init__.py
│   │   │   ├── dependencies.py     # Dependency injection
│   │   │   ├── middlewares.py      # CORS, logging, error handling
│   │   │   └── v1/                 # API v1 endpoints
│   │   │       ├── __init__.py
│   │   │       ├── dictionaries.py
│   │   │       ├── versions.py
│   │   │       ├── exports.py
│   │   │       └── search.py
│   │   ├── core/                   # Core configuration
│   │   │   ├── __init__.py
│   │   │   ├── config.py           # Settings (Pydantic BaseSettings)
│   │   │   ├── database.py         # DB connection, session
│   │   │   ├── security.py         # Auth utilities
│   │   │   └── logging.py          # Logging configuration
│   │   ├── models/                 # Database Models (SQLAlchemy)
│   │   │   ├── __init__.py
│   │   │   ├── dictionary.py
│   │   │   ├── field.py
│   │   │   ├── version.py
│   │   │   └── annotation.py
│   │   ├── schemas/                # DTOs (Pydantic)
│   │   │   ├── __init__.py
│   │   │   ├── dictionary.py
│   │   │   ├── field.py
│   │   │   ├── version.py
│   │   │   └── common.py           # Shared schemas
│   │   ├── services/               # Business Logic
│   │   │   ├── __init__.py
│   │   │   ├── dictionary_service.py
│   │   │   ├── version_service.py
│   │   │   ├── export_service.py
│   │   │   └── analysis_service.py
│   │   ├── processors/             # Processing Components
│   │   │   ├── __init__.py
│   │   │   ├── json_parser.py      # JSON parsing
│   │   │   ├── type_inferrer.py    # Type inference
│   │   │   ├── quality_analyzer.py # Data quality metrics
│   │   │   ├── semantic_detector.py # Semantic type detection
│   │   │   ├── pii_detector.py     # PII detection
│   │   │   └── ai_generator.py     # AI descriptions
│   │   ├── repositories/           # Data Access
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Base repository
│   │   │   ├── dictionary_repo.py
│   │   │   ├── field_repo.py
│   │   │   └── version_repo.py
│   │   ├── exporters/              # Export Handlers
│   │   │   ├── __init__.py
│   │   │   ├── base.py             # Base exporter interface
│   │   │   └── excel_exporter.py
│   │   └── main.py                 # FastAPI application
│   ├── tests/
│   │   ├── unit/
│   │   ├── integration/
│   │   └── fixtures/
│   ├── pyproject.toml              # Project metadata, dependencies
│   ├── requirements.txt            # Production dependencies
│   ├── requirements-dev.txt        # Development dependencies
│   └── Dockerfile
├── frontend/                       # (Future - React app)
├── docs/
└── docker-compose.yml
```

### 2.3 Dependency Injection Pattern

Using FastAPI's dependency injection system:

```python
# api/dependencies.py
from typing import Annotated
from fastapi import Depends
from sqlalchemy.orm import Session

def get_db() -> Generator[Session, None, None]:
    """Database session dependency"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_dictionary_service(
    db: Session = Depends(get_db)
) -> DictionaryService:
    """Dictionary service dependency"""
    repo = DictionaryRepository(db)
    return DictionaryService(repo)

# Usage in endpoints
@router.post("/dictionaries")
async def create_dictionary(
    service: Annotated[DictionaryService, Depends(get_dictionary_service)]
):
    ...
```

---

## 3. Database Design

### 3.1 Entity Relationship Diagram

```
┌─────────────────────────────────┐
│        dictionaries             │
├─────────────────────────────────┤
│ id (UUID, PK)                   │
│ name (VARCHAR)                  │
│ description (TEXT)              │
│ source_file_name (VARCHAR)      │
│ source_file_size (BIGINT)       │
│ total_records_analyzed (INT)    │
│ created_at (TIMESTAMP)          │
│ created_by (VARCHAR)            │
│ updated_at (TIMESTAMP)          │
│ metadata (JSONB)                │ # Additional flexible metadata
└────────────┬────────────────────┘
             │ 1
             │
             │ N
┌────────────▼────────────────────┐
│          versions               │
├─────────────────────────────────┤
│ id (UUID, PK)                   │
│ dictionary_id (UUID, FK)        │
│ version_number (INT)            │
│ schema_hash (VARCHAR)           │ # For change detection
│ created_at (TIMESTAMP)          │
│ created_by (VARCHAR)            │
│ notes (TEXT)                    │
│ processing_stats (JSONB)        │ # Processing metrics
└────────────┬────────────────────┘
             │ 1
             │
             │ N
┌────────────▼────────────────────┐
│           fields                │
├─────────────────────────────────┤
│ id (UUID, PK)                   │
│ version_id (UUID, FK)           │
│ field_path (VARCHAR)            │ # e.g., "user.address.city"
│ field_name (VARCHAR)            │ # Last part of path
│ parent_path (VARCHAR)           │ # Parent path for hierarchy
│ nesting_level (INT)             │
│ data_type (VARCHAR)             │ # string, integer, float, etc.
│ semantic_type (VARCHAR)         │ # email, date, currency, etc.
│ is_nullable (BOOLEAN)           │
│ is_array (BOOLEAN)              │
│ array_item_type (VARCHAR)       │
│ sample_values (JSONB)           │ # Array of sample values
│ null_count (INT)                │
│ null_percentage (DECIMAL)       │
│ total_count (INT)               │
│ distinct_count (INT)            │
│ cardinality_ratio (DECIMAL)     │
│ min_value (DECIMAL)             │ # For numeric fields
│ max_value (DECIMAL)             │
│ mean_value (DECIMAL)            │
│ median_value (DECIMAL)          │
│ std_dev (DECIMAL)               │
│ percentile_25 (DECIMAL)         │
│ percentile_50 (DECIMAL)         │
│ percentile_75 (DECIMAL)         │
│ is_pii (BOOLEAN)                │
│ pii_type (VARCHAR)              │ # email, phone, ssn, etc.
│ confidence_score (DECIMAL)      │ # Type inference confidence
│ created_at (TIMESTAMP)          │
│ position (INT)                  │ # Original field order
└────────────┬────────────────────┘
             │ 1
             │
             │ N
┌────────────▼────────────────────┐
│        annotations              │
├─────────────────────────────────┤
│ id (UUID, PK)                   │
│ field_id (UUID, FK)             │
│ description (TEXT)              │ # User or AI-generated
│ business_name (VARCHAR)         │ # Business-friendly name
│ is_ai_generated (BOOLEAN)       │
│ ai_model_version (VARCHAR)      │
│ business_owner (VARCHAR)        │
│ tags (JSONB)                    │ # Array of tags
│ created_at (TIMESTAMP)          │
│ created_by (VARCHAR)            │
│ updated_at (TIMESTAMP)          │
│ updated_by (VARCHAR)            │
└─────────────────────────────────┘
```

### 3.2 Database Schema (SQL)

```sql
-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Dictionaries table
CREATE TABLE dictionaries (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    source_file_name VARCHAR(500),
    source_file_size BIGINT,
    total_records_analyzed INTEGER,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB,
    CONSTRAINT name_not_empty CHECK (length(name) > 0)
);

-- Indexes for dictionaries
CREATE INDEX idx_dictionaries_created_at ON dictionaries(created_at DESC);
CREATE INDEX idx_dictionaries_created_by ON dictionaries(created_by);
CREATE INDEX idx_dictionaries_name ON dictionaries(name);

-- Versions table
CREATE TABLE versions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    dictionary_id UUID NOT NULL REFERENCES dictionaries(id) ON DELETE CASCADE,
    version_number INTEGER NOT NULL,
    schema_hash VARCHAR(64) NOT NULL, -- SHA-256 hash
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    notes TEXT,
    processing_stats JSONB,
    CONSTRAINT unique_version_per_dictionary UNIQUE (dictionary_id, version_number),
    CONSTRAINT version_number_positive CHECK (version_number > 0)
);

-- Indexes for versions
CREATE INDEX idx_versions_dictionary_id ON versions(dictionary_id);
CREATE INDEX idx_versions_created_at ON versions(created_at DESC);
CREATE INDEX idx_versions_schema_hash ON versions(schema_hash);

-- Fields table
CREATE TABLE fields (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    version_id UUID NOT NULL REFERENCES versions(id) ON DELETE CASCADE,
    field_path VARCHAR(1000) NOT NULL,
    field_name VARCHAR(255) NOT NULL,
    parent_path VARCHAR(1000),
    nesting_level INTEGER NOT NULL DEFAULT 0,
    data_type VARCHAR(50) NOT NULL,
    semantic_type VARCHAR(50),
    is_nullable BOOLEAN DEFAULT TRUE,
    is_array BOOLEAN DEFAULT FALSE,
    array_item_type VARCHAR(50),
    sample_values JSONB,
    null_count INTEGER DEFAULT 0,
    null_percentage DECIMAL(5, 2),
    total_count INTEGER DEFAULT 0,
    distinct_count INTEGER DEFAULT 0,
    cardinality_ratio DECIMAL(5, 4),
    min_value DECIMAL(20, 6),
    max_value DECIMAL(20, 6),
    mean_value DECIMAL(20, 6),
    median_value DECIMAL(20, 6),
    std_dev DECIMAL(20, 6),
    percentile_25 DECIMAL(20, 6),
    percentile_50 DECIMAL(20, 6),
    percentile_75 DECIMAL(20, 6),
    is_pii BOOLEAN DEFAULT FALSE,
    pii_type VARCHAR(50),
    confidence_score DECIMAL(5, 2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    position INTEGER,
    CONSTRAINT unique_field_per_version UNIQUE (version_id, field_path),
    CONSTRAINT nesting_level_non_negative CHECK (nesting_level >= 0),
    CONSTRAINT null_percentage_range CHECK (null_percentage BETWEEN 0 AND 100),
    CONSTRAINT cardinality_ratio_range CHECK (cardinality_ratio BETWEEN 0 AND 1)
);

-- Indexes for fields
CREATE INDEX idx_fields_version_id ON fields(version_id);
CREATE INDEX idx_fields_field_path ON fields(field_path);
CREATE INDEX idx_fields_data_type ON fields(data_type);
CREATE INDEX idx_fields_semantic_type ON fields(semantic_type);
CREATE INDEX idx_fields_is_pii ON fields(is_pii) WHERE is_pii = TRUE;
CREATE INDEX idx_fields_parent_path ON fields(parent_path);
CREATE INDEX idx_fields_nesting_level ON fields(nesting_level);
-- GIN index for JSONB sample_values for efficient queries
CREATE INDEX idx_fields_sample_values ON fields USING GIN (sample_values);

-- Annotations table
CREATE TABLE annotations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    field_id UUID NOT NULL REFERENCES fields(id) ON DELETE CASCADE,
    description TEXT,
    business_name VARCHAR(255),
    is_ai_generated BOOLEAN DEFAULT FALSE,
    ai_model_version VARCHAR(50),
    business_owner VARCHAR(255),
    tags JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(255),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_by VARCHAR(255)
);

-- Indexes for annotations
CREATE INDEX idx_annotations_field_id ON annotations(field_id);
CREATE INDEX idx_annotations_business_owner ON annotations(business_owner);
CREATE INDEX idx_annotations_is_ai_generated ON annotations(is_ai_generated);
CREATE INDEX idx_annotations_tags ON annotations USING GIN (tags);

-- Full-text search (Phase 2)
-- CREATE INDEX idx_fields_search ON fields USING GIN (
--     to_tsvector('english', coalesce(field_path, '') || ' ' || coalesce(field_name, ''))
-- );
-- CREATE INDEX idx_annotations_search ON annotations USING GIN (
--     to_tsvector('english', coalesce(description, '') || ' ' || coalesce(business_name, ''))
-- );

-- Triggers for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_dictionaries_updated_at
    BEFORE UPDATE ON dictionaries
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_annotations_updated_at
    BEFORE UPDATE ON annotations
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### 3.3 SQLAlchemy Models

```python
# models/dictionary.py
from datetime import datetime
from uuid import uuid4
from sqlalchemy import Column, String, Text, BigInteger, Integer, TIMESTAMP, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .base import Base

class Dictionary(Base):
    __tablename__ = "dictionaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    source_file_name = Column(String(500))
    source_file_size = Column(BigInteger)
    total_records_analyzed = Column(Integer)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    created_by = Column(String(255))
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON)

    # Relationships
    versions = relationship("Version", back_populates="dictionary", cascade="all, delete-orphan")


# models/version.py
class Version(Base):
    __tablename__ = "versions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    dictionary_id = Column(UUID(as_uuid=True), ForeignKey("dictionaries.id", ondelete="CASCADE"), nullable=False)
    version_number = Column(Integer, nullable=False)
    schema_hash = Column(String(64), nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    created_by = Column(String(255))
    notes = Column(Text)
    processing_stats = Column(JSON)

    # Relationships
    dictionary = relationship("Dictionary", back_populates="versions")
    fields = relationship("Field", back_populates="version", cascade="all, delete-orphan")


# models/field.py
class Field(Base):
    __tablename__ = "fields"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    version_id = Column(UUID(as_uuid=True), ForeignKey("versions.id", ondelete="CASCADE"), nullable=False)
    field_path = Column(String(1000), nullable=False)
    field_name = Column(String(255), nullable=False)
    parent_path = Column(String(1000))
    nesting_level = Column(Integer, nullable=False, default=0)
    data_type = Column(String(50), nullable=False)
    semantic_type = Column(String(50))
    is_nullable = Column(Boolean, default=True)
    is_array = Column(Boolean, default=False)
    array_item_type = Column(String(50))
    sample_values = Column(JSON)
    null_count = Column(Integer, default=0)
    null_percentage = Column(Numeric(5, 2))
    total_count = Column(Integer, default=0)
    distinct_count = Column(Integer, default=0)
    cardinality_ratio = Column(Numeric(5, 4))
    min_value = Column(Numeric(20, 6))
    max_value = Column(Numeric(20, 6))
    mean_value = Column(Numeric(20, 6))
    median_value = Column(Numeric(20, 6))
    std_dev = Column(Numeric(20, 6))
    percentile_25 = Column(Numeric(20, 6))
    percentile_50 = Column(Numeric(20, 6))
    percentile_75 = Column(Numeric(20, 6))
    is_pii = Column(Boolean, default=False)
    pii_type = Column(String(50))
    confidence_score = Column(Numeric(5, 2))
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    position = Column(Integer)

    # Relationships
    version = relationship("Version", back_populates="fields")
    annotations = relationship("Annotation", back_populates="field", cascade="all, delete-orphan")


# models/annotation.py
class Annotation(Base):
    __tablename__ = "annotations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    field_id = Column(UUID(as_uuid=True), ForeignKey("fields.id", ondelete="CASCADE"), nullable=False)
    description = Column(Text)
    business_name = Column(String(255))
    is_ai_generated = Column(Boolean, default=False)
    ai_model_version = Column(String(50))
    business_owner = Column(String(255))
    tags = Column(JSON)
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow)
    created_by = Column(String(255))
    updated_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)
    updated_by = Column(String(255))

    # Relationships
    field = relationship("Field", back_populates="annotations")
```

---

## 4. API Design

### 4.1 REST API Principles

1. **Resource-Based URLs**: Use nouns, not verbs
2. **HTTP Methods**: GET (read), POST (create), PATCH (partial update), DELETE (delete)
3. **Status Codes**: Proper HTTP status codes (200, 201, 400, 404, 500)
4. **Versioning**: `/api/v1/` prefix
5. **Pagination**: Limit/offset or cursor-based
6. **Filtering**: Query parameters
7. **Error Format**: Consistent error response structure

### 4.2 API Endpoints

#### 4.2.1 Dictionaries

```
POST   /api/v1/dictionaries              # Create dictionary from JSON
GET    /api/v1/dictionaries              # List all dictionaries (paginated)
GET    /api/v1/dictionaries/{id}         # Get dictionary details
PATCH  /api/v1/dictionaries/{id}         # Update dictionary metadata
DELETE /api/v1/dictionaries/{id}         # Delete dictionary
GET    /api/v1/dictionaries/{id}/fields  # Get fields for dictionary (latest version)
```

#### 4.2.2 Versions

```
GET    /api/v1/dictionaries/{id}/versions           # List versions
POST   /api/v1/dictionaries/{id}/versions           # Create new version
GET    /api/v1/dictionaries/{id}/versions/{vid}     # Get specific version
GET    /api/v1/dictionaries/{id}/versions/{vid}/fields  # Get fields for version
```

#### 4.2.3 Version Comparison

```
GET    /api/v1/dictionaries/{id}/compare?v1={vid1}&v2={vid2}  # Compare versions
```

#### 4.2.4 Fields & Annotations

```
GET    /api/v1/fields/{field_id}                    # Get field details
PATCH  /api/v1/fields/{field_id}/annotation         # Update field annotation
```

#### 4.2.5 Export

```
GET    /api/v1/dictionaries/{id}/export/excel       # Export to Excel
GET    /api/v1/dictionaries/{id}/versions/{vid}/export/excel  # Export specific version
```

#### 4.2.6 Batch Processing (Phase 1.5)

```
POST   /api/v1/batch/dictionaries                   # Batch create from multiple files
GET    /api/v1/batch/jobs/{job_id}                  # Get batch job status
```

#### 4.2.7 Search (Phase 2)

```
GET    /api/v1/search?q={query}&type={type}         # Search across all dictionaries
```

#### 4.2.8 Health & Monitoring

```
GET    /health                                       # Health check
GET    /metrics                                      # Prometheus metrics (future)
```

### 4.3 Request/Response Schemas

#### 4.3.1 Create Dictionary

**Request:**
```http
POST /api/v1/dictionaries
Content-Type: multipart/form-data

file: <JSON file>
name: "Customer Events Dataset"
description: "Event stream from customer service"
created_by: "john.doe@company.com"
generate_ai_descriptions: true
```

**Response:** (201 Created)
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Customer Events Dataset",
    "description": "Event stream from customer service",
    "source_file_name": "customer_events.json",
    "source_file_size": 1048576,
    "total_records_analyzed": 1000,
    "created_at": "2025-11-08T10:30:00Z",
    "created_by": "john.doe@company.com",
    "latest_version": {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "version_number": 1,
      "field_count": 47,
      "created_at": "2025-11-08T10:30:00Z"
    }
  },
  "meta": {
    "processing_time_ms": 2340
  }
}
```

#### 4.3.2 List Dictionaries

**Request:**
```http
GET /api/v1/dictionaries?limit=20&offset=0&sort_by=created_at&order=desc
```

**Response:** (200 OK)
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "name": "Customer Events Dataset",
      "description": "Event stream from customer service",
      "created_at": "2025-11-08T10:30:00Z",
      "created_by": "john.doe@company.com",
      "version_count": 3,
      "latest_version_number": 3,
      "field_count": 47
    }
  ],
  "meta": {
    "total": 125,
    "limit": 20,
    "offset": 0,
    "has_more": true
  }
}
```

#### 4.3.3 Get Dictionary Details

**Request:**
```http
GET /api/v1/dictionaries/{id}
```

**Response:** (200 OK)
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "name": "Customer Events Dataset",
    "description": "Event stream from customer service",
    "source_file_name": "customer_events.json",
    "source_file_size": 1048576,
    "total_records_analyzed": 1000,
    "created_at": "2025-11-08T10:30:00Z",
    "created_by": "john.doe@company.com",
    "updated_at": "2025-11-08T14:22:00Z",
    "metadata": {},
    "versions": [
      {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "version_number": 1,
        "field_count": 47,
        "created_at": "2025-11-08T10:30:00Z",
        "created_by": "john.doe@company.com"
      }
    ]
  }
}
```

#### 4.3.4 Get Fields for Dictionary

**Request:**
```http
GET /api/v1/dictionaries/{id}/fields?limit=100&offset=0&filter_pii=true
```

**Response:** (200 OK)
```json
{
  "data": [
    {
      "id": "770e8400-e29b-41d4-a716-446655440002",
      "field_path": "user.email",
      "field_name": "email",
      "parent_path": "user",
      "nesting_level": 1,
      "data_type": "string",
      "semantic_type": "email",
      "is_nullable": false,
      "is_array": false,
      "sample_values": [
        "john@example.com",
        "jane@example.com",
        "bob@example.com"
      ],
      "null_count": 0,
      "null_percentage": 0.0,
      "total_count": 1000,
      "distinct_count": 987,
      "cardinality_ratio": 0.987,
      "is_pii": true,
      "pii_type": "email",
      "confidence_score": 99.5,
      "annotation": {
        "description": "User email address for communication and identification",
        "business_name": "User Email Address",
        "is_ai_generated": true,
        "ai_model_version": "gpt-4",
        "tags": ["contact", "pii", "required"]
      }
    }
  ],
  "meta": {
    "total": 47,
    "limit": 100,
    "offset": 0
  }
}
```

#### 4.3.5 Compare Versions

**Request:**
```http
GET /api/v1/dictionaries/{id}/compare?v1=1&v2=2
```

**Response:** (200 OK)
```json
{
  "data": {
    "dictionary_id": "550e8400-e29b-41d4-a716-446655440000",
    "version_1": {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "version_number": 1,
      "created_at": "2025-11-08T10:30:00Z"
    },
    "version_2": {
      "id": "660e8400-e29b-41d4-a716-446655440002",
      "version_number": 2,
      "created_at": "2025-11-09T11:15:00Z"
    },
    "summary": {
      "fields_added": 3,
      "fields_removed": 1,
      "fields_modified": 2,
      "breaking_changes": 1
    },
    "changes": [
      {
        "change_type": "added",
        "field_path": "user.phone_number",
        "version_2_data": {
          "data_type": "string",
          "semantic_type": "phone",
          "is_pii": true
        }
      },
      {
        "change_type": "removed",
        "field_path": "user.legacy_id",
        "version_1_data": {
          "data_type": "integer"
        },
        "is_breaking": true
      },
      {
        "change_type": "modified",
        "field_path": "order.total",
        "version_1_data": {
          "data_type": "integer"
        },
        "version_2_data": {
          "data_type": "float"
        },
        "is_breaking": true
      }
    ]
  }
}
```

#### 4.3.6 Error Response

**Standard Error Format:**
```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid JSON file format",
    "details": [
      {
        "field": "file",
        "issue": "JSON syntax error at line 42"
      }
    ],
    "request_id": "req_abc123xyz"
  }
}
```

**Error Codes:**
- `VALIDATION_ERROR` (400)
- `NOT_FOUND` (404)
- `CONFLICT` (409) - e.g., duplicate version
- `INTERNAL_ERROR` (500)
- `FILE_TOO_LARGE` (413)
- `UNSUPPORTED_FORMAT` (415)

### 4.4 Pydantic Schemas (DTOs)

```python
# schemas/dictionary.py
from datetime import datetime
from uuid import UUID
from typing import Optional, List
from pydantic import BaseModel, Field, validator

class DictionaryCreate(BaseModel):
    """Request schema for creating dictionary"""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    created_by: Optional[str] = None
    generate_ai_descriptions: bool = True

    @validator('name')
    def name_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()


class VersionSummary(BaseModel):
    """Summary of a version"""
    id: UUID
    version_number: int
    field_count: int
    created_at: datetime
    created_by: Optional[str]

    class Config:
        from_attributes = True  # For SQLAlchemy models


class DictionaryResponse(BaseModel):
    """Response schema for dictionary"""
    id: UUID
    name: str
    description: Optional[str]
    source_file_name: Optional[str]
    source_file_size: Optional[int]
    total_records_analyzed: Optional[int]
    created_at: datetime
    created_by: Optional[str]
    updated_at: datetime
    latest_version: Optional[VersionSummary]

    class Config:
        from_attributes = True


class DictionaryListItem(BaseModel):
    """List item for dictionaries"""
    id: UUID
    name: str
    description: Optional[str]
    created_at: datetime
    created_by: Optional[str]
    version_count: int
    latest_version_number: int
    field_count: int


class PaginatedResponse(BaseModel):
    """Generic paginated response"""
    data: List[DictionaryListItem]
    meta: dict  # total, limit, offset, has_more


# schemas/field.py
class AnnotationResponse(BaseModel):
    """Annotation data"""
    description: Optional[str]
    business_name: Optional[str]
    is_ai_generated: bool
    ai_model_version: Optional[str]
    tags: Optional[List[str]]
    business_owner: Optional[str]


class FieldResponse(BaseModel):
    """Field response schema"""
    id: UUID
    field_path: str
    field_name: str
    parent_path: Optional[str]
    nesting_level: int
    data_type: str
    semantic_type: Optional[str]
    is_nullable: bool
    is_array: bool
    array_item_type: Optional[str]
    sample_values: Optional[List]
    null_count: int
    null_percentage: Optional[float]
    total_count: int
    distinct_count: int
    cardinality_ratio: Optional[float]
    min_value: Optional[float]
    max_value: Optional[float]
    mean_value: Optional[float]
    median_value: Optional[float]
    std_dev: Optional[float]
    percentile_25: Optional[float]
    percentile_50: Optional[float]
    percentile_75: Optional[float]
    is_pii: bool
    pii_type: Optional[str]
    confidence_score: Optional[float]
    annotation: Optional[AnnotationResponse]

    class Config:
        from_attributes = True


class AnnotationUpdate(BaseModel):
    """Update annotation"""
    description: Optional[str]
    business_name: Optional[str]
    business_owner: Optional[str]
    tags: Optional[List[str]]
    updated_by: Optional[str]
```

---

## 5. Core Processing Components

### 5.1 JSON Parser

**Purpose:** Parse JSON files and extract field structure

**Algorithm:**
```python
# processors/json_parser.py
from typing import Dict, List, Any, Iterator
import ijson
from pathlib import Path

class JSONParser:
    """
    Streaming JSON parser for large files.
    Extracts field structure and sample values.
    """

    def __init__(self, max_samples: int = 1000, max_depth: int = 10):
        self.max_samples = max_samples
        self.max_depth = max_depth

    def parse_file(self, file_path: Path) -> Dict[str, Any]:
        """
        Parse JSON file and extract field metadata.

        Returns:
            {
                'fields': [...],  # List of field metadata
                'total_records': int,
                'is_array': bool  # Root is array or object
            }
        """
        # Check if root is array or object
        with open(file_path, 'rb') as f:
            first_char = self._skip_whitespace(f)
            is_array = first_char == b'['

        if is_array:
            return self._parse_array_root(file_path)
        else:
            return self._parse_object_root(file_path)

    def _parse_array_root(self, file_path: Path) -> Dict[str, Any]:
        """Parse JSON array of objects"""
        fields_map = {}  # field_path -> FieldMetadata
        records_processed = 0

        with open(file_path, 'rb') as f:
            # Use ijson for streaming parsing
            items = ijson.items(f, 'item')

            for item in items:
                if records_processed >= self.max_samples:
                    break

                # Extract fields from this record
                self._extract_fields(
                    item,
                    parent_path='',
                    fields_map=fields_map,
                    depth=0
                )
                records_processed += 1

        return {
            'fields': list(fields_map.values()),
            'total_records': records_processed,
            'is_array': True
        }

    def _parse_object_root(self, file_path: Path) -> Dict[str, Any]:
        """Parse single JSON object"""
        fields_map = {}

        with open(file_path, 'rb') as f:
            obj = ijson.items(f, '')
            for item in obj:
                self._extract_fields(
                    item,
                    parent_path='',
                    fields_map=fields_map,
                    depth=0
                )

        return {
            'fields': list(fields_map.values()),
            'total_records': 1,
            'is_array': False
        }

    def _extract_fields(
        self,
        obj: Any,
        parent_path: str,
        fields_map: Dict[str, 'FieldMetadata'],
        depth: int
    ):
        """Recursively extract fields from object"""
        if depth > self.max_depth:
            return

        if isinstance(obj, dict):
            for key, value in obj.items():
                field_path = f"{parent_path}.{key}" if parent_path else key

                # Update or create field metadata
                if field_path not in fields_map:
                    fields_map[field_path] = FieldMetadata(
                        field_path=field_path,
                        field_name=key,
                        parent_path=parent_path,
                        nesting_level=depth
                    )

                field_meta = fields_map[field_path]
                field_meta.observe_value(value)

                # Recurse for nested objects/arrays
                if isinstance(value, (dict, list)):
                    self._extract_fields(value, field_path, fields_map, depth + 1)

        elif isinstance(obj, list):
            # For arrays, analyze sample items
            for i, item in enumerate(obj[:10]):  # Sample first 10 items
                self._extract_fields(item, parent_path, fields_map, depth)


class FieldMetadata:
    """Accumulates metadata for a single field"""

    def __init__(self, field_path: str, field_name: str, parent_path: str, nesting_level: int):
        self.field_path = field_path
        self.field_name = field_name
        self.parent_path = parent_path
        self.nesting_level = nesting_level
        self.values = []  # Sample values
        self.types_seen = set()
        self.null_count = 0
        self.total_count = 0
        self.is_array = False
        self.array_item_types = set()

    def observe_value(self, value: Any):
        """Record observation of a value"""
        self.total_count += 1

        if value is None:
            self.null_count += 1
            self.types_seen.add('null')
        elif isinstance(value, bool):
            self.types_seen.add('boolean')
            self._add_sample(value)
        elif isinstance(value, int):
            self.types_seen.add('integer')
            self._add_sample(value)
        elif isinstance(value, float):
            self.types_seen.add('float')
            self._add_sample(value)
        elif isinstance(value, str):
            self.types_seen.add('string')
            self._add_sample(value)
        elif isinstance(value, list):
            self.is_array = True
            self.types_seen.add('array')
            # Analyze array item types
            for item in value[:10]:
                self.array_item_types.add(type(item).__name__)
        elif isinstance(value, dict):
            self.types_seen.add('object')

    def _add_sample(self, value: Any):
        """Add sample value (up to 10 unique)"""
        if len(self.values) < 10 and value not in self.values:
            self.values.append(value)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'field_path': self.field_path,
            'field_name': self.field_name,
            'parent_path': self.parent_path,
            'nesting_level': self.nesting_level,
            'types_seen': list(self.types_seen),
            'is_array': self.is_array,
            'array_item_types': list(self.array_item_types),
            'sample_values': self.values,
            'null_count': self.null_count,
            'total_count': self.total_count,
            'null_percentage': (self.null_count / self.total_count * 100) if self.total_count > 0 else 0
        }
```

### 5.2 Type Inferrer

**Purpose:** Infer data types with confidence scores

```python
# processors/type_inferrer.py
from typing import List, Tuple
from collections import Counter

class TypeInferrer:
    """Infers data types from observed values"""

    def infer_type(self, types_seen: List[str]) -> Tuple[str, float]:
        """
        Infer primary type and confidence score.

        Args:
            types_seen: List of observed types

        Returns:
            (data_type, confidence_score)
        """
        if not types_seen:
            return ('unknown', 0.0)

        # Count type occurrences
        type_counts = Counter(types_seen)
        total = sum(type_counts.values())

        # Remove null from consideration if other types exist
        if len(type_counts) > 1 and 'null' in type_counts:
            non_null_counts = {k: v for k, v in type_counts.items() if k != 'null'}
            if non_null_counts:
                type_counts = Counter(non_null_counts)
                total = sum(type_counts.values())

        # Get most common type
        most_common_type, count = type_counts.most_common(1)[0]
        confidence = (count / total) * 100

        # Type hierarchy: if integer and float both present, use float
        if 'integer' in type_counts and 'float' in type_counts:
            return ('float', (type_counts['integer'] + type_counts['float']) / total * 100)

        return (most_common_type, confidence)

    def infer_array_item_type(self, item_types: List[str]) -> str:
        """Infer array item type"""
        if not item_types:
            return 'unknown'

        unique_types = set(item_types)
        if len(unique_types) == 1:
            return list(unique_types)[0]
        else:
            return 'mixed'
```

### 5.3 Semantic Type Detector

**Purpose:** Detect semantic types (email, date, URL, etc.)

```python
# processors/semantic_detector.py
import re
from typing import Optional, List
from datetime import datetime

class SemanticTypeDetector:
    """Detects semantic types from field values"""

    # Regex patterns
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    PHONE_PATTERN = re.compile(r'^[\+]?[(]?[0-9]{1,4}[)]?[-\s\.]?[(]?[0-9]{1,4}[)]?[-\s\.]?[0-9]{1,4}[-\s\.]?[0-9]{1,9}$')
    URL_PATTERN = re.compile(r'^https?://[^\s]+$')
    UUID_PATTERN = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$', re.I)
    ZIP_CODE_PATTERN = re.compile(r'^\d{5}(-\d{4})?$')

    # Date formats to try
    DATE_FORMATS = [
        '%Y-%m-%d',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%S.%f',
        '%Y-%m-%dT%H:%M:%S.%fZ',
        '%m/%d/%Y',
        '%d/%m/%Y',
    ]

    def detect(self, field_name: str, sample_values: List[Any], data_type: str) -> Optional[str]:
        """
        Detect semantic type.

        Args:
            field_name: Field name (may contain hints)
            sample_values: Sample values
            data_type: Basic data type

        Returns:
            Semantic type or None
        """
        if data_type != 'string':
            # Only detect semantic types for strings currently
            return None

        if not sample_values:
            return None

        # Check samples
        matches = {
            'email': 0,
            'phone': 0,
            'url': 0,
            'uuid': 0,
            'date': 0,
            'zip_code': 0,
            'currency': 0
        }

        for value in sample_values[:10]:
            if not isinstance(value, str):
                continue

            if self.EMAIL_PATTERN.match(value):
                matches['email'] += 1
            elif self.PHONE_PATTERN.match(value):
                matches['phone'] += 1
            elif self.URL_PATTERN.match(value):
                matches['url'] += 1
            elif self.UUID_PATTERN.match(value):
                matches['uuid'] += 1
            elif self._is_date(value):
                matches['date'] += 1
            elif self.ZIP_CODE_PATTERN.match(value):
                matches['zip_code'] += 1
            elif self._is_currency(value):
                matches['currency'] += 1

        # Find best match (>70% of samples)
        total_samples = len(sample_values[:10])
        for semantic_type, count in matches.items():
            if count / total_samples >= 0.7:
                return semantic_type

        # Check field name hints
        field_lower = field_name.lower()
        if 'email' in field_lower:
            return 'email'
        elif 'phone' in field_lower or 'mobile' in field_lower:
            return 'phone'
        elif 'url' in field_lower or 'link' in field_lower:
            return 'url'
        elif 'date' in field_lower or 'time' in field_lower:
            return 'date'
        elif 'zip' in field_lower or 'postal' in field_lower:
            return 'zip_code'
        elif 'price' in field_lower or 'amount' in field_lower or 'cost' in field_lower:
            return 'currency'

        return None

    def _is_date(self, value: str) -> bool:
        """Check if value is a date"""
        for fmt in self.DATE_FORMATS:
            try:
                datetime.strptime(value, fmt)
                return True
            except ValueError:
                continue
        return False

    def _is_currency(self, value: str) -> bool:
        """Check if value looks like currency"""
        # Simple check for currency symbols
        return value.startswith(('$', '€', '£', '¥')) and any(c.isdigit() for c in value)
```

### 5.4 PII Detector

**Purpose:** Identify potential PII fields

```python
# processors/pii_detector.py
import re
from typing import List, Tuple, Optional

class PIIDetector:
    """Detects potential PII in fields"""

    # SSN pattern: XXX-XX-XXXX
    SSN_PATTERN = re.compile(r'^\d{3}-\d{2}-\d{4}$')

    # Credit card pattern (basic Luhn check)
    CC_PATTERN = re.compile(r'^\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}$')

    def detect_pii(
        self,
        field_path: str,
        field_name: str,
        semantic_type: Optional[str],
        sample_values: List[Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Detect if field contains PII.

        Returns:
            (is_pii, pii_type)
        """
        # Semantic type-based detection
        if semantic_type in ('email', 'phone'):
            return (True, semantic_type)

        # Field name-based detection
        field_lower = field_name.lower()
        pii_indicators = {
            'email': 'email',
            'phone': 'phone',
            'mobile': 'phone',
            'ssn': 'ssn',
            'social_security': 'ssn',
            'credit_card': 'credit_card',
            'passport': 'passport',
            'driver_license': 'drivers_license',
            'address': 'address',
            'ip_address': 'ip_address'
        }

        for indicator, pii_type in pii_indicators.items():
            if indicator in field_lower:
                return (True, pii_type)

        # Value-based detection
        if sample_values:
            ssn_count = sum(1 for v in sample_values if isinstance(v, str) and self.SSN_PATTERN.match(v))
            if ssn_count / len(sample_values) > 0.5:
                return (True, 'ssn')

            cc_count = sum(1 for v in sample_values if isinstance(v, str) and self._is_credit_card(v))
            if cc_count / len(sample_values) > 0.5:
                return (True, 'credit_card')

        return (False, None)

    def _is_credit_card(self, value: str) -> bool:
        """Check if value is credit card using Luhn algorithm"""
        if not self.CC_PATTERN.match(value):
            return False

        # Remove spaces/dashes
        digits = re.sub(r'[\s-]', '', value)

        # Luhn algorithm
        def luhn_check(card_number):
            def digits_of(n):
                return [int(d) for d in str(n)]

            digits = digits_of(card_number)
            odd_digits = digits[-1::-2]
            even_digits = digits[-2::-2]
            checksum = sum(odd_digits)
            for d in even_digits:
                checksum += sum(digits_of(d * 2))
            return checksum % 10 == 0

        return luhn_check(digits)
```

### 5.5 Quality Analyzer

**Purpose:** Calculate data quality metrics

```python
# processors/quality_analyzer.py
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional

class QualityAnalyzer:
    """Analyzes data quality metrics for fields"""

    def analyze_field(self, values: List[Any], data_type: str) -> Dict[str, Any]:
        """
        Analyze field quality metrics.

        Returns:
            Dictionary of quality metrics
        """
        if not values:
            return {}

        # Convert to pandas Series for analysis
        series = pd.Series(values)

        metrics = {
            'total_count': len(values),
            'null_count': series.isna().sum(),
            'null_percentage': (series.isna().sum() / len(values)) * 100,
            'distinct_count': series.nunique(),
            'cardinality_ratio': series.nunique() / len(values)
        }

        # Numeric-specific metrics
        if data_type in ('integer', 'float'):
            numeric_values = pd.to_numeric(series, errors='coerce').dropna()
            if len(numeric_values) > 0:
                metrics.update({
                    'min_value': float(numeric_values.min()),
                    'max_value': float(numeric_values.max()),
                    'mean_value': float(numeric_values.mean()),
                    'median_value': float(numeric_values.median()),
                    'std_dev': float(numeric_values.std()),
                    'percentile_25': float(numeric_values.quantile(0.25)),
                    'percentile_50': float(numeric_values.quantile(0.50)),
                    'percentile_75': float(numeric_values.quantile(0.75))
                })

        return metrics

    def get_sample_values(self, values: List[Any], max_samples: int = 10) -> List[Any]:
        """Get up to max_samples unique values"""
        unique_values = []
        seen = set()

        for value in values:
            if value not in seen and len(unique_values) < max_samples:
                unique_values.append(value)
                seen.add(value)

        return unique_values
```

### 5.6 AI Description Generator

**Purpose:** Generate field descriptions using AI

```python
# processors/ai_generator.py
from typing import List, Optional
import openai
from openai import OpenAI
import os

class AIDescriptionGenerator:
    """Generates field descriptions using OpenAI"""

    def __init__(self, api_key: Optional[str] = None, model: str = "gpt-3.5-turbo"):
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))
        self.model = model
        self.cache = {}  # Simple in-memory cache

    def generate_description(
        self,
        field_path: str,
        field_name: str,
        data_type: str,
        semantic_type: Optional[str],
        sample_values: List[Any]
    ) -> Tuple[str, str]:
        """
        Generate description and business-friendly name.

        Returns:
            (description, business_name)
        """
        # Check cache
        cache_key = f"{field_path}:{data_type}:{semantic_type}"
        if cache_key in self.cache:
            return self.cache[cache_key]

        # Build prompt
        prompt = self._build_prompt(field_path, field_name, data_type, semantic_type, sample_values)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a data documentation expert. Generate concise, clear descriptions for data fields."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=150
            )

            content = response.choices[0].message.content.strip()
            description, business_name = self._parse_response(content)

            # Cache result
            self.cache[cache_key] = (description, business_name)

            return (description, business_name)

        except Exception as e:
            # Fallback to simple description
            return self._fallback_description(field_name, data_type, semantic_type)

    def _build_prompt(
        self,
        field_path: str,
        field_name: str,
        data_type: str,
        semantic_type: Optional[str],
        sample_values: List[Any]
    ) -> str:
        """Build prompt for AI"""
        samples_str = ", ".join(str(v) for v in sample_values[:5])

        prompt = f"""Generate a description and business-friendly name for this data field:

Field Path: {field_path}
Field Name: {field_name}
Data Type: {data_type}
Semantic Type: {semantic_type or 'N/A'}
Sample Values: {samples_str}

Please respond in this format:
DESCRIPTION: <1-2 sentence description>
BUSINESS_NAME: <Business-friendly name>"""

        return prompt

    def _parse_response(self, content: str) -> Tuple[str, str]:
        """Parse AI response"""
        lines = content.split('\n')
        description = ""
        business_name = ""

        for line in lines:
            if line.startswith("DESCRIPTION:"):
                description = line.replace("DESCRIPTION:", "").strip()
            elif line.startswith("BUSINESS_NAME:"):
                business_name = line.replace("BUSINESS_NAME:", "").strip()

        return (description, business_name)

    def _fallback_description(
        self,
        field_name: str,
        data_type: str,
        semantic_type: Optional[str]
    ) -> Tuple[str, str]:
        """Generate fallback description"""
        # Simple rule-based description
        business_name = field_name.replace('_', ' ').title()
        description = f"{business_name} field of type {semantic_type or data_type}"

        return (description, business_name)

    async def generate_batch(
        self,
        fields: List[Dict[str, Any]],
        batch_size: int = 10
    ) -> List[Tuple[str, str]]:
        """Generate descriptions for multiple fields"""
        # TODO: Implement batch processing with rate limiting
        results = []
        for field in fields:
            result = self.generate_description(
                field['field_path'],
                field['field_name'],
                field['data_type'],
                field.get('semantic_type'),
                field.get('sample_values', [])
            )
            results.append(result)
        return results
```

---

## 6. Service Layer Design

### 6.1 Dictionary Service

**Responsibilities:**
- Orchestrate dictionary creation workflow
- Coordinate between parsers, analyzers, and repositories
- Handle business logic for dictionary operations

```python
# services/dictionary_service.py
from typing import Optional, List
from uuid import UUID
from pathlib import Path
import hashlib
from sqlalchemy.orm import Session

from ..repositories.dictionary_repo import DictionaryRepository
from ..repositories.field_repo import FieldRepository
from ..repositories.version_repo import VersionRepository
from ..processors.json_parser import JSONParser
from ..processors.type_inferrer import TypeInferrer
from ..processors.semantic_detector import SemanticTypeDetector
from ..processors.pii_detector import PIIDetector
from ..processors.quality_analyzer import QualityAnalyzer
from ..processors.ai_generator import AIDescriptionGenerator
from ..models.dictionary import Dictionary
from ..schemas.dictionary import DictionaryCreate, DictionaryResponse

class DictionaryService:
    """Business logic for dictionary operations"""

    def __init__(
        self,
        db: Session,
        dictionary_repo: DictionaryRepository,
        field_repo: FieldRepository,
        version_repo: VersionRepository
    ):
        self.db = db
        self.dictionary_repo = dictionary_repo
        self.field_repo = field_repo
        self.version_repo = version_repo

        # Initialize processors
        self.json_parser = JSONParser()
        self.type_inferrer = TypeInferrer()
        self.semantic_detector = SemanticTypeDetector()
        self.pii_detector = PIIDetector()
        self.quality_analyzer = QualityAnalyzer()
        self.ai_generator = AIDescriptionGenerator()

    async def create_dictionary(
        self,
        file_path: Path,
        metadata: DictionaryCreate
    ) -> DictionaryResponse:
        """
        Create dictionary from JSON file.

        Workflow:
        1. Parse JSON file
        2. Infer types and semantic types
        3. Detect PII
        4. Calculate quality metrics
        5. Generate AI descriptions (if enabled)
        6. Save to database
        """
        # Step 1: Parse JSON
        parse_result = self.json_parser.parse_file(file_path)

        # Step 2: Create dictionary record
        dictionary = Dictionary(
            name=metadata.name,
            description=metadata.description,
            source_file_name=file_path.name,
            source_file_size=file_path.stat().st_size,
            total_records_analyzed=parse_result['total_records'],
            created_by=metadata.created_by
        )
        self.dictionary_repo.create(dictionary)

        # Step 3: Create version
        schema_hash = self._calculate_schema_hash(parse_result['fields'])
        version = self.version_repo.create(
            dictionary_id=dictionary.id,
            version_number=1,
            schema_hash=schema_hash,
            created_by=metadata.created_by
        )

        # Step 4: Process fields
        for field_meta in parse_result['fields']:
            # Infer type
            data_type, confidence = self.type_inferrer.infer_type(
                field_meta['types_seen']
            )

            # Detect semantic type
            semantic_type = self.semantic_detector.detect(
                field_meta['field_name'],
                field_meta['sample_values'],
                data_type
            )

            # Detect PII
            is_pii, pii_type = self.pii_detector.detect_pii(
                field_meta['field_path'],
                field_meta['field_name'],
                semantic_type,
                field_meta['sample_values']
            )

            # Calculate quality metrics
            # (Would need full dataset for accurate metrics - this is simplified)
            quality_metrics = {
                'null_percentage': field_meta['null_percentage'],
                # Add more metrics from actual data analysis
            }

            # Create field record
            field = self.field_repo.create(
                version_id=version.id,
                field_path=field_meta['field_path'],
                field_name=field_meta['field_name'],
                parent_path=field_meta['parent_path'],
                nesting_level=field_meta['nesting_level'],
                data_type=data_type,
                semantic_type=semantic_type,
                is_pii=is_pii,
                pii_type=pii_type,
                confidence_score=confidence,
                sample_values=field_meta['sample_values'],
                null_percentage=field_meta['null_percentage'],
                # ... other fields
            )

            # Step 5: Generate AI description (if enabled)
            if metadata.generate_ai_descriptions:
                description, business_name = self.ai_generator.generate_description(
                    field_meta['field_path'],
                    field_meta['field_name'],
                    data_type,
                    semantic_type,
                    field_meta['sample_values']
                )

                # Create annotation
                self.field_repo.create_annotation(
                    field_id=field.id,
                    description=description,
                    business_name=business_name,
                    is_ai_generated=True,
                    ai_model_version="gpt-3.5-turbo"
                )

        # Commit transaction
        self.db.commit()

        return DictionaryResponse.from_orm(dictionary)

    def _calculate_schema_hash(self, fields: List[Dict]) -> str:
        """Calculate hash of schema structure for version detection"""
        # Create deterministic representation
        field_signatures = []
        for field in sorted(fields, key=lambda x: x['field_path']):
            sig = f"{field['field_path']}:{field.get('data_type', 'unknown')}"
            field_signatures.append(sig)

        schema_str = '|'.join(field_signatures)
        return hashlib.sha256(schema_str.encode()).hexdigest()

    async def get_dictionary(self, dictionary_id: UUID) -> Optional[DictionaryResponse]:
        """Get dictionary by ID"""
        dictionary = self.dictionary_repo.get_by_id(dictionary_id)
        if not dictionary:
            return None
        return DictionaryResponse.from_orm(dictionary)

    async def list_dictionaries(
        self,
        limit: int = 20,
        offset: int = 0,
        sort_by: str = 'created_at',
        order: str = 'desc'
    ) -> List[DictionaryResponse]:
        """List dictionaries with pagination"""
        dictionaries = self.dictionary_repo.list(
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            order=order
        )
        return [DictionaryResponse.from_orm(d) for d in dictionaries]
```

---

## 7. Data Flow & Algorithms

### 7.1 Dictionary Creation Flow

```
┌─────────────────────────────────────────────────────────────────┐
│ 1. File Upload (API Endpoint)                                   │
│    - Validate file format (.json)                               │
│    - Validate file size (<100MB)                                │
│    - Save temporarily                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 2. JSON Parsing (JSONParser)                                    │
│    - Stream parse JSON                                          │
│    - Extract field paths                                        │
│    - Collect sample values                                      │
│    - Track types seen                                           │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 3. Type Inference (TypeInferrer)                                │
│    - Analyze types seen for each field                          │
│    - Calculate confidence scores                                │
│    - Handle mixed types                                         │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 4. Semantic Detection (SemanticTypeDetector)                    │
│    - Pattern matching (email, phone, URL)                       │
│    - Date format detection                                      │
│    - Field name analysis                                        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 5. PII Detection (PIIDetector)                                  │
│    - Regex pattern matching                                     │
│    - Field name indicators                                      │
│    - Luhn algorithm for credit cards                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 6. Quality Analysis (QualityAnalyzer)                           │
│    - Calculate null percentages                                 │
│    - Compute cardinality                                        │
│    - Statistical metrics (min, max, mean, std)                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 7. AI Description Generation (AIDescriptionGenerator)           │
│    - Build prompts for each field                               │
│    - Call OpenAI API (batch if possible)                        │
│    - Parse responses                                            │
│    - Cache results                                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│ 8. Database Persistence                                         │
│    - Create Dictionary record                                   │
│    - Create Version record (v1)                                 │
│    - Create Field records (bulk insert)                         │
│    - Create Annotation records                                  │
│    - Commit transaction                                         │
└─────────────────────────────────────────────────────────────────┘
```

### 7.2 Version Comparison Algorithm

```python
# services/version_service.py
class VersionService:
    """Business logic for version operations"""

    def compare_versions(
        self,
        dictionary_id: UUID,
        version1_number: int,
        version2_number: int
    ) -> Dict[str, Any]:
        """
        Compare two versions and identify changes.

        Algorithm:
        1. Fetch all fields for both versions
        2. Create maps: field_path -> field_data
        3. Identify added fields (in v2, not in v1)
        4. Identify removed fields (in v1, not in v2)
        5. Identify modified fields (in both, but different)
        6. Classify breaking changes
        """
        # Get fields for both versions
        v1_fields = self.field_repo.get_by_version(version1_id)
        v2_fields = self.field_repo.get_by_version(version2_id)

        # Create maps
        v1_map = {f.field_path: f for f in v1_fields}
        v2_map = {f.field_path: f for f in v2_fields}

        changes = []

        # Find added fields
        for path, field in v2_map.items():
            if path not in v1_map:
                changes.append({
                    'change_type': 'added',
                    'field_path': path,
                    'version_2_data': self._field_to_dict(field)
                })

        # Find removed fields
        for path, field in v1_map.items():
            if path not in v2_map:
                changes.append({
                    'change_type': 'removed',
                    'field_path': path,
                    'version_1_data': self._field_to_dict(field),
                    'is_breaking': True  # Removed fields are breaking
                })

        # Find modified fields
        for path in set(v1_map.keys()) & set(v2_map.keys()):
            v1_field = v1_map[path]
            v2_field = v2_map[path]

            if self._fields_differ(v1_field, v2_field):
                is_breaking = self._is_breaking_change(v1_field, v2_field)
                changes.append({
                    'change_type': 'modified',
                    'field_path': path,
                    'version_1_data': self._field_to_dict(v1_field),
                    'version_2_data': self._field_to_dict(v2_field),
                    'is_breaking': is_breaking
                })

        # Summary
        summary = {
            'fields_added': sum(1 for c in changes if c['change_type'] == 'added'),
            'fields_removed': sum(1 for c in changes if c['change_type'] == 'removed'),
            'fields_modified': sum(1 for c in changes if c['change_type'] == 'modified'),
            'breaking_changes': sum(1 for c in changes if c.get('is_breaking', False))
        }

        return {
            'summary': summary,
            'changes': changes
        }

    def _is_breaking_change(self, v1_field, v2_field) -> bool:
        """Determine if change is breaking"""
        # Type changes are breaking
        if v1_field.data_type != v2_field.data_type:
            return True

        # Nullability changes (non-null -> null is not breaking, opposite is)
        if not v1_field.is_nullable and v2_field.is_nullable:
            return False
        if v1_field.is_nullable and not v2_field.is_nullable:
            return True

        return False
```

---

## 8. Security Design

### 8.1 Security Principles for Internal Tools

**Note:** As an internal tool, security requirements are simplified compared to public-facing applications. However, basic security hygiene is still important.

**Security Priorities:**
1. **Data Protection**: Prevent data leakage or corruption
2. **Input Validation**: Prevent injection attacks and malformed data
3. **Audit Trail**: Track who did what and when
4. **Basic Authentication**: Identify users for audit purposes
5. **API Security**: Prevent abuse and unauthorized access

### 8.2 Authentication & Authorization

#### 8.2.1 Authentication Strategy (Phase 1)

For MVP, implement simple authentication:

```python
# core/security.py
from typing import Optional
from fastapi import Header, HTTPException, status

class SecurityService:
    """Basic security for internal tool"""

    def __init__(self, valid_api_keys: set[str] = None):
        # In production, load from env or secret manager
        self.valid_api_keys = valid_api_keys or set()

    async def verify_api_key(
        self,
        x_api_key: Optional[str] = Header(None)
    ) -> str:
        """
        Verify API key from header.

        For internal tool, this is primarily for audit trail,
        not strict access control.
        """
        if not x_api_key:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="API key required"
            )

        if x_api_key not in self.valid_api_keys:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )

        return x_api_key

    def get_user_from_api_key(self, api_key: str) -> str:
        """Map API key to user identifier"""
        # Simple mapping for internal tool
        # In production: query database or external auth service
        return f"user_{api_key[:8]}"


# Usage in endpoints
@router.post("/dictionaries")
async def create_dictionary(
    api_key: str = Depends(security_service.verify_api_key),
    ...
):
    user = security_service.get_user_from_api_key(api_key)
    # Use user for audit trail
    ...
```

#### 8.2.2 Future: SSO Integration (Phase 3)

For enterprise deployment, integrate with existing SSO:

```python
# Future: OAuth2/OIDC integration
from fastapi.security import OAuth2AuthorizationCodeBearer

oauth2_scheme = OAuth2AuthorizationCodeBearer(
    authorizationUrl="https://company-sso/authorize",
    tokenUrl="https://company-sso/token"
)

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Validate JWT token from SSO"""
    # Decode and validate JWT
    # Return user info
    ...
```

### 8.3 Input Validation

#### 8.3.1 File Upload Validation

```python
# api/v1/dictionaries.py
from fastapi import UploadFile, HTTPException
import json

class FileValidator:
    """Validate uploaded files"""

    MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB
    ALLOWED_EXTENSIONS = {'.json'}

    async def validate_json_file(self, file: UploadFile) -> None:
        """Validate JSON file upload"""

        # Check extension
        if not file.filename.endswith('.json'):
            raise HTTPException(
                status_code=400,
                detail="Only .json files are allowed"
            )

        # Check file size
        file.file.seek(0, 2)  # Seek to end
        file_size = file.file.tell()
        file.file.seek(0)  # Reset

        if file_size > self.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=413,
                detail=f"File too large. Max size: {self.MAX_FILE_SIZE / 1024 / 1024}MB"
            )

        # Validate JSON syntax (first 1MB)
        try:
            sample = await file.read(1024 * 1024)
            file.file.seek(0)
            json.loads(sample.decode('utf-8'))
        except json.JSONDecodeError as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid JSON format: {str(e)}"
            )
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=400,
                detail="File must be UTF-8 encoded"
            )
```

#### 8.3.2 Pydantic Validation

```python
# schemas/dictionary.py
from pydantic import BaseModel, Field, validator
import re

class DictionaryCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=5000)
    created_by: Optional[str] = Field(None, max_length=255)

    @validator('name')
    def validate_name(cls, v):
        # Prevent SQL injection attempts
        if re.search(r'[;<>]', v):
            raise ValueError('Name contains invalid characters')
        return v.strip()

    @validator('created_by')
    def validate_email(cls, v):
        if v and '@' in v:
            # Basic email validation
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
                raise ValueError('Invalid email format')
        return v
```

### 8.4 SQL Injection Prevention

**Strategy:** Use SQLAlchemy ORM with parameterized queries

```python
# repositories/dictionary_repo.py
from sqlalchemy.orm import Session
from sqlalchemy import select

class DictionaryRepository:
    """Repository with safe database access"""

    def __init__(self, db: Session):
        self.db = db

    def get_by_name(self, name: str) -> Optional[Dictionary]:
        """Safe parameterized query"""
        # SQLAlchemy automatically parameterizes
        stmt = select(Dictionary).where(Dictionary.name == name)
        result = self.db.execute(stmt)
        return result.scalar_one_or_none()

    # NEVER do this:
    # def unsafe_query(self, name: str):
    #     query = f"SELECT * FROM dictionaries WHERE name = '{name}'"
    #     return self.db.execute(query)  # DANGEROUS!
```

### 8.5 Data Encryption

#### 8.5.1 Encryption at Rest

```python
# core/config.py
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Application settings"""

    # Database encryption (PostgreSQL built-in)
    database_url: str
    enable_db_encryption: bool = True  # Use PostgreSQL TDE

    # File storage encryption
    encrypt_uploaded_files: bool = False  # Phase 2
    encryption_key: Optional[str] = None

    class Config:
        env_file = ".env"
```

#### 8.5.2 Encryption in Transit

```python
# main.py
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# HTTPS enforcement (in production)
if settings.environment == "production":
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=settings.allowed_hosts
    )

# CORS for internal network
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,  # Internal domains only
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["*"],
)
```

### 8.6 Rate Limiting (Phase 2)

```python
# middleware/rate_limit.py
from fastapi import Request, HTTPException
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

# Apply to app
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Apply to endpoints
@router.post("/dictionaries")
@limiter.limit("10/minute")  # 10 requests per minute
async def create_dictionary(request: Request, ...):
    ...
```

### 8.7 Secrets Management

```python
# core/config.py
import os
from typing import Optional

class Settings(BaseSettings):
    """Secure settings management"""

    # Database
    postgres_user: str
    postgres_password: str  # From environment
    postgres_host: str
    postgres_port: int = 5432
    postgres_db: str

    # OpenAI
    openai_api_key: str  # From environment

    # Security
    api_keys: str  # Comma-separated, from environment
    secret_key: str  # For session encryption

    @property
    def database_url(self) -> str:
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def valid_api_keys(self) -> set[str]:
        return set(self.api_keys.split(','))

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'


# .env.example (never commit .env)
"""
POSTGRES_USER=datadict
POSTGRES_PASSWORD=<generate-secure-password>
POSTGRES_HOST=localhost
POSTGRES_DB=datadict

OPENAI_API_KEY=sk-...

API_KEYS=key1,key2,key3
SECRET_KEY=<generate-random-key>
"""
```

### 8.8 Audit Logging

```python
# core/audit.py
from typing import Optional
from datetime import datetime
import logging

class AuditLogger:
    """Audit trail for important operations"""

    def __init__(self):
        self.logger = logging.getLogger("audit")
        # Configure to write to separate audit log file
        handler = logging.FileHandler("logs/audit.log")
        handler.setFormatter(logging.Formatter(
            '{"timestamp": "%(asctime)s", "user": "%(user)s", "action": "%(action)s", "resource": "%(resource)s", "result": "%(result)s"}'
        ))
        self.logger.addHandler(handler)
        self.logger.setLevel(logging.INFO)

    def log_action(
        self,
        user: str,
        action: str,
        resource: str,
        result: str,
        metadata: Optional[dict] = None
    ):
        """Log auditable action"""
        self.logger.info(
            "",
            extra={
                "user": user,
                "action": action,
                "resource": resource,
                "result": result,
                "metadata": metadata or {}
            }
        )


# Usage in service
class DictionaryService:
    def __init__(self, ..., audit_logger: AuditLogger):
        self.audit_logger = audit_logger

    async def create_dictionary(self, file_path: Path, metadata: DictionaryCreate):
        try:
            # ... processing ...

            self.audit_logger.log_action(
                user=metadata.created_by or "unknown",
                action="CREATE_DICTIONARY",
                resource=f"dictionary:{dictionary.id}",
                result="SUCCESS",
                metadata={"file_name": file_path.name}
            )

            return result
        except Exception as e:
            self.audit_logger.log_action(
                user=metadata.created_by or "unknown",
                action="CREATE_DICTIONARY",
                resource="dictionary",
                result="FAILURE",
                metadata={"error": str(e)}
            )
            raise
```

---

## 9. Error Handling & Logging

### 9.1 Exception Hierarchy

```python
# core/exceptions.py
class DataDictException(Exception):
    """Base exception for all application errors"""
    def __init__(self, message: str, details: dict = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class ValidationError(DataDictException):
    """Input validation errors"""
    pass


class NotFoundError(DataDictException):
    """Resource not found"""
    pass


class ProcessingError(DataDictException):
    """Errors during JSON processing"""
    pass


class ExportError(DataDictException):
    """Errors during export generation"""
    pass


class ExternalServiceError(DataDictException):
    """Errors from external services (OpenAI, etc.)"""
    pass
```

### 9.2 Global Exception Handler

```python
# api/middlewares.py
from fastapi import Request, status
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
import logging
import traceback
import uuid

logger = logging.getLogger(__name__)

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """Handle all uncaught exceptions"""

    request_id = str(uuid.uuid4())

    # Log full error
    logger.error(
        f"Unhandled exception: {exc}",
        extra={
            "request_id": request_id,
            "path": request.url.path,
            "method": request.method,
            "traceback": traceback.format_exc()
        }
    )

    # Map exception to HTTP status
    if isinstance(exc, ValidationError):
        status_code = status.HTTP_400_BAD_REQUEST
        error_code = "VALIDATION_ERROR"
    elif isinstance(exc, NotFoundError):
        status_code = status.HTTP_404_NOT_FOUND
        error_code = "NOT_FOUND"
    elif isinstance(exc, ProcessingError):
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        error_code = "PROCESSING_ERROR"
    elif isinstance(exc, ExternalServiceError):
        status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        error_code = "EXTERNAL_SERVICE_ERROR"
    else:
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        error_code = "INTERNAL_ERROR"

    return JSONResponse(
        status_code=status_code,
        content={
            "error": {
                "code": error_code,
                "message": str(exc),
                "details": getattr(exc, 'details', {}),
                "request_id": request_id
            }
        }
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle Pydantic validation errors"""
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Request validation failed",
                "details": exc.errors(),
                "request_id": str(uuid.uuid4())
            }
        }
    )


# Register handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
```

### 9.3 Structured Logging

```python
# core/logging.py
import logging
import sys
from pythonjsonlogger import jsonlogger

def setup_logging(log_level: str = "INFO", environment: str = "development"):
    """Configure structured logging"""

    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)

    if environment == "production":
        # JSON format for production
        formatter = jsonlogger.JsonFormatter(
            fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S'
        )
    else:
        # Human-readable for development
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler for errors
    error_handler = logging.FileHandler('logs/error.log')
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)

    # Separate audit log
    audit_logger = logging.getLogger('audit')
    audit_handler = logging.FileHandler('logs/audit.log')
    audit_handler.setFormatter(jsonlogger.JsonFormatter())
    audit_logger.addHandler(audit_handler)
    audit_logger.setLevel(logging.INFO)

    return root_logger
```

### 9.4 Request Logging Middleware

```python
# api/middlewares.py
import time
import logging
from fastapi import Request

logger = logging.getLogger(__name__)

async def log_requests_middleware(request: Request, call_next):
    """Log all HTTP requests"""

    start_time = time.time()

    # Log request
    logger.info(
        "Request started",
        extra={
            "method": request.method,
            "path": request.url.path,
            "client_ip": request.client.host if request.client else None,
            "user_agent": request.headers.get("user-agent")
        }
    )

    # Process request
    response = await call_next(request)

    # Log response
    duration_ms = (time.time() - start_time) * 1000
    logger.info(
        "Request completed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration_ms, 2)
        }
    )

    # Add headers
    response.headers["X-Process-Time"] = str(duration_ms)

    return response


# Register middleware
app.middleware("http")(log_requests_middleware)
```

### 9.5 Error Recovery Strategies

```python
# processors/ai_generator.py
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

class AIDescriptionGenerator:

    @retry(
        retry=retry_if_exception_type((openai.RateLimitError, openai.APIError)),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10)
    )
    def generate_description(self, ...):
        """Generate with automatic retry on transient failures"""
        try:
            response = self.client.chat.completions.create(...)
            return self._parse_response(response)

        except openai.RateLimitError as e:
            logger.warning(f"Rate limit hit, retrying: {e}")
            raise  # Retry

        except openai.APIError as e:
            logger.error(f"OpenAI API error, retrying: {e}")
            raise  # Retry

        except Exception as e:
            logger.error(f"Unexpected error, using fallback: {e}")
            # Don't retry, use fallback
            return self._fallback_description(...)
```

---

## 10. Performance Optimization

### 10.1 Database Optimization

#### 10.1.1 Indexing Strategy

```sql
-- Core indexes (from schema)
CREATE INDEX idx_dictionaries_created_at ON dictionaries(created_at DESC);
CREATE INDEX idx_dictionaries_name ON dictionaries(name);
CREATE INDEX idx_fields_version_id ON fields(version_id);
CREATE INDEX idx_fields_field_path ON fields(field_path);
CREATE INDEX idx_fields_is_pii ON fields(is_pii) WHERE is_pii = TRUE;

-- Composite indexes for common queries
CREATE INDEX idx_fields_version_type ON fields(version_id, data_type);
CREATE INDEX idx_fields_version_semantic ON fields(version_id, semantic_type);

-- JSONB indexes
CREATE INDEX idx_fields_sample_values ON fields USING GIN (sample_values);
```

#### 10.1.2 Query Optimization

```python
# repositories/field_repo.py
from sqlalchemy.orm import joinedload, selectinload

class FieldRepository:

    def get_fields_with_annotations(self, version_id: UUID) -> List[Field]:
        """Optimized query with eager loading"""
        stmt = (
            select(Field)
            .where(Field.version_id == version_id)
            .options(selectinload(Field.annotations))  # Avoid N+1
            .order_by(Field.position)
        )
        result = self.db.execute(stmt)
        return result.scalars().all()

    def bulk_insert_fields(self, fields: List[Field]) -> None:
        """Bulk insert for performance"""
        self.db.bulk_save_objects(fields)
        self.db.commit()
```

#### 10.1.3 Connection Pooling

```python
# core/database.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool

engine = create_engine(
    settings.database_url,
    poolclass=QueuePool,
    pool_size=20,          # Connections to keep open
    max_overflow=10,       # Additional connections when needed
    pool_pre_ping=True,    # Verify connections before use
    pool_recycle=3600,     # Recycle connections after 1 hour
    echo=False             # Don't log SQL (use in dev only)
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
```

### 10.2 Streaming & Async Processing

#### 10.2.1 Streaming JSON Parsing

```python
# processors/json_parser.py
import ijson

class JSONParser:
    """Streaming parser for large files"""

    def parse_large_file(self, file_path: Path) -> Generator[dict, None, None]:
        """Stream parse without loading entire file into memory"""
        with open(file_path, 'rb') as f:
            # Use ijson for streaming
            parser = ijson.items(f, 'item')
            for item in parser:
                yield self._process_item(item)

    def _process_item(self, item: dict) -> dict:
        """Process single item"""
        # Extract fields incrementally
        return {...}
```

#### 10.2.2 Background Jobs (Phase 2)

```python
# Using Celery for background processing
from celery import Celery

celery_app = Celery('datadict', broker=settings.redis_url)

@celery_app.task
def process_dictionary_async(file_path: str, metadata: dict):
    """Process dictionary in background"""
    # Long-running processing
    service = DictionaryService(...)
    return service.create_dictionary(Path(file_path), metadata)


# Trigger from API
@router.post("/dictionaries/async")
async def create_dictionary_async(...):
    task = process_dictionary_async.delay(file_path, metadata)
    return {"job_id": task.id, "status": "processing"}
```

### 10.3 Caching Strategy

```python
# core/cache.py
from functools import lru_cache
import redis
import pickle

class CacheService:
    """Redis-based caching"""

    def __init__(self, redis_url: str):
        self.redis = redis.from_url(redis_url)
        self.default_ttl = 3600  # 1 hour

    def get(self, key: str):
        """Get cached value"""
        value = self.redis.get(key)
        return pickle.loads(value) if value else None

    def set(self, key: str, value, ttl: int = None):
        """Set cached value"""
        self.redis.setex(
            key,
            ttl or self.default_ttl,
            pickle.dumps(value)
        )

    def invalidate(self, pattern: str):
        """Invalidate cache by pattern"""
        for key in self.redis.scan_iter(pattern):
            self.redis.delete(key)


# Usage
cache = CacheService(settings.redis_url)

class DictionaryService:
    def get_dictionary(self, dictionary_id: UUID):
        # Check cache
        cache_key = f"dictionary:{dictionary_id}"
        cached = cache.get(cache_key)
        if cached:
            return cached

        # Fetch from DB
        dictionary = self.dictionary_repo.get_by_id(dictionary_id)

        # Cache result
        cache.set(cache_key, dictionary, ttl=3600)

        return dictionary
```

### 10.4 Pagination & Limiting

```python
# repositories/base.py
from typing import List, TypeVar, Generic
from sqlalchemy import select, func

T = TypeVar('T')

class BaseRepository(Generic[T]):
    """Base repository with pagination"""

    def __init__(self, model: type, db: Session):
        self.model = model
        self.db = db

    def paginate(
        self,
        limit: int = 20,
        offset: int = 0,
        filters: list = None,
        order_by = None
    ) -> tuple[List[T], int]:
        """
        Paginate query.

        Returns:
            (items, total_count)
        """
        # Base query
        stmt = select(self.model)

        # Apply filters
        if filters:
            for filter_clause in filters:
                stmt = stmt.where(filter_clause)

        # Get total count
        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = self.db.execute(count_stmt).scalar()

        # Apply ordering
        if order_by is not None:
            stmt = stmt.order_by(order_by)

        # Apply pagination
        stmt = stmt.limit(limit).offset(offset)

        # Execute
        result = self.db.execute(stmt)
        items = result.scalars().all()

        return items, total
```

### 10.5 Excel Export Optimization

```python
# exporters/excel_exporter.py
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.utils import get_column_letter

class ExcelExporter:
    """Optimized Excel export"""

    def export_dictionary(
        self,
        dictionary: Dictionary,
        fields: List[Field],
        output_path: Path
    ):
        """Export with write-only mode for large datasets"""

        # Use write_only for memory efficiency
        wb = Workbook(write_only=True)
        ws = wb.create_sheet("Data Dictionary")

        # Write header
        header = [
            "Field Path", "Data Type", "Semantic Type",
            "Description", "Sample Values", "Null %",
            "Cardinality", "PII Flag"
        ]
        ws.append(header)

        # Write rows (streaming)
        for field in fields:
            row = [
                field.field_path,
                field.data_type,
                field.semantic_type or "",
                field.annotation.description if field.annotation else "",
                ", ".join(str(v) for v in field.sample_values[:5]) if field.sample_values else "",
                f"{field.null_percentage:.1f}%" if field.null_percentage else "",
                field.distinct_count,
                "Yes" if field.is_pii else "No"
            ]
            ws.append(row)

        # Save
        wb.save(output_path)
```

---

## 11. Testing Strategy

### 11.1 Testing Pyramid

```
        ┌─────────────────┐
        │   E2E Tests     │  5-10%
        │   (Slow)        │
        ├─────────────────┤
        │                 │
        │ Integration     │  20-30%
        │ Tests           │
        │                 │
        ├─────────────────┤
        │                 │
        │                 │
        │  Unit Tests     │  60-75%
        │  (Fast)         │
        │                 │
        └─────────────────┘
```

### 11.2 Unit Tests

```python
# tests/unit/processors/test_type_inferrer.py
import pytest
from src.processors.type_inferrer import TypeInferrer

class TestTypeInferrer:
    """Unit tests for type inference"""

    @pytest.fixture
    def inferrer(self):
        return TypeInferrer()

    def test_infer_integer_type(self, inferrer):
        """Should infer integer with 100% confidence"""
        types_seen = ['integer', 'integer', 'integer']
        data_type, confidence = inferrer.infer_type(types_seen)

        assert data_type == 'integer'
        assert confidence == 100.0

    def test_infer_mixed_numeric_types(self, inferrer):
        """Should infer float when both integer and float present"""
        types_seen = ['integer', 'integer', 'float']
        data_type, confidence = inferrer.infer_type(types_seen)

        assert data_type == 'float'
        assert confidence == 100.0

    def test_infer_with_nulls(self, inferrer):
        """Should ignore nulls when other types present"""
        types_seen = ['string', 'string', 'null', 'null']
        data_type, confidence = inferrer.infer_type(types_seen)

        assert data_type == 'string'
        assert confidence == 100.0

    def test_infer_unknown_when_empty(self, inferrer):
        """Should return unknown with 0 confidence for empty input"""
        types_seen = []
        data_type, confidence = inferrer.infer_type(types_seen)

        assert data_type == 'unknown'
        assert confidence == 0.0


# tests/unit/processors/test_pii_detector.py
class TestPIIDetector:
    """Unit tests for PII detection"""

    @pytest.fixture
    def detector(self):
        return PIIDetector()

    def test_detect_email_pii(self, detector):
        """Should detect email as PII"""
        is_pii, pii_type = detector.detect_pii(
            field_path="user.email",
            field_name="email",
            semantic_type="email",
            sample_values=["test@example.com"]
        )

        assert is_pii is True
        assert pii_type == "email"

    def test_detect_credit_card(self, detector):
        """Should detect valid credit card numbers"""
        # Valid test card number
        is_pii, pii_type = detector.detect_pii(
            field_path="payment.card",
            field_name="card",
            semantic_type=None,
            sample_values=["4532015112830366"]
        )

        assert is_pii is True
        assert pii_type == "credit_card"

    def test_no_pii_for_regular_field(self, detector):
        """Should not detect PII for regular fields"""
        is_pii, pii_type = detector.detect_pii(
            field_path="product.name",
            field_name="name",
            semantic_type=None,
            sample_values=["Widget", "Gadget"]
        )

        assert is_pii is False
        assert pii_type is None
```

### 11.3 Integration Tests

```python
# tests/integration/test_dictionary_service.py
import pytest
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from src.services.dictionary_service import DictionaryService
from src.models.base import Base

@pytest.fixture(scope="function")
def test_db():
    """Create test database"""
    engine = create_engine("postgresql://test:test@localhost/test_datadict")
    Base.metadata.create_all(engine)

    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()

    yield db

    db.close()
    Base.metadata.drop_all(engine)


@pytest.fixture
def sample_json_file(tmp_path):
    """Create sample JSON file for testing"""
    json_content = {
        "user": {
            "id": 123,
            "email": "test@example.com",
            "name": "Test User"
        },
        "order": {
            "total": 99.99,
            "items": [{"sku": "ABC", "qty": 2}]
        }
    }

    file_path = tmp_path / "sample.json"
    with open(file_path, 'w') as f:
        json.dump(json_content, f)

    return file_path


class TestDictionaryService:
    """Integration tests for DictionaryService"""

    def test_create_dictionary_end_to_end(self, test_db, sample_json_file):
        """Should create complete dictionary from JSON"""
        # Arrange
        service = DictionaryService(
            db=test_db,
            dictionary_repo=DictionaryRepository(test_db),
            # ... other dependencies
        )

        metadata = DictionaryCreate(
            name="Test Dictionary",
            description="Integration test",
            created_by="test@example.com",
            generate_ai_descriptions=False  # Skip AI for test
        )

        # Act
        result = service.create_dictionary(sample_json_file, metadata)

        # Assert
        assert result.id is not None
        assert result.name == "Test Dictionary"

        # Verify database
        dictionary = test_db.query(Dictionary).filter_by(id=result.id).first()
        assert dictionary is not None
        assert len(dictionary.versions) == 1

        version = dictionary.versions[0]
        assert version.version_number == 1
        assert len(version.fields) > 0

        # Verify fields
        email_field = next((f for f in version.fields if f.field_path == "user.email"), None)
        assert email_field is not None
        assert email_field.semantic_type == "email"
        assert email_field.is_pii is True
```

### 11.4 API Tests

```python
# tests/api/test_dictionaries.py
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)

class TestDictionariesAPI:
    """API endpoint tests"""

    def test_create_dictionary(self, sample_json_file):
        """Should create dictionary via API"""
        with open(sample_json_file, 'rb') as f:
            response = client.post(
                "/api/v1/dictionaries",
                files={"file": ("test.json", f, "application/json")},
                data={
                    "name": "API Test Dictionary",
                    "created_by": "test@example.com"
                },
                headers={"X-API-Key": "test-key"}
            )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data["data"]
        assert data["data"]["name"] == "API Test Dictionary"

    def test_list_dictionaries(self):
        """Should list dictionaries with pagination"""
        response = client.get(
            "/api/v1/dictionaries?limit=10&offset=0",
            headers={"X-API-Key": "test-key"}
        )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "meta" in data
        assert "total" in data["meta"]

    def test_unauthorized_access(self):
        """Should reject requests without API key"""
        response = client.get("/api/v1/dictionaries")

        assert response.status_code == 401
```

### 11.5 Test Coverage

```bash
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    --cov=src
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=80
```

---

## 12. Deployment Architecture

### 12.1 Local Development

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: datadict
      POSTGRES_PASSWORD: dev_password
      POSTGRES_DB: datadict
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile.dev
    command: uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
    ports:
      - "8000:8000"
    volumes:
      - ./backend:/app
    environment:
      - DATABASE_URL=postgresql://datadict:dev_password@postgres:5432/datadict
      - REDIS_URL=redis://redis:6379/0
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    depends_on:
      - postgres
      - redis

volumes:
  postgres_data:
  redis_data:
```

### 12.2 Production Deployment

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim as base

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY src/ ./src/
COPY alembic/ ./alembic/
COPY alembic.ini .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Run migrations and start app
CMD alembic upgrade head && \
    uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 12.3 Environment Configuration

```python
# core/config.py
from enum import Enum

class Environment(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"


class Settings(BaseSettings):
    """Environment-specific settings"""

    environment: Environment = Environment.DEVELOPMENT

    # Database
    database_url: str

    # Redis (optional in dev)
    redis_url: Optional[str] = None

    # API
    api_title: str = "Data Dictionary Generator"
    api_version: str = "1.0.0"

    # Security
    api_keys: str
    cors_origins: List[str] = ["http://localhost:3000"]

    # OpenAI
    openai_api_key: str

    # Performance
    worker_count: int = 4
    max_file_size_mb: int = 100

    # Logging
    log_level: str = "INFO"

    class Config:
        env_file = f".env.{Environment.DEVELOPMENT}"
```

### 12.4 Database Migrations

```python
# alembic/env.py
from alembic import context
from sqlalchemy import engine_from_config, pool
from src.core.config import settings
from src.models.base import Base

config = context.config
config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata

def run_migrations_online():
    """Run migrations in 'online' mode"""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()
```

```bash
# Migration commands
alembic revision --autogenerate -m "Create initial tables"
alembic upgrade head
alembic downgrade -1
```

### 12.5 Health Checks

```python
# api/v1/health.py
from fastapi import APIRouter, Depends
from sqlalchemy import text
from src.core.database import get_db

router = APIRouter()

@router.get("/health")
async def health_check(db: Session = Depends(get_db)):
    """
    Health check endpoint.

    Verifies:
    - API is responding
    - Database is accessible
    - Redis is accessible (if configured)
    """
    health_status = {
        "status": "healthy",
        "version": settings.api_version,
        "environment": settings.environment,
        "checks": {}
    }

    # Database check
    try:
        db.execute(text("SELECT 1"))
        health_status["checks"]["database"] = "ok"
    except Exception as e:
        health_status["status"] = "unhealthy"
        health_status["checks"]["database"] = f"error: {str(e)}"

    # Redis check (if configured)
    if settings.redis_url:
        try:
            redis_client.ping()
            health_status["checks"]["redis"] = "ok"
        except Exception as e:
            health_status["checks"]["redis"] = f"error: {str(e)}"

    return health_status


@router.get("/ready")
async def readiness_check():
    """Kubernetes readiness probe"""
    return {"status": "ready"}


@router.get("/live")
async def liveness_check():
    """Kubernetes liveness probe"""
    return {"status": "alive"}
```

### 12.6 Monitoring (Future)

```python
# core/metrics.py
from prometheus_client import Counter, Histogram, Gauge
from prometheus_fastapi_instrumentator import Instrumentator

# Custom metrics
dictionaries_created = Counter(
    'dictionaries_created_total',
    'Total number of dictionaries created'
)

processing_duration = Histogram(
    'dictionary_processing_seconds',
    'Time spent processing dictionaries',
    buckets=[1, 5, 10, 30, 60, 120, 300]
)

active_dictionaries = Gauge(
    'active_dictionaries',
    'Number of active dictionaries'
)

# Instrument FastAPI app
Instrumentator().instrument(app).expose(app, endpoint="/metrics")
```

---

## Appendix A: Project Setup Guide

### Quick Start

```bash
# 1. Clone repository
git clone <repo-url>
cd data-dictionary-gen

# 2. Set up backend
cd backend
python -m venv venv
source venv/bin/activate  # or `venv\Scripts\activate` on Windows
pip install -r requirements-dev.txt

# 3. Configure environment
cp .env.example .env
# Edit .env with your settings

# 4. Start infrastructure
docker-compose up -d postgres redis

# 5. Run migrations
alembic upgrade head

# 6. Start development server
uvicorn src.main:app --reload

# 7. Access API docs
open http://localhost:8000/docs
```

---

## Appendix B: API Documentation

OpenAPI specification available at: `/api/v1/openapi.json`
Interactive docs at: `/docs` (Swagger UI)
Alternative docs at: `/redoc` (ReDoc)

---

## Document Control

**Version:** 1.0 (Complete)
**Date:** 2025-11-08
**Status:** Final Draft
**Authors:** Data Platform Team
**Reviewers:** TBD

**Change History:**
| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2025-11-08 | Data Platform Team | Initial complete version |

---

**End of Document**
