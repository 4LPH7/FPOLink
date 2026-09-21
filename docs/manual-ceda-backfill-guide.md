# Operational Playbook: Manual CEDA Backfill, Coverage Audit & External Feeds

This playbook provides actionable, step-by-step procedures for loading verified agricultural data, resolving CEDA API limitations, activating the OGD API, and capturing real Meta WhatsApp payloads.

---

## 1. Manual CEDA CSV Export & Ingestion

Because the CEDA programmatic endpoint experiences intermittent 504 Gateway Timeouts on broad date queries, historical data can be immediately acquired directly from the web portal.

### Step 1: Download from CEDA Portal
1. Navigate to the CEDA Agri-Market data portal:  
   **[https://agrimarket.ceda.ashoka.edu.in/](https://agrimarket.ceda.ashoka.edu.in/)**
2. In the query interface:
   - **State**: `Tamil Nadu`
   - **District**: `Erode` (and optionally neighboring western TN districts: `Salem`, `Coimbatore`, `Dharmapuri`)
   - **Commodity**: Select `Turmeric` and `Banana`
   - **Date Range**: `2020-01-01` to Present (or 2015-present for deep ML training)
3. Click **Download / Export CSV**.
4. Save the downloaded files into the project repository under `ml/datasets/`:
   - `ml/datasets/ceda_erode_turmeric_real.csv`
   - `ml/datasets/ceda_erode_banana_real.csv`

> [!IMPORTANT]
> The filename must NOT include `synthetic` or `sample`. Files containing `_real.csv` are explicitly recognized by `CEDAProvider` as ground-truth data.

### Step 2: Ingest with Verified `--source ceda` Tag
Run the backfill script for each crop:

```bash
# Ingest Erode Turmeric
python backend/scripts/backfill_ceda.py \
  --csv-path ml/datasets/ceda_erode_turmeric_real.csv \
  --crop turmeric \
  --district Erode \
  --source ceda

# Ingest Erode Banana
python backend/scripts/backfill_ceda.py \
  --csv-path ml/datasets/ceda_erode_banana_real.csv \
  --crop banana \
  --district Erode \
  --source ceda
```

### Step 3: Run the Coverage Audit
Analyze monthly record frequency across mandis (verified sources only):

```bash
python backend/scripts/check_market_coverage.py --crop turmeric --district Erode
python backend/scripts/check_market_coverage.py --crop banana --district Erode
```

The script evaluates whether reporting frequency is sufficient for per-mandi statistical models or requires global LightGBM cross-mandi pooling.

---

## 2. CEDA Support Communication & API Key Extension

Your current CEDA API key expires on **September 27, 2026**. Below is the formal draft to report 504 Gateway Timeouts and request a validity extension.

```text
To: ceda@ashoka.edu.in
Subject: FPOLink TN — 504 Gateway Timeouts on /agmarknet/prices & API Key Extension Request

Dear CEDA Agri-Market Team,

We are developing FPOLink TN (https://github.com/4LPH7/FPOLink), an open-source digital operating system supporting Farmer Producer Organizations (FPOs) and smallholder farmers in Tamil Nadu with price intelligence and harvest aggregation.

We are currently utilizing the CEDA Agmarknet Data Portal API (https://api.ceda.ashoka.edu.in/v1) for price backfills, but have encountered recurring 504 Gateway Timeouts when querying the /agmarknet/prices endpoint.

1. Incident Details:
- Endpoint: POST https://api.ceda.ashoka.edu.in/v1/agmarknet/prices
- Request Payload: {"commodity_id": 14, "state_id": 33, "district_id": [610], "from_date": "2024-01-01", "to_date": "2026-09-20"}
- Observed Behavior: The HTTP request hangs for 70+ seconds before the upstream reverse proxy terminates the connection with a 504 Gateway Timeout.
- Narrower Queries: Smaller date windows (e.g. 7-14 days) occasionally succeed, but larger backfills consistently timeout.
- Recommendation/Question: Does CEDA recommend pagination parameters (e.g., page/limit) or a specific query chunk size for state-level queries?

2. API Key Validity Extension:
Our current API key is scheduled to expire on September 27, 2026.
Could you please extend our API key validity by 12 months to support our upcoming FPO field pilot in Erode district?

Organization: FPOLink TN (Open Source Agricultural Intelligence)
Registered Contact Email: [Your Contact Email]
Key Prefix: [First 8 characters of your API key]

Thank you very much for your invaluable academic work and dataset curation.

Warm regards,
FPOLink Development Team
```

---

## 3. Data.gov.in (OGD) Live API Key Setup

To fetch real-time, daily mandi price feeds alongside CEDA historical records:

1. Register an account on India's Open Government Data platform:  
   **[https://data.gov.in/](https://data.gov.in/)**
2. Navigate to **My Account > API Key Management** and generate a new key.
3. Locate the Agmarknet current daily market price resource:
   - Resource ID: `9ef84268-d588-465a-a308-a864a43d0070`
4. Add your key to `.env`:
   ```bash
   OGD_API_KEY="your-data-gov-in-api-key-here"
   ```
5. Test a live OGD query:
   ```bash
   python -c "from app.data_sources.ogd import OGDProvider; p = OGDProvider(); print(p.fetch_prices('turmeric', 'Erode'))"
   ```

---

## 4. Meta Test App Setup & Webhook Payload Capture (T0.3)

To capture verified Meta Cloud API payloads for T0.3 contract verification:

1. Go to the **[Meta for Developers Console](https://developers.facebook.com/)**.
2. Create a **Business App** and add the **WhatsApp** product.
3. Under **WhatsApp > API Setup**, copy the temporary access token and Test Phone Number ID.
4. Set up an HTTPS forwarding tunnel for local development:
   ```bash
   # Using cloudflared or ngrok:
   cloudflared tunnel --url http://localhost:8000
   ```
5. Configure the Webhook in Meta App Dashboard:
   - Callback URL: `https://<your-subdomain>.trycloudflare.com/api/whatsapp/webhook`
   - Verify Token: Match `WHATSAPP_VERIFY_TOKEN` in `.env`
   - Webhook Subscriptions: Subscribe to `messages`.
6. Send live WhatsApp messages from your mobile phone to the test number:
   - Send: `"வணக்கம்"` (Tamil greeting)
   - Send: `"மஞ்சள் விலை"` (Turmeric price query)
   - Send: `"MENU"`
7. Inspect the incoming request bodies and redact before committing:
   > [!CAUTION]
   - **Ephemeral handling and restricted temporary storage**:
     - Treat raw webhook captures as strictly ephemeral. Use restricted temporary storage outside Git (e.g., a secured temporary directory or in-memory shell buffer).
     - Do not retain raw captures on developer storage; permanently delete all temporary captures and shell artifacts immediately after creating sanitized fixtures and the provenance record.
     - Writing real phone numbers to persistent files, commit history, logs, or fixtures is strictly prohibited under DPDP compliance.
   - **Commit only sanitized fixtures** to `backend/tests/fixtures/` using repository-defined, clearly synthetic non-routable values:
     - Phone numbers / WhatsApp IDs: Replace with repository-defined, clearly synthetic non-routable test numbers (e.g., `"919876543210"` or `"919000000001"`).
     - User profile names: Replace with `"Test Farmer"`.
     - Business Account IDs & Phone Number IDs: Replace with repository-defined synthetic test placeholders (e.g., `"1234567890"` or `"test-phone-id-001"`).
     - Message IDs: Replace with synthetic dummy identifiers (e.g., `"wamid.test.001"`).
     - Contributors must verify that every value and identifier in the fixture is test-only before committing.
   - Target fixture files:
     - `backend/tests/fixtures/meta_webhook_text_real.json` (redacted)
     - `backend/tests/fixtures/meta_webhook_button_reply_real.json` (redacted)
8. Record the provenance details in [docs/data-provenance.md](docs/data-provenance.md) documenting schema structure, capture date, and payload type without exposing real message content or user/account identifiers.
