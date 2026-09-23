# Human Checkpoints Operational Guide (Checkpoints A, B, C, D)

This guide provides structured, 5-minute operational verification protocols for each human checkpoint defined in [`tasks/todo.md`](file:///d:/PROJECTS/FPOLink/tasks/todo.md) and [`tasks/plan.md`](file:///d:/PROJECTS/FPOLink/tasks/plan.md).

---

## Checkpoint A: First End-to-End Inbound Message

**Goal**: Verify a real mobile phone can query the WhatsApp bot and receive authentic market prices in English and Tamil without secret leakage or duplicate execution bugs.

### Prerequisites:
1. Docker stack running (`docker compose up -d`).
2. Cloudflare Tunnel or local tunnel active exposing `http://localhost:8000/api/whatsapp/webhook`.
3. In Meta Developer Portal: Webhook verified with verify token, subscribed to `messages`.
4. Recipient test phone registered in Sandbox.

### Verification Protocol (5 mins):
1. **Send English Price Query**:
   - Send: `"PRICE"` from your phone to the Meta test number.
   - Assert: Bot replies within 3 seconds with current Erode market prices in English:
     `"Vanakkam! Erode Mandi turmeric modal price is ₹154.50/kg on 2026-09-23..."`
2. **Send Tamil Price Query**:
   - Send: `"விலை"` from your phone.
   - Assert: Bot replies in Tamil with appropriate market names and Tamil numerals/prices:
     `"வணக்கம்! ஈரோடு ஒழுங்குமுறை விற்பனைக்கூடம் மஞ்சள் மாதிரி விலை ₹154.50/கிலோ..."`
3. **Duplicate Delivery Test**:
   - Resend the identical webhook payload via curl:
     ```bash
     curl -X POST http://localhost:8000/api/whatsapp/webhook -H "Content-Type: application/json" -d @backend/tests/fixtures/whatsapp/text_en.json
     ```
   - Assert: Webhook returns `HTTP 200 OK`, but database deduplication skips re-sending outbound message (atomic dedup on `message_id`).
4. **Secret Scan Check**:
   ```bash
   git grep -iE "(AIza|EAAG|whsec_|ghp_)" || echo "No secrets detected"
   ```

---

## Checkpoint B: Harvest Submission by Chat Visible to Staff

**Goal**: Verify a farmer can submit harvest volume, grade, and date over chat, and that the record appears in the FPO staff dashboard.

### Verification Protocol (5 mins):
1. **Initiate Harvest Flow**:
   - Text `"HARVEST"` or tap the interactive `"அறுவடை பதிவு"` button.
   - Bot prompts for crop name: Reply `"Turmeric"` (or `"மஞ்சள்"`).
   - Bot prompts for quantity: Reply `"25"` (quintals).
   - Bot prompts for grade: Reply `"A"`.
   - Bot prompts for harvest date: Reply `"tomorrow"` or `"2026-09-24"`.
2. **Bot Confirmation**:
   - Bot returns confirmation message:
     `"Harvest recorded! 25 quintals of Grade A Turmeric scheduled for 2026-09-24. Reference ticket: wamid..."`
3. **Staff Dashboard Verification**:
   - Open browser: `http://localhost:3000/farmers`.
   - Search for the farmer's name or village.
   - Verify the harvest entry is listed with status `SUBMITTED`.
4. **Idempotency Check**:
   - Resend the final confirmation packet; verify that duplicate harvest records are not created.

---

## Checkpoint C: Proactive Daily Digest Dry Run (3 Test Farmers)

**Goal**: Verify proactive template broadcasts to 3 test numbers, immediate honoring of `STOP` keyword, and accurate billing usage tracking.

### Verification Protocol (5 mins):
1. **Setup Test Farmers**:
   - Ensure 3 registered test farmer numbers have `alerts_opt_in=true`.
2. **Trigger Digest Worker Job**:
   ```bash
   docker compose exec worker python -c "from app.worker import send_daily_digests; send_daily_digests()"
   ```
3. **Verify Arrival**:
   - Confirm all 3 test phones receive the approved `daily_price_digest` WhatsApp template.
4. **Test Instant Opt-Out**:
   - On Phone #2, reply `"STOP"` (or `"நிறுத்து"`).
   - Assert: Bot replies immediately confirming alerts are turned off.
   - Trigger worker job again: Phone #1 and #3 receive digest; Phone #2 receives nothing.
5. **Usage & Cost Reconciliation**:
   - Open `http://localhost:3000/whatsapp`.
   - Verify: Outbound messages counter incremented by 3.
   - Verify estimated cost calculation reflects Meta utility rate (approx ₹0.115 per message).

---

## Checkpoint D: Staging E2E behind Cloudflare Tunnel

**Goal**: Verify full end-to-end stack under production HTTPS with zero open inbound ports.

### Verification Protocol (5 mins):
1. **Probe Health Endpoint**:
   ```bash
   curl -i https://api.yourfpo.org/api/health
   ```
   - Assert: Returns `HTTP 200 OK`, `{"status":"ok", "service":"fpolink-api", "db":"ok"}`.
2. **Probe SSL Certificate**:
   - Verify TLS 1.3 negotiated via Cloudflare Edge.
3. **Verify DPDP Retention Cron**:
   - Trigger DPDP retention purge:
     ```bash
     docker compose exec worker python -c "from app.worker import purge_dpdp_records; purge_dpdp_records()"
     ```
   - Verify query logs confirm inbound messages older than 7 days and states older than 24h are purged.
4. **Verify Frontend Staff Dashboard**:
   - Visit `https://app.yourfpo.org` (or `http://localhost:3000`).
   - Navigate through `/prices`, `/farmers`, `/admin`, `/whatsapp`.
   - Verify zero client-side JavaScript console errors and live backend connectivity.
