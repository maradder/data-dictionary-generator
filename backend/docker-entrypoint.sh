#!/bin/sh
# ==============================================================================
# Docker Entrypoint Script
# ==============================================================================
# This script runs database migrations and starts the application
# ==============================================================================

set -e  # Exit on error

echo "=========================================="
echo "Data Dictionary Generator - Starting"
echo "=========================================="
echo ""

# Auto-detect database type from URL
if echo "${DATABASE_URL}" | grep -q "postgresql"; then
    DETECTED_DB_TYPE="postgresql"
else
    DETECTED_DB_TYPE="sqlite"
fi

# Print configuration
echo "Configuration:"
echo "  Database Type: ${DETECTED_DB_TYPE}"
echo "  Database URL: ${DATABASE_URL}"
echo "  Environment: ${ENVIRONMENT:-development}"
echo "  Log Level: ${LOG_LEVEL:-INFO}"
echo ""

# Wait for PostgreSQL if using it
if [ "${DETECTED_DB_TYPE}" = "postgresql" ]; then
    echo "Waiting for PostgreSQL to be ready..."

    # Extract host and port from DATABASE_URL
    # Format: postgresql://user:pass@host:port/db
    DB_HOST=$(echo "$DATABASE_URL" | sed -n 's/.*@\([^:]*\):.*/\1/p')
    DB_PORT=$(echo "$DATABASE_URL" | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')

    # Default values if extraction fails
    DB_HOST=${DB_HOST:-postgres}
    DB_PORT=${DB_PORT:-5432}

    # Wait for PostgreSQL to be ready (max 60 seconds)
    COUNTER=0
    MAX_TRIES=60

    until pg_isready -h "$DB_HOST" -p "$DB_PORT" > /dev/null 2>&1 || [ $COUNTER -eq $MAX_TRIES ]; do
        COUNTER=$((COUNTER + 1))
        echo "Waiting for PostgreSQL... ($COUNTER/$MAX_TRIES)"
        sleep 1
    done

    if [ $COUNTER -eq $MAX_TRIES ]; then
        echo "✗ PostgreSQL failed to become ready in time!"
        exit 1
    fi

    echo "✓ PostgreSQL is ready!"
fi

# Run database migrations with rollback on failure
echo ""
echo "Running database migrations..."

# Get current migration version before upgrade
CURRENT_VERSION=$(alembic current 2>/dev/null | grep -oE '[a-f0-9]+' | head -1 || echo "none")
echo "Current migration version: ${CURRENT_VERSION}"

# Run migrations
if alembic upgrade head 2>&1 | tee /tmp/migration.log; then
    echo "✓ Migrations completed successfully"
else
    echo "✗ Migration failed!"
    echo ""
    echo "Migration error details:"
    cat /tmp/migration.log
    echo ""

    if [ "${CURRENT_VERSION}" != "none" ]; then
        echo "Attempting to rollback to previous version: ${CURRENT_VERSION}"
        if alembic downgrade "${CURRENT_VERSION}" 2>/dev/null; then
            echo "✓ Rollback successful"
        else
            echo "✗ Rollback failed - database may be in inconsistent state"
        fi
    fi

    exit 1
fi

# Start the application
echo ""
echo "Starting FastAPI application..."
echo "=========================================="
echo ""

# Convert LOG_LEVEL to lowercase for uvicorn
LOG_LEVEL_LOWER=$(echo "${LOG_LEVEL:-INFO}" | tr '[:upper:]' '[:lower:]')

# Trap SIGTERM and SIGINT for graceful shutdown
trap 'echo "Received shutdown signal, gracefully stopping..."; kill -TERM $PID; wait $PID' TERM INT

# Start uvicorn in background to handle signals properly
uvicorn src.main:app \
    --host 0.0.0.0 \
    --port 8000 \
    --log-level "$LOG_LEVEL_LOWER" &

PID=$!
wait $PID
