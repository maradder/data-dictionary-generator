# Concept of Operations (ConOps)
## Data Dictionary Generator

**Version:** 1.0
**Date:** 2025-11-08
**Status:** Draft

---

## Executive Summary

### Project Vision
The Data Dictionary Generator is a robust, intelligent tool designed to automatically generate comprehensive data dictionaries from JSON documents, including those with deeply nested structures. The system will provide a modern web-based user interface and export capabilities to Excel workbooks, enabling data teams to efficiently document, version, and maintain metadata for data lake assets.

### Objectives
1. **Automate Documentation**: Eliminate manual data dictionary creation, reducing time from hours to minutes
2. **Enable Schema Evolution Tracking**: Provide version comparison and change detection capabilities
3. **Enhance Data Quality**: Surface data quality metrics and potential issues automatically
4. **Democratize Data Understanding**: Make data accessible to technical and non-technical users alike
5. **Scale Documentation Practices**: Support batch processing of hundreds of datasets

### Target Users
Medium-sized data teams (10-50 people) working with JSON-based data lake/warehouse files who need to maintain documentation at scale while ensuring data quality and governance.

### Business Value
- **Time Savings**: 80% reduction in documentation time
- **Data Quality**: Early detection of schema changes and data quality issues
- **Compliance**: Improved governance through consistent, auditable documentation
- - **Collaboration**: Shared understanding of data assets across technical and business teams

---

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Web User Interface                      │
│                    (React Frontend)                         │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │ REST API
                         │
┌────────────────────────▼────────────────────────────────────┐
│                  Application Server                         │
│                  (Python FastAPI)                           │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │ JSON Parser  │ Quality      │ AI Description           │ │
│  │ & Analyzer   │ Analyzer     │ Generator                │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
└────────────────────────┬────────────────────────────────────┘
                         │
                         │
