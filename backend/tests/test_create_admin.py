"""Unit tests for create_admin.py script."""

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.models.base import Base
from app.models.fpo import FPO
from app.models.user import UserRole
from app.services.auth import verify_password
from scripts.create_admin import create_or_update_admin


@pytest.fixture
def mock_db(monkeypatch):
    """Provide isolated in-memory SQLite database for create_admin tests."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSession = sessionmaker(bind=engine)

    monkeypatch.setattr("scripts.create_admin.SessionLocal", TestingSession)
    yield TestingSession
    Base.metadata.drop_all(bind=engine)


def test_create_admin_creates_fpo_and_user(mock_db):
    user = create_or_update_admin(
        phone="8072845239",
        password="SuperSecretPassword@123",
        name="Chief Admin",
        fpo_name="Erode Farmers Collective",
    )

    assert user.phone == "8072845239"
    assert user.name == "Chief Admin"
    assert user.role == UserRole.ADMIN
    assert user.is_active is True
    assert user.password_change_required is False
    assert verify_password("SuperSecretPassword@123", user.hashed_password) is True
    assert user.fpo_id is not None

    db = mock_db()
    fpo = db.query(FPO).filter(FPO.id == user.fpo_id).first()
    assert fpo is not None
    assert fpo.name == "Erode Farmers Collective"
    db.close()


def test_create_admin_idempotent_update(mock_db):
    # First creation
    u1 = create_or_update_admin(
        phone="8072845239",
        password="InitialPassword@123",
        name="Admin One",
    )
    assert u1.name == "Admin One"
    assert verify_password("InitialPassword@123", u1.hashed_password) is True

    # Second execution: updates password and name
    u2 = create_or_update_admin(
        phone="8072845239",
        password="UpdatedPassword@456",
        name="Admin Updated",
        must_change_password=True,
    )
    assert u2.id == u1.id
    assert u2.name == "Admin Updated"
    assert u2.password_change_required is True
    assert verify_password("UpdatedPassword@456", u2.hashed_password) is True
    assert verify_password("InitialPassword@123", u2.hashed_password) is False


def test_create_admin_invalid_phone(mock_db):
    with pytest.raises(ValueError, match="Invalid phone number format"):
        create_or_update_admin(phone="123", password="Password@123")


def test_create_admin_short_password(mock_db):
    with pytest.raises(ValueError, match="Password must be at least 8 characters"):
        create_or_update_admin(phone="8072845239", password="short")
