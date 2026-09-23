# Community 19

> 24 nodes · cohesion 0.16

## Key Concepts

- **api/auth.py** (29 connections) — `backend/app/api/auth.py`
- **login()** (10 connections) — `backend/app/api/auth.py`
- **refresh()** (10 connections) — `backend/app/api/auth.py`
- **register()** (10 connections) — `backend/app/api/auth.py`
- **schemas/auth.py** (9 connections) — `backend/app/schemas/auth.py`
- **services/auth.py** (8 connections) — `backend/app/services/auth.py`
- **hash_password()** (8 connections) — `backend/app/services/auth.py`
- **TokenResponse** (6 connections) — `backend/app/schemas/auth.py`
- **BaseModel** (5 connections)
- **LoginRequest** (4 connections) — `backend/app/schemas/auth.py`
- **RefreshRequest** (4 connections) — `backend/app/schemas/auth.py`
- **RegisterRequest** (4 connections) — `backend/app/schemas/auth.py`
- **UserResponse** (4 connections) — `backend/app/schemas/auth.py`
- **verify_password()** (4 connections) — `backend/app/services/auth.py`
- **Session** (3 connections)
- **Authentication endpoints — register, login, refresh.** (1 connections) — `backend/app/api/auth.py`
- **Authenticate user and return JWT tokens.** (1 connections) — `backend/app/api/auth.py`
- **Get new access token using refresh token.** (1 connections) — `backend/app/api/auth.py`
- **Auth request/response schemas.** (1 connections) — `backend/app/schemas/auth.py`
- **Authentication service — password hashing with Argon2 via pwdlib.** (1 connections) — `backend/app/services/auth.py`
- **Hash a password using Argon2id.** (1 connections) — `backend/app/services/auth.py`
- **Verify a password against its Argon2id hash.** (1 connections) — `backend/app/services/auth.py`
- **pwdlib** (1 connections)
- **pwdlib_hashers_argon2** (1 connections)

## Relationships

- [Community 35](Community_35.md) (9 shared connections)
- [Community 25](Community_25.md) (8 shared connections)
- [Community 15](Community_15.md) (5 shared connections)
- [Community 10](Community_10.md) (4 shared connections)
- [Community 9](Community_9.md) (3 shared connections)
- [Community 11](Community_11.md) (3 shared connections)
- [Community 7](Community_7.md) (3 shared connections)
- [Community 47](Community_47.md) (2 shared connections)
- [Community 2](Community_2.md) (1 shared connections)
- [Community 8](Community_8.md) (1 shared connections)

## Source Files

- `backend/app/api/auth.py`
- `backend/app/schemas/auth.py`
- `backend/app/services/auth.py`

## Audit Trail

- EXTRACTED: 72 (87%)
- INFERRED: 11 (13%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*