# Community 25

> 19 nodes · cohesion 0.19

## Key Concepts

- **User** (47 connections) — `backend/app/models/user.py`
- **test_auth_deps.py** (25 connections) — `backend/tests/test_auth_deps.py`
- **create_test_app()** (12 connections) — `backend/tests/test_auth_deps.py`
- **require_role()** (10 connections) — `backend/app/api/deps.py`
- **create_access_token()** (10 connections) — `backend/app/services/jwt.py`
- **test_require_role_authorized_returns_200()** (5 connections) — `backend/tests/test_auth_deps.py`
- **test_require_role_insufficient_permission_returns_403()** (5 connections) — `backend/tests/test_auth_deps.py`
- **test_expired_token_returns_401()** (2 connections) — `backend/tests/test_auth_deps.py`
- **test_invalid_token_returns_401()** (2 connections) — `backend/tests/test_auth_deps.py`
- **test_require_role_unauthenticated_returns_401()** (2 connections) — `backend/tests/test_auth_deps.py`
- **test_unauthenticated_request_returns_401()** (2 connections) — `backend/tests/test_auth_deps.py`
- **test_wrong_token_type_returns_401()** (2 connections) — `backend/tests/test_auth_deps.py`
- **Dependency factory: restrict endpoint to specific roles.** (1 connections) — `backend/app/api/deps.py`
- **role_checker()** (1 connections) — `backend/app/api/deps.py`
- **Base** (1 connections)
- **Create a short-lived access token.** (1 connections) — `backend/app/services/jwt.py`
- **test_admin_endpoint()** (1 connections) — `backend/tests/test_auth_deps.py`
- **test_user_endpoint()** (1 connections) — `backend/tests/test_auth_deps.py`
- **Unit tests for authentication and authorization dependencies in app.api.deps.** (1 connections) — `backend/tests/test_auth_deps.py`

## Relationships

- [Community 7](Community_7.md) (11 shared connections)
- [Community 35](Community_35.md) (8 shared connections)
- [Community 19](Community_19.md) (8 shared connections)
- [Community 5](Community_5.md) (6 shared connections)
- [Community 15](Community_15.md) (6 shared connections)
- [Community 10](Community_10.md) (5 shared connections)
- [Community 16](Community_16.md) (5 shared connections)
- [Community 2](Community_2.md) (5 shared connections)
- [Community 4](Community_4.md) (2 shared connections)
- [Community 32](Community_32.md) (2 shared connections)
- [Community 8](Community_8.md) (2 shared connections)
- [Community 9](Community_9.md) (2 shared connections)

## Source Files

- `backend/app/api/deps.py`
- `backend/app/models/user.py`
- `backend/app/services/jwt.py`
- `backend/tests/test_auth_deps.py`

## Audit Trail

- EXTRACTED: 68 (69%)
- INFERRED: 31 (31%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*