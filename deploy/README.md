# FPOLink TN — Production Deployment Guide

> The `render.yaml` blueprint provisions a **staging** service on Render's free plan. It is useful for pilot validation, but it is not the durable production deployment described below. Choose a hosting and database plan with persistence, backups, and availability appropriate for production before relying on it for live operations.

## Render staging administrator bootstrap

The API startup command applies database migrations only. It does not create or reset an administrator account during deploys. After the first successful deploy, set `ADMIN_PHONE` and a strong `ADMIN_PASSWORD` in the Render service environment, then run `python scripts/create_admin.py` once from the service's Shell. This script is idempotent but updates the password for an existing account, so do not run it as a startup command or during routine deploys. Store the credentials in the organization's password manager and rotate them through the documented account flow.

For durable production, use the persistent Docker/VM deployment below, configure backups and restore checks, and keep the initial administrator provisioning as an explicit one-time operation.

This guide covers deploying the FPOLink backend, scheduled background worker, database, and active Telegram webhook using **Docker Compose** and **Cloudflare Tunnel (`cloudflared`)**. WhatsApp is an optional channel with separate Meta prerequisites.

---

## 1. Architecture

```text
[ Telegram Webhook / Farmers / Staff (optional WhatsApp) ]
                   │
                   ▼ (HTTPS on standard 443)
        [ Cloudflare Edge ]
                   │
                   │ (Outbound encrypted QUIC / TLS tunnel)
                   ▼
     [ cloudflared sidecar container ]
                   │
                   │ (Docker bridge network: port 8000)
                   ▼
         [ backend (FastAPI) ] ───▶ [ worker (APScheduler) ]
                   │                         │
                   ▼                         ▼
             [ postgres (PostgreSQL 16-alpine) ]
```

### Why Cloudflare Tunnel?
- **Zero inbound open ports**: No need for public IP, port forwarding, or firewall punch-through.
- **Automatic SSL/TLS**: Cloudflare handles SSL certificates and DDoS protection.
- **Cost**: 100% free under Cloudflare Zero Trust free tier (up to 50 users).

---

## 2. Prerequisites

1. **Docker Engine 24+** and **Docker Compose v2+** installed on the host machine/VM.
2. A domain name active on Cloudflare (e.g. `yourfpo.org`).
3. Telegram bot token from BotFather. Meta Developer WhatsApp credentials are only needed if you choose to enable WhatsApp (see [`docs/META_PRODUCTION_CHECKLIST.md`](../docs/META_PRODUCTION_CHECKLIST.md)).

---

## 3. Cloudflare Tunnel Setup

### Option A: Cloudflare Zero Trust Dashboard (Recommended)

1. Log in to [Cloudflare Zero Trust Dashboard](https://one.dash.cloudflare.com/).
2. Navigate to **Networks** > **Tunnels** > **Create a tunnel**.
3. Choose **Cloudflared** as the connector.
4. Name the tunnel: `fpolink-production`.
5. Under **Install and run a connector**, select **Docker** and copy the tunnel token.
   - Example token format: `eyJhIjoi...`
6. Under **Public Hostnames**, configure:
   - **Subdomain**: `api`
   - **Domain**: `yourfpo.org`
   - **Path**: leave empty
   - **Type**: `HTTP`
   - **URL**: `backend:8000` (resolves via Docker Compose internal DNS)
7. Save the hostname.

---

## 4. Configuration

1. Copy the environment template:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with production secrets:
   ```env
   ENVIRONMENT=production
   SECRET_KEY=<generate-a-long-random-string-at-least-32-chars>

   # PostgreSQL
   POSTGRES_USER=fpolink_prod
   POSTGRES_PASSWORD=<strong-database-password>
   POSTGRES_DB=fpolink_prod
   DATABASE_URL=postgresql+psycopg://fpolink_prod:<strong-database-password>@postgres:5432/fpolink_prod

   # Active farmer channel: Telegram
   TELEGRAM_ENABLED=true
   TELEGRAM_BOT_TOKEN=<from-botfather>
   TELEGRAM_WEBHOOK_SECRET=<optional-random-secret>
   PUBLIC_API_URL=https://api.yourfpo.org
   TELEGRAM_AUTO_SET_WEBHOOK=true

   # WhatsApp stays disabled unless Meta setup is complete
   WHATSAPP_ENABLED=false

   # Cloudflare Tunnel
   CLOUDFLARE_TUNNEL_TOKEN=<token-copied-from-step-3>

   # Optional Sentry Monitoring
   SENTRY_DSN=https://<key>@sentry.io/<project-id>
   ```

---

## 5. Launch Stack

Launch the stack with the production compose override:

```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build
```

### What this runs:
- `postgres`: PostgreSQL 16 database with persisted volume `postgres_data`.
- `backend`: FastAPI API server (2 uvicorn workers, automatic `alembic upgrade head` on startup, healthcheck).
- `worker`: APScheduler worker (03:00 IST data retention, 07:30 IST price digest, 07:45 IST price alerts, 10-minute at-least-once inbound sweep).
- `tunnel`: Cloudflare Tunnel sidecar routing `api.yourfpo.org` directly to `backend:8000`.

---

## 6. Verification

### Step 1: Check Container Health
```bash
docker compose ps
```
All containers (`postgres`, `backend`, `worker`, `tunnel`) should report `running` / `healthy`.

### Step 2: Test Health Check Endpoint
```bash
curl -i https://api.yourfpo.org/api/health
```
Expected output:
```json
HTTP/2 200
content-type: application/json

{"status":"ok","service":"fpolink-api","version":"0.1.0","db":"ok"}
```

### Step 3: Verify Telegram Webhook
Set `PUBLIC_API_URL` to the public HTTPS API origin. The backend registers `/api/telegram/webhook` at startup. In the dashboard's `/telegram` page, confirm the webhook is present; then test `/start`, a price query, and harvest submission from a Telegram account.

### Optional: Configure Meta WhatsApp Webhook
Only enable this after completing the Meta business, number, token, template, billing, and webhook prerequisites in [`docs/META_PRODUCTION_CHECKLIST.md`](../docs/META_PRODUCTION_CHECKLIST.md).
In the [Meta App Dashboard](https://developers.facebook.com/apps/):
1. Navigate to **WhatsApp** > **Configuration**.
2. **Callback URL**: `https://api.yourfpo.org/api/whatsapp/webhook`
3. **Verify token**: matches `WHATSAPP_VERIFY_TOKEN` from `.env`.
4. Click **Verify and save**.
5. Under **Webhook fields**, click **Manage** and subscribe to `messages`.

---

## 7. Operational Runbook & Maintenance

- **Emergency Kill Switch**: See [`docs/OPS_RUNBOOK.md`](../docs/OPS_RUNBOOK.md).
- **View Backend Logs**:
  ```bash
  docker compose logs -f backend
  ```
- **View Worker Logs**:
  ```bash
  docker compose logs -f worker
  ```
- **Restart Backend / Worker**:
  ```bash
  docker compose restart backend worker
  ```
- **Database Backup**:
  ```bash
  docker compose exec postgres pg_dump -U fpolink_prod fpolink_prod > backup_$(date +%Y%m%d_%H%M%S).sql
  ```
