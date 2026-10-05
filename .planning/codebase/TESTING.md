# FPOLink Testing Architecture & Conventions

Test frameworks, suites organization, mock strategies, and execution commands.

---

## 1. Testing Framework & Tooling

| Tool | Version / Plugin | Purpose |
|---|---|---|
| **pytest** | `^8.1.0` | Primary test execution framework |
| **pytest-asyncio** | `^1.4.0` | Asynchronous test execution (`@pytest.mark.asyncio`) |
| **pytest-mock** | `^3.15.1` | Mocking and patching fixtures |
| **respx** | `^0.23.1` | Mocking HTTPX requests to upstream APIs (CEDA, OGD, Telegram) |
| **FastAPI TestClient** | Starlette test client | Synchronous HTTP testing of FastAPI endpoints |

---

## 2. Test Suite Organization

All tests reside under `backend/tests/` and are strictly automated:

### A. Authentication & Security (25 tests)
- `test_auth.py`: User registration, login, JWT token issuance, refresh tokens, forced password reset flow.
- `test_auth_deps.py`: Token validation, expiration handling, and unauthorized 401 response checks.
- `test_multitenant_rbac.py`: Role-based access control boundaries between Admin, FPO Staff, Farmer, and Buyer roles.

### B. Multi-Channel Messaging & Bots (74 tests)
- `test_telegram_bot.py`: Telegram slash command routing, phone contact linking, auto-registration of farmers, bilingual toggle, webhook security.
- `test_whatsapp_bot.py`: Webhook verification handshake, HMAC-SHA256 signature verification, Tamil/English price query parsing, harvest submission flow.
- `test_whatsapp_onboarding.py`: First contact consent notices, `STOP` / `நிறுத்து` opt-out handling, unregistered number barriers.
- `test_whatsapp_price_alerts.py`: 5% price movement triggers, daily frequency rate limiting.
- `test_db_bot_services.py`: Conversation state persistence, atomic deduplication, session TTL expirations.

### C. Ingestion, Parsers & Data Hygiene (42 tests)
- `test_parsers.py`: OGD India XML/JSON and CEDA CSV response parsing and schema normalization.
- `test_mandiprices_ingest.py`: Scraping and fallback parsing for statewide MandiPrices feeds.
- `test_data_cleaning.py`: MAD (Median Absolute Deviation) z-score outlier detection and synthetic hygiene.
- `test_raw_replay.py`: Lineage verification and reproducible replay from raw ingestion payloads.

### D. Core Domain & Business Logic (65 tests)
- `test_fpo_api.py`: FPO creation, tenant isolation, and dashboard metrics aggregation.
- `test_farmers_api.py`: Farmer registry, acreage tracking, and search pagination.
- `test_harvest_service_and_api.py`: Harvest lifecycle (`submitted` → `inspected` → `aggregated` → `sold`).
- `test_tasks_api.py`: FPO operational tasks, assignments, status transitions, and priority filtering.
- `test_supply_demand_*.py`: Farm plot registration, yield estimation algorithms, buyer demand catalog, and AI matching rankings.

### E. Health, Retention & Platform Infrastructure (22 tests)
- `test_health_and_observability.py`: `/api/health` probes and Sentry integration lifecycle.
- `test_retention.py`: Data retention purging jobs for expired inbound/outbound chat logs.
- `test_units.py`: Quintal vs. kg vs. tonne unit conversions.

---

## 3. Running Tests

### Standard Test Run
```powershell
pytest backend/tests -v
```

### Fast Test Run (Skipping Live Network Tests)
```powershell
pytest backend/tests -v -k "not test_agmarknet_live"
```

### Running Specific Module Tests
```powershell
# Run Telegram bot tests:
pytest backend/tests/test_telegram_bot.py -v

# Run Supply & Demand matching tests:
pytest backend/tests/test_supply_demand_api_and_bot.py -v
```
