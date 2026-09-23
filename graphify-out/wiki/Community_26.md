# Community 26

> 19 nodes · cohesion 0.12

## Key Concepts

- **Settings** (13 connections) — `backend/app/config.py`
- **test_config_security.py** (8 connections) — `backend/tests/test_config_security.py`
- **test_production_accepts_valid_whatsapp_secrets()** (3 connections) — `backend/tests/test_whatsapp_wiring_and_killswitch.py`
- **test_production_allows_disabled_whatsapp_without_secrets()** (3 connections) — `backend/tests/test_whatsapp_wiring_and_killswitch.py`
- **test_production_refuses_missing_whatsapp_secrets()** (3 connections) — `backend/tests/test_whatsapp_wiring_and_killswitch.py`
- **.use_psycopg3()** (2 connections) — `backend/app/config.py`
- **.validate_production_secrets()** (2 connections) — `backend/app/config.py`
- **test_development_allows_default_secret_key()** (2 connections) — `backend/tests/test_config_security.py`
- **test_production_accepts_strong_secret_key()** (2 connections) — `backend/tests/test_config_security.py`
- **test_production_refuses_default_secret_key()** (2 connections) — `backend/tests/test_config_security.py`
- **Application settings loaded from environment variables and .env file.** (1 connections) — `backend/app/config.py`
- **Tests for production security enforcement in configuration.** (1 connections) — `backend/tests/test_config_security.py`
- **In production with WhatsApp enabled, missing secrets must raise a fatal…** (1 connections) — `backend/tests/test_whatsapp_wiring_and_killswitch.py`
- **In production with WhatsApp disabled, missing secrets should not raise.** (1 connections) — `backend/tests/test_whatsapp_wiring_and_killswitch.py`
- **In production with WhatsApp enabled and all secrets present, startup succeeds.** (1 connections) — `backend/tests/test_whatsapp_wiring_and_killswitch.py`
- **BaseSettings** (1 connections)
- **field_validator** (1 connections)
- **model_validator** (1 connections)
- **pydantic_core** (1 connections)

## Relationships

- [Community 14](Community_14.md) (4 shared connections)
- [Community 9](Community_9.md) (2 shared connections)
- [Community 3](Community_3.md) (1 shared connections)

## Source Files

- `backend/app/config.py`
- `backend/tests/test_config_security.py`
- `backend/tests/test_whatsapp_wiring_and_killswitch.py`

## Audit Trail

- EXTRACTED: 28 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*