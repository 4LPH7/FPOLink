# FPOLink TN — Tenant Isolation & Production Security Audit Report

> **Sprint / Milestone:** M-Series MVP Sprint — Phase M4  
> **Document Version:** 1.0.0  
> **Audited Date:** 2026-10-07  
> **Status:** Fully Audited & Automated Regression Verified (269 Passed Tests)  

---

## 1. Executive Summary

FPOLink TN operates a statewide agricultural operating system serving multiple Farmer Producer Organizations (FPOs), district agricultural officers, and commercial buyers across all 38 districts of Tamil Nadu.

This security audit establishes that:
1. **Multi-tenant isolation is enforced strictly at the database and API dependency layer**, completely independent of frontend UI state.
2. **Cross-FPO access is blocked**: FPO staff cannot inspect, mutate, or delete records belonging to another FPO.
3. **District administrative boundaries are enforced**: District administrators (`district_admin`) can only access FPOs, farmers, harvests, and tasks within their assigned `district_id`, and are forbidden (HTTP 403) from accessing records outside their district.
4. **Bulk and matching operations respect tenant boundaries**: Cross-tenant CSV buyer imports and candidate requirement inquiries are rejected.
5. **Authentication and token lifecycle are cryptographically secure**: Expired, tampered, and restricted `password_change` tokens cannot access protected APIs; mandatory password rotation cannot be bypassed.
6. **Administrator bootstrapping is hardened**: Provisioning enforces minimum 12-character complexity in production, rejects common dictionary defaults, hashes with Argon2id, and defaults to mandatory password change.
7. **CORS origins are tightly scoped**: Wildcards (`*`) are rejected in production, and ephemeral previews are restricted strictly to official project subdomains (`^https://fpolink(-[a-z0-9-]+)?\.vercel\.app$`).

---

## 2. Multi-Tenant Role Hierarchy & RBAC Matrix

FPOLink supports 9 role tiers defined in `UserRole` (`app.models.user.py`):

| Role Tier | Scope | Permissions & Access Boundaries |
|---|---|---|
| **Super Admin (`admin`)** | Statewide | Global system administration, provider ingestion triggers, FPO onboarding, audit logs. |
| **State Admin (`state_admin`)** | Statewide | Cross-district oversight, statewide supply-demand analytics, mandi price monitoring. |
| **District Admin (`district_admin`)** | District (`district_id`) | Scoped administrative oversight of all FPOs, farmers, tasks, and harvests within their assigned district only. |
| **FPO Admin (`fpo_admin`)** | FPO Tenant (`fpo_id`) | Full administrative management of their assigned FPO, staff members, farmers, and buyer contracts. |
| **FPO Staff (`fpo_staff`)** | FPO Tenant (`fpo_id`) | Day-to-day operations: farmer enrollment, harvest verification, task completion, buyer requirements. |
| **Field Agent (`field_agent`)** | FPO Tenant (`fpo_id`) | Mobile harvest logging, plot inspections, farmer data collection. |
| **Data Operator (`data_operator`)** | Statewide / FPO | Mandi quote data entry, market price uploads, ingestion error remediation. |
| **Analyst (`analyst`)** | Read-Only | Price intelligence, quantile forecasts, and inter-district arbitrage models. |
| **Commercial Buyer (`buyer`)** | Buyer-Scoped | Procurement requirement registration, matched harvest confirmations. |
| **Farmer (`farmer`)** | Self (`user_id`) | Personal harvests, plot registrations, price lookups via bot/web. |

---

## 3. Defense-in-Depth Isolation Implementation

### 3.1 Database-Aware `verify_fpo_access`
The primary tenant guard `verify_fpo_access` (`app.api.deps.py`) validates tenant ownership on every protected request:
- **Statewide Roles**: `admin`, `state_admin`, `data_operator`, `analyst` pass automatically.
- **FPO-Scoped Roles**: Verified against `current_user.fpo_id == target_fpo_id`.
- **District Administrators**: Verified against the database; if `fpo.district_id != current_user.district_id` (and district name differs), access is immediately denied (`False`), yielding HTTP 403 Forbidden.

### 3.2 Farmer Registry Scoping
`_enforce_farmer_fpo_scope` (`app.api.farmers.py` and `app.api.v1/farmers.py`):
- Cross-FPO lookups, creation, updates, and WhatsApp invite link generations are blocked.
- District Administrators attempting to access farmers outside their district receive `HTTP 403 Forbidden ("District administrator cannot access records outside assigned district")`.

### 3.3 Task Board Tenant Scoping
`_scoped` (`app.api.tasks.py`):
- Queries are filtered automatically at the SQL level.
- Staff see only tasks where `Task.fpo_id == user.fpo_id`.
- District administrators query only tasks belonging to FPOs in their assigned `district_id`.
- Direct attempts to mutate or delete foreign tasks result in `HTTP 404 Not Found` (hiding existence from unauthorized tenants) or `HTTP 403 Forbidden`.

