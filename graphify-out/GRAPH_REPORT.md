# Graph Report - FPOLink  (2026-09-23)

## Corpus Check
- 153 files · ~49,692 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 20 file(s) not represented in the graph (top: (none) 14, .csv 2, .example 1)

## Summary
- 1318 nodes · 3249 edges · 77 communities (57 shown, 20 thin omitted)
- Extraction: 91% EXTRACTED · 9% INFERRED · 0% AMBIGUOUS · INFERRED: 307 edges (avg confidence: 0.94)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ab10fa57`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- services/prices.py
- InMemoryServices
- models/__init__.py
- test_units.py
- DbBotServices
- test_harvest_service_and_api.py
- alembic
- farmers.py
- Farmer
- datetime
- deps.py
- test_whatsapp_bot.py
- test_whatsapp_onboarding.py
- BotEngine
- test_whatsapp_wiring_and_killswitch.py
- test_whatsapp_status_webhook.py
- api/fpo.py
- BotServices
- page.tsx
- api/auth.py
- CEDAAPIProvider
- weather_service.py
- test_whatsapp_harvest_flow.py
- CEDAProvider
- test_parsers.py
- User
- Settings
- compilerOptions
- Crop
- TestClient
- IngestionService
- DataSourceRegistry
- whatsapp_cloud.py
- package.json
- normalise_phone
- test_whatsapp_payload_contracts.py
- OGDProvider
- worker.py
- PriceChart.tsx
- crops.py
- price.py
- layout.tsx
- dependencies
- devDependencies
- check_market_coverage.py
- scripts
- bot.py
- WhatsApp Integration: Task List
- PriceRecord
- test_farmers_api.py
- test_fpo_api.py
- next.config.mjs
- postcss.config.mjs
- core/__init__.py
- api/whatsapp.py
- entrypoint.sh
- next-env.d.ts
- WhatsAppCloudChannel
- Operational Playbook: Manual CEDA Backfill, Coverage Audit & External Feeds
- FPOLink TN
- Implementation Plan: WhatsApp Integration for FPOLink TN
- FakeChannel
- Data Provenance & Fixture Verification Ledger
- Task List
- Quick Start
- .mark_notice_delivered
- rules/graphify.md
- workflows/graphify.md

## God Nodes (most connected - your core abstractions)
1. `User` - 58 edges
2. `DbBotServices` - 52 edges
3. `Farmer` - 49 edges
4. `Crop` - 40 edges
5. `PriceRecord` - 35 edges
6. `BotEngine` - 35 edges
7. `MarketPrice` - 31 edges
8. `InMemoryServices` - 31 edges
9. `Market` - 28 edges
10. `UserRole` - 28 edges

## Surprising Connections (you probably didn't know these)
- `2. Sample Data Isolation Guarantee` --references--> `CEDAProvider`  [INFERRED]
  docs/data-provenance.md → backend/app/data_sources/ceda.py
- `Step 1: Download from CEDA Portal` --references--> `CEDAProvider`  [INFERRED]
  docs/manual-ceda-backfill-guide.md → backend/app/data_sources/ceda.py
- `Phase 3: Harvest submission by chat` --references--> `DbBotServices`  [INFERRED]
  tasks/plan.md → backend/app/services/db_bot_services.py
- `Testing Strategy` --references--> `DbBotServices`  [INFERRED]
  tasks/plan.md → backend/app/services/db_bot_services.py
- `Files (copy into `backend/`, same paths)` --references--> `InboundMessage`  [INFERRED]
  docs/WHATSAPP_SETUP.md → backend/app/messaging/base.py

## Import Cycles
- None detected.

## Communities (77 total, 20 thin omitted)

### Community 0 - "services/prices.py"
Cohesion: 0.10
Nodes (33): latest_prices(), price_anomalies(), price_history(), price_trend(), get, Session, Price endpoints — latest prices, history, trends, anomalies., Get latest prices for all crops in a district. (+25 more)

### Community 1 - "InMemoryServices"
Cohesion: 0.07
Nodes (16): Farmer, InMemoryServices, PriceInfo, Retrieve newest available price for crop in district, with state fallback.…, Check if price date exceeds staleness threshold., Match farmer by last 10 digits of phone., env(), make_services() (+8 more)

### Community 2 - "models/__init__.py"
Cohesion: 0.12
Nodes (30): AggregationBatch, BatchItem, BatchStatus, Base, str, TimestampMixin, Buyer, BuyerRequirement (+22 more)

### Community 3 - "test_units.py"
Cohesion: 0.23
Nodes (13): convert_from_per_kg(), convert_to_per_kg(), Decimal, Unit conversion utilities for agricultural commodities., Convert a price from any unit to Rs/kg. Args: price: Price in the original unit…, Convert Rs/kg to another unit., Tests for unit conversions., test_convert_from_per_kg() (+5 more)

### Community 4 - "DbBotServices"
Cohesion: 0.06
Nodes (36): asyncio, Prediction, Base, ConversationState, Base, Log incoming WhatsApp webhook message IDs for deduplication / idempotency., Store active conversation state machines per WhatsApp ID with TTL., WhatsAppInbound (+28 more)

### Community 5 - "test_harvest_service_and_api.py"
Cohesion: 0.07
Nodes (57): create_harvest(), get_harvest(), list_harvests(), date, get, Session, UUID, Harvest submission, querying, and verification endpoints. (+49 more)

### Community 7 - "farmers.py"
Cohesion: 0.14
Nodes (32): create(), _enforce_farmer_fpo_scope(), get_one(), get_whatsapp_invite(), list_all(), get, put, Session (+24 more)

### Community 8 - "Farmer"
Cohesion: 0.13
Nodes (24): Farm, Base, Farmer, Base, OutboundMessage, WhatsApp bot models for message idempotency, conversation state, and outbound…, Log outbound messages sent via Meta Cloud API for auditing, status updates, and…, get_dashboard_stats() (+16 more)

### Community 9 - "datetime"
Cohesion: 0.11
Nodes (25): ABC, Run migrations in 'offline' mode. This configures the context with just a URL…, Run migrations in 'online' mode. In this scenario we need to create an Engine…, run_migrations_offline(), run_migrations_online(), MarketDataProvider, Base market data provider interface. All data source adapters inherit from this…, Abstract base class for market data providers. (+17 more)

### Community 10 - "deps.py"
Cohesion: 0.07
Nodes (29): Session, Admin endpoints — manual ingestion trigger, system status., Manually trigger price data ingestion (admin only)., trigger_ingestion(), get_whatsapp_usage(), get, Admin endpoints for WhatsApp usage tracking, cost audits, and circuit breaker…, Get aggregated WhatsApp message usage, delivery rates, cost breakdown, and… (+21 more)

### Community 11 - "test_whatsapp_bot.py"
Cohesion: 0.23
Nodes (16): parse_qty(), button_payload(), post(), test_alerts_opt_in_and_out(), test_cancel_clears_state(), test_duplicate_delivery_processed_once(), test_harvest_flow_end_to_end(), test_menu_button_tap_triggers_price() (+8 more)

### Community 12 - "test_whatsapp_onboarding.py"
Cohesion: 0.14
Nodes (19): WhatsAppSettings, build_payload(), FailingChannel, MockChannel, post_webhook(), TestClient, Tests for WhatsApp Phase 2: Onboarding, Identity, Consent, and Scoping (T2.1 -…, T2.3: STOP and நிறுத்து take effect immediately from within active harvest flow. (+11 more)

### Community 13 - "BotEngine"
Cohesion: 0.15
Nodes (14): InboundMessage, MessageChannel, Protocol, BotEngine, ConvState, normalize_phone(), WhatsApp ids look like 919876543210. Match on the last 10 digits (India-only…, Entry point for background tasks: never raises. (+6 more)

### Community 14 - "test_whatsapp_wiring_and_killswitch.py"
Cohesion: 0.11
Nodes (17): _bot(), get_bot(), Return active BotEngine or raise 503 if WhatsApp is disabled via kill switch., Unit tests for WhatsApp bot wiring, settings validation, and kill switch., When WHATSAPP_ENABLED is False, both GET and POST webhooks return 503., get_bot() returns an active BotEngine when enabled., test_get_bot_dependency_wired(), test_kill_switch_returns_503() (+9 more)

### Community 15 - "test_whatsapp_status_webhook.py"
Cohesion: 0.08
Nodes (29): get_usage_service(), Track recipient delivery health and mark unreachable numbers after repeated…, WhatsAppRecipientStatus, Processes Meta status callbacks (sent, delivered, read, failed) and updates…, WhatsAppStatusService, Calculates monthly message volumes, applies configurable cost rates, and gates…, WhatsAppUsageService, compile_jsonb_sqlite() (+21 more)

### Community 16 - "api/fpo.py"
Cohesion: 0.19
Nodes (23): create(), dashboard(), get_one(), list_all(), get, put, Session, FPO management endpoints. (+15 more)

### Community 17 - "BotServices"
Cohesion: 0.09
Nodes (10): BotServices, Decimal, Protocol, Everything the bot needs from your app. Implement against your DB/services., Atomically record message_id; False if already seen (Meta retries webhooks)., Store opt-in/out with a timestamp (consent evidence for DPDP / WhatsApp opt-in)., Atomically claim notice lease. Returns True only if claim was acquired., Record timestamp when first-contact DPDP notice was confirmed delivered. (+2 more)

### Community 18 - "page.tsx"
Cohesion: 0.14
Nodes (19): Home(), AggregationSummary(), AggregationSummaryProps, AlertPanel(), AlertPanelProps, FarmerInviteCard(), FarmerInviteCardProps, SAMPLE_FARMERS (+11 more)

### Community 19 - "api/auth.py"
Cohesion: 0.11
Nodes (32): get_me(), login(), get, Session, Authentication endpoints — register, login, refresh., Get current authenticated user's profile., Authenticate user and return JWT tokens., Get new access token using refresh token. (+24 more)

### Community 20 - "CEDAAPIProvider"
Cohesion: 0.07
Nodes (28): CEDAAPIProvider, Any, date, Execute HTTP request with short timeout, retries, and circuit breaker., Retrieve list of all commodities: [{"id": int, "name": str}]., Retrieve geographies: [{"state_id": int, "state_name": str, "districts": [...]}], Fetch prices from CEDA API with narrow query targeting., Parse CEDA API JSON item into standardized PriceRecord. (+20 more)

### Community 21 - "weather_service.py"
Cohesion: 0.09
Nodes (19): NASAPowerProvider, Any, date, NASA POWER provider — long-term weather history for ML training. Free, no API…, Fetch long-term weather history from NASA POWER., Fetch daily weather data from NASA POWER., Any, date (+11 more)

### Community 22 - "test_whatsapp_harvest_flow.py"
Cohesion: 0.11
Nodes (13): Button, FakeChannel, build_payload(), compile_jsonb_sqlite(), compile_uuid_sqlite(), MockChannel, post_webhook(), compiles (+5 more)

### Community 23 - "CEDAProvider"
Cohesion: 0.14
Nodes (11): CEDAProvider, date, Decimal, Parse a single CSV row into a PriceRecord., Parse CEDA historical CSV data for price backfill., Try multiple possible column names., Try multiple date formats., Parse CEDA CSV and return standardized price records. Expected CSV columns (may… (+3 more)

### Community 24 - "test_parsers.py"
Cohesion: 0.15
Nodes (19): days_to_nearest_festival(), get_festival_features(), is_festival(), date, Tamil Nadu holiday/festival features for price prediction. Uses Python…, Check if a date is a known festival day., Days until the nearest festival within a window. Returns window+1 if none., Generate festival-related features for a given date. (+11 more)

### Community 25 - "User"
Cohesion: 0.16
Nodes (17): get_current_user(), Session, Extract and validate the current user from the JWT token., Dependency factory: restrict endpoint to specific roles., require_role(), Base, User, create_test_app() (+9 more)

### Community 26 - "Settings"
Cohesion: 0.12
Nodes (16): Application settings loaded from environment variables and .env file., Settings, Tests for production security enforcement in configuration., test_development_allows_default_secret_key(), test_production_accepts_strong_secret_key(), test_production_refuses_default_secret_key(), In production with WhatsApp enabled, missing secrets must raise a fatal…, In production with WhatsApp disabled, missing secrets should not raise. (+8 more)

### Community 27 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 28 - "Crop"
Cohesion: 0.07
Nodes (52): Crop, Base, FPO, Base, Market, MarketPrice, Base, Market price model — daily commodity prices from various sources. (+44 more)

### Community 29 - "TestClient"
Cohesion: 0.18
Nodes (6): TestClient, Authentication endpoint tests., TestLogin, TestProtectedRoutes, TestRefresh, TestRegister

### Community 30 - "IngestionService"
Cohesion: 0.17
Nodes (13): IngestionLog, Base, Base, RawIngest, IngestionService, date, Store price records in the database, deduplicating by unique constraint., Find or create a market entry. (+5 more)

### Community 31 - "DataSourceRegistry"
Cohesion: 0.10
Nodes (15): ManualProvider, date, Decimal, Handles manually-entered price data from FPO staff., Manual prices are entered via API, not fetched. This provider returns an empty…, Create a PriceRecord from manual entry., DataSourceRegistry, date (+7 more)

### Community 32 - "whatsapp_cloud.py"
Cohesion: 0.13
Nodes (19): receive(), mask(), Transport-agnostic messaging types. Bot logic depends on these, not on WhatsApp., Mask a phone number for logs (phone numbers are personal data under DPDP)., StatusUpdate, Messaging package: transport-agnostic types and WhatsApp Cloud API adapter., parse_status_updates(), parse_webhook() (+11 more)

### Community 33 - "package.json"
Cohesion: 0.12
Nodes (14): name, private, version, config, autoprefixer, clsx, postcss, react-dom (+6 more)

### Community 34 - "normalise_phone"
Cohesion: 0.05
Nodes (29): date, Decimal, Session, Calculate modal price change between latest price on/before target_date and…, Find opted-in, reachable farmers growing the specific crop., Verify whether an alert has already been sent to this farmer today (limit…, Scan for price swings >= threshold and dispatch alerts. Guarantees: 1. Checks…, date (+21 more)

### Community 35 - "test_whatsapp_payload_contracts.py"
Cohesion: 0.17
Nodes (15): client(), create_tables(), fixture, Create all tables before tests, drop after., Provide a test client using the shared test database session., anyio, mock, Contract tests for WhatsApp Cloud API outgoing payloads using respx. (+7 more)

### Community 36 - "OGDProvider"
Cohesion: 0.24
Nodes (6): OGDProvider, date, Case-tolerant field retriever., Fetch daily mandi prices from data.gov.in OGD API., Fetch prices from data.gov.in API., Parse an OGD API record into a PriceRecord.

### Community 37 - "worker.py"
Cohesion: 0.16
Nodes (17): apscheduler_schedulers_blocking, get_wa_settings(), main(), FPOLink TN — Background Worker Runs scheduled tasks in a separate container.…, Fetch daily prices from configured data sources., # TODO: Import and call ingestion service, Fetch weather data from Open-Meteo / NASA POWER., # TODO: Import and call weather service (+9 more)

### Community 38 - "PriceChart.tsx"
Cohesion: 0.21
Nodes (10): MandiPricesTable(), MandiPricesTableProps, PriceChart(), PriceChartProps, BANANA_DATA_30D, MANDI_DATA, MandiRow, PricePoint (+2 more)

### Community 39 - "crops.py"
Cohesion: 0.31
Nodes (8): list_crops(), get, Session, Crop listing endpoints., List all configured crops., CropListResponse, CropResponse, BaseModel

### Community 40 - "price.py"
Cohesion: 0.39
Nodes (7): ManualPriceEntry, MarketPriceResponse, PriceHistoryPoint, PriceHistoryResponse, PriceTrend, BaseModel, Price-related request/response schemas.

### Community 41 - "layout.tsx"
Cohesion: 0.25
Nodes (4): frontend_app_globals, metadata, viewport, next

### Community 42 - "dependencies"
Cohesion: 0.25
Nodes (8): dependencies, clsx, lucide-react, next, react, react-dom, recharts, tailwind-merge

### Community 43 - "devDependencies"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

### Community 44 - "check_market_coverage.py"
Cohesion: 0.22
Nodes (12): argparse, check_coverage(), main(), print_coverage_report(), Market price data coverage analyzer for FPOLink TN. Checks monthly price record…, Execute monthly coverage query across markets., Format and print coverage statistics and advisory., Tests for the market coverage audit script. (+4 more)

### Community 45 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, start

### Community 46 - "bot.py"
Cohesion: 0.29
Nodes (10): crop_name(), detect_crop(), detect_intent(), format_price(), _match(), WhatsApp bot engine. Transport-agnostic: depends only on MessageChannel (send)…, _tokens(), test_intent_and_crop_detection() (+2 more)

### Community 47 - "WhatsApp Integration: Task List"
Cohesion: 0.17
Nodes (12): Checkpoint A: end-to-end from a real phone; CI green; no secrets in repo, Checkpoint B: harvest submitted by chat is visible to FPO staff, Checkpoint C: dry run with 3 test farmers, Checkpoint D: staging E2E with a real phone, Phase 0: De-risk external dependencies (start now, in parallel), Phase 1: Vertical slice, PRICE returns a real price (Code-Complete, Pending Live Verification), Phase 2: Onboarding, identity, consent, Phase 3: Harvest by chat (+4 more)

### Community 48 - "PriceRecord"
Cohesion: 0.14
Nodes (21): PriceRecord, date, Standardized price record from any data source., Fetch price records for a crop in a district within a date range., clean_price_records(), detect_anomaly_mad(), _normalize_record(), Decimal (+13 more)

### Community 54 - "api/whatsapp.py"
Cohesion: 0.22
Nodes (10): _channel(), get_channel(), get_status_service(), get, WhatsApp Cloud API webhook. GET /api/whatsapp/webhook -> Meta's one-time…, _status_service(), verify(), dataclasses (+2 more)

### Community 65 - "WhatsAppCloudChannel"
Cohesion: 0.29
Nodes (4): AsyncClient, Business-initiated message (e.g. daily digest). Template must be approved by…, Send template and return tuple of (success, meta_message_id)., WhatsAppCloudChannel

### Community 66 - "Operational Playbook: Manual CEDA Backfill, Coverage Audit & External Feeds"
Cohesion: 0.22
Nodes (8): 1. Manual CEDA CSV Export & Ingestion, 2. CEDA Support Communication & API Key Extension, 3. Data.gov.in (OGD) Live API Key Setup, 4. Meta Test App Setup & Webhook Payload Capture (T0.3), Operational Playbook: Manual CEDA Backfill, Coverage Audit & External Feeds, Step 1: Download from CEDA Portal, Step 2: Ingest with Verified `--source ceda` Tag, Step 3: Run the Coverage Audit

### Community 67 - "FPOLink TN"
Cohesion: 0.25
Nodes (8): Architecture, Data Sourcing: Real vs. Synthetic Fixtures, FPOLink TN, Language Support, License, Modules, Obtaining Real Mandi Data, Tech Stack

### Community 68 - "Implementation Plan: WhatsApp Integration for FPOLink TN"
Cohesion: 0.25
Nodes (8): Agent Working Rules (paste at the top of every agent task), Constraints, Dates that matter, Implementation Plan: WhatsApp Integration for FPOLink TN, Open Questions (need your answers), Overview, Risks and Mitigations, Testing Strategy

### Community 69 - "FakeChannel"
Cohesion: 0.33
Nodes (4): FakeChannel, anyio, Daily digest must abort immediately when circuit breaker is tripped., test_daily_digest_aborts_when_circuit_breaker_tripped()

### Community 70 - "Data Provenance & Fixture Verification Ledger"
Cohesion: 0.29
Nodes (6): 1. Fixture Inventory & Verification Status, 2. Sample Data Isolation Guarantee, 3. Guide: Ingesting Verified Real Mandi Data, A. Live Daily Ingestion (data.gov.in OGD Agmarknet), B. Historical Backfill (CEDA Ashoka University), Data Provenance & Fixture Verification Ledger

### Community 71 - "Task List"
Cohesion: 0.29
Nodes (7): Later backlog (only if the pilot justifies it), Phase 2: Onboarding, identity and consent, Phase 3: Harvest submission by chat, Phase 4: Proactive messages (digest and alerts) with cost control, Phase 5: Production readiness, Phase 6: Pilot (10-20 farmers, one FPO, 2 weeks), Task List

### Community 72 - "Quick Start"
Cohesion: 0.40
Nodes (5): Access, Database Seeding & Authentication, Prerequisites, Quick Start, Setup

## Knowledge Gaps
- **105 isolated node(s):** `entrypoint.sh script`, `metadata`, `viewport`, `AggregationSummaryProps`, `AlertPanelProps` (+100 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 571 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **20 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DbBotServices` connect `DbBotServices` to `InMemoryServices`, `Implementation Plan: WhatsApp Integration for FPOLink TN`, `test_harvest_service_and_api.py`, `Task List`, `Farmer`, `.mark_notice_delivered`, `BotEngine`, `test_whatsapp_wiring_and_killswitch.py`, `test_whatsapp_status_webhook.py`, `WhatsApp Integration: Task List`, `api/whatsapp.py`, `test_whatsapp_harvest_flow.py`, `User`, `Crop`?**
  _High betweenness centrality (0.125) - this node is a cross-community bridge._
