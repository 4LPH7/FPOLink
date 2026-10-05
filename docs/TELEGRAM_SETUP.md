# Telegram bot (@Fpo_Link_Bot)

WhatsApp is disabled (`WHATSAPP_ENABLED=false`); Telegram is the farmer channel.

## Production (Render, webhook)
1. Set `TELEGRAM_BOT_TOKEN` in the Render dashboard (never commit it).
2. On startup the API calls `setWebhook` on `$RENDER_EXTERNAL_URL/api/telegram/webhook`
   (or `PUBLIC_API_URL`) with a secret derived from the token, and registers commands.
3. Admins can re-register via `POST /api/telegram/set-webhook`; staff can inspect `GET /api/telegram/status`.

## Local dev (long polling)
```bash
cd backend && TELEGRAM_BOT_TOKEN=... python scripts/telegram_poll.py
```
This deletes any webhook — re-run `set-webhook` afterwards for production.

## Commands
/start, /help, /menu, /price, /harvest, /forecast, /weather, /buyers, /alerts, /lang ta|en, /unlink, /cancel.
Farmers link their chat by sharing their own contact; unknown phones are auto-registered
as FARMER (with DPDP consent recorded) when `TELEGRAM_AUTO_REGISTER=true`.
