# Phase M4: Tenant Isolation & Production Security Audits — Context & Locked Decisions

> **Milestone:** M-Series MVP Sprint / Phase M4  
> **Topic:** Tenant Isolation, Role-Based Access Control, Production Authentication & Security Hardening  
> **Status:** Locked & Approved  

---

## 1. Goal & Objectives

Establish uncompromising, defense-in-depth tenant isolation and production security verification across FPOLink TN:
1. **Enforce Backend Scoping Everywhere**: Ensure that authorization is enforced strictly by the backend for every operation, regardless of what the frontend UI hides or renders.
2. **Prevent Cross-FPO Boundary Violations**: Ensure an FPO user cannot read, query, create, update, or delete another FPO's records (farmers, harvests, tasks, buyers, requirements, matches).
3. **Strict District Admin Boundaries**: Ensure District Administrators can only inspect and manage FPOs and resources within their assigned `district_id`, and are strictly blocked (HTTP 403) from accessing records outside their district.
4. **Tenant-Safe Bulk & Export Operations**: Guarantee that bulk CSV imports, exports, and multi-record queries strictly honor tenant scoping and forbid cross-tenant injection.
5. **Rigorous Token & Credential Lifecycle**: Ensure expired tokens, signature-tampered tokens, and restricted `password_change` tokens cannot access protected business resources; verify that required password rotation cannot be bypassed.
6. **Hardened Administrator Provisioning**: Enforce password strength, Argon2id hashing, and mandatory rotation defaults during initial bootstrap via CLI.
7. **Scoped CORS Origin Defense**: Enforce explicit trusted origins for production deployments, rejecting overly broad wildcard origins while retaining controlled preview regexes.

---

## 2. Threat Model & Key Audit Vectors

| Threat Vector | Description | Defense Implementation |
|---|---|---|
| **Cross-FPO Data Mutation** | Staff user from FPO A attempts to update or delete a farmer, task, or buyer in FPO B. | Resource ownership check against `current_user.fpo_id`; reject with HTTP 403 or 404. |
| **District Admin Privilege Leakage** | District Administrator of District X tries to view or manage FPOs/farmers in District Y. | DB-aware `verify_fpo_access` and `_enforce_farmer_fpo_scope` verifying `fpo.district_id == current_user.district_id`. |
| **Bypassing Password Rotation** | Bootstrapped admin attempts to access management endpoints using initial temporary token. | `get_current_user` rejects any user with `password_change_required=True` (HTTP 403). `get_password_change_user` accepts only `password_change` token type. |
| **Token Forgery & Expiration** | Attacker uses expired token, bad secret key signature, or tampered claims. | `decode_token` validates cryptographic signature, expiration timestamp (`exp`), and token type claim (`type`). |
| **Bulk Import Tenant Injection** | FPO staff submits CSV to `/buyers/import-csv` specifying another FPO's UUID in the query or body. | Explicit backend validation enforcing `fpo_id == current_user.fpo_id`. |
| **CORS Origin Hijacking** | Third-party website attempts to make authenticated credentialed requests to FPOLink API. | Explicit origin matching; regex restricted to official `fpolink(-[a-z0-9-]+)?\.vercel\.app` domain; no wildcard `*` allowed in production. |

---

## 3. Locked Architectural Decisions

### Decision 1: Database-Aware `verify_fpo_access`
Upgrade `verify_fpo_access(target_fpo_id: UUID, current_user: User, db: Optional[Session] = None) -> bool`:
- Statewide super-roles (`admin`, `state_admin`, `data_operator`, `analyst`) retain statewide read/write permissions.
- FPO-scoped roles (`fpo_admin`, `fpo_staff`, `field_agent`) must match `str(current_user.fpo_id) == str(target_fpo_id)`.
- District administrators (`district_admin`):
  - Must have `current_user.district_id` defined.
  - When `db` is provided, look up `target_fpo = db.query(FPO).filter(FPO.id == target_fpo_id).first()`.
  - Validate that `target_fpo.district_id == current_user.district_id` (or matching district name as fallback).
  - Return `False` if the target FPO is outside the administrator's district.

### Decision 2: District Admin Route Scoping
1. **Farmers**: Update `_enforce_farmer_fpo_scope` and endpoint role lists to include `district_admin`. Allow access if the farmer's FPO is within the admin's district; raise HTTP 403 if in another district.
2. **Tasks**: Update `_scoped(db, user)` so that `district_admin` queries all tasks belonging to FPOs in `user.district_id`. Add `district_admin` to `STAFF_ROLES`.
3. **Harvests**: Update `_enforce_harvest_scope` and `get_harvest_aggregation` to authorize `district_admin` within their district and block cross-district queries.
4. **FPOs**: `list_all` filters FPOs to `current_user.district_id` for `district_admin`. `get_one` verifies district matching.
5. **Demand & Matching**: In `candidates/{requirement_id}`, enforce `verify_fpo_access(req.fpo_id, current_user, db)`.

### Decision 3: Bulk Import & Tenant Boundaries
- In `/buyers/import-csv`, enforce that non-global users can only import for their own assigned `fpo_id`. For `district_admin`, enforce that `fpo_id` belongs to their district.
- In `/api/prices/upload-csv`, enforce authentication and operator/admin roles.

### Decision 4: Production Bootstrap Security Standards
In `backend/scripts/create_admin.py`:
- In production (`ENVIRONMENT == "production"`), enforce minimum 12-character password complexity (rejecting dictionary phrases or common defaults).
- Default `must_change_password=True` in production if `ADMIN_MUST_CHANGE_PASSWORD` is not explicitly set to false.

### Decision 5: CORS Origin Policy Refinement
- Ensure `CORS_ORIGINS` supports explicit production URLs (e.g. `https://fpolink.vercel.app`).
- Retain the strict prefix regex `^https://fpolink(-[a-z0-9-]+)?\.vercel\.app$` for ephemeral preview deployments.
- Verify that arbitrary `.vercel.app` domains and attacker domains are firmly rejected.

---

## 4. Scope Boundaries & Out of Scope
- **In Scope**:
  - `backend/app/api/deps.py` (enhanced `verify_fpo_access` and `require_role`)
  - `backend/app/api/farmers.py` & `backend/app/api/v1/farmers.py`
  - `backend/app/api/fpo.py` & `backend/app/api/v1/fpos.py`
  - `backend/app/api/tasks.py`
  - `backend/app/api/harvest.py`
  - `backend/app/api/v1/buyers.py`
  - `backend/app/api/v1/matching.py`
  - `backend/scripts/create_admin.py`
  - `backend/tests/test_tenant_isolation_security.py`
  - `docs/SECURITY_AUDIT.md` (audit report artifact)
- **Out of Scope**:
  - OAuth2 external identity provider / SSO integration (deferred to v1.0).
  - Hardware security token (FIDO2/WebAuthn) support.
