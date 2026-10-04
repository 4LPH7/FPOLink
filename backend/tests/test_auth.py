"""Authentication endpoint tests."""

from fastapi.testclient import TestClient


class TestRegister:
    def test_register_success(self, client: TestClient):
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Test User",
                "phone": "9000000001",
                "password": "testpass123",
                "role": "farmer",
                "consent_given": True,
            },
        )
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_register_duplicate_phone(self, client: TestClient):
        # Register first
        client.post(
            "/api/auth/register",
            json={
                "name": "First User",
                "phone": "9000000002",
                "password": "testpass123",
                "role": "farmer",
            },
        )
        # Try duplicate
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Second User",
                "phone": "9000000002",
                "password": "testpass123",
                "role": "farmer",
            },
        )
        assert response.status_code == 409

    def test_register_invalid_role(self, client: TestClient):
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Bad Role",
                "phone": "9000000003",
                "password": "testpass123",
                "role": "superadmin",
            },
        )
        assert response.status_code == 422

    def test_public_registration_cannot_assign_privileged_role(self, client: TestClient):
        response = client.post(
            "/api/auth/register",
            json={
                "name": "Escalation",
                "phone": "9000000004",
                "password": "testpass123",
                "role": "admin",
            },
        )
        assert response.status_code == 422


class TestLogin:
    def test_login_success(self, client: TestClient):
        # Register
        client.post(
            "/api/auth/register",
            json={
                "name": "Login Test",
                "phone": "9000000010",
                "password": "mypassword",
                "role": "farmer",
            },
        )
        # Login
        response = client.post(
            "/api/auth/login",
            json={
                "phone": "9000000010",
                "password": "mypassword",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_login_wrong_password(self, client: TestClient):
        client.post(
            "/api/auth/register",
            json={
                "name": "Wrong Pass",
                "phone": "9000000011",
                "password": "correctpassword",
                "role": "farmer",
            },
        )
        response = client.post(
            "/api/auth/login",
            json={
                "phone": "9000000011",
                "password": "wrongpassword",
            },
        )
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client: TestClient):
        response = client.post(
            "/api/auth/login",
            json={
                "phone": "0000000000",
                "password": "whatever",
            },
        )
        assert response.status_code == 401


class TestProtectedRoutes:
    def test_me_authenticated(self, client: TestClient):
        # Register and get token
        reg = client.post(
            "/api/auth/register",
            json={
                "name": "Auth Me",
                "phone": "9000000020",
                "password": "testpass123",
                "role": "farmer",
            },
        )
        token = reg.json()["access_token"]

        # Access protected endpoint
        response = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Auth Me"
        assert data["role"] == "farmer"

    def test_me_unauthenticated(self, client: TestClient):
        response = client.get("/api/auth/me")
        assert response.status_code == 401  # No auth header -> 401 Unauthorized

    def test_me_invalid_token(self, client: TestClient):
        response = client.get(
            "/api/auth/me", headers={"Authorization": "Bearer invalid-token-here"}
        )
        assert response.status_code == 401


class TestRefresh:
    def test_refresh_token(self, client: TestClient):
        # Register
        reg = client.post(
            "/api/auth/register",
            json={
                "name": "Refresh Test",
                "phone": "9000000030",
                "password": "testpass123",
                "role": "farmer",
            },
        )
        refresh_token = reg.json()["refresh_token"]

        # Refresh
        response = client.post(
            "/api/auth/refresh",
            json={
                "refresh_token": refresh_token,
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data


class TestRequiredPasswordChange:
    def test_staff_must_change_password_before_access(self, client: TestClient, db):
        import uuid

        from app.models.user import User, UserRole
        from app.services.auth import hash_password

        phone = f"8{uuid.uuid4().int % 1_000_000_000:09d}"
        user = User(
            name="Temporary Admin",
            phone=phone,
            role=UserRole.ADMIN,
            hashed_password=hash_password("temporary-admin-password"),
            password_change_required=True,
            is_active=True,
        )
        db.add(user)
        db.commit()

        login = client.post(
            "/api/auth/login",
            json={"phone": phone, "password": "temporary-admin-password"},
        )
        assert login.status_code == 200
        challenge = login.json()
        assert challenge["password_change_required"] is True
        assert challenge.get("refresh_token") is None
        challenge_headers = {"Authorization": f"Bearer {challenge['access_token']}"}

        # The restricted token cannot be used as a normal access token.
        assert client.get("/api/auth/me", headers=challenge_headers).status_code == 401

        wrong_password = client.post(
            "/api/auth/change-password",
            headers=challenge_headers,
            json={
                "current_password": "incorrect-password",
                "new_password": "a-new-secure-password",
            },
        )
        assert wrong_password.status_code == 401

        changed = client.post(
            "/api/auth/change-password",
            headers=challenge_headers,
            json={
                "current_password": "temporary-admin-password",
                "new_password": "a-new-secure-password",
            },
        )
        assert changed.status_code == 200
        session = changed.json()
        assert session["password_change_required"] is False
        assert session["refresh_token"]
        user_headers = {"Authorization": f"Bearer {session['access_token']}"}
        profile = client.get("/api/auth/me", headers=user_headers)
        assert profile.status_code == 200
        assert profile.json()["password_change_required"] is False

        old_password_login = client.post(
            "/api/auth/login",
            json={"phone": phone, "password": "temporary-admin-password"},
        )
        assert old_password_login.status_code == 401

        new_password_login = client.post(
            "/api/auth/login",
            json={"phone": phone, "password": "a-new-secure-password"},
        )
        assert new_password_login.status_code == 200
        assert new_password_login.json()["password_change_required"] is False

    def test_change_password_rejects_normal_access_token(self, client: TestClient):
        registration = client.post(
            "/api/auth/register",
            json={
                "name": "Farmer Password Test",
                "phone": "9000000040",
                "password": "testpass123",
            },
        )
        response = client.post(
            "/api/auth/change-password",
            headers={"Authorization": f"Bearer {registration.json()['access_token']}"},
            json={
                "current_password": "testpass123",
                "new_password": "a-new-secure-password",
            },
        )
        assert response.status_code == 401

    def test_change_password_rejects_short_new_password(self, client: TestClient, db):
        import uuid

        from app.models.user import User, UserRole
        from app.services.auth import hash_password
        from app.services.jwt import create_password_change_token

        user = User(
            name="Short Password Admin",
            phone=f"7{uuid.uuid4().int % 1_000_000_000:09d}",
            role=UserRole.ADMIN,
            hashed_password=hash_password("temporary-admin-password"),
            password_change_required=True,
            is_active=True,
        )
        db.add(user)
        db.commit()
        token = create_password_change_token(user.id)
        response = client.post(
            "/api/auth/change-password",
            headers={"Authorization": f"Bearer {token}"},
            json={"current_password": "temporary-admin-password", "new_password": "short"},
        )
        assert response.status_code == 422