- **Why does `CEDAAPIProvider` connect `CEDAAPIProvider` to `PriceRecord`, `datetime`, `DataSourceRegistry`?**
  _High betweenness centrality (0.057) - this node is a cross-community bridge._
- **Why does `User` connect `User` to `models/__init__.py`, `DbBotServices`, `test_harvest_service_and_api.py`, `farmers.py`, `Farmer`, `deps.py`, `test_whatsapp_status_webhook.py`, `api/fpo.py`, `api/auth.py`, `test_whatsapp_harvest_flow.py`, `Crop`?**
  _High betweenness centrality (0.052) - this node is a cross-community bridge._
- **Are the 32 inferred relationships involving `User` (e.g. with `trigger_ingestion()` and `get_whatsapp_usage()`) actually correct?**
  _`User` has 32 INFERRED edges - model-reasoned connections that need verification._
- **Are the 28 inferred relationships involving `DbBotServices` (e.g. with `_bot()` and `Crop`) actually correct?**
  _`DbBotServices` has 28 INFERRED edges - model-reasoned connections that need verification._
- **Are the 23 inferred relationships involving `Farmer` (e.g. with `create()` and `update()`) actually correct?**
  _`Farmer` has 23 INFERRED edges - model-reasoned connections that need verification._
- **What connects `entrypoint.sh script`, `metadata`, `viewport` to the rest of the system?**
  _105 weakly-connected nodes found - possible documentation gaps or missing edges._