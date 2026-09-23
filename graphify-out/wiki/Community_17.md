# Community 17

> 26 nodes · cohesion 0.08

## Key Concepts

- **BotServices** (17 connections) — `backend/app/services/bot.py`
- **Record timestamp when first-contact DPDP notice was confirmed delivered.** (3 connections) — `backend/app/services/bot.py`
- **.mark_notice_delivered()** (3 connections) — `backend/app/services/db_bot_services.py`
- **.mark_notice_sent()** (3 connections) — `backend/app/services/db_bot_services.py`
- **.__init__()** (2 connections) — `backend/app/services/bot.py`
- **.claim_notice()** (2 connections) — `backend/app/services/bot.py`
- **.find_farmer()** (2 connections) — `backend/app/services/bot.py`
- **.first_time()** (2 connections) — `backend/app/services/bot.py`
- **.get_state()** (2 connections) — `backend/app/services/bot.py`
- **.latest_price()** (2 connections) — `backend/app/services/bot.py`
- **.mark_notice_delivered()** (2 connections) — `backend/app/services/bot.py`
- **.mark_notice_sent()** (2 connections) — `backend/app/services/bot.py`
- **.release_notice_claim()** (2 connections) — `backend/app/services/bot.py`
- **.set_alerts()** (2 connections) — `backend/app/services/bot.py`
- **.set_state()** (2 connections) — `backend/app/services/bot.py`
- **.submit_harvest()** (2 connections) — `backend/app/services/bot.py`
- **Release leased claim after send failure so future inbound messages can retry.** (2 connections) — `backend/app/services/bot.py`
- **.release_notice_claim()** (2 connections) — `backend/app/services/db_bot_services.py`
- **.forecast_text()** (1 connections) — `backend/app/services/bot.py`
- **.weather_text()** (1 connections) — `backend/app/services/bot.py`
- **Protocol** (1 connections)
- **Everything the bot needs from your app. Implement against your DB/services.** (1 connections) — `backend/app/services/bot.py`
- **Atomically record message_id; False if already seen (Meta retries webhooks).** (1 connections) — `backend/app/services/bot.py`
- **Store opt-in/out with a timestamp (consent evidence for DPDP / WhatsApp opt-in).** (1 connections) — `backend/app/services/bot.py`
- **Atomically claim notice lease. Returns True only if claim was acquired.** (1 connections) — `backend/app/services/bot.py`
- *... and 1 more nodes in this community*

## Relationships

- [Community 13](Community_13.md) (3 shared connections)
- [Community 1](Community_1.md) (3 shared connections)
- [Community 4](Community_4.md) (3 shared connections)
- [Community 12](Community_12.md) (1 shared connections)

## Source Files

- `backend/app/services/bot.py`
- `backend/app/services/db_bot_services.py`

## Audit Trail

- EXTRACTED: 36 (100%)
- INFERRED: 0 (0%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*