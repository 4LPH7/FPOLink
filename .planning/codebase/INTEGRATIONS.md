# FPOLink External Integrations

Catalog of third-party APIs, data feeds, messaging gateways, and external system dependencies.

---

## 1. Agricultural Mandi & Price Data Feeds

### A. OGD India (Agmarknet Daily Mandi API)
- **Source**: `data.gov.in` (Ministry of Agriculture & Farmers Welfare)
- **Endpoint**: `https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070`
- **Catalog**: Current Daily Price of Various Commodities from Various Markets (Mandi)
- **Authentication**: API Key via query param `api-key`
- **Adapter**: `backend/app/services/parsers/ogd_parser.py`
- **Granularity**: Daily wholesale mandi modal, min, and max prices per quintal
- **Handling**: Automatic conversion to standard ₹/quintal and ₹/kg, normalized crop canonical names

### B. CEDA Agri-Market Data Portal
- **Source**: Ashoka University Centre for Economic Data and Analysis (CEDA)
- **Endpoint**: `https://agrimarket.ceda.ashoka.edu.in/api/`
- **Authentication**: Bearer Token API Key via environment `CEDA_API_KEY`
- **Adapter**: `backend/app/services/ceda_api.py` and `backend/app/services/parsers/ceda_parser.py`
- **Resilience**: Integrated circuit breaker with exponential backoff on HTTP 504 / gateway timeouts

### C. MandiPrices.co.in Scraper / Feed
- **Source**: `mandiprices.co.in/state/tamil-nadu`
- **Adapter**: `backend/app/services/mandiprices_ingest.py`
- **Purpose**: Fallback / supplementary statewide mandi price coverage for Tamil Nadu markets
- **Handling**: Cached fallback mechanism with HTML table parsing and date sanitization

---

## 2. Weather & Agrometeorology

### Open-Meteo Weather API
- **Endpoint**: `https://api.open-meteo.com/v1/forecast`
- **Service**: `backend/app/services/weather_service.py`
- **Authentication**: Free public tier, no API key required
- **Parameters**: Latitude/Longitude of district headquarters (e.g. Erode: 11.3410, 77.7172)
- **Data Retrieved**:
  - Daily rainfall sum (`precipitation_sum_mm`)
  - Maximum & minimum temperatures (`temperature_2m_max`, `temperature_2m_min`)
  - Relative humidity (`relative_humidity_2m_max`)
  - Weather interpretation codes (WMO code mapped to Tamil/English descriptions)
- **Usage**: Merged into feature store for ML price forecasting and displayed to farmers via bots

---

## 3. Messaging & Bot Gateways

### A. Telegram Bot API
- **Bot Handle**: `@Fpo_Link_Bot` ([t.me/Fpo_Link_Bot](https://t.me/Fpo_Link_Bot))
- **Service**: `backend/app/services/telegram_bot.py` & `backend/app/messaging/telegram.py`
- **API Base**: `https://api.telegram.org/bot<TOKEN>/`
- **Webhook Endpoint**: `POST https://fpolink-api.onrender.com/api/telegram/webhook`
- **Polling Fallback**: `backend/scripts/telegram_poll.py` for local dev
- **Capabilities**:
  - Contact request card (`Send Phone Number`) for automatic farmer phone verification
  - Auto-registration of verified farmers under default FPO when `TELEGRAM_AUTO_REGISTER=true`
  - Inline keyboards for price checking, forecasts, weather, and harvest reporting
  - Slash commands registered: `/start`, `/price`, `/forecast`, `/harvest`, `/weather`, `/buyers`, `/help`

### B. WhatsApp Cloud API (Meta Graph API)
- **API Version**: Graph API `v19.0+` (`https://graph.facebook.com/v19.0/`)
- **Service**: `backend/app/services/whatsapp.py` & `backend/app/services/bot.py`
- **Webhook Endpoint**: `POST /api/whatsapp/webhook` with HMAC-SHA256 signature verification (`X-Hub-Signature-256`)
- **Features**:
  - Transport-agnostic `BotEngine` with session TTL and rate limiting
  - Daily price digest notifications via registered WhatsApp templates
  - Interactive buttons and quick-reply menus for price queries and harvest logging
  - Opt-in / opt-out compliance (Tamil keyword `நிறுத்து` / English `STOP`)
  - Circuit breaker to halt outbound messages if delivery failure thresholds are exceeded

---

## 4. Monitoring & Telemetry

### Sentry
- **Package**: `sentry-sdk[fastapi]`
- **Configuration**: `SENTRY_DSN` in environment
- **Behavior**: Auto-instruments FastAPI HTTP requests, background task exceptions, and worker sweep failures; gracefully bypassed when DSN is empty.
