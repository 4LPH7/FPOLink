# Phase M4: Tenant Isolation & Production Security Audits — Implementation Plan

> **Phase:** M4  
> **Milestone:** M-Series MVP Sprint  
> **Prerequisites:** Phase M0 (Pre-flight), Phase M1 (Real Price Data), Phase M2 (Honest Forecasting), Phase M3 (Defensible Arbitrage) complete  
> **Context Document:** [M4-CONTEXT.md](file:///d:/PROJECTS/FPOLink/.planning/phases/M4-CONTEXT.md)  

---

## 1. Phase Overview

This phase performs a rigorous, defense-in-depth security verification and hardening of the multi-tenant authorization boundaries, token authentication lifecycle, and production administration bootstrap.

Every acceptance criterion from the sprint audit will be verified with automated regression tests:
1. **Cross-FPO Isolation**: FPO staff attempting to read, create, update, or delete another FPO's records are strictly blocked.
2. **District Admin Boundary**: District administrators can manage records within their assigned district but are blocked (HTTP 403) from accessing records outside their district.
3. **Cross-Tenant Tasks & Bulk Operations**: Bulk imports and task mutations cannot inject or alter foreign tenant data.
4. **Token Security & Password Rotation**: Expired/invalid tokens are rejected (HTTP 401); temporary password rotation tokens cannot access protected business APIs.
5. **Production Admin Bootstrap**: Secure CLI provisioning with Argon2id hashing, complexity rules, and rotation defaults.
6. **Scoped CORS Origin Defense**: Tight regex/origin validation blocking attacker origins while supporting official preview branches.

---

## 2. Tasks & Execution Sequence (Tracer-First)

### Task M4.1: Database-Aware Multi-Tenant Scoping (`verify_fpo_access`)
- **Target File:** `backend/app/api/deps.py`
- **Work Items:**
  1. Update `verify_fpo_access(target_fpo_id: UUID, current_user: User, db: Optional[Session] = None) -> bool`:
     - Allow global roles: `admin`, `state_admin`, `data_operator`, `analyst`.
     - Allow FPO-assigned roles if `current_user.fpo_id == target_fpo_id`.
     - For `district_admin`:
       - If `current_user.district_id` is missing, return `False`.
       - If `db` is provided, look up `target_fpo = db.query(FPO).filter(FPO.id == target_fpo_id).first()`.
       - If `target_fpo.district_id == current_user.district_id` or `target_fpo.district` matches the district's name, return `True`.
       - Otherwise, return `False`.
  2. Ensure `require_role` smoothly handles district admin and other roles without false positives.
- **Verification:** Unit tests for `verify_fpo_access` covering all 9 roles and cross-district checks.

---

### Task M4.2: Audit and Enforce Tenant Isolation Across All Endpoints
- **Target Files:**
  - `backend/app/api/farmers.py` & `backend/app/api/v1/farmers.py`
  - `backend/app/api/fpo.py` & `backend/app/api/v1/fpos.py`
  - `backend/app/api/tasks.py`
  - `backend/app/api/harvest.py`
  - `backend/app/api/v1/buyers.py`
  - `backend/app/api/v1/matching.py`
- **Work Items:**
  1. **Farmers**: Update `_enforce_farmer_fpo_scope` and route dependencies to include `district_admin`. Allow access if the farmer's FPO belongs to `current_user.district_id`; block (HTTP 403) if outside.
  2. **FPOs**:
     - In `list_all`: If `district_admin`, return only FPOs located in `current_user.district_id`.
     - In `get_one`: Verify `verify_fpo_access(fpo.id, current_user, db)`.
  3. **Tasks**:
     - Add `district_admin` and `state_admin` to `STAFF_ROLES`.
     - Update `_scoped(db, user)` so `district_admin` queries all tasks in FPOs in their district.
     - Pass `db` to `verify_fpo_access` in `create_task` and `update_task`.
  4. **Harvests**:
     - Update `_enforce_harvest_scope` for `district_admin` (allow if farmer's FPO is in district, else 403).
     - In `get_harvest_aggregation`: If `district_admin`, enforce district scoping when `fpo_id` is passed or default to district FPOs.
  5. **Commercial Buyers & Demand**:
     - In `import-csv`: Check that staff cannot import for foreign FPO; district admin can only import for FPOs in their district.
     - In `get_candidates`: Check that if `req.fpo_id` is set, `verify_fpo_access(req.fpo_id, current_user, db)` is verified.
- **Verification:** Fast endpoint checks with test client.

---

### Task M4.3: Hardened Production Admin Provisioning
- **Target File:** `backend/scripts/create_admin.py`
- **Work Items:**
  1. Add password complexity validation: minimum 8 chars for dev, minimum 12 chars in production (`ENVIRONMENT == 'production'`), rejection of common defaults ("admin", "password", "12345678").
  2. If `ENVIRONMENT == 'production'` and `ADMIN_MUST_CHANGE_PASSWORD` is not explicitly set, default `must_change_password=True` to enforce immediate credential rotation on first login.
  3. Ensure no credential leakage in logs or exceptions.
- **Verification:** `backend/tests/test_create_admin.py` with production and dev configurations.

---

### Task M4.4: CORS Origin Configuration Verification & Documentation
- **Target Files:**
  - `backend/app/config.py`
  - `docs/HOSTING.md`
- **Work Items:**
  1. Validate that `CORS_ORIGIN_REGEX` strictly prevents open wildcard `.vercel.app` matches while allowing official project previews (`^https://fpolink(-[a-z0-9-]+)?\.vercel\.app$`).
  2. Document production CORS configuration best practices in `docs/HOSTING.md`.
- **Verification:** Unit test regex checks for both authorized and malicious origins.

---

### Task M4.5: Comprehensive Automated Security Test Suite
- **Target File:** `backend/tests/test_tenant_isolation_security.py`
- **Work Items:**
  1. Test Cross-FPO farmer access, creation, updates, and WhatsApp invites are blocked.
  2. Test District Administrator isolation:
     - Access permitted for FPOs, farmers, tasks, and harvests in assigned district.
     - Access blocked (HTTP 403 or 404) for FPOs, farmers, tasks, and harvests in other districts.
  3. Test Cross-tenant task updates, deletion, listings, and summary isolation.
  4. Test Cross-tenant bulk CSV import for buyers is blocked.
  5. Test Candidate matching scoping blocks foreign FPO staff from inspecting requirements.
  6. Test Password rotation workflow: temporary token rejection on business APIs, required change enforcement.
  7. Test Token security: expired tokens, forged signature tokens, missing tokens.
  8. Test Production admin bootstrap with complexity enforcement and rotation defaults.
  9. Test CORS origin security with authorized and blocked domain fixtures.
- **Verification:** `pytest backend/tests/test_tenant_isolation_security.py` all passing.

---

### Task M4.6: Security Audit Report Documentation
- **Target File:** `docs/SECURITY_AUDIT.md` (New Documentation)
- **Work Items:**
  1. Produce comprehensive audit matrix detailing each threat vector, code defenses, endpoints tested, and test evidence.
  2. Detail role permission boundaries for all 9 platform roles.
- **Verification:** Document generated and linked in `README.md`.

---

### Task M4.7: Regression Testing, Graph Sync & Git Commit
- **Work Items:**
  1. Run `pytest` on the entire test suite (264+ tests) to guarantee zero regressions.
  2. Run `ruff check .` and `ruff format --check .`.
  3. Run `graphify update .`.
  4. Commit changes with atomic commit message:
     `feat(m4): implement comprehensive tenant isolation, district admin boundaries, and production security audits`.