┌────────────────────────▼────────────────────────────────────┐
│                    Database Layer                           │
│         (PostgreSQL with JSONB support)                     │
│  - Data Dictionaries    - Schema Versions                   │
│  - Annotations          - Quality Metrics                   │
└─────────────────────────────────────────────────────────────┘
```

### Core Capabilities

#### 1. JSON Processing
- Parse arbitrarily nested JSON structures
- Infer data types and semantic types
- Extract sample values and statistical metrics
- Handle arrays, objects, and primitive types

#### 2. Data Dictionary Generation
- Automatic field cataloging with path notation
- Data type inference (string, integer, float, boolean, array, object)
- Semantic type detection (email, URL, date, currency, etc.)
- Sample value extraction
- Null/missing value analysis

#### 3. Version Management
- Store multiple versions of schemas
- Side-by-side version comparison
- Change detection (added, removed, modified fields)
- Breaking change identification
- Audit trail with timestamps and attribution

#### 4. Data Quality Analysis
- Sample value collection
- Null percentage calculation
- Cardinality metrics
- Distribution statistics (min, max, median, percentiles)
- PII detection patterns

#### 5. AI-Powered Documentation
- Auto-generate field descriptions from names
- Suggest business-friendly names
- Batch annotation for similar fields
- Context-aware documentation

#### 6. Export & Integration
- Excel export with formatting and filters
- REST API for programmatic access
- Batch processing capabilities
- Data catalog integration ready

---

## Personas

### 1. Data Engineer - Sarah
**Role:** Senior Data Engineer
**Experience:** 5+ years
**Technical Level:** High

**Responsibilities:**
- Build and maintain data pipelines
- Document data assets
- Ensure data quality
- Manage schema evolution

**Goals:**
- Automate repetitive documentation tasks
- Track schema changes over time
- Identify data quality issues early
- Maintain pipeline stability

**Pain Points:**
- Manual documentation is time-consuming and error-prone
- Schema changes break downstream consumers without warning
- Hard to maintain documentation as data evolves
- Difficult to track lineage across systems

**How This Tool Helps:**
- Automatic dictionary generation from JSON files
- Version comparison to detect breaking changes
- Batch processing for multiple datasets
- Quality metrics surface issues immediately

**Key User Stories:** #1, #2, #6, #11, #22, #23, #26

---

### 2. Data Analyst - Marcus
**Role:** Business Intelligence Analyst
**Experience:** 3 years
**Technical Level:** Medium

**Responsibilities:**
- Build dashboards and reports
- Analyze business metrics
- Validate data accuracy
- Communicate insights to stakeholders

**Goals:**
- Quickly understand available datasets
- Find the right fields for analysis
- Validate data before using in reports
- Share data documentation with business users

**Pain Points:**
- Unclear field meanings waste time
- Unknown data quality issues lead to incorrect reports
- Hard to search across datasets
- Can't easily share technical documentation with non-technical stakeholders

**How This Tool Helps:**
- Searchable data dictionaries
- Clear field descriptions with samples
- Excel export for sharing with stakeholders
- Null percentage helps assess data completeness

**Key User Stories:** #3, #10, #14, #18, #19

---

### 3. Data Scientist - Priya
**Role:** Machine Learning Engineer
**Experience:** 4 years
**Technical Level:** High

**Responsibilities:**
- Build predictive models
- Feature engineering
- Evaluate feature quality
- Ensure model reproducibility

**Goals:**
- Explore available features quickly
- Understand data distributions
- Identify high-quality features
- Document feature engineering decisions

**Pain Points:**
- Missing metadata requires manual exploration
- Can't assess feature quality without querying
- Unclear which fields are reliable
- Hard to reproduce experiments when schemas change

**How This Tool Helps:**
- Sample values and distributions visible upfront
- Cardinality metrics identify useful features
- Version tracking ensures reproducibility
- AI-generated descriptions speed understanding

**Key User Stories:** #4, #9, #12, #16, #25

---

### 4. Analytics Engineer - James
**Role:** Analytics Engineer
**Experience:** 4 years
**Technical Level:** High

**Responsibilities:**
- Build dbt models and transformations
- Maintain data contracts
- Document transformation logic
- Monitor pipeline health

**Goals:**
- Detect upstream schema changes early
- Document data contracts
- Communicate changes to stakeholders
- Maintain pipeline reliability

**Pain Points:**
- Upstream changes break models unexpectedly
- Hard to know who to notify about changes
- Manual contract documentation is tedious
- Difficult to assess change impact

**How This Tool Helps:**
- Version comparison detects schema changes
- Breaking change alerts
- Export to data contract formats (dbt YAML)
- Impact analysis shows downstream dependencies

**Key User Stories:** #5, #6, #20, #27

---

### 5. Data Governance Lead - Chen
**Role:** Data Governance Manager
**Experience:** 7 years
**Technical Level:** Medium

**Responsibilities:**
- Ensure regulatory compliance
- Maintain data catalog
- Enforce documentation standards
- Audit data lineage

**Goals:**
- Consistent documentation across teams
- PII identification and protection
- Audit trail for schema changes
- Compliance reporting

**Pain Points:**
- Inconsistent documentation practices
- Hard to audit data lineage
- Manual PII discovery is risky
- Compliance violations due to undocumented data

**How This Tool Helps:**
- Automated PII detection
- Version history with audit trail
- Standardized documentation format
- Batch reporting across datasets

**Key User Stories:** #7, #13, #17, #24, #30

---

### 6. Product Manager - Alex
**Role:** Product Manager (Data Products)
**Experience:** 5 years
**Technical Level:** Low

**Responsibilities:**
- Define product requirements
- Assess feasibility of analytics requests
- Communicate with business stakeholders
- Prioritize data initiatives

**Goals:**
- Understand what data is available
- Assess feasibility without engineering help
- Communicate data capabilities to executives
- Make data-driven decisions

**Pain Points:**
- Can't search for available data
- Depends on engineers for basic questions
- Technical documentation is incomprehensible
- Unclear what metrics mean

**How This Tool Helps:**
- Search across all dictionaries
- Business-friendly descriptions
- Visual schema diagrams
- Excel export for executive presentations

**Key User Stories:** #3, #19, #29

---

### 7. Data Platform Engineer - Jordan
**Role:** Staff Platform Engineer
**Experience:** 8 years
**Technical Level:** Very High

**Responsibilities:**
- Maintain data infrastructure
- Build automation tools
- Ensure metadata accuracy
- Integrate systems

**Goals:**
- Automate documentation at scale
- Integrate with existing catalog
- Provide API access for custom tools
- Ensure system reliability

**Pain Points:**
- Manual processes don't scale
- Multiple metadata silos
- Hard to keep documentation current
- Need programmatic access

**How This Tool Helps:**
- Batch processing and scheduling
- REST API for integrations
- Data catalog connectors
- Automated quality reporting

**Key User Stories:** #8, #21, #22, #23, #28

---

## User Stories

### Core Functionality

**US-001: Upload and Generate Dictionary**
**As a** Data Engineer
**I want to** upload a JSON file and automatically generate a complete data dictionary
**So that** I can quickly document new datasets without manual work

**Acceptance Criteria:**
- Support JSON files up to 100MB
- Parse all fields including nested objects
- Generate dictionary within 30 seconds for typical files
- Display progress indicator during processing

---

**US-002: Handle Deeply Nested JSON**
**As a** Data Engineer
**I want the** tool to handle deeply nested JSON (5+ levels)
**So that** complex event data and API responses are fully documented

**Acceptance Criteria:**
- Support nesting depth of at least 10 levels
- Use dot notation for field paths (e.g., `user.address.city`)
- Clearly indicate nesting level in output
- Handle circular references gracefully

---

**US-003: Export to Excel**
**As a** Data Analyst
**I want to** export the data dictionary to Excel with formatting and filters
**So that** I can share it with non-technical stakeholders

**Acceptance Criteria:**
- Export includes all fields and metadata
- Excel file has frozen headers and filters
- Formatting is professional and readable
- Export completes in under 1 minute for 1000+ fields

---

**US-004: Infer Data Types**
**As a** Data Scientist
**I want to** see data types inferred for each field
**So that** I understand the structure without inspecting raw data

**Acceptance Criteria:**
- Detect basic types: string, integer, float, boolean, null, array, object
- Indicate array item types (e.g., `array[string]`)
- Show mixed types when detected
- Confidence score for type inference

---

### Version Comparison & Schema Evolution

**US-005: Compare Schema Versions**
**As an** Analytics Engineer
**I want to** compare two versions of a JSON schema side-by-side
**So that** I can identify breaking changes before they impact my pipelines

**Acceptance Criteria:**
- Display both versions in parallel columns
- Highlight differences visually
- Filter to show only changed fields
- Export comparison report

---

**US-006: View Schema Diff**
**As a** Data Engineer
**I want to** see a diff highlighting added, removed, and modified fields between versions
**So that** I can communicate changes to downstream consumers

**Acceptance Criteria:**
- Color-coded changes (green=added, red=removed, yellow=modified)
- Show before/after values for modified fields
- Summary count of changes by type
- Copy-friendly change log format

---

**US-007: Track Version History**
**As a** Data Governance Lead
**I want to** track schema version history with timestamps and user attribution
**So that** I can audit when and why schemas changed

**Acceptance Criteria:**
- Store all versions with timestamps
- Record user who uploaded each version
- Display version timeline
- Annotate versions with notes/comments

---

**US-008: Detect Breaking Changes**
**As a** Data Platform Engineer
**I want to** automatically detect backward-incompatible changes
**So that** I can alert teams before deploying

**Acceptance Criteria:**
- Flag removed fields
- Flag type changes
- Flag required field additions
- Generate alert summary

---

### Data Quality Metrics

**US-009: Show Sample Values**
**As a** Data Scientist
**I want to** see sample values for each field (first 5-10 unique values)
**So that** I can quickly understand the data without querying the source

**Acceptance Criteria:**
- Display up to 10 unique sample values
- Show value frequency if available
- Truncate long values with ellipsis
- Indicate total unique count

---

**US-010: Display Null Percentages**
**As a** Data Analyst
**I want to** see null/missing value percentages for each field
**So that** I know data completeness before building reports

**Acceptance Criteria:**
- Calculate null percentage for each field
- Visual indicator (progress bar or color)
- Sort/filter by null percentage
- Flag fields with >50% nulls

---

**US-011: Show Value Distributions**
**As a** Data Engineer
**I want to** see value distributions (min, max, median, percentiles for numeric fields)
**So that** I can identify data quality issues

**Acceptance Criteria:**
- Calculate min, max, mean, median for numeric fields
- Show 25th, 50th, 75th percentiles
- Display standard deviation
- Histogram visualization for distributions

---

**US-012: Display Cardinality Metrics**
**As a** Data Scientist
**I want to** see cardinality metrics (distinct count) for each field
**So that** I can identify high-cardinality dimensions and potential PII

**Acceptance Criteria:**
- Show distinct value count
- Calculate cardinality ratio (distinct/total)
- Flag high-cardinality fields (>80% unique)
- Indicate potential ID/PII fields

---

**US-013: Flag Potential PII**
**As a** Data Governance Lead
**I want to** flag fields with potential PII based on patterns
**So that** I can ensure compliance

**Acceptance Criteria:**
- Detect emails via regex
- Detect phone numbers
- Detect SSN patterns
- Detect credit card numbers
- Flag with warning icon and label

---

### Auto-Documentation & Intelligence

**US-014: AI-Generated Descriptions**
**As a** Data Analyst
**I want** AI-generated descriptions for field names
**So that** I don't have to guess cryptic abbreviations

**Acceptance Criteria:**
- Generate description from field name (e.g., `cust_id` → "Customer Identifier")
- Handle common abbreviations
- Consider field type and samples
- Allow manual override

---

**US-015: Suggest Business-Friendly Names**
**As a** Data Engineer
**I want to** suggest business-friendly names for technical fields
**So that** stakeholders can understand the data

**Acceptance Criteria:**
- Suggest readable name (e.g., `usr_crt_ts` → "User Created Timestamp")
- Show both technical and suggested names
- Allow accepting/rejecting suggestions
- Learn from user corrections

---

**US-016: Infer Semantic Types**
**As a** Data Scientist
**I want the** tool to infer semantic types (date, email, currency, URL)
**So that** I can apply appropriate transformations

**Acceptance Criteria:**
- Detect dates in various formats
- Detect email addresses
- Detect URLs
- Detect currency (with symbol detection)
- Detect geographic data (zip codes, coordinates)

---

**US-017: Batch Annotation**
**As a** Data Governance Lead
**I want to** batch-annotate similar fields across multiple datasets
**So that** documentation is consistent

**Acceptance Criteria:**
- Find similar fields by name pattern
- Apply description to all matches
- Preview before applying
- Undo bulk changes

---

### Collaboration & Workflow

**US-018: Add Manual Annotations**
**As a** Data Analyst
**I want to** add manual annotations and business context
**So that** domain knowledge is captured

**Acceptance Criteria:**
- Edit field descriptions
- Add tags/labels
- Add business owner
- Track who made annotations

---

**US-019: Search Data Dictionaries**
**As a** Product Manager
**I want to** search across all data dictionaries by field name or description
**So that** I can discover what data exists

**Acceptance Criteria:**
- Full-text search across all fields
- Search by field name, description, type
- Filter by dataset, owner, date
- Ranked results

---

**US-020: Export Lineage Information**
**As an** Analytics Engineer
**I want to** export data lineage showing downstream dependencies
**So that** I can assess change impact

**Acceptance Criteria:**
- Show which dashboards use each field
- Show which models reference fields
- Export lineage graph
- Integration with lineage tools

---

**US-021: Integrate with Data Catalog**
**As a** Data Platform Engineer
**I want to** integrate with our data catalog
**So that** metadata is centralized

**Acceptance Criteria:**
- Push dictionaries to catalog via API
- Support common catalogs (DataHub, Alation)
- Bi-directional sync
- Configurable mapping

---

### Batch Processing & Scale

**US-022: Process Directories in Batch**
**As a** Data Platform Engineer
**I want to** process entire directories of JSON files in batch
**So that** I can document hundreds of datasets at once

**Acceptance Criteria:**
- Upload directory or provide path
- Process all JSON files found
- Progress tracking for batch jobs
- Summary report of results

---

**US-023: Schedule Automated Generation**
**As a** Data Engineer
**I want to** schedule automated dictionary generation
**So that** documentation stays current

**Acceptance Criteria:**
- Configure schedule (daily, weekly)
- Monitor S3/data lake for new files
- Automatic version detection
- Email notifications on changes

---

**US-024: Generate Health Report**
**As a** Data Governance Lead
**I want to** generate a dataset health report
**So that** I can prioritize cleanup efforts

**Acceptance Criteria:**
- Aggregate quality metrics across datasets
- Rank datasets by quality score
- Identify datasets with PII
- Export summary to Excel

---

### Advanced Features (Future)

**US-025: Show Correlation Matrices**
**As a** Data Scientist
**I want to** see correlation matrices between numeric fields
**So that** I can identify redundant features

---

**US-026: Validate Against Schema**
**As a** Data Engineer
**I want to** validate JSON files against a schema and flag violations
**So that** data quality issues are caught early

---

**US-027: Generate Data Contracts**
**As an** Analytics Engineer
**I want to** generate data contracts (dbt YAML, Great Expectations)
**So that** I can enforce quality rules

---

**US-028: Provide REST API**
**As a** Data Platform Engineer
**I want** REST API access to all dictionary data
**So that** I can build custom integrations

---

**US-029: Visual Schema Diagrams**
**As a** Product Manager
**I want** a visual schema diagram showing relationships
**So that** I can understand complex structures at a glance

---

**US-030: Role-Based Access Control**
**As a** Data Governance Lead
**I want** role-based access control
**So that** sensitive metadata is protected

---

## MVP Scope & Phasing

### Phase 1: MVP (Weeks 1-8)

**Must-Have Features:**
- ✅ JSON file upload (single file)
- ✅ Parse nested JSON (up to 10 levels)
- ✅ Basic data type inference
- ✅ Excel export with formatting
- ✅ Simple web UI (upload → view → export)
- ✅ Field path with dot notation
- ✅ Sample value display (first 10)
- ✅ Manual description editing
- ✅ Null percentage calculation

**User Stories Covered:** US-001, US-002, US-003, US-004, US-009, US-010, US-018

**Success Criteria:**
- Process typical JSON file (1000 fields) in <30 seconds
- Export to Excel in <10 seconds
- Support 100MB file size
- Handle 10-level nesting

---

### Phase 2: Intelligence & Quality (Weeks 9-16)

**Should-Have Features:**
- ✅ Version storage and history
- ✅ Side-by-side version comparison
- ✅ Schema diff with change highlighting
- ✅ AI-generated field descriptions
- ✅ Semantic type inference (email, date, URL)
- ✅ Cardinality metrics
- ✅ Distribution statistics (min, max, mean, median)
- ✅ PII detection
- ✅ Batch file processing

**User Stories Covered:** US-005, US-006, US-007, US-011, US-012, US-013, US-014, US-016, US-022

**Success Criteria:**
- Generate descriptions for 90%+ fields
- Detect PII with 95%+ precision
- Process 100-file batch in <10 minutes
- Accurate semantic type detection (80%+)

---

### Phase 3: Scale & Integration (Weeks 17-24)

**Nice-to-Have Features:**
- ✅ Breaking change detection
- ✅ Full-text search across dictionaries
- ✅ Dataset health reporting
- ✅ Scheduled automation
- ✅ REST API
- ✅ Batch annotation
- ✅ Data catalog integration (DataHub)
- ✅ Visual schema diagrams

**User Stories Covered:** US-008, US-017, US-019, US-021, US-023, US-024, US-028, US-029

**Success Criteria:**
- API handles 100 requests/second
- Search returns results in <500ms
- Successfully sync to DataHub
- Support 1000+ datasets

---

### Phase 4: Advanced Features (Future)

**Future Enhancements:**
- ✅ Lineage tracking (US-020)
- ✅ Correlation analysis (US-025)
- ✅ Schema validation (US-026)
- ✅ Data contract generation (US-027)
- ✅ RBAC (US-030)
- ✅ Collaborative annotations with approval workflows
- ✅ ML-powered anomaly detection
- ✅ Real-time monitoring dashboards

---

## Technical Approach

### Technology Stack

**Frontend:**
- React 18+ with TypeScript
- Material-UI or Ant Design for components
- Redux Toolkit for state management
- React Query for API data fetching
- D3.js or Recharts for visualizations

**Backend:**
- Python 3.11+
- FastAPI for REST API
- SQLAlchemy 2.0 for ORM
- Pydantic for data validation
- Pandas for data analysis
- OpenAI API or local LLM for AI descriptions

**Database:**
- PostgreSQL 15+ with JSONB support
- Redis for caching and job queues
- Alembic for migrations

**Infrastructure:**
- Docker & Docker Compose for local development
- GitHub Actions for CI/CD
- AWS S3 for file storage (future)
- Kubernetes for production deployment (future)

**Key Libraries:**
- `openpyxl` or `xlsxwriter` for Excel generation
- `python-multipart` for file uploads
- `celery` for background jobs (Phase 2+)
- `pytest` for testing

---

### Architecture Patterns

**Backend:**
- Layered architecture (API → Service → Repository)
- Dependency injection with FastAPI
- Repository pattern for data access
- Service layer for business logic

**Frontend:**
- Component-based architecture
- Custom hooks for reusable logic
- Context for global state (auth, theme)
- Feature-based folder structure

**Data Processing:**
- Streaming JSON parser for large files
- Worker pool for batch processing
- Incremental analysis for progressive feedback

---

## Success Metrics

### User Adoption
- **Target:** 80% of data team actively using within 3 months
- **Measure:** Weekly active users, dictionaries generated per week

### Efficiency Gains
- **Target:** 80% reduction in documentation time
- **Measure:** Time to document (before/after), survey feedback

### Data Quality
- **Target:** 50% increase in documented datasets
- **Measure:** # of datasets with documentation, completeness score

### Schema Change Management
- **Target:** Zero production incidents from undocumented schema changes
- **Measure:** Incident reports related to schema changes

### User Satisfaction
- **Target:** NPS score > 50
- **Measure:** Quarterly user surveys, feature request volume

---

## Risks & Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| AI description quality poor | Medium | Medium | Allow manual override, iterate on prompts, provide examples |
| Performance issues with large files | High | Medium | Implement streaming parsing, add file size limits, optimize queries |
| User adoption low | High | Low | Conduct user research, involve users early, provide training |
| Version storage grows too large | Medium | High | Implement retention policies, compress old versions, archive to S3 |
| Integration complexity with catalogs | Medium | Medium | Start with one catalog, use standard APIs, provide webhooks |

---

## Assumptions

1. Users have JSON files accessible locally or in cloud storage
2. JSON files are well-formed and valid
3. Users have basic technical knowledge to upload files
4. Data lake files are primarily JSON (not Parquet, Avro, etc.)
5. OpenAI API or similar LLM service is available for AI features
6. PostgreSQL is acceptable for metadata storage
7. Team has capacity to provide feedback and testing

---

## Dependencies

### External Dependencies
- OpenAI API (or alternative LLM) for AI descriptions
- Data catalog APIs (DataHub, Alation) for integration
- Cloud storage (S3, Azure Blob) for file storage (future)

### Internal Dependencies
- Access to sample JSON files for testing
- User availability for feedback sessions
- Infrastructure/DevOps support for deployment

---

## Glossary

**Data Dictionary:** A structured catalog of data elements, including field names, types, descriptions, and metadata

**Schema Evolution:** The process of tracking changes to data structures over time

**Cardinality:** The number of distinct values in a field

**PII (Personally Identifiable Information):** Data that can identify an individual (email, phone, SSN, etc.)

**Semantic Type:** The meaning or purpose of data beyond its technical type (e.g., email, currency, date)

**Breaking Change:** A schema modification that makes previous versions incompatible (removed fields, type changes)

**Data Lineage:** The tracking of data flow from source to destination, including transformations

**Data Contract:** A formal agreement defining the structure and quality of data between producer and consumer

---

## Appendix A: Sample JSON Structures

### Simple Nested Example
```json
{
  "user": {
    "id": 12345,
    "name": "John Doe",
    "email": "john@example.com",
    "created_at": "2023-01-15T10:30:00Z"
  },
  "order": {
    "order_id": "ORD-2023-001",
    "total": 99.99,
    "items": [
      {
        "sku": "PROD-123",
        "quantity": 2,
        "price": 49.99
      }
    ]
  }
}
```

### Complex Nested Example (5+ levels)
```json
{
  "event": {
    "metadata": {
      "source": {
        "application": {
          "name": "mobile-app",
          "version": "2.3.1",
          "environment": "production"
        },
        "device": {
          "os": "iOS",
          "version": "16.4",
          "identifier": "ABC123"
        }
      },
      "timestamp": "2023-11-08T14:22:33.123Z"
    },
    "payload": {
      "user_action": {
        "type": "purchase",
        "details": {
          "cart": {
            "items": [...]
          }
        }
      }
    }
  }
}
```

---

## Appendix B: Sample Excel Output Format

| Field Path | Data Type | Semantic Type | Description | Sample Values | Null % | Cardinality | PII Flag |
|------------|-----------|---------------|-------------|---------------|--------|-------------|----------|
| user.id | integer | identifier | User unique identifier | 12345, 12346, 12347 | 0% | 1000 | No |
| user.email | string | email | User email address | john@example.com, jane@... | 2% | 998 | Yes |
| order.total | float | currency | Order total amount in USD | 99.99, 149.50, 75.00 | 0% | 856 | No |

---

**Document Control:**
- **Author:** Data Platform Team
- **Reviewers:** Engineering Leadership, Data Governance
- **Next Review Date:** 2025-12-08
- **Version History:**
  - v1.0 (2025-11-08): Initial draft
