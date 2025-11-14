# Data Dictionary Generator - Documentation

Welcome to the comprehensive documentation for the Data Dictionary Generator. This directory contains all technical documentation, guides, and reference materials organized for easy navigation.

## Documentation Structure

```
docs/
├── README.md                              # This file - documentation index
├── deployment/                            # Deployment and infrastructure
│   ├── DOCKER_DEPLOYMENT.md              # Docker deployment guide (SQLite & PostgreSQL)
│   └── PRODUCTION_DEPLOYMENT.md          # Production deployment guide
├── guides/                                # User and developer guides
│   ├── QUICK_START.md                    # Get started in 2 minutes
│   ├── QUICKSTART.md                     # Detailed quickstart tutorial
│   ├── MIGRATION_GUIDE.md                # Database migration procedures
│   ├── SECURITY_QUICKSTART.md            # Security hardening quick guide
│   └── OPENAI_CONFIGURATION.md           # OpenAI/LM Studio integration guide
├── reference/                             # Technical reference docs
│   ├── XML_DTD_XSD_SUPPORT.md            # XML schema support documentation
│   ├── XML_PARSER_HARDENING_SUMMARY.md   # XML security hardening details
│   ├── SECURITY.md                       # Security architecture reference
│   ├── CONOPS.md                         # Concept of operations
│   ├── REQUIREMENTS.md                   # System requirements
│   ├── SOFTWARE_DESIGN.md                # Software architecture
│   ├── CODEBASE_ANALYSIS.md              # Codebase analysis and metrics
│   ├── ANALYSIS_INDEX.md                 # Analysis documentation index
│   ├── ANALYSIS_SUMMARY.txt              # Executive summary of analysis
│   └── ARCHITECTURE_DIAGRAM.txt          # System architecture diagram
└── samples/                               # Sample data documentation
    └── SAMPLE_XML_README.md              # XML sample files guide
```

---

## Quick Navigation

### Getting Started

**New to the project?** Start here:

1. **[Quick Start Guide](guides/QUICK_START.md)** (2 minutes)
   - One-command deployment
   - First-time setup
   - Common commands

2. **[Docker Deployment](deployment/DOCKER_DEPLOYMENT.md)** (Complete Guide)
   - SQLite mode (recommended)
   - PostgreSQL mode (advanced)
   - Configuration options
   - Common operations

3. **[Sample Data](samples/SAMPLE_XML_README.md)**
   - Test with sample XML files
   - Understanding output
   - Progressive testing strategy

### Deployment

**Deploy to production:**

- **[Docker Deployment](deployment/DOCKER_DEPLOYMENT.md)**
  - Quick start (SQLite & PostgreSQL)
  - Container architecture
  - Configuration reference
  - Troubleshooting

- **[Production Deployment](deployment/PRODUCTION_DEPLOYMENT.md)**
  - Deployment architectures
  - Security hardening
  - Performance optimization
  - Monitoring and logging
  - Backup strategies
  - Disaster recovery

### Guides

**Step-by-step guides:**

- **[Quick Start](guides/QUICK_START.md)**
  - One-command start
  - Common commands
  - Basic troubleshooting

- **[Quickstart Tutorial](guides/QUICKSTART.md)**
  - Detailed walkthrough
  - Feature exploration
  - Best practices

- **[OpenAI Configuration](guides/OPENAI_CONFIGURATION.md)**
  - LM Studio integration
  - Timeout & retry settings
  - Cache configuration
  - Cost tracking & metrics

- **[Security Quickstart](guides/SECURITY_QUICKSTART.md)**
  - Security hardening checklist
  - Attack prevention
  - Best practices

- **[Migration Guide](guides/MIGRATION_GUIDE.md)**
  - PostgreSQL ↔ SQLite migration
  - Schema version upgrades
  - Data export/import
  - Rollback procedures

### Technical Reference

**In-depth technical documentation:**

- **[XML DTD/XSD Support](reference/XML_DTD_XSD_SUPPORT.md)**
  - DTD schema parsing
  - XSD validation
  - Metadata extraction
  - Sample files

- **[XML Parser Hardening](reference/XML_PARSER_HARDENING_SUMMARY.md)**
  - Security improvements (XXE/SSRF prevention)
  - Timeout protection
  - Error handling

- **[Security Architecture](reference/SECURITY.md)**
  - Threat model
  - Security controls
  - Authentication/authorization
  - Data protection

- **[Software Design](reference/SOFTWARE_DESIGN.md)**
  - System architecture
  - Component design
  - API specifications
  - Database schema

- **[Codebase Analysis](reference/CODEBASE_ANALYSIS.md)**
  - Code metrics
  - Complexity analysis
  - Security review
  - Recommendations

- **[Requirements](reference/REQUIREMENTS.md)**
  - Functional requirements
  - Non-functional requirements
  - Use cases
  - Acceptance criteria

