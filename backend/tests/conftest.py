"""Test configuration and fixtures."""

import os
import sys

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Ensure app imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Override DATABASE_URL for tests BEFORE importing app
os.environ["DATABASE_URL"] = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg://fpolink:fpolink@localhost:5432/fpolink_test"
)

from app.config import settings
from app.database import get_db
from app.main import app
from app.models.base import Base

TEST_DATABASE_URL = settings.DATABASE_URL

engine = create_engine(TEST_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Create all tables before tests, drop after."""
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        yield
        return

    yield
    try:
        Base.metadata.drop_all(bind=engine)
    except Exception:
        pass


@pytest.fixture()
def db():
    """Provide a clean database session for each test."""
    try:
        connection = engine.connect()
    except Exception as e:
        pytest.skip(f"Database connection not available: {e}")

    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    def _override_get_db():
        yield session

    app.dependency_overrides[get_db] = _override_get_db
    yield session
    app.dependency_overrides.pop(get_db, None)
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db):
    """Provide a test client using the shared test database session."""
    return TestClient(app)
