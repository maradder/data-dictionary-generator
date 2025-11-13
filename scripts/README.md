# Scripts Directory

This directory contains utility scripts for development, testing, and deployment.

## Directory Structure

```
scripts/
├── docker/          # Docker-related helper scripts
├── testing/         # Ad-hoc testing scripts
└── run-semgrep.sh   # Security scanning script
```

## Docker Scripts (`docker/`)

Helper scripts for Docker operations:

- **`docker-build.sh`** - Build Docker images
- **`docker-run-postgres.sh`** - Run application with PostgreSQL backend
- **`docker-run-sqlite.sh`** - Run application with SQLite backend

### Usage

```bash
# Build Docker images
./scripts/docker/docker-build.sh

# Run with PostgreSQL
./scripts/docker/docker-run-postgres.sh

# Run with SQLite
./scripts/docker/docker-run-sqlite.sh
```

## Testing Scripts (`testing/`)

Ad-hoc test scripts for manual testing and validation:

- **`test_batch_api.py`** - Test batch API operations
- **`test_batch_export.py`** - Test batch export functionality
- **`test_protobuf_parser.py`** - Test Protocol Buffer parsing
- **`test_xml_sample.py`** - Test XML parsing

**Note:** These are manual test scripts. For automated unit tests, see:
- Backend tests: `backend/tests/`
- Frontend tests: `frontend/tests/` (if applicable)

### Usage

```bash
# Run from project root
python scripts/testing/test_batch_api.py
python scripts/testing/test_protobuf_parser.py
```

## Security Scripts

- **`run-semgrep.sh`** - Run Semgrep security scanning

```bash
./scripts/run-semgrep.sh
```

## Best Practices

1. **Keep scripts executable**: Use `chmod +x script.sh` for shell scripts
2. **Document scripts**: Add comments explaining what the script does
3. **Use relative paths**: Scripts should work from the project root
4. **Error handling**: Scripts should handle errors gracefully
5. **Version control**: Commit scripts that others will need

## Adding New Scripts

When adding new scripts:

1. Choose the appropriate subdirectory (or create a new one)
2. Make the script executable: `chmod +x your-script.sh`
3. Add documentation to this README
4. Test the script from the project root directory