- **[Concept of Operations](reference/CONOPS.md)**
  - System overview
  - Operational scenarios
  - User workflows
  - Integration patterns

- **[Analysis Summary](reference/ANALYSIS_SUMMARY.txt)**
  - Executive summary
  - Project status
  - Key findings

- **[Architecture Diagram](reference/ARCHITECTURE_DIAGRAM.txt)**
  - System architecture
  - Component relationships
  - Data flow

---

## Documentation by Use Case

### I want to...

#### Deploy the Application

**Development/Testing:**
1. Read [Quick Start](guides/QUICK_START.md)
2. Run `./docker-run-sqlite.sh`
3. Access http://localhost:8000

**Production Deployment:**
1. Read [Production Deployment](deployment/PRODUCTION_DEPLOYMENT.md)
2. Choose deployment architecture
3. Follow security checklist
4. Configure monitoring
5. Set up backups

#### Migrate Between Databases

**PostgreSQL → SQLite:**
1. Read [Migration Guide](guides/MIGRATION_GUIDE.md#postgresql-to-sqlite-migration)
2. Export data via XLSX
3. Switch configuration
4. Import data
5. Verify migration

**SQLite → PostgreSQL:**
1. Read [Migration Guide](guides/MIGRATION_GUIDE.md#sqlite-to-postgresql-migration)
2. Set up PostgreSQL
3. Export/import data
4. Optimize database

#### Process XML Files

**Basic XML:**
1. Upload via web UI
2. System auto-detects structure
3. Review generated dictionary

**XML with Schema (DTD/XSD):**
1. Read [XML DTD/XSD Support](reference/XML_DTD_XSD_SUPPORT.md)
2. Prepare XML with schema
3. Upload file
4. Review extracted metadata

**Test with Samples:**
1. Read [Sample XML README](samples/SAMPLE_XML_README.md)
2. Use provided sample files
3. Progressive testing (simple → complex)

#### Understand the Architecture

1. Read [Software Design](reference/SOFTWARE_DESIGN.md)
2. Review system components
3. Understand data flow
4. Explore API design

#### Configure for Production

1. Read [Docker Deployment - Configuration](deployment/DOCKER_DEPLOYMENT.md#configuration)
2. Copy appropriate `.env.example`
3. Set required variables
4. Configure security settings
5. Set up monitoring

#### Troubleshoot Issues

**Deployment Issues:**
- [Docker Deployment - Troubleshooting](deployment/DOCKER_DEPLOYMENT.md#troubleshooting)
- [Production Deployment - Troubleshooting](deployment/PRODUCTION_DEPLOYMENT.md#troubleshooting)

**Migration Issues:**
- [Migration Guide - Troubleshooting](guides/MIGRATION_GUIDE.md#troubleshooting)

**XML Processing Issues:**
- [Sample XML README - Troubleshooting](samples/SAMPLE_XML_README.md#troubleshooting)

---

## Documentation Categories

### By Audience

#### End Users
- [Quick Start](guides/QUICK_START.md)
- [Sample Data](samples/SAMPLE_XML_README.md)

#### System Administrators
- [Docker Deployment](deployment/DOCKER_DEPLOYMENT.md)
- [Production Deployment](deployment/PRODUCTION_DEPLOYMENT.md)
- [Migration Guide](guides/MIGRATION_GUIDE.md)

#### Developers
- [Software Design](reference/SOFTWARE_DESIGN.md)
- [Requirements](reference/REQUIREMENTS.md)
- [XML DTD/XSD Support](reference/XML_DTD_XSD_SUPPORT.md)

#### Architects
- [Concept of Operations](reference/CONOPS.md)
- [Software Design](reference/SOFTWARE_DESIGN.md)
- [Production Deployment](deployment/PRODUCTION_DEPLOYMENT.md)

### By Topic

#### Deployment
- [Quick Start](guides/QUICK_START.md) - Fastest deployment
- [Docker Deployment](deployment/DOCKER_DEPLOYMENT.md) - Complete Docker guide
- [Production Deployment](deployment/PRODUCTION_DEPLOYMENT.md) - Enterprise deployment

#### Configuration
- [Docker Deployment - Configuration](deployment/DOCKER_DEPLOYMENT.md#configuration)
- [Production Deployment - Pre-Deployment Checklist](deployment/PRODUCTION_DEPLOYMENT.md#pre-deployment-checklist)

#### Data Processing
- [Sample XML README](samples/SAMPLE_XML_README.md)
- [XML DTD/XSD Support](reference/XML_DTD_XSD_SUPPORT.md)

#### Database Management
- [Migration Guide](guides/MIGRATION_GUIDE.md)
- [Production Deployment - Backup Strategies](deployment/PRODUCTION_DEPLOYMENT.md#backup-strategies)

#### Security
- [Docker Deployment - Security Hardening](deployment/DOCKER_DEPLOYMENT.md#security-hardening)
- [Production Deployment - Security Hardening](deployment/PRODUCTION_DEPLOYMENT.md#security-hardening)

#### Monitoring
- [Docker Deployment - Monitoring](deployment/DOCKER_DEPLOYMENT.md#monitoring-and-health-checks)
- [Production Deployment - Monitoring and Logging](deployment/PRODUCTION_DEPLOYMENT.md#monitoring-and-logging)

---

## Quick Reference

### Common Tasks

| Task | Documentation | Command |
|------|--------------|---------|
| **Deploy (SQLite)** | [Quick Start](guides/QUICK_START.md) | `./docker-run-sqlite.sh` |
| **Deploy (PostgreSQL)** | [Docker Deployment](deployment/DOCKER_DEPLOYMENT.md#postgresql-mode) | `./docker-run-postgres.sh` |
| **Backup SQLite** | [Docker Deployment](deployment/DOCKER_DEPLOYMENT.md#backup-and-restore) | `cp ./data/app.db backup.db` |
| **Backup PostgreSQL** | [Docker Deployment](deployment/DOCKER_DEPLOYMENT.md#backup-and-restore) | `pg_dump > backup.sql` |
| **View Logs** | [Docker Deployment](deployment/DOCKER_DEPLOYMENT.md#viewing-logs) | `docker-compose logs -f app` |
| **Migrate DB** | [Migration Guide](guides/MIGRATION_GUIDE.md) | See guide |

### Key Concepts

**Deployment Modes:**
- **SQLite**: Single-file database, zero config, perfect for <5 users
- **PostgreSQL**: Production database, concurrent access, enterprise features

**Container Architecture:**
- **Single Container**: Frontend (React) + Backend (FastAPI) + Database access
- **Multi-Stage Build**: Optimized image size (~300-400MB)
- **Automatic Migrations**: Runs on startup

**Data Formats Supported:**
- JSON (including MongoDB Extended JSON)
- XML (with DTD/XSD schema support)
- SQLite databases
- GeoPackage files
- Protocol Buffers (.proto, .desc)

---

## Documentation Standards

### Cross-References

All documentation uses relative paths for cross-references:
- From `docs/`: Use relative paths like `./deployment/DOCKER_DEPLOYMENT.md`
- From subdirectories: Use `../` to navigate up
- To root: Use `../../README.md`

### Maintenance

**Last Updated**: 2025-11-12

**Review Schedule**:
- Quick Start: Monthly
- Deployment Guides: Quarterly
- Technical Reference: As needed with releases

**Contributing**:
- Keep documentation in sync with code
- Update cross-references when moving files
- Test all code examples before committing
- Use clear, concise language
- Include examples and use cases

---

## External Resources

### Official Documentation
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)
- [Docker Documentation](https://docs.docker.com/)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)

### Related Tools
- [Alembic (Migrations)](https://alembic.sqlalchemy.org/)
- [SQLAlchemy (ORM)](https://www.sqlalchemy.org/)
- [Pydantic (Validation)](https://docs.pydantic.dev/)

---

## Getting Help

### Documentation Issues

If you find errors or gaps in documentation:
1. Check if information exists in another document
2. Search for keywords across all files
3. Open a GitHub issue with:
   - Document name
   - Section reference
   - What's missing/incorrect
   - Suggested improvement

### Technical Support

For technical issues:
1. Check [Troubleshooting sections](#troubleshoot-issues)
2. Review relevant documentation
3. Check application logs
4. Open GitHub issue with:
   - Deployment mode (SQLite/PostgreSQL)
   - Error messages
   - Steps to reproduce
   - Environment details

---

## Document History

### Recent Changes

**2025-11-12**: Documentation reorganization
- Consolidated Docker deployment documentation
- Organized into logical directories
- Created comprehensive index (this file)
- Updated all cross-references
- Added quick navigation sections

### Previous Structure

Root-level documentation files (now organized):
- `DEPLOYMENT.md` → `docs/deployment/PRODUCTION_DEPLOYMENT.md`
- `DOCKER_BUILD_SUMMARY.md` → Consolidated into `DOCKER_DEPLOYMENT.md`
- `DOCKER_DEPLOYMENT.md` → `docs/deployment/DOCKER_DEPLOYMENT.md`
- `DOCKER_DEPLOYMENT_REVIEW.md` → Consolidated into `DOCKER_DEPLOYMENT.md`
- `MIGRATION_GUIDE.md` → `docs/guides/MIGRATION_GUIDE.md`
- `QUICK_START.md` → `docs/guides/QUICK_START.md`
- `SAMPLE_XML_README.md` → `docs/samples/SAMPLE_XML_README.md`
- `XML_DTD_XSD_SUPPORT.md` → `docs/reference/XML_DTD_XSD_SUPPORT.md`

---

**Happy documenting! 📚**

For questions or suggestions, please open a GitHub issue or submit a pull request.
