# FPOLink TN — Production Deployment Guide

This guide covers deploying the FPOLink backend, scheduled background worker, database, and WhatsApp webhook using **Docker Compose** and **Cloudflare Tunnel (`cloudflared`)**.

---

## 1. Architecture

```text
[ Meta WhatsApp Webhook / Mobile Users ]
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
3. Meta Developer WhatsApp App with App Secret, Access Token, and Phone Number ID (see [`docs/META_PRODUCTION_CHECKLIST.md`](../docs/META_PRODUCTION_CHECKLIST.md)).

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

   # WhatsApp Cloud API
   WHATSAPP_ENABLED=true
   WHATSAPP_VERIFY_TOKEN=<secure-random-verify-token>
   WHATSAPP_APP_SECRET=<from-meta-app-basic-settings>
   WHATSAPP_ACCESS_TOKEN=<system-user-permanent-token>
   WHATSAPP_PHONE_NUMBER_ID=<from-whatsapp-manager>
   WHATSAPP_BOT_PHONE=<registered-waba-phone-e.g.-919876543210>

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

### Step 3: Configure Meta Webhook
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