### 3.4 Harvest Aggregation & Lifecycle
`_enforce_harvest_scope` (`app.api.harvest.py`):
- Farmers can only access their own harvests (`harvest.farmer.user_id == user.id`).
- FPO staff can only verify or view harvests within their FPO (`harvest.farmer.fpo_id == user.fpo_id`).
- District administrators are restricted strictly to harvests from farmers in their district.
- Harvest aggregation (`/api/harvest/aggregation`) filters pools by district FPOs when called by a district administrator.

### 3.5 Demand & Supply Matching Scoping
- In `/api/v1/matching/candidates/{requirement_id}`, staff can only search candidates for buyer requirements belonging to their permitted FPO (`verify_fpo_access(req.fpo_id, current_user, db)`).
- In `/api/v1/buyers/import-csv`, non-super-admins cannot import buyers or requirements for another FPO.

---

## 4. Token & Credential Security Lifecycle

### 4.1 Cryptographic Token Integrity
- **Algorithm**: HMAC-SHA256 with minimum 32-character production secret keys.
- **Payload Verification**:
  - Validates `sub` (User UUID), `role`, `type`, and expiration `exp`.
  - Rejects expired tokens with `HTTP 401 Unauthorized ("Invalid or expired token")`.
  - Rejects tampered signatures with `HTTP 401 Unauthorized`.
  - Rejects wrong token types (e.g. `type: "refresh"` passed to access endpoints) with `HTTP 401 Unauthorized ("Invalid token type")`.

### 4.2 Mandatory Password Rotation Boundary
1. Bootstrapped or reset accounts have `password_change_required = True`.
2. Login issues a restricted token with `type: "password_change"`.
3. `get_current_user` dependency blocks `password_change_required` accounts from all business APIs (`HTTP 403 Forbidden ("Password change required")`).
4. The user can only call `/api/auth/change-password` using the restricted token.
5. Only upon successful rotation is `password_change_required` flipped to `False` and a standard business access token issued.

---

## 5. Production Admin Provisioning Governance

`backend/scripts/create_admin.py` enforces production hygiene:
- **Password Complexity**:
  - Minimum 12 characters when `ENVIRONMENT == "production"`.
  - Rejection of common dictionary markers (`"admin"`, `"password"`, `"fpolink"`, `"changeme"`, `"123456"`).
- **Mandatory Rotation**: Defaults `must_change_password = True` in production environments.
- **Hashing**: Strong Argon2id password hashing with unique salts.
- **Log Sanitation**: Plaintext credentials are never written to standard output, error streams, or log files.

---

## 6. Network & CORS Origin Protection

- **Production Wildcard Prohibition**: `validate_production_secrets()` raises a fatal configuration exception if `CORS_ORIGINS` contains wildcard `'*'` in production.
- **Scoped Preview Regex**: `CORS_ORIGIN_REGEX = r"^https://fpolink(-[a-z0-9-]+)?\.vercel\.app$"` tightly scopes preview access to official project domains while blocking attacker-controlled Vercel apps (e.g. `attacker.vercel.app`, `evil-fpolink.vercel.app`).

---

## 7. Automated Test Verification Matrix

All security boundaries are continuously verified by the automated regression test suite (`backend/tests/test_tenant_isolation_security.py` and full suite):

| Test Case | Acceptance Criteria | Result |
|---|---|---|
| `test_cross_fpo_farmer_access_blocked` | Staff A cannot list, view, or register farmers in FPO B (HTTP 403) | **PASSED** |
| `test_cross_fpo_task_isolation_and_modification_blocked` | Staff A cannot list, update, or delete tasks in FPO B (HTTP 404) | **PASSED** |
| `test_district_admin_boundary_isolation` | District Admin Erode can access Erode FPOs/farmers but is blocked from Salem FPOs/farmers (HTTP 403) | **PASSED** |
| `test_cross_tenant_bulk_csv_import_blocked` | Staff A cannot bulk import buyers for FPO B (HTTP 403) | **PASSED** |
| `test_cross_tenant_matching_candidates_blocked` | Staff A cannot inspect match candidates for FPO B requirement (HTTP 403) | **PASSED** |
| `test_expired_and_invalid_tokens_rejected` | Expired, signature-tampered, or missing tokens return HTTP 401 | **PASSED** |
| `test_password_rotation_workflow_enforced` | Temporary token blocked from business APIs until password is changed | **PASSED** |
| `test_demo_data_isolation_when_demo_mode_false` | Synthetic `demo_seed` records never leak to production price feeds | **PASSED** |
| `test_cors_origin_regex_security` | Official preview branches match; arbitrary attacker domains rejected | **PASSED** |
| `test_wildcard_cors_rejected_in_production` | Wildcard CORS origins raise fatal error on startup in production | **PASSED** |
| `test_production_bootstrap_password_hardening` | Bootstrapping enforces 12-char complexity and rotation defaults in production | **PASSED** |

**Total Regression Suite Passing:** **269 / 269 tests**
