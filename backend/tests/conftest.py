"""Pytest configuration and shared fixtures."""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.core.config import settings
from src.models.base import Base


@pytest.fixture(scope="session")
def test_engine():
    """Create test database engine."""
    # Use in-memory SQLite for tests
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def test_db(test_engine):
    """Create test database session."""
    TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)
    session = TestSessionLocal()
    yield session
    session.close()


@pytest.fixture
def sample_json_data():
    """Sample JSON data for testing."""
    return {
        "users": [
            {
                "id": 1,
                "name": "John Doe",
                "email": "john@example.com",
                "age": 30,
                "address": {
                    "street": "123 Main St",
                    "city": "New York",
                    "zip": "10001"
                }
            },
            {
                "id": 2,
                "name": "Jane Smith",
                "email": "jane@example.com",
                "age": 25,
                "address": {
                    "street": "456 Oak Ave",
                    "city": "Boston",
                    "zip": "02101"
                }
            }
        ]
    }
