"""Unit tests for authentication and authorization dependencies in app.api.deps."""

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import jwt
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.api.deps import get_current_user, require_role
from app.config import settings
from app.database import get_db
from app.models.user import User, UserRole
from app.services.jwt import ALGORITHM, create_access_token


def create_test_app():
    test_app = FastAPI()

    @test_app.get("/test/user")
    def test_user_endpoint(user: User = Depends(get_current_user)):
        return {"id": str(user.id), "phone": user.phone}

    @test_app.get("/test/admin-only")
    def test_admin_endpoint(user: User = Depends(require_role(["admin"]))):
        return {
            "id": str(user.id),
            "role": user.role.value if hasattr(user.role, "value") else str(user.role),
        }

    return test_app


def test_unauthenticated_request_returns_401():
    app = create_test_app()
    client = TestClient(app)

    response = client.get("/test/user")
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"
    assert response.json()["detail"] == "Not authenticated"


def test_invalid_token_returns_401():
    app = create_test_app()
    client = TestClient(app)

    response = client.get("/test/user", headers={"Authorization": "Bearer not-a-real-token"})
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"
    assert response.json()["detail"] == "Invalid or expired token"


def test_expired_token_returns_401():
    app = create_test_app()
    client = TestClient(app)

    expired_time = datetime.now(timezone.utc) - timedelta(hours=1)
    token = jwt.encode(
        {"sub": str(uuid.uuid4()), "role": "admin", "exp": expired_time, "type": "access"},
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )

    response = client.get("/test/user", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"


def test_wrong_token_type_returns_401():
    app = create_test_app()
    client = TestClient(app)

    valid_time = datetime.now(timezone.utc) + timedelta(hours=1)
    token = jwt.encode(
        {"sub": str(uuid.uuid4()), "role": "admin", "exp": valid_time, "type": "refresh"},
        settings.SECRET_KEY,
        algorithm=ALGORITHM,
    )

    response = client.get("/test/user", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token type"


def test_require_role_unauthenticated_returns_401():
    app = create_test_app()
    client = TestClient(app)

    # Missing credentials must return 401, not 403
    response = client.get("/test/admin-only")
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Bearer"


def test_require_role_insufficient_permission_returns_403():
    app = create_test_app()
    user_id = uuid.uuid4()
    mock_user = MagicMock(spec=User)
    mock_user.id = user_id
    mock_user.is_active = True
    mock_user.role = UserRole.FARMER
    mock_user.phone = "9876543210"

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    app.dependency_overrides[get_db] = lambda: mock_db
    client = TestClient(app)

    token = create_access_token(user_id, "farmer")
    response = client.get("/test/admin-only", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 403
    assert "not authorized" in response.json()["detail"]


def test_require_role_authorized_returns_200():
    app = create_test_app()
    user_id = uuid.uuid4()
    mock_user = MagicMock(spec=User)
    mock_user.id = user_id
    mock_user.is_active = True
    mock_user.role = UserRole.ADMIN
    mock_user.phone = "9876543210"

    mock_db = MagicMock()
    mock_db.query.return_value.filter.return_value.first.return_value = mock_user

    app.dependency_overrides[get_db] = lambda: mock_db
    client = TestClient(app)

    token = create_access_token(user_id, "admin")
    response = client.get("/test/admin-only", headers={"Authorization": f"Bearer {token}"})

    assert response.status_code == 200
    assert response.json()["role"] == "admin"
