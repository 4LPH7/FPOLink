# Community 22

> 23 nodes · cohesion 0.12

## Key Concepts

- **Button** (22 connections) — `backend/app/messaging/base.py`
- **whatsapp_cloud.py** (16 connections) — `backend/app/messaging/whatsapp_cloud.py`
- **messaging/base.py** (14 connections) — `backend/app/messaging/base.py`
- **MessageChannel** (10 connections) — `backend/app/messaging/base.py`
- **messaging/__init__.py** (10 connections) — `backend/app/messaging/__init__.py`
- **mask()** (7 connections) — `backend/app/messaging/base.py`
- **FakeChannel** (7 connections) — `backend/tests/test_whatsapp_bot.py`
- **hmac** (5 connections)
- **dataclasses** (4 connections)
- **hashlib** (4 connections)
- **.send_buttons()** (2 connections) — `backend/app/messaging/base.py`
- **.send_buttons()** (2 connections) — `backend/tests/test_whatsapp_bot.py`
- **.send_buttons()** (2 connections) — `backend/tests/test_whatsapp_harvest_flow.py`
- **.send_template()** (1 connections) — `backend/app/messaging/base.py`
- **.send_text()** (1 connections) — `backend/app/messaging/base.py`
- **Protocol** (1 connections)
- **Transport-agnostic messaging types. Bot logic depends on these, not on WhatsApp.** (1 connections) — `backend/app/messaging/base.py`
- **Mask a phone number for logs (phone numbers are personal data under DPDP).** (1 connections) — `backend/app/messaging/base.py`
- **Messaging package: transport-agnostic types and WhatsApp Cloud API adapter.** (1 connections) — `backend/app/messaging/__init__.py`
- **WhatsApp Cloud API (Meta) adapter: webhook parsing, signature check, sending.** (1 connections) — `backend/app/messaging/whatsapp_cloud.py`
- **.__init__()** (1 connections) — `backend/tests/test_whatsapp_bot.py`
- **.send_template()** (1 connections) — `backend/tests/test_whatsapp_bot.py`
- **.send_text()** (1 connections) — `backend/tests/test_whatsapp_bot.py`

## Relationships

- [Community 13](Community_13.md) (16 shared connections)
- [Community 11](Community_11.md) (11 shared connections)
- [Community 14](Community_14.md) (8 shared connections)
- [Community 1](Community_1.md) (6 shared connections)
- [Community 12](Community_12.md) (6 shared connections)
- [Community 9](Community_9.md) (4 shared connections)
- [Community 3](Community_3.md) (4 shared connections)

## Source Files

- `backend/app/messaging/__init__.py`
- `backend/app/messaging/base.py`
- `backend/app/messaging/whatsapp_cloud.py`
- `backend/tests/test_whatsapp_bot.py`
- `backend/tests/test_whatsapp_harvest_flow.py`

## Audit Trail

- EXTRACTED: 78 (92%)
- INFERRED: 7 (8%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*