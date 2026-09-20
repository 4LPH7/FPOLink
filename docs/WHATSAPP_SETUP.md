# FPOLink WhatsApp bot: integration guide

Skeleton for the WhatsApp Cloud API (Meta) webhook and a Tamil/English bot. It is tested with
fakes only (17 tests). Nothing here has been run against Meta's live API yet.

## Files (copy into `backend/`, same paths)

| File | Purpose |
|---|---|
| `app/messaging/base.py` | `InboundMessage`, `Button`, `MessageChannel` protocol, phone masking |
| `app/messaging/whatsapp_cloud.py` | Signature check, webhook parser, Cloud API sender (text, buttons, template) |
| `app/services/bot.py` | Bot engine: intents, Tamil/English copy, harvest flow, `InMemoryServices` |
| `app/api/whatsapp.py` | `GET/POST /api/whatsapp/webhook`, settings, dependencies |
| `tests/test_whatsapp_bot.py` | 17 tests: signature, dedup, price, harvest flow, alerts, Tamil matching |

Run tests: `cd backend && PYTHONPATH=. pytest tests/test_whatsapp_bot.py`

## Wire it into the app

1. In `app/main.py`: `from app.api import whatsapp` then `app.include_router(whatsapp.router)`.
2. Implement `BotServices` (see the Protocol in `bot.py`) on top of your existing services:
   - `find_farmer(phone10)`: look up by the **last 10 digits**; store phones normalised.
   - `latest_price(crop)`: newest modal/min/max from `market_prices` (Rs/kg; the bot shows Rs/quintal).
   - `submit_harvest(...)`: call your harvest service.
   - `forecast_text`, `weather_text`: return `None` until those features exist.
3. Replace `get_bot()` in `app/api/whatsapp.py` with a cached
   `BotEngine(DbBotServices(...))`. Until then the endpoint returns 503.
4. Add tables (via Alembic):
   - `whatsapp_inbound(message_id text primary key, received_at timestamptz)`: dedup. Use
     `INSERT ... ON CONFLICT DO NOTHING` and check the row count. Purge rows older than 7 days.
   - `conversation_state(wa_id text primary key, step text, data jsonb, updated_at timestamptz)`:
     expire after about 30 minutes of inactivity.
   - On farmers: `lang` ('ta'/'en'), `alerts_opt_in`, `alerts_opt_in_at`, `alerts_opt_out_at`.

## Environment variables (never commit values; `.env` is gitignored)

```
WHATSAPP_VERIFY_TOKEN=<long random string you choose>
WHATSAPP_APP_SECRET=<Meta app secret>
WHATSAPP_ACCESS_TOKEN=<token with whatsapp_business_messaging>
WHATSAPP_PHONE_NUMBER_ID=<from the WhatsApp product page>
WHATSAPP_API_VERSION=<a currently supported Graph API version; check Meta's docs>
```

## Meta setup checklist (check Meta's current docs; menus change)

- [ ] Create a Meta developer app (Business type) and add the WhatsApp product.
- [ ] Use the free test number for development, and add your own phone as a recipient (test mode allows only a few verified recipients).
- [ ] Webhook needs a public HTTPS URL. For development use a free tunnel (Cloudflare Tunnel or ngrok). Callback: `https://<host>/api/whatsapp/webhook`, verify token = `WHATSAPP_VERIFY_TOKEN`, subscribe to the `messages` field.
- [ ] Temporary test tokens expire quickly. For anything long-running, create a System User token.
- [ ] Production: your own number, Meta business verification (FPO documents), and a payment method on the account.
- [ ] Daily digest: create a **utility** template (language `ta`), get it approved, then call `send_template`.

## Design notes

- **Reply fast, work later:** the webhook returns 200 immediately; Meta retries slow or failed
  deliveries, so `first_time(message_id)` must be atomic (DB unique constraint).
- **Signature check** uses the raw request bytes and rejects when the app secret is empty.
- **Cost:** each bot reply may count as a billable service message once free allowances end.
  Prefer one combined reply over several, and one digest template per farmer per day.
- **Consent:** `ALERTS ON` / `ALERTS OFF` are stored with timestamps. Send templates only to opted-in farmers.
- **Privacy:** logs mask phone numbers. Do not log payloads or tokens.

## Not done yet

- Voice notes and images are ignored (`kind="unsupported"`); reply asking the farmer to type.
- Per-number rate limiting, and a message queue if volume grows.
- List messages (3 buttons max), WhatsApp Flows for forms, the daily-digest worker job.
- Native-speaker review of the Tamil text.
