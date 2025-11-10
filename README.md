# Data Dictionary Generator

**An intelligent, automated tool that generates comprehensive data dictionaries from JSON files with AI-powered insights.**

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-19-61dafb.svg)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.2+-3178c6.svg)](https://www.typescriptlang.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-336791.svg)](https://www.postgresql.org/)

---

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Technology Stack](#technology-stack)
- [Quick Start](#quick-start)
- [Project Structure](#project-structure)
- [Documentation](#documentation)
- [Architecture Highlights](#architecture-highlights)
- [Current Limitations](#current-limitations)
- [Roadmap](#roadmap)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

The Data Dictionary Generator is a powerful tool designed to help data engineers, analysts, and scientists understand their data structures quickly and comprehensively. Simply upload a JSON file, and the system will:

- **Parse** complex nested structures (up to 500MB files)
- **Analyze** data types, statistics, and quality metrics
- **Detect** personally identifiable information (PII)
- **Generate** intelligent field descriptions using GPT-4
- **Track** schema versions over time
- **Export** professional Excel reports

This tool bridges the gap between raw data and documentation, making it easier for teams to maintain data catalogs, onboard new members, and ensure data quality.

---

## Key Features

### Data Processing
- **Streaming JSON Parser**: Handles large files (up to 500MB) with memory-efficient streaming
- **Nested Structure Support**: Automatically flattens and documents nested objects and arrays
- **Automatic Type Inference**: Intelligently detects data types from sample values
- **Semantic Type Detection**: Recognizes emails, URLs, phone numbers, dates, currencies, and more

### Analytics & Quality
- **Comprehensive Statistics**: Min, max, mean, median, percentiles, standard deviation
- **Quality Metrics**: Null percentage, cardinality ratio, distinct counts
- **PII Detection**: Identifies emails, phone numbers, SSNs, credit cards
- **Sample Values**: Stores representative examples for each field

### AI-Powered Insights
- **GPT-4 Integration**: Generates contextual field descriptions automatically
- **Batch Processing**: Efficiently processes multiple fields in a single API call
- **Configurable**: Toggle AI generation on/off per dictionary

### Version Management
- **Schema Tracking**: Monitors field additions, removals, and type changes
- **Version Comparison**: Visualize differences between schema versions
- **Change History**: Complete audit trail of all schema modifications

### Export & Integration
- **Excel Export**: Professional, formatted spreadsheets with color-coded metrics
- **REST API**: Comprehensive API for programmatic access
- **Interactive UI**: Modern React interface with search, filters, and visualizations

---

## Technology Stack

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** (0.104+) - Modern, high-performance Python web framework
- **[PostgreSQL](https://www.postgresql.org/)** (15+) - Robust relational database with JSONB support
- **[SQLAlchemy](https://www.sqlalchemy.org/)** (2.0) - Python SQL toolkit and ORM
- **[Pydantic](https://docs.pydantic.dev/)** (2.5+) - Data validation using Python type hints
- **[OpenAI API](https://platform.openai.com/)** - GPT-4 for field description generation
- **[pandas](https://pandas.pydata.org/)** - Statistical analysis and data processing
- **[ijson](https://pypi.org/project/ijson/)** - Streaming JSON parser for large files
- **[openpyxl](https://openpyxl.readthedocs.io/)** - Excel file generation
- **[Redis](https://redis.io/)** (7+) - Caching layer (planned for Phase 2)

### Frontend
- **[React](https://react.dev/)** (19) - Component-based UI library
- **[TypeScript](https://www.typescriptlang.org/)** (5.2+) - Type-safe JavaScript
- **[TanStack Query](https://tanstack.com/query)** - Server state management
- **[shadcn/ui](https://ui.shadcn.com/)** - Accessible component library
- **[TailwindCSS](https://tailwindcss.com/)** (3) - Utility-first CSS framework
- **[Vite](https://vitejs.dev/)** - Fast build tool and dev server
- **[React Router](https://reactrouter.com/)** (v6) - Client-side routing
- **[Recharts](https://recharts.org/)** - Data visualization library

### Infrastructure
- **[Docker](https://www.docker.com/)** - Containerization
- **[Docker Compose](https://docs.docker.com/compose/)** - Multi-container orchestration
- **[Alembic](https://alembic.sqlalchemy.org/)** - Database migration tool

---

## Quick Start

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Docker & Docker Compose** (for database)
- **OpenAI API Key** (optional, for AI descriptions)

### Option 1: Local Development (Recommended for Testing)

#### 1. Start Infrastructure Services

```bash
# Start PostgreSQL and Redis
docker-compose up -d postgres redis
```

#### 2. Setup Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements-dev.txt

# Configure environment
cp .env.example .env
# Edit .env with your settings (especially OPENAI_API_KEY if using AI)

# Start backend server
uvicorn src.main:app --reload
```

Backend will be available at:
- **API**: http://localhost:8000
- **API Docs**: http://localhost:8000/api/docs
- **Health Check**: http://localhost:8000/health

#### 3. Setup Frontend (New Terminal)

```bash
cd frontend
npm install

# Configure environment
cp .env.example .env

# Start frontend dev server
npm run dev
```

Frontend will be available at: **http://localhost:5173**

#### 4. Test with Sample Data

1. Open http://localhost:5173 in your browser
2. Click "Upload New" button
3. Upload `sample-data.json` from the project root
4. Fill in the form:
   - Name: "User Analytics Data"
   - Description: "Sample customer data with PII and nested structures"
   - Enable AI descriptions (if you have an API key)
5. Click "Create Dictionary"
6. Explore the generated data dictionary!

For a detailed walkthrough, see [QUICK_START.md](QUICK_START.md).

---

## Project Structure

```
data-dictionary-gen/
├── backend/                    # FastAPI backend application
│   ├── src/
│   │   ├── api/               # API routes and endpoints
│   │   │   └── v1/            # API version 1
│   │   ├── core/              # Core configuration (config, logging, security)
│   │   ├── models/            # SQLAlchemy ORM models
│   │   ├── schemas/           # Pydantic schemas (DTOs)
│   │   ├── services/          # Business logic layer
│   │   ├── processors/        # Data processing (parsing, type detection, PII)
│   │   ├── repositories/      # Data access layer
│   │   ├── exporters/         # Export handlers (Excel, CSV)
│   │   └── main.py           # Application entry point
│   ├── tests/                 # Test suite (unit & integration)
│   ├── alembic/              # Database migrations
│   └── requirements.txt       # Python dependencies
│
├── frontend/                   # React frontend application
│   ├── src/
│   │   ├── api/              # API client and service functions
│   │   ├── components/       # React components
│   │   │   ├── ui/           # shadcn/ui base components
│   │   │   └── layout/       # Layout components
│   │   ├── hooks/            # Custom React hooks
│   │   ├── pages/            # Route pages
│   │   ├── types/            # TypeScript type definitions
│   │   └── lib/              # Utility functions
│   └── package.json          # Node.js dependencies
│
├── docs/                      # Design documentation
│   ├── CONOPS.md             # Concept of Operations
│   ├── REQUIREMENTS.md       # System Requirements
│   └── SOFTWARE_DESIGN.md    # Technical Architecture
│
├── docker-compose.yml         # Docker services configuration
├── sample-data.json          # Sample dataset for testing
├── QUICK_START.md            # 3-minute getting started guide
└── IMPLEMENTATION_STATUS.md  # Current implementation status (~70%)
```

---

## Documentation

### Getting Started
- **[docs/QUICK_START.md](docs/QUICK_START.md)** - Get up and running in 3 minutes
- **[backend/README.md](backend/README.md)** - Backend setup and API documentation
- **[frontend/README.md](frontend/README.md)** - Frontend setup and development guide
- **[docs/SAMPLE_DATA_README.md](docs/SAMPLE_DATA_README.md)** - Understanding the sample dataset

### Design & Architecture
- **[docs/CONOPS.md](docs/CONOPS.md)** - Concept of Operations
- **[docs/REQUIREMENTS.md](docs/REQUIREMENTS.md)** - System Requirements Specification
- **[docs/SOFTWARE_DESIGN.md](docs/SOFTWARE_DESIGN.md)** - Detailed Technical Architecture

---

## Architecture Highlights

### Clean Architecture Pattern

The backend follows a layered architecture with clear separation of concerns:

```
┌─────────────────────────────────────┐
│        API Layer (FastAPI)          │  ← HTTP endpoints, validation
├─────────────────────────────────────┤
│       Service Layer (Business)      │  ← Orchestration, workflows
├─────────────────────────────────────┤
│    Repository Layer (Data Access)   │  ← Database operations, ORM
├─────────────────────────────────────┤
│      Processor Layer (Analysis)     │  ← Parsing, type detection, PII
└─────────────────────────────────────┘
            ↓
┌─────────────────────────────────────┐
│    Database Layer (PostgreSQL)      │  ← Persistence, JSONB storage
└─────────────────────────────────────┘
```

### Key Design Patterns

- **Repository Pattern**: Abstracts data access with generic CRUD operations
- **Dependency Injection**: Services and repositories injected via FastAPI dependencies
- **Service Orchestration**: Complex workflows coordinated in service layer
- **Streaming Processing**: Memory-efficient handling of large JSON files
- **Type-Safe Schemas**: Pydantic models ensure data validation throughout the stack

### Database Schema

Four core entities with relationships:

- **Dictionary**: Top-level container for a dataset
- **Version**: Snapshot of schema at a point in time
- **Field**: Individual data field with comprehensive metadata
- **Annotation**: User-provided or AI-generated field documentation

All entities support JSONB columns for flexible metadata storage.

---

## Current Limitations

### Features Intentionally Not Implemented (Phase 1 MVP)

The following features were mentioned in requirements but are **not yet implemented**:

#### Authentication & Authorization
- No user authentication system (placeholder only)
- No multi-user management
- No role-based access control (RBAC)
- `API_KEY_ENABLED=false` by default

#### Performance & Scalability
- No rate limiting (configured but disabled)
- No request throttling
- No distributed caching (Redis configured but not used)

#### Monitoring & Operations
- No production metrics/monitoring
- No alerting system
- No health dashboards
- Basic health check endpoint only

#### Notifications
- No email notifications
- No webhook integrations
- No real-time updates (WebSocket)

#### Background Processing
- Celery configured but not actively used
- All processing happens synchronously
- No job queues or task scheduling

### Known Technical Gaps

According to [IMPLEMENTATION_STATUS.md](IMPLEMENTATION_STATUS.md), the project is approximately **70% complete** with the following gaps:

- Some API endpoints may be stubs
- Limited test coverage (target: 80%)
- No database migrations created yet (Alembic configured)
- No Dockerfile for backend (docker-compose has commented backend service)
- Security implementation is basic (suitable for development only)

**Recommendation**: This project is suitable for development, testing, and internal tools but requires additional hardening for production use.

---

## Roadmap

### Phase 1: MVP Foundation (Current - ~70% Complete)
- [x] Core data processing pipeline
- [x] Database models and relationships
- [x] Service layer orchestration
- [x] React UI with basic features
- [ ] Complete API endpoint implementation
- [ ] Comprehensive test suite (80% coverage)
- [ ] Database migrations
- [ ] Docker containerization

### Phase 2: Enhanced Features (Planned)
- [ ] Full authentication/authorization system
- [ ] Advanced search with full-text indexing
- [ ] Redis caching layer
- [ ] Rate limiting and quota management
- [ ] Background job processing with Celery
- [ ] Webhook integrations

### Phase 3: Production Readiness (Future)
- [ ] Monitoring and metrics (Prometheus/Grafana)
- [ ] Distributed tracing
- [ ] Email notifications
- [ ] Real-time updates (WebSocket)
- [ ] Multi-tenancy support
- [ ] Advanced data visualizations
- [ ] API versioning strategy

### Phase 4: Advanced Analytics (Future)
- [ ] Data profiling and anomaly detection
- [ ] Schema drift alerts
- [ ] Data lineage tracking
- [ ] Integration with data catalogs (e.g., DataHub, Amundsen)
- [ ] ML-based type inference improvements
- [ ] Custom semantic type definitions

---

## Contributing

We welcome contributions! Here's how you can help:

### Development Setup

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Follow the setup instructions in [Quick Start](#quick-start)
4. Make your changes
5. Run tests and linting
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to your branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

### Coding Standards

**Backend (Python)**
- Follow PEP 8 style guide
- Use type hints throughout
- Write docstrings for all public functions/classes
- Run `ruff check --fix` and `ruff format` before committing
- Maintain test coverage above 80%

**Frontend (TypeScript)**
- Follow TypeScript strict mode
- Use functional components with hooks
- Follow shadcn/ui component patterns
- Use Tailwind utility classes (avoid custom CSS)
- Ensure `npm run build` succeeds

### Testing

```bash
# Backend tests
cd backend
pytest --cov=src --cov-report=html

# Frontend tests (when implemented)
cd frontend
npm test
```

### Areas Needing Help

- Complete API endpoint implementations
- Expand test coverage (currently minimal)
- Add database migrations
- Create Dockerfile for backend
- Implement authentication system
- Add search functionality
- Performance optimization
- Documentation improvements

---

## License

This project does not currently have a license specified. Please contact the repository owner for usage rights and licensing information.

---

## Acknowledgments

- **FastAPI** - For the excellent modern Python web framework
- **shadcn/ui** - For the beautiful, accessible component library
- **OpenAI** - For GPT-4 API enabling intelligent descriptions
- **SQLAlchemy** - For the robust ORM and database toolkit
- **TanStack Query** - For elegant server state management

---

## Support & Contact

- **Issues**: Please report bugs and feature requests via GitHub Issues
- **Documentation**: See the [docs/](docs/) directory for detailed specifications
- **API Docs**: Access interactive API documentation at http://localhost:8000/api/docs when running

---

**Built with care for data professionals who value comprehensive documentation**
