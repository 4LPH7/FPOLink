# Data Provenance & Fixture Verification Ledger

This document tracks the origin, verification status, and data integrity guarantees for all datasets, fixtures, and ingestion feeds in **FPOLink TN**.

---

## 1. Fixture Inventory & Verification Status

To ensure complete transparency and prevent unverified mock or assumed data from corrupting forecasting models or operational logic, every data file in this repository is cataloged below with its verification level:

| File Path | Status | Source / Schema Authority | Verification Date | Description & Purpose |
|---|---|---|---|---|
| `backend/tests/fixtures/ogd_turmeric_response_synthetic.json` | **Synthetic** | [data.gov.in](https://data.gov.in/) Resource `9ef84268-d588-465a-a308-a864a43d0070` | 2026-09-20 | Modeled on the documented Agmarknet daily mandi JSON schema (Tamil Nadu, Erode: Turmeric & Banana). Used strictly for unit testing parser field extraction, variety extraction, and price unit conversions. **Not real market quotes.** |
| `backend/tests/fixtures/ceda_sample_tamilnadu_synthetic.csv` | **Synthetic** | [CEDA Agri Market Data](https://agrimarket.ceda.ashoka.edu.in/) | 2026-09-20 | Modeled on CEDA historical CSV export schema (columns: State, District, Market, Commodity, Variety, Grade, Min/Max/Modal, Date, Arrival). Hand-crafted multi-month sample for testing CEDA parser and deduplication logic. **Not real market quotes.** |
| `ml/datasets/ceda_sample_tamilnadu_synthetic.csv` | **Synthetic (Sample)** | Internal test suite | 2026-09-20 | Sample file for developer onboarding and dry-run backfills. Tagged automatically with `source='ceda_synthetic'`. |

---

## 2. Sample Data Isolation Guarantee

To protect ML forecasting pipelines and analytics from contamination by synthetic test rows:

1. **Automatic Detection & Tagging**:
   - In `backend/app/data_sources/ceda.py`, `CEDAProvider` inspects the file path.
   - Any CSV file containing `synthetic` or `sample` in its filename is tagged with:
     ```python
     source = "ceda_synthetic"
     ```
   - Standard official backfill files are tagged with `source = "ceda"`.
2. **Explicit Override**:
   - The CLI backfill script (`backend/scripts/backfill_ceda.py`) supports an explicit `--source` parameter (e.g. `--source ceda` vs `--source sample`).
3. **Database Segregation**:
   - In `market_prices`, the unique constraint is:
     ```sql
     (crop_id, market_id, variety_id, price_date, source)
     ```
   - Because `source` is part of the unique identity, `ceda_synthetic` rows are stored separately and will never overwrite, merge with, or mask verified `ceda` or `ogd` observations.
4. **ML Training Filter**:
   - ML training queries strictly filter on `WHERE source IN ('ceda', 'ogd')` and exclude `source LIKE '%synthetic%'`.

---

## 3. Guide: Ingesting Verified Real Mandi Data

### A. Live Daily Ingestion (data.gov.in OGD Agmarknet)

The Open Government Data (OGD) platform hosts live mandi prices from Agmarknet.

1. **Obtain API Key**:
   - Register at [data.gov.in](https://data.gov.in/).
   - Open your profile / dashboard and copy your free API key.
   - Set in your local `.env`:
     ```bash
     OGD_API_KEY=your_actual_api_key_here
     ```
   - **Never commit `.env` or your API key to Git.**
2. **Resource Details**:
   - **Dataset**: *Current Daily Price of Various Commodities from various Markets (Mandi)*
   - **Resource ID**: `9ef84268-d588-465a-a308-a864a43d0070`
   - **Endpoint**: `https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070`
3. **Make a Real Call**:
   ```bash
   curl "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070?api-key=$OGD_API_KEY&format=json&limit=20&filters[State.keyword]=Tamil%20Nadu&filters[District.keyword]=Erode&filters[Commodity.keyword]=Turmeric" -o real_ogd_erode_turmeric.json
   ```
4. **Promoting to Verified Fixture**:
   - Strip the `api-key` parameter from the file or headers.
   - Save the response to `backend/tests/fixtures/ogd_turmeric_response_real.json`.
   - Update this provenance ledger with the exact fetch timestamp and HTTP parameters.

### B. Historical Backfill (CEDA Ashoka University)

The Centre for Economic Data and Analysis (CEDA) at Ashoka University provides 20+ years of standardized Agmarknet records.

1. **Download Official Extract**:
   - Go to [CEDA Agri Market Data Portal](https://agrimarket.ceda.ashoka.edu.in/) (or use [CEDA API](https://api.ceda.ashoka.edu.in)).
   - Select:
     - **State**: `Tamil Nadu`
     - **District**: `Erode`
     - **Commodity**: `Turmeric`, `Banana`
     - **Date Range**: Select maximum available range (e.g. 2018–present or 2000–present).
   - Click **Download Data (CSV)**.
2. **Place in Dataset Directory**:
   - Move the downloaded file to: `ml/datasets/ceda_erode_turmeric_real.csv`.
3. **Run Real Backfill**:
   ```bash
   python backend/scripts/backfill_ceda.py \
     --csv-path ml/datasets/ceda_erode_turmeric_real.csv \
     --crop turmeric \
     --district Erode \
     --source ceda
   ```
4. **Audit Market Coverage**:
   - After backfilling, run the audit query to evaluate data density:
     ```bash
     python backend/scripts/check_market_coverage.py --crop turmeric --district Erode
     ```
   - Review which markets report regularly (e.g. Erode Mandi, Gobichettipalayam, Perundurai) to inform ML model selection.

---

## 4. WhatsApp Webhook Fixture Provenance Ledger (T0.3)

To ensure contract test reliability without leaking real phone numbers or customer data, WhatsApp webhook fixtures are derived directly from the official Meta Cloud API v23.0 webhook payload specification with PII sanitized:

| Fixture File | Type | Origin / Source Schema | Sanitization Applied | Test Coverage |
|---|---|---|---|---|
| `backend/tests/fixtures/whatsapp/text_en.json` | Inbound Text | Meta Cloud API Webhook (`messages[].type='text'`) | Phone masked to `919000000001`, name `Ravi Kumar`, mock WAMID | `test_whatsapp_fixtures.py::test_text_en_fixture` |
| `backend/tests/fixtures/whatsapp/text_ta.json` | Inbound Text | Meta Cloud API Webhook (`messages[].type='text'`) | Phone masked to `919876543210`, name `முத்துசாமி`, body `விலை` | `test_whatsapp_fixtures.py::test_text_ta_fixture` |
| `backend/tests/fixtures/whatsapp/button_price.json` | Interactive Button | Meta Cloud API Webhook (`interactive.type='button_reply'`) | Button ID `b_price`, masked recipient | `test_whatsapp_fixtures.py::test_button_price_fixture` |
| `backend/tests/fixtures/whatsapp/button_harvest.json` | Interactive Button | Meta Cloud API Webhook (`interactive.type='button_reply'`) | Button ID `b_harvest`, masked recipient | `test_whatsapp_fixtures.py::test_button_harvest_fixture` |
| `backend/tests/fixtures/whatsapp/unsupported_voice.json` | Voice / Audio | Meta Cloud API Webhook (`messages[].type='voice'`) | Synthetic media ID, OGG Opus codec | `test_whatsapp_fixtures.py::test_unsupported_voice_fixture` |
| `backend/tests/fixtures/whatsapp/unsupported_image.json` | Media Image | Meta Cloud API Webhook (`messages[].type='image'`) | Synthetic media ID, JPEG mime | `test_whatsapp_fixtures.py::test_unsupported_image_fixture` |
| `backend/tests/fixtures/whatsapp/status_delivered.json` | Status Callback | Meta Cloud API Webhook (`statuses[].status='delivered'`) | Billable CBP utility pricing metadata | `test_whatsapp_fixtures.py::test_status_delivered_fixture` |
| `backend/tests/fixtures/whatsapp/status_read.json` | Status Callback | Meta Cloud API Webhook (`statuses[].status='read'`) | Masked recipient ID | `test_whatsapp_fixtures.py::test_status_read_fixture` |
| `backend/tests/fixtures/whatsapp/status_failed.json` | Status Callback | Meta Cloud API Webhook (`statuses[].status='failed'`) | Standard Meta error code `131026` (Undeliverable) | `test_whatsapp_fixtures.py::test_status_failed_fixture` |
