# Graph Report - FPOLink  (2026-09-25)

## Corpus Check
- 267 files · ~109,815 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 20 file(s) not represented in the graph (top: (none) 14, .csv 2, .example 1)

## Summary
- 2348 nodes · 5982 edges · 122 communities (98 shown, 24 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 576 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `ad7c40e4`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- InMemoryServices
- Step-by-Step Production Runbook
- sqlalchemy
- test_units.py
- DbBotServices
- test_harvest_service_and_api.py
- alembic
- api/farmers.py
- PriceMoveAlertService
- datetime
- typing
- test_whatsapp_bot.py
- test_whatsapp_onboarding.py
- BotEngine
- crop_resolver.py
- test_whatsapp_status_webhook.py
- fpo_service.py
- BotServices
- app/page.tsx
- api/auth.py
- test_ceda_api.py
- weather_service.py
- MockChannel
- CEDAProvider
- extract_features_for_series
- admin/page.tsx
- Settings
- compilerOptions
- User
- TestClient
- Crop
- DataSourceRegistry
- api/whatsapp.py
- package.json
- commodities.py
- test_send_buttons_contract
- cn
- worker.py
- api.ts
- v1/crops.py
- test_whatsapp_price_alerts.py
- react
- models/crop.py
- v1/intelligence.py
- replay_raw_ingestion.py
- District
- bot.py
- WhatsApp Integration: Task List
- PriceRecord
- test_farmers_api.py
- test_fpo_api.py
- next.config.mjs
- postcss.config.mjs
- core/__init__.py
- test_retention.py
- entrypoint.sh
- next-env.d.ts
- v1/geography.py
- Operational Playbook: Manual CEDA Backfill, Coverage Audit & External Feeds
- FPOLink TN
- Implementation Plan: WhatsApp Integration for FPOLink TN
- FakeChannel
- README.md
- test_whatsapp_usage_and_circuit_breaker.py
- 1. Architectural Pillars
- test_inbound_sweep.py
- parse_webhook
- rules/graphify.md
- workflows/graphify.md
- test_ingestion_center_api.py
- CEDAAPIProvider
- Production Hosting Guide: Oracle Cloud Always Free + Cloudflare Tunnel
- register_whatsapp_templates.py
- ensureToken
- calculate_quality_score
- markets.py
- Detailed Task Specifications
- services/prices.py
- 2. Gaps Identified & Remediated During Audit
- resolve_market
- components.json
- 3. Verify First Successful Requests
- 2. Locked Architectural Decisions
- FPOLink TN — Production Deployment Guide
- Detailed Task Specifications
- WhatsAppCloudChannel
- test_source_safety.py
- Meta WhatsApp Cloud API — Production Setup Checklist
- run_inbound_sweep
- 2. Locked Architectural Decisions
- 2. Locked Decisions & Core Tenets
- receive
- pydantic
- Human Checkpoints Operational Guide (Checkpoints A, B, C, D)
- FPOLink TN: 2-Week Field Pilot Runbook (Final: Pilot)
- 1. Resolution of Core Operational Questions
- 1. Emergency WhatsApp Kill Switch
- lucide-react
- Phase 5 — Production Readiness: CONTEXT.md
- env
- dependencies
- Market Price Data Coverage & Readiness Audit (T0.5)
- MockChannel
- devDependencies
- TestBotModelsMetadata
- marketData.ts
- entrypoint.prod.sh
- Task List
- FPOLink WhatsApp bot: integration guide
- db
- trigger_ingestion
- .mark_notice_delivered
- compile_jsonb_sqlite
- .first_time

## God Nodes (most connected - your core abstractions)
1. `User` - 89 edges
2. `Crop` - 83 edges
3. `Market` - 78 edges
4. `MarketPrice` - 70 edges
5. `DbBotServices` - 60 edges
6. `Farmer` - 54 edges
7. `PriceRecord` - 47 edges
8. `TimestampMixin` - 40 edges
9. `BotEngine` - 40 edges
10. `FPO` - 37 edges

## Surprising Connections (you probably didn't know these)
- `Step 2: Route Hostnames` --references--> `dashboard()`  [INFERRED]
  docs/HOSTING.md → backend/app/api/fpo.py
- `D7: `.env.example` Update` --references--> `Settings`  [INFERRED]
  tasks/5-CONTEXT.md → backend/app/config.py
- `2. Sample Data Isolation Guarantee` --references--> `CEDAProvider`  [INFERRED]
  docs/data-provenance.md → backend/app/data_sources/ceda.py
- `Step 1: Download from CEDA Portal` --references--> `CEDAProvider`  [INFERRED]
  docs/manual-ceda-backfill-guide.md → backend/app/data_sources/ceda.py
- `Phase 0: De-risk the external dependencies (start immediately, in parallel)` --references--> `parse_webhook()`  [INFERRED]
  tasks/plan.md → backend/app/messaging/whatsapp_cloud.py

## Import Cycles
- None detected.

## Communities (122 total, 24 thin omitted)

### Community 0 - "InMemoryServices"
Cohesion: 0.10
Nodes (8): ConvState, InMemoryServices, Retrieve conversation state, returning None if expired beyond 30m TTL., T3.1 & T3.2: Duplicate delivery of final confirmation creates only 1 harvest., test_harvest_webhook_retry_idempotency(), anyio, Verify claim_notice only allows one concurrent sender, and failure leaves…, test_notice_atomic_claim_concurrency_and_retry()

### Community 1 - "Step-by-Step Production Runbook"
Cohesion: 0.12
Nodes (15): Check if price date exceeds staleness threshold., English (`en`) Template:, Optional: Template Specification for `price_move_alert`, Step 1: Create Meta Business Account, Step 2: Create Meta Developer App, Step 3: Business Verification, Step 4: Phone Number Registration, Step 5: System User Token Generation (+7 more)

### Community 2 - "sqlalchemy"
Cohesion: 0.10
Nodes (36): Run migrations in 'offline' mode. This configures the context with just a URL…, Run migrations in 'online' mode. In this scenario we need to create an Engine…, run_migrations_offline(), run_migrations_online(), AggregationBatch, BatchItem, BatchStatus, Base (+28 more)

### Community 3 - "test_units.py"
Cohesion: 0.23
Nodes (13): convert_from_per_kg(), convert_to_per_kg(), Decimal, Unit conversion utilities for agricultural commodities., Convert a price from any unit to Rs/kg. Args: price: Price in the original unit…, Convert Rs/kg to another unit., Tests for unit conversions., test_convert_from_per_kg() (+5 more)

### Community 4 - "DbBotServices"
Cohesion: 0.05
Nodes (49): asyncio, Farmer, Base, DbBotServices, Decimal, Database implementation of BotServices protocol for FPOLink. Provides atomic…, Atomically claim notice sending lease for farmer. Return True if claim acquired., Release leased claim after send failure so future inbound messages can retry. (+41 more)

### Community 5 - "test_harvest_service_and_api.py"
Cohesion: 0.08
Nodes (57): create_harvest(), get_harvest(), get_harvest_aggregation(), list_harvests(), date, get, Session, UUID (+49 more)

### Community 7 - "api/farmers.py"
Cohesion: 0.07
Nodes (57): create(), _enforce_farmer_fpo_scope(), get_one(), get_whatsapp_invite(), list_all(), get, put, Session (+49 more)

### Community 8 - "PriceMoveAlertService"
Cohesion: 0.22
Nodes (9): PriceMoveAlertService, date, Decimal, Session, Calculate modal price change between latest price on/before target_date and…, Find opted-in, reachable farmers growing the specific crop., Verify whether an alert has already been sent to this farmer today (limit…, Detects modal price shifts >= threshold (default 5%) and dispatches alerts max… (+1 more)

### Community 9 - "datetime"
Cohesion: 0.17
Nodes (15): ABC, MarketDataProvider, Base market data provider interface. All data source adapters inherit from this…, Abstract base class for market data providers., Check if this data source is currently accessible., CEDA Data Portal API provider (Ashoka University). Programmatic access to raw…, CEDA Agri-Market provider (Ashoka University). Parses the historical CSV data…, Manual data provider — FPO staff manually enters observed prices. (+7 more)

### Community 10 - "typing"
Cohesion: 0.08
Nodes (27): Admin endpoints — manual ingestion trigger, system status., get_buyers(), get, Crop listing endpoints., UUID, FastAPI dependencies for authentication, authorization, and multi-tenant…, Dependency factory: restrict endpoint to specific roles. Automatically maps…, require_role() (+19 more)

### Community 11 - "test_whatsapp_bot.py"
Cohesion: 0.22
Nodes (15): button_payload(), post(), test_alerts_opt_in_and_out(), test_cancel_clears_state(), test_duplicate_delivery_processed_once(), test_harvest_flow_end_to_end(), test_menu_button_tap_triggers_price(), test_menu_has_three_buttons() (+7 more)

### Community 12 - "test_whatsapp_onboarding.py"
Cohesion: 0.11
Nodes (21): WhatsAppSettings, Farmer, PriceInfo, Retrieve newest available price for crop in district, with state fallback.…, Match farmer by last 10 digits of phone., build_payload(), FailingChannel, MockChannel (+13 more)

### Community 13 - "BotEngine"
Cohesion: 0.21
Nodes (10): Button, InboundMessage, MessageChannel, Protocol, BotEngine, normalize_phone(), WhatsApp ids look like 919876543210. Match on the last 10 digits (India-only…, Entry point for background tasks: never raises. (+2 more)

### Community 14 - "crop_resolver.py"
Cohesion: 0.07
Nodes (43): CropAlias, Base, CropSourceMapping, MarketSourceMapping, Base, VarietySourceMapping, Base, VarietyAlias (+35 more)

### Community 15 - "test_whatsapp_status_webhook.py"
Cohesion: 0.07
Nodes (42): mask(), Transport-agnostic messaging types. Bot logic depends on these, not on WhatsApp., Mask a phone number for logs (phone numbers are personal data under DPDP)., StatusUpdate, Messaging package: transport-agnostic types and WhatsApp Cloud API adapter., WhatsApp Cloud API (Meta) adapter: webhook parsing, signature check, sending., Farm, Base (+34 more)

### Community 16 - "fpo_service.py"
Cohesion: 0.14
Nodes (37): create(), dashboard(), get_one(), list_all(), get, put, Session, FPO management endpoints. (+29 more)

### Community 17 - "BotServices"
Cohesion: 0.10
Nodes (9): BotServices, Protocol, Everything the bot needs from your app. Implement against your DB/services., Atomically record message_id; False if already seen (Meta retries webhooks)., Store opt-in/out with a timestamp (consent evidence for DPDP / WhatsApp opt-in)., Atomically claim notice lease. Returns True only if claim was acquired., Record timestamp when first-contact DPDP notice was confirmed delivered., Release leased claim after send failure so future inbound messages can retry. (+1 more)

### Community 18 - "app/page.tsx"
Cohesion: 0.20
Nodes (16): DashboardHome(), loadKPIs(), WhatsAppPage(), AlertPanel(), buildAlerts(), AlertPanelProps, LiveAlert, MandiPricesTable() (+8 more)

### Community 19 - "api/auth.py"
Cohesion: 0.10
Nodes (32): get_me(), login(), get, Session, Authentication endpoints — register, login, refresh., Get current authenticated user's profile., Authenticate user and return JWT tokens., Get new access token using refresh token. (+24 more)

### Community 20 - "test_ceda_api.py"
Cohesion: 0.12
Nodes (19): ceda_provider(), fixture, mock, Unit and contract tests for CEDA Data Portal API provider., Verify provider retries on 504 Gateway Timeout before failing., Verify circuit breaker trips after consecutive failures and fast-fails., Verify non-transient 4xx errors propagate immediately without retry and without…, Assert commodities endpoint returns list matching schema. (+11 more)

### Community 21 - "weather_service.py"
Cohesion: 0.09
Nodes (19): NASAPowerProvider, Any, date, NASA POWER provider — long-term weather history for ML training. Free, no API…, Fetch long-term weather history from NASA POWER., Fetch daily weather data from NASA POWER., Any, date (+11 more)

### Community 22 - "MockChannel"
Cohesion: 0.12
Nodes (12): build_payload(), MockChannel, post_webhook(), TestClient, T3.2: Complete multi-step conversational harvest flow., T3.3: 3 invalid input attempts reset state and send menu., T3.3: Inbound audio/image receives friendly guidance message., T3.3: Sliding window rate limit stops replies and warns once. (+4 more)

### Community 23 - "CEDAProvider"
Cohesion: 0.08
Nodes (25): CEDAProvider, date, Decimal, Parse a single CSV row into a PriceRecord., Parse CEDA historical CSV data for price backfill., Try multiple possible column names., Try multiple date formats., Parse CEDA CSV and return standardized price records. Expected CSV columns (may… (+17 more)

### Community 24 - "extract_features_for_series"
Cohesion: 0.10
Nodes (31): days_to_nearest_festival(), get_festival_features(), is_festival(), date, Tamil Nadu holiday/festival features for price prediction. Uses Python…, Check if a date is a known festival day., Days until the nearest festival within a window. Returns window+1 if none., Generate festival-related features for a given date. (+23 more)

### Community 25 - "admin/page.tsx"
Cohesion: 0.13
Nodes (13): AdapterRow, AdminPage(), frontend_app_globals, metadata, viewport, Providers(), getIngestionRuns(), getStatewideFreshness() (+5 more)

### Community 26 - "Settings"
Cohesion: 0.12
Nodes (15): Application settings loaded from environment variables and .env file., Settings, Tests for production security enforcement in configuration., test_development_allows_default_secret_key(), test_production_accepts_strong_secret_key(), test_production_refuses_default_secret_key(), In production with WhatsApp enabled, missing secrets must raise a fatal…, In production with WhatsApp disabled, missing secrets should not raise. (+7 more)

### Community 27 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 28 - "User"
Cohesion: 0.09
Nodes (40): Check if current user has authorization to access/modify a specific FPO tenant., verify_fpo_access(), FPO, Base, Base, str, User, UserRole (+32 more)

### Community 29 - "TestClient"
Cohesion: 0.18
Nodes (6): TestClient, Authentication endpoint tests., TestLogin, TestProtectedRoutes, TestRefresh, TestRegister

### Community 30 - "Crop"
Cohesion: 0.05
Nodes (75): get_ingestion_run(), get_statewide_freshness(), list_ingestion_runs(), BaseModel, get, Session, UUID, Ingestion Center Telemetry and Control API (v1). (+67 more)

### Community 31 - "DataSourceRegistry"
Cohesion: 0.10
Nodes (15): ManualProvider, date, Decimal, Handles manually-entered price data from FPO staff., Manual prices are entered via API, not fetched. This provider returns an empty…, Create a PriceRecord from manual entry., DataSourceRegistry, date (+7 more)

### Community 32 - "api/whatsapp.py"
Cohesion: 0.12
Nodes (19): _bot(), _channel(), get_bot(), get_channel(), get_status_service(), get_whatsapp_activity(), get, Session (+11 more)

### Community 33 - "package.json"
Cohesion: 0.10
Nodes (19): name, private, scripts, build, dev, lint, start, version (+11 more)

### Community 34 - "commodities.py"
Cohesion: 0.24
Nodes (13): get_commodity_detail(), list_commodities(), get, Session, UUID, Commodity registry API endpoints — Canonical commodity intelligence., List canonical crops with counts of varieties, aliases, source mappings, and…, Get rich commodity profile with varieties, aliases, source mappings, and active… (+5 more)

### Community 35 - "test_send_buttons_contract"
Cohesion: 0.29
Nodes (10): client(), Provide a test client using the shared test database session., anyio, mock, Assert exact JSON payload and headers for text messages., Assert exact JSON for interactive buttons, max 3 buttons, and 20 char title…, Assert exact JSON for business-initiated templates with body parameters., test_send_buttons_contract() (+2 more)

### Community 36 - "cn"
Cohesion: 0.13
Nodes (34): CATEGORIES, AddFarmerForm, EMPTY_FORM, Card, CardContent, CardDescription, CardFooter, CardHeader (+26 more)

### Community 37 - "worker.py"
Cohesion: 0.17
Nodes (16): apscheduler_schedulers_blocking, get_wa_settings(), main(), FPOLink TN — Background Worker Runs scheduled tasks in a separate container.…, Fetch daily prices from configured data sources., # TODO: Import and call ingestion service, Fetch weather data from Open-Meteo / NASA POWER., # TODO: Import and call weather service (+8 more)

### Community 38 - "api.ts"
Cohesion: 0.08
Nodes (33): CommoditiesRegistryPage(), PricesPage(), MandiPricesTableProps, PriceChart(), PriceChartProps, ArbitrageOpportunity, ArbitrageResponse, CommodityDetail (+25 more)

### Community 39 - "v1/crops.py"
Cohesion: 0.16
Nodes (25): list_crops(), get, Session, List all configured crops., get_crop(), list_crop_varieties(), list_crops(), get (+17 more)

### Community 40 - "test_whatsapp_price_alerts.py"
Cohesion: 0.19
Nodes (12): alert_db(), compile_jsonb_sqlite(), compile_uuid_sqlite(), FakeChannel, anyio, compiles, fixture, Tests for T4.3: Price-move alerts (>= 5% threshold) and max 1 alert per farmer… (+4 more)

### Community 41 - "react"
Cohesion: 0.14
Nodes (20): LanguageSwitcher(), AppShell(), Header(), pageTitles, NavItem, navItems, Sidebar(), Badge() (+12 more)

### Community 42 - "models/crop.py"
Cohesion: 0.08
Nodes (28): Dual-Engine Agricultural Price Forecasting for FPOLink TN. Primary Engine:…, Crop model — agricultural crop ontology., ForecastLog, Base, ModelVersion, Base, Prediction, Base (+20 more)

### Community 43 - "v1/intelligence.py"
Cohesion: 0.10
Nodes (33): get_arbitrage_opportunities(), get_crop_forecast(), get_price_spreads(), get, Session, UUID, Agricultural Intelligence API v1: Forecasting, Arbitrage & Spread Analysis., Analyze statewide price dispersion and identify highest/lowest reporting… (+25 more)

### Community 44 - "replay_raw_ingestion.py"
Cohesion: 0.11
Nodes (23): argparse, main(), CEDA Historical Data Backfill Script. Loads historical agricultural market…, check_coverage(), main(), print_coverage_report(), Market price data coverage analyzer for FPOLink TN. Checks monthly price record…, Execute monthly coverage query across markets. (+15 more)

### Community 45 - "District"
Cohesion: 0.13
Nodes (23): Block, District, Base, State, Taluk, Village, intelligence_fixture(), fixture (+15 more)

### Community 46 - "bot.py"
Cohesion: 0.22
Nodes (12): crop_name(), detect_crop(), detect_intent(), format_price(), _match(), parse_qty(), Decimal, WhatsApp bot engine. Transport-agnostic: depends only on MessageChannel (send)… (+4 more)

### Community 47 - "WhatsApp Integration: Task List"
Cohesion: 0.10
Nodes (19): Checkpoint A: end-to-end from a real phone; CI green; no secrets in repo, Checkpoint B: harvest submitted by chat is visible to FPO staff, Checkpoint C: dry run with 3 test farmers, Checkpoint D: staging E2E with a real phone, Checkpoint E: Statewide Foundation Sign-Off, Checkpoint G: Agricultural Intelligence Sign-Off, Future Strategic Roadmap (v0.8 to v1.0), Phase 0: De-risk external dependencies (start now, in parallel) (+11 more)

### Community 48 - "PriceRecord"
Cohesion: 0.14
Nodes (21): PriceRecord, date, Standardized price record from any data source., Fetch price records for a crop in a district within a date range., clean_price_records(), detect_anomaly_mad(), _normalize_record(), Decimal (+13 more)

### Community 54 - "test_retention.py"
Cohesion: 0.12
Nodes (27): Manually trigger DPDP retention purge., trigger_retention_purge(), ConversationState, Store active conversation state machines per WhatsApp ID with TTL., Persist or remove conversation state., purge_conversation_state(), purge_inbound(), purge_outbound() (+19 more)

### Community 65 - "v1/geography.py"
Cohesion: 0.13
Nodes (32): create_district(), create_state(), create_taluk(), create_village(), get_district(), list_districts(), list_states(), list_taluks_for_district() (+24 more)

### Community 66 - "Operational Playbook: Manual CEDA Backfill, Coverage Audit & External Feeds"
Cohesion: 0.22
Nodes (8): 1. Manual CEDA CSV Export & Ingestion, 2. CEDA Support Communication & API Key Extension, 3. Data.gov.in (OGD) Live API Key Setup, 4. Meta Test App Setup & Webhook Payload Capture (T0.3), Operational Playbook: Manual CEDA Backfill, Coverage Audit & External Feeds, Step 1: Download from CEDA Portal, Step 2: Ingest with Verified `--source ceda` Tag, Step 3: Run the Coverage Audit

### Community 67 - "FPOLink TN"
Cohesion: 0.13
Nodes (15): 1. Clone & Configure, 2. Launch Stack with Docker Compose, 3. Seed Reference Data, API v1 Routing Matrix, Architecture Overview, Data Provenance & Real Data Guarantee, Database Schema & Migrations, Documentation Index (+7 more)

### Community 68 - "Implementation Plan: WhatsApp Integration for FPOLink TN"
Cohesion: 0.22
Nodes (8): Agent Working Rules (paste at the top of every agent task), Constraints, Dates that matter, Implementation Plan: WhatsApp Integration for FPOLink TN, Open Questions (need your answers), Overview, Risks and Mitigations, Testing Strategy

### Community 69 - "FakeChannel"
Cohesion: 0.33
Nodes (4): FakeChannel, anyio, Daily digest must abort immediately when circuit breaker is tripped., test_daily_digest_aborts_when_circuit_breaker_tripped()

### Community 70 - "README.md"
Cohesion: 0.22
Nodes (6): 1. Fixture Inventory & Verification Status, 2. Sample Data Isolation Guarantee, 3. Guide: Ingesting Verified Real Mandi Data, A. Live Daily Ingestion (data.gov.in OGD Agmarknet), B. Historical Backfill (CEDA Ashoka University), Data Provenance & Fixture Verification Ledger

### Community 71 - "test_whatsapp_usage_and_circuit_breaker.py"
Cohesion: 0.08
Nodes (33): get_admin_inbound(), get_usage_service(), get_whatsapp_usage(), get, Session, Admin endpoints for WhatsApp usage tracking, cost audits, and circuit breaker…, Get aggregated WhatsApp message usage, delivery rates, cost breakdown, and…, Get recent inbound WhatsApp messages for audit. (+25 more)

### Community 72 - "1. Architectural Pillars"
Cohesion: 0.07
Nodes (27): AuditLog, Base, log_audit_event(), Any, Session, UUID, Audit service — records operational mutations into immutable audit trail., Record an audit log entry. (+19 more)

### Community 73 - "test_inbound_sweep.py"
Cohesion: 0.18
Nodes (22): Log incoming WhatsApp webhook message IDs for deduplication / idempotency., WhatsAppInbound, At-least-once sweep: reprocess WhatsApp inbound messages stuck in 'received'.…, Find and increment retry on messages stuck in 'received' status. Messages that…, sweep_stuck_inbound(), DummyChannel, anyio, fixture (+14 more)

### Community 74 - "parse_webhook"
Cohesion: 0.16
Nodes (25): parse_webhook(), Extract user messages. Delivery/read status callbacks yield an empty list., load_fixture(), Parametrized contract tests verifying WhatsApp Cloud API fixtures against…, Verify read receipt status webhook parsing., Verify delivery failure callback parsing and error extraction., Load JSON fixture file., Verify parsing of English text message 'PRICE'. (+17 more)

### Community 77 - "test_ingestion_center_api.py"
Cohesion: 0.25
Nodes (7): Tests for Ingestion Center Telemetry and Control API (v1)., Verify paginated listing of ingestion runs., Verify retrieving detailed telemetry for a single run., Verify statewide coverage and freshness telemetry., test_get_ingestion_run_detail(), test_list_ingestion_runs(), test_statewide_freshness_endpoint()

### Community 78 - "CEDAAPIProvider"
Cohesion: 0.13
Nodes (12): CEDAAPIProvider, Any, date, Execute HTTP request with short timeout, retries, and circuit breaker., Retrieve list of all commodities: [{"id": int, "name": str}]., Retrieve geographies: [{"state_id": int, "state_name": str, "districts": [...]}], Fetch prices from CEDA API with narrow query targeting., Parse CEDA API JSON item into standardized PriceRecord. (+4 more)

### Community 79 - "Production Hosting Guide: Oracle Cloud Always Free + Cloudflare Tunnel"
Cohesion: 0.08
Nodes (24): 1. Architecture & Cost Model, 2. Oracle Cloud VM Provisioning, 3. Host Initialization & Docker Installation, 4. Cloudflare Zero Trust Tunnel Setup, 5. Clone and Configure FPOLink, 6. Launch Production Stack, 7. Verification & Meta Webhook Wiring, 8. Automated Systemd Boot Service (+16 more)

### Community 80 - "register_whatsapp_templates.py"
Cohesion: 0.27
Nodes (9): get_waba_id(), list_templates(), main(), CLI utility to register and check status of WhatsApp message templates with…, Retrieve WhatsApp Business Account ID or fall back to Phone Number ID., Fetch and display all registered templates in the WABA., Submit templates defined in JSON file to Meta Graph API for approval., submit_templates() (+1 more)

### Community 81 - "ensureToken"
Cohesion: 0.21
Nodes (14): FarmersPage(), FarmerInviteCard(), load(), FarmerInviteCardProps, API_BASE, createFarmer(), Farmer, getFarmers() (+6 more)

### Community 82 - "calculate_quality_score"
Cohesion: 0.11
Nodes (18): calculate_quality_score(), Any, date, Decimal, Explainable Data Quality Scoring Service for Mandi Prices., Compute an explainable data quality score (0.0 to 100.0) with granular…, Checkpoint E: Statewide Platform Foundation Sign-Off, Detailed Task Specifications (+10 more)

### Community 83 - "markets.py"
Cohesion: 0.20
Nodes (17): get_market(), list_markets(), get, Session, UUID, Market API v1 endpoints — market registry and resolution., List markets with optional district and type filtering., Get single market by ID with its configured aliases. (+9 more)

### Community 84 - "Detailed Task Specifications"
Cohesion: 0.11
Nodes (18): Detailed Task Specifications, Executive Summary, Implementation Plan: Phase 11 — Agricultural Intelligence (v0.7 Architecture), Task 11.10: Checkpoint G Sign-Off & Documentation, Task 11.2: Feature Store Test Suite (`backend/tests/test_feature_store.py`), Task 11.3: LightGBM Quantile & Baseline Forecasting Engine (`backend/app/ml/forecasting.py`), Task 11.4: Signal Generation & Model Versioning, Task 11.5: Worker Scheduled Prediction Pipeline (+10 more)

### Community 85 - "services/prices.py"
Cohesion: 0.06
Nodes (58): latest_prices(), list_markets(), price_anomalies(), price_history(), price_trend(), get, Session, Price endpoints — latest prices, history, trends, anomalies. (+50 more)

### Community 86 - "2. Gaps Identified & Remediated During Audit"
Cohesion: 0.14
Nodes (16): lifespan(), anyio, Verify /api/health returns 200 and db: ok when database engine succeeds., Verify /api/health returns 503 and db: error when database engine fails., Verify lifespan initializes Sentry when SENTRY_DSN is set., Verify lifespan skips Sentry when SENTRY_DSN is None or empty., Verify .env.example contains all critical Settings fields (T5.7 Nyquist check)., test_env_example_contains_all_critical_settings() (+8 more)

### Community 87 - "resolve_market"
Cohesion: 0.13
Nodes (19): MarketAlias, Base, _clean_str(), Session, UUID, Market canonicalization resolver service., Normalize input string: strip, lowercase, collapse whitespace., Resolve any raw mandi string or code to a canonical Market entity. Precedence:… (+11 more)

### Community 88 - "components.json"
Cohesion: 0.12
Nodes (16): aliases, components, hooks, lib, ui, utils, rsc, $schema (+8 more)

### Community 89 - "3. Verify First Successful Requests"
Cohesion: 0.12
Nodes (15): 1. Backend Health Probe, 1. Prerequisites, 2. Statewide Districts Probe (v1), 2. Step-by-Step Setup, 2. Verified Crops Feed, 3. Latest Verified Mandi Prices (v1), 3. Staff Web Dashboard, 3. Verify First Successful Requests (+7 more)

### Community 90 - "2. Locked Architectural Decisions"
Cohesion: 0.13
Nodes (14): 1. Vision & Roadmap Positioning, 2. Locked Architectural Decisions, 3. Scope Boundaries, D1: Reference-Data Invariant Assertions & CI Protection, D2: Comprehensive Regulated Market Master Registry, D4: Commodity Registry UI & Administrative Portal, D5: Reproducible Raw Ingestion Persistence & Replayability, D6: Real Statewide Ingestion Pipeline (8-Stage Flow) (+6 more)

### Community 91 - "FPOLink TN — Production Deployment Guide"
Cohesion: 0.14
Nodes (14): 1. Architecture, 2. Prerequisites, 3. Cloudflare Tunnel Setup, 4. Configuration, 5. Launch Stack, 6. Verification, 7. Operational Runbook & Maintenance, FPOLink TN — Production Deployment Guide (+6 more)

### Community 92 - "Detailed Task Specifications"
Cohesion: 0.14
Nodes (13): Detailed Task Specifications, Executive Summary, Implementation Plan: Phase 9 — Statewide Data Network (v0.6 Architecture), Task 9.10: Checkpoint F Statewide Data Network Sign-Off, Task 9.1: Reference Invariants & Automated Count Assertions, Task 9.2: Complete Regulated Market Master Registry, Task 9.3: External Source Mapping Models & Migration 0010, Task 9.4: Commodity Registry UI & Admin API (+5 more)

### Community 93 - "WhatsAppCloudChannel"
Cohesion: 0.29
Nodes (4): AsyncClient, Business-initiated message (e.g. daily digest). Template must be approved by…, Send template and return tuple of (success, meta_message_id)., WhatsAppCloudChannel

### Community 94 - "test_source_safety.py"
Cohesion: 0.21
Nodes (12): compile_jsonb_sqlite(), compile_uuid_sqlite(), anyio, compiles, fixture, Safety tests for source isolation and synthetic price prevention. Guarantees:…, Verify that latest_price and dashboard only return prices from whitelisted…, Verify that seed demo prices are never picked up by DbBotServices.latest_price. (+4 more)

### Community 95 - "Meta WhatsApp Cloud API — Production Setup Checklist"
Cohesion: 0.15
Nodes (10): Environment Variables Reference, Meta WhatsApp Cloud API — Production Setup Checklist, Prerequisites, Production Readiness Verification Sign-Off, 2. System Health Check, FPOLink Operations Runbook, Health Endpoint Usage, Quick Reference Links (+2 more)

### Community 96 - "run_inbound_sweep"
Cohesion: 0.17
Nodes (12): At-least-once sweep for stuck inbound messages (T5.4)., run_inbound_sweep(), Verify app.worker.run_inbound_sweep runs without error., test_worker_run_inbound_sweep(), D1: Deployment Strategy — Cloudflare Tunnel, D2: Meta Production Checklist, D3: Data Retention Policy, D4: At-Least-Once Processing Sweep (+4 more)

### Community 97 - "2. Locked Architectural Decisions"
Cohesion: 0.17
Nodes (11): 1. Vision & Roadmap Positioning, 2. Locked Architectural Decisions, 3. Scope Boundaries, D1: Dual-Engine Forecasting Architecture (LightGBM Quantile Regression + Robust Baseline), D3: Inter-District Arbitrage & Net Realized Margin Engine (`backend/app/services/arbitrage.py`), D5: Scheduled Autonomous Intelligence Worker, Deferred to Phase 13–15 (v0.8), In Scope (Phase 11) (+3 more)

### Community 98 - "2. Locked Decisions & Core Tenets"
Cohesion: 0.17
Nodes (11): 1. Vision & Architectural Transformation, 2. Locked Decisions & Core Tenets, 3. Explicitly Out of Scope for Phase 8, D2: Multi-Tenant RBAC & Organization Scoping, D3: Agricultural Crop Ontology & Canonical Alias Registry, D4: Market Registry & Canonical Market Aliases, D5: Ingestion Orchestration & Explainable Data Quality Framework, D6: API Versioning (v1) & Seamless Compatibility (+3 more)

### Community 99 - "receive"
Cohesion: 0.20
Nodes (10): receive(), parse_status_updates(), Check Meta's X-Hub-Signature-256 header (HMAC-SHA256 of the raw body)., Extract message status updates (sent, delivered, read, failed)., verify_signature(), test_empty_app_secret_never_verifies(), Verify parse_status_updates extracts delivered, read, and failed statuses from…, test_parse_status_updates_payload() (+2 more)

### Community 100 - "pydantic"
Cohesion: 0.28
Nodes (8): list_audit_logs(), get, Session, List audit log records (admin only)., AuditLogListResponse, AuditLogResponse, BaseModel, pydantic

### Community 101 - "Human Checkpoints Operational Guide (Checkpoints A, B, C, D)"
Cohesion: 0.18
Nodes (10): Checkpoint A: First End-to-End Inbound Message, Checkpoint B: Harvest Submission by Chat Visible to Staff, Checkpoint C: Proactive Daily Digest Dry Run (3 Test Farmers), Checkpoint D: Staging E2E behind Cloudflare Tunnel, Human Checkpoints Operational Guide (Checkpoints A, B, C, D), Prerequisites:, Verification Protocol (5 mins):, Verification Protocol (5 mins): (+2 more)

### Community 102 - "FPOLink TN: 2-Week Field Pilot Runbook (Final: Pilot)"
Cohesion: 0.20
Nodes (9): 1. Pilot Objectives & Key Results (OKRs), 2. Pre-Pilot Verification Checklist (Day -3 to Day 0), 3. Weekly Execution Timeline, 4. Daily Operational Telemetry & Monitoring Protocol, 5. Post-Pilot Evaluation & Go/No-Go Decision Matrix, Decision Pathways:, FPOLink TN: 2-Week Field Pilot Runbook (Final: Pilot), Week 1: Onboarding, Price Discovery & Harvest Flow (+1 more)

### Community 103 - "1. Resolution of Core Operational Questions"
Cohesion: 0.20
Nodes (9): 1. Resolution of Core Operational Questions, 2. Key Constraints & Compliance Fences, FPOLink TN: Pilot Specification & Open Decisions Resolution (T0.1), Q1: Bot Phone Number Allocation, Q2: Meta Business Manager & WABA Ownership, Q3: Pilot FPO & Cohort Selection, Q4: Harvest Submission Governance, Q5: Default Language & Localization (+1 more)

### Community 104 - "1. Emergency WhatsApp Kill Switch"
Cohesion: 0.22
Nodes (9): 1. Emergency WhatsApp Kill Switch, Expected Output:, How to Disable WhatsApp, How to Verify the Kill Switch Is Active, Re-Enabling Procedure, Verification Command (Local Docker Host):, Verification Command (Remote / Public Endpoint):, What the Kill Switch Affects (+1 more)

### Community 105 - "lucide-react"
Cohesion: 0.14
Nodes (11): AggregationSummary(), AggregationSummaryProps, BatchCard(), CROP_EMOJI, cropEmoji(), FooterProps, NavbarProps, getHarvestAggregation() (+3 more)

### Community 106 - "Phase 5 — Production Readiness: CONTEXT.md"
Cohesion: 0.29
Nodes (6): model_validator, Codebase Assets to Reuse, Deferred Ideas (out of Phase 5 scope), Next Step, Phase 5 — Production Readiness: CONTEXT.md, Prior Decisions Carried Forward

### Community 107 - "env"
Cohesion: 0.22
Nodes (4): env(), FakeChannel, make_services(), fixture

### Community 108 - "dependencies"
Cohesion: 0.25
Nodes (8): dependencies, clsx, lucide-react, next, react, react-dom, recharts, tailwind-merge

### Community 109 - "Market Price Data Coverage & Readiness Audit (T0.5)"
Cohesion: 0.29
Nodes (6): 1. Executive Summary, 2. Coverage Audit Results (2026-09), 3. Data Source Strategies & Risk Mitigation, Banana Coverage (Erode District), Market Price Data Coverage & Readiness Audit (T0.5), Turmeric Coverage (Erode District)

### Community 111 - "devDependencies"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

### Community 115 - "Task List"
Cohesion: 0.25
Nodes (8): Later backlog (only if the pilot justifies it), Phase 0: De-risk the external dependencies (start immediately, in parallel), Phase 2: Onboarding, identity and consent, Phase 3: Harvest submission by chat, Phase 4: Proactive messages (digest and alerts) with cost control, Phase 5: Production readiness, Phase 6: Pilot (10-20 farmers, one FPO, 2 weeks), Task List

### Community 116 - "FPOLink WhatsApp bot: integration guide"
Cohesion: 0.29
Nodes (6): Design notes, Environment variables (never commit values; `.env` is gitignored), FPOLink WhatsApp bot: integration guide, Meta setup checklist (check Meta's current docs; menus change), Not done yet, Wire it into the app

### Community 117 - "db"
Cohesion: 0.33
Nodes (5): create_tables(), db(), fixture, Create all tables before tests, drop after., Provide a clean database session for each test.

### Community 118 - "trigger_ingestion"
Cohesion: 0.40
Nodes (5): Session, Manually trigger price data ingestion (admin only)., Trigger live weather forecast ingestion from Open-Meteo., trigger_ingestion(), trigger_weather_ingest()

### Community 120 - "compile_jsonb_sqlite"
Cohesion: 0.67
Nodes (3): compile_jsonb_sqlite(), compile_uuid_sqlite(), compiles

## Knowledge Gaps
- **307 isolated node(s):** `entrypoint.prod.sh script`, `entrypoint.sh script`, `CATEGORIES`, `AdapterRow`, `AddFarmerForm` (+302 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1050 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **24 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `DbBotServices` connect `DbBotServices` to `api/whatsapp.py`, `InMemoryServices`, `Step-by-Step Production Runbook`, `Implementation Plan: WhatsApp Integration for FPOLink TN`, `test_harvest_service_and_api.py`, `test_inbound_sweep.py`, `models/crop.py`, `test_whatsapp_onboarding.py`, `test_whatsapp_status_webhook.py`, `WhatsApp Integration: Task List`, `Task List`, `test_source_safety.py`, `test_retention.py`, `.mark_notice_delivered`, `.first_time`, `User`, `Crop`?**
  _High betweenness centrality (0.096) - this node is a cross-community bridge._
- **Why does `Market` connect `Crop` to `sqlalchemy`, `commodities.py`, `DbBotServices`, `FPOLink TN`, `PriceMoveAlertService`, `test_whatsapp_price_alerts.py`, `models/crop.py`, `v1/intelligence.py`, `1. Architectural Pillars`, `District`, `crop_resolver.py`, `test_whatsapp_status_webhook.py`, `Detailed Task Specifications`, `markets.py`, `services/prices.py`, `resolve_market`, `User`, `test_source_safety.py`?**
  _High betweenness centrality (0.082) - this node is a cross-community bridge._
- **Why does `User` connect `User` to `v1/geography.py`, `sqlalchemy`, `pydantic`, `test_harvest_service_and_api.py`, `DbBotServices`, `test_whatsapp_usage_and_circuit_breaker.py`, `api/farmers.py`, `test_whatsapp_price_alerts.py`, `typing`, `1. Architectural Pillars`, `test_whatsapp_status_webhook.py`, `fpo_service.py`, `api/auth.py`, `test_retention.py`, `trigger_ingestion`?**
  _High betweenness centrality (0.073) - this node is a cross-community bridge._
- **Are the 51 inferred relationships involving `User` (e.g. with `trigger_ingestion()` and `trigger_retention_purge()`) actually correct?**
  _`User` has 51 INFERRED edges - model-reasoned connections that need verification._
- **Are the 31 inferred relationships involving `Crop` (e.g. with `list_crops()` and `get_commodity_detail()`) actually correct?**
  _`Crop` has 31 INFERRED edges - model-reasoned connections that need verification._
- **Are the 29 inferred relationships involving `Market` (e.g. with `list_markets()` and `record_manual_price()`) actually correct?**
  _`Market` has 29 INFERRED edges - model-reasoned connections that need verification._
- **Are the 31 inferred relationships involving `MarketPrice` (e.g. with `record_manual_price()` and `get_commodity_detail()`) actually correct?**
  _`MarketPrice` has 31 INFERRED edges - model-reasoned connections that need verification._
