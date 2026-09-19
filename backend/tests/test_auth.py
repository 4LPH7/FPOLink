"""Authentication endpoint tests."""

import pytest
from fastapi.testclient import TestClient


class TestRegister:
    def test_register_success(self, client: TestClient):
        response = client.post("/api/auth/register", json={
            "name": "Test User",
            "phone": "9000000001",
            "password": "testpass123",
            "role": "farmer",
            "consent_given": True,
        })
        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_register_duplicate_phone(self, client: TestClient):
        # Register first
        client.post("/api/auth/register", json={
            "name": "First User",
            "phone": "9000000002",
            "password": "testpass123",
            "role": "farmer",
        })
        # Try duplicate
        response = client.post("/api/auth/register", json={
            "name": "Second User",
            "phone": "9000000002",
            "password": "testpass123",
            "role": "farmer",
        })
        assert response.status_code == 409

    def test_register_invalid_role(self, client: TestClient):
        response = client.post("/api/auth/register", json={
            "name": "Bad Role",
            "phone": "9000000003",
            "password": "testpass123",
            "role": "superadmin",
        })
        assert response.status_code == 400


class TestLogin:
    def test_login_success(self, client: TestClient):
        # Register
        client.post("/api/auth/register", json={
            "name": "Login Test",
            "phone": "9000000010",
            "password": "mypassword",
            "role": "admin",
        })
        # Login
        response = client.post("/api/auth/login", json={
            "phone": "9000000010",
            "password": "mypassword",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data

    def test_login_wrong_password(self, client: TestClient):
        client.post("/api/auth/register", json={
            "name": "Wrong Pass",
            "phone": "9000000011",
            "password": "correctpassword",
            "role": "farmer",
        })
        response = client.post("/api/auth/login", json={
            "phone": "9000000011",
            "password": "wrongpassword",
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client: TestClient):
        response = client.post("/api/auth/login", json={
            "phone": "0000000000",
            "password": "whatever",
        })
        assert response.status_code == 401


class TestProtectedRoutes:
    def test_me_authenticated(self, client: TestClient):
        # Register and get token
        reg = client.post("/api/auth/register", json={
            "name": "Auth Me",
            "phone": "9000000020",
            "password": "testpass123",
            "role": "fpo_staff",
        })
        token = reg.json()["access_token"]

        # Access protected endpoint
        response = client.get("/api/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Auth Me"
        assert data["role"] == "fpo_staff"

    def test_me_unauthenticated(self, client: TestClient):
        response = client.get("/api/auth/me")
        assert response.status_code == 403  # No auth header

    def test_me_invalid_token(self, client: TestClient):
        response = client.get("/api/auth/me", headers={
            "Authorization": "Bearer invalid-token-here"
        })
        assert response.status_code == 401


class TestRefresh:
    def test_refresh_token(self, client: TestClient):
        # Register
        reg = client.post("/api/auth/register", json={
            "name": "Refresh Test",
            "phone": "9000000030",
            "password": "testpass123",
            "role": "farmer",
        })
        refresh_token = reg.json()["refresh_token"]

        # Refresh
        response = client.post("/api/auth/refresh", json={
            "refresh_token": refresh_token,
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
