# FPOLink Operations Runbook

> **Target Audience:** DevOps on-call engineers, system administrators, and technical operators.  
> **Project:** FPOLink (FastAPI + PostgreSQL + Docker).  
> **Scope:** Emergency procedures and operational health monitoring, focused on the WhatsApp bot integration and system availability.

---

## 1. Emergency WhatsApp Kill Switch

FPOLink includes a global kill switch governed by the `WHATSAPP_ENABLED` configuration parameter in [backend/app/config.py](file:///d:/PROJECTS/FPOLink/backend/app/config.py). When deactivated, all WhatsApp ingress endpoints, bot processing, and scheduled outbound broadcast jobs are halted immediately.

### When to Activate the Kill Switch

Activate the kill switch immediately if any of the following scenarios occur:

1. **Phone Number Flagged / Low Quality:** Meta flags the WhatsApp Business phone number or reduces the quality rating to "Low" in WhatsApp Manager due to user block or spam reports.
2. **Cost Spike / Budget Risk:** Abnormal outbound traffic volume, unexpected message burst, or risk of exceeding the monthly messaging budget (`WHATSAPP_MONTHLY_BUDGET_INR`).
3. **Meta API Outage / Instability:** Upstream Meta Cloud API errors (e.g. 500/503 errors, rate-limiting loops) causing cascading timeouts or unhandled retries.
4. **Security Incident / Secret Leak:** Suspected compromise of `WHATSAPP_ACCESS_TOKEN` or `WHATSAPP_APP_SECRET`, or unauthorized traffic targeting the webhook endpoint.
5. **Runaway Loop / Accidental Spam:** A software bug causing repeated or duplicate broadcast messages to farmers.

---

### How to Disable WhatsApp

To immediately disable WhatsApp functionality across the platform:

1. Open the production environment configuration file ([.env](file:///d:/PROJECTS/FPOLink/.env)) on the host:
   ```bash
   nano .env
   # or
   sed -i 's/^WHATSAPP_ENABLED=.*/WHATSAPP_ENABLED=false/' .env
   ```

2. Set the kill switch flag:
   ```dotenv
   WHATSAPP_ENABLED=false
   ```

3. Restart both the API backend and background worker containers:
   ```bash
   docker compose restart backend worker
   ```

*(Alternatively, if running without editing the `.env` file directly, inject the variable directly into the docker-compose environment: `WHATSAPP_ENABLED=false docker compose up -d backend worker`)*.

---

### What the Kill Switch Affects

When `WHATSAPP_ENABLED=false`:

| Component | Behavior When Disabled |
|---|---|
| **Webhook Verification** (`GET /api/whatsapp/webhook`) | Immediately returns **HTTP 503 Service Unavailable** with `{"detail": "WhatsApp bot is currently disabled"}`. |
| **Inbound Message Webhook** (`POST /api/whatsapp/webhook`) | Immediately returns **HTTP 503 Service Unavailable**. Meta's Cloud API treats this as a temporary server failure and queues retries per its exponential backoff policy (up to 24–48 hours) rather than dropping inbound messages permanently. |
| **Daily Digest Job** (07:30 IST) | The background worker job skips sending price digests to opted-in farmers. |
| **Price-Move Alert Job** (07:45 IST) | The background worker job skips evaluating and sending price swing alerts. |
| **Farmer Inbound Processing** | Inbound requests (keyword lookups, harvest logging, crop queries) are completely paused. Bot services and database writes for inbound messages do not execute. |

---

### How to Verify the Kill Switch Is Active

Verify that the kill switch is actively rejecting webhook requests:

#### Verification Command (Remote / Public Endpoint):
```bash
curl -s -i "https://api.yourdomain.com/api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=test"
```

#### Verification Command (Local Docker Host):
```bash
curl -s -i "http://localhost:8000/api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=test&hub.challenge=test"
```

#### Expected Output:
```http
HTTP/1.1 503 Service Unavailable
content-type: application/json

{"detail":"WhatsApp bot is currently disabled"}
```

If you receive HTTP 503, the kill switch is confirmed active.

---

### Re-Enabling Procedure

Once the underlying issue (credential rotation, Meta ticket resolution, rate-limit reset, bugfix) has been resolved:

1. Edit [.env](file:///d:/PROJECTS/FPOLink/.env) and set:
   ```dotenv
   WHATSAPP_ENABLED=true
   ```

2. Restart the backend and worker containers to pick up the updated configuration:
   ```bash
   docker compose restart backend worker
   ```

3. Test webhook reachability using curl:
   ```bash
   curl -s -i "http://localhost:8000/api/whatsapp/webhook?hub.mode=subscribe&hub.verify_token=YOUR_TOKEN&hub.challenge=test"
   # Should return HTTP 200 with the challenge string "test"
   ```

4. Verify webhook status in [Meta Developer Dashboard](https://developers.facebook.com):
   - Navigate to **WhatsApp > Configuration**.
   - Verify callback URL shows a green checkmark.
   - If subscriptions were paused by Meta during the 503 downtime, click **Test** or **Verify and Save**.

5. Monitor live container logs for the first incoming and outgoing messages:
   ```bash
   docker compose logs -f --tail=100 backend worker
   ```

6. Execute a sanity check from a test mobile number:
   - Send `வணக்கம்` or `price turmeric`.
   - Verify prompt response and check that HTTP 200 is returned to Meta.

---

## 2. System Health Check

FPOLink provides an automated health check endpoint at `GET /api/health` for uptime monitors (UptimeRobot, Datadog, Pingdom, Docker container health checks).

### Health Endpoint Usage

```bash
curl -s https://api.yourdomain.com/api/health
```

### Response Statuses

- **Healthy State (HTTP 200):**  
  Application is running and database connectivity (`SELECT 1`) is verified:
  ```json
  {
    "status": "ok",
    "db": "ok"
  }
  ```

- **Degraded State (HTTP 503 / 500):**  
  Application server is running, but the PostgreSQL database is unreachable or unresponsive:
  ```json
  {
    "status": "degraded",
    "db": "error"
  }
  ```

### Triage Steps if Health Check is Degraded

If `/api/health` reports `"db": "error"`:

1. Check if the PostgreSQL container is running:
   ```bash
   docker compose ps postgres
   ```
2. Inspect PostgreSQL database logs:
   ```bash
   docker compose logs --tail=100 postgres
   ```
3. Test direct PostgreSQL connectivity from the host:
   ```bash
   docker compose exec backend python -c "from app.database import SessionLocal; from sqlalchemy import text; db=SessionLocal(); print(db.execute(text('SELECT 1')).scalar())"
   ```
4. If Postgres is stopped or crashed:
   ```bash
   docker compose restart postgres
   docker compose restart backend worker
   ```

---

## Quick Reference Links

- [Meta Production Setup Checklist](file:///d:/PROJECTS/FPOLink/docs/META_PRODUCTION_CHECKLIST.md)
- [WhatsApp Cloud API Routing Code](file:///d:/PROJECTS/FPOLink/backend/app/api/whatsapp.py)
- [Application Settings & Kill Switch Definition](file:///d:/PROJECTS/FPOLink/backend/app/config.py)
- [Example Environment File](file:///d:/PROJECTS/FPOLink/.env.example)
