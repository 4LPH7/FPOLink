# Telegram bot (@Fpo_Link_Bot)

WhatsApp is disabled (`WHATSAPP_ENABLED=false`); Telegram is the farmer channel.

## Production (Render, webhook)
1. Set `TELEGRAM_BOT_TOKEN` in the Render dashboard (never commit it).
2. On startup the API calls `setWebhook` on `$RENDER_EXTERNAL_URL/api/telegram/webhook`
   (or `PUBLIC_API_URL`) with a secret derived from the token, and registers commands.
3. Admins can re-register via `POST /api/telegram/set-webhook`; staff can inspect `GET /api/telegram/status`.

## Production (Docker / Cloudflare Tunnel)
1. Set `TELEGRAM_ENABLED=true`, `TELEGRAM_BOT_TOKEN`, and
   `PUBLIC_API_URL=https://api.yourfpo.org` in the server's `.env` file. The URL must
   be the public HTTPS origin routed to the backend by Cloudflare Tunnel.
2. `TELEGRAM_AUTO_SET_WEBHOOK=true` is the default. On API startup, the app registers
   `https://api.yourfpo.org/api/telegram/webhook`; set `TELEGRAM_WEBHOOK_SECRET` to a
   random secret if you want an independently managed secret instead of the token-derived
   default.
3. Confirm `GET /api/telegram/status` reports the expected bot and webhook details, then
   exercise `/start`, a price query, and a harvest submission from a test account.

## Local dev (long polling)
```bash
cd backend && TELEGRAM_BOT_TOKEN=... python scripts/telegram_poll.py
```
This deletes any webhook — re-run `set-webhook` afterwards for production.

## Commands
/start, /help, /menu, /price, /harvest, /forecast, /weather, /buyers, /alerts, /lang ta|en, /unlink, /cancel.
Farmers link their chat by sharing their own contact; unknown phones are auto-registered
as FARMER (with DPDP consent recorded) when `TELEGRAM_AUTO_REGISTER=true`.
