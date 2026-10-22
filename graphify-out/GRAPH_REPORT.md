# Graph Report - FPOLink  (2026-10-22)

## Corpus Check
- 354 files · ~210,298 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 23 file(s) not represented in the graph (top: (none) 15, .csv 3, .example 1)

## Summary
- 3328 nodes · 9231 edges · 173 communities (145 shown, 28 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 969 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `a8596a74`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- v1/farmers.py
- Step-by-Step Production Runbook
- datetime
- test_units.py
- DbBotServices
- Harvest
- alembic
- Farmer
- test_supply_demand_services.py
- typing
- PriceMoveAlertService
- post
- InMemoryServices
- seed_data
- Crop
- test_whatsapp_status_webhook.py
- api/fpo.py
- BotServices
- getLatestPrices
- api/auth.py
- test_ceda_api.py
- WeatherProvider
- BotEngine
- CEDAProvider
- extract_features_for_series
- admin_whatsapp.py
- Settings
- compilerOptions
- create_access_token
- TestClient
- Market
- DataSourceRegistry
- _get
- package.json
- backtest_forecaster.py
- verify_fpo_access
- farmers/page.tsx
- main.py
- api.ts
- v1/crops.py
- _sqlite_pragmas
- react
- arbitrage.py
- test_price_catchup.py
- check_market_coverage.py
- District
- bot.py
- WhatsApp Integration: Task List
- PriceRecord
- forecasting.py
- config.py
- next.config.mjs
- postcss.config.mjs
- core/__init__.py
- test_retention.py
- entrypoint.sh
- next-env.d.ts
- schemas/__init__.py
- db
- v1/geography.py
- Operational Playbook: Manual CEDA Backfill, Coverage Audit & External Feeds
- FPOLink TN
- Implementation Plan: WhatsApp Integration for FPOLink TN
- FakeChannel
- Data Provenance & Fixture Verification Ledger
- WhatsAppUsageService
- 1. Architectural Pillars
- test_inbound_sweep.py
- parse_webhook
- rules/graphify.md
- workflows/graphify.md
- fastapi_testclient
- CEDAAPIProvider
- Production Hosting Guide: Oracle Cloud Always Free + Cloudflare Tunnel
- backfill_ceda.py
- district-context.tsx
- calculate_quality_score
- markets.py
- Detailed Task Specifications
- v1/intelligence.py
- 2. Gaps Identified & Remediated During Audit
- FPO
- components.json
- 3. Verify First Successful Requests
- 2. Locked Architectural Decisions
- FPOLink TN — Production Deployment Guide
- Detailed Task Specifications
- WhatsAppCloudChannel
- test_latest_price_and_dashboard_whitelist_real_sources_only
- 1. Emergency Messaging Kill Switches
- Decisions Made in This Discussion
- 2. Locked Architectural Decisions
- 2. Locked Decisions & Core Tenets
- ForecastAreaChart.tsx
- FastAPI
- Human Checkpoints Operational Guide (Checkpoints A, B, C, D)
- FPOLink TN: 2-Week Field Pilot Runbook (Final: Pilot)
- 1. Resolution of Core Operational Questions
- MandiPricesProvider
- test_telegram_bot.py
- .validate_production_secrets
- MockChannel
- jwt.py
- Market Price Data Coverage & Readiness Audit (T0.5)
- api/telegram.py
- getHealth
- 3. Locked Architectural Decisions
- marketData.ts
- entrypoint.prod.sh
- _get_price_on_date
- api/whatsapp.py
- v1/matching.py
- sys
- test_conversation_state_ttl
- FPOLink TN — Phase 13: Supply + Demand Network (v0.8 Architecture Plan)
- User
- normalise_phone
- ingest_ceda_live.py
- FPOLink TN — Tenant Isolation & Production Security Audit Report
- FPOLink Technology Stack
- 2. Tasks & Execution Sequence (Tracer-First)
- FPOLink External Integrations
- 2. Test Suite Organization
- get_db
- telegram_bot.py
- deps.py
- import_farms_csv
- 1. Python & Backend Conventions
- 2. Locked Architectural Decisions
- README.md
- FPOLink TN — Inter-District Arbitrage & Transport Realization Specification
- FPOLink Technical Concerns & Architecture Watchpoints
- 2. Tasks & Execution Sequence (Tracer-First)
- FPOLink TN — Product Roadmap
- generate_erode_historical.py
- TelegramChatChannel
- AggregationSummary.tsx
- tasks/page.tsx
- 2. Core Subsystems & Data Pipelines
- 2. Ingested Assets & Evidence
- FPOLink TN — Product Requirements Document (PRD)
- AuditLog
- TelegramClient
- test_worker_module_bootstraps_as_main
- 2. Technical Decisions & Architectural Matrix
- status
- FakeClient
- Telegram bot (@Fpo_Link_Bot)
- FPOLink TN — Project Specification
- vercel.json
- 3. Defense-in-Depth Isolation Implementation
- frontend/vercel.json
- FPOLink Project Status
- STRUCTURE.md
- FPOLink TN — Current Workflow State
- _jsonb_on_sqlite
- compile_jsonb_sqlite
- compile_jsonb_sqlite
- compile_jsonb_sqlite
- compile_jsonb_sqlite
- .use_psycopg3
- init_sqlite_schema
- BatchStatus
- test_harvest_api_flow
- test_production_refuses_missing_whatsapp_secrets
- test_production_allows_disabled_whatsapp_without_secrets
- test_production_accepts_valid_whatsapp_secrets

## God Nodes (most connected - your core abstractions)
1. `User` - 187 edges
2. `Crop` - 131 edges
3. `Market` - 102 edges
4. `Farmer` - 96 edges
5. `MarketPrice` - 92 edges
6. `FPO` - 78 edges
7. `_get()` - 75 edges
8. `UserRole` - 74 edges
9. `DbBotServices` - 72 edges
10. `District` - 69 edges

## Surprising Connections (you probably didn't know these)
- `4.2 Mandatory Password Rotation Boundary` --references--> `get_current_user()`  [INFERRED]
  docs/SECURITY_AUDIT.md → backend/app/api/deps.py
- `3.1 Database-Aware `verify_fpo_access`` --references--> `verify_fpo_access()`  [INFERRED]
  docs/SECURITY_AUDIT.md → backend/app/api/deps.py
- `Step 2: Route Hostnames` --references--> `dashboard()`  [INFERRED]
  docs/HOSTING.md → backend/app/api/fpo.py
- `3.4 Harvest Aggregation & Lifecycle` --references--> `_enforce_harvest_scope()`  [INFERRED]
  docs/SECURITY_AUDIT.md → backend/app/api/harvest.py
- `3.3 Task Board Tenant Scoping` --references--> `_scoped()`  [INFERRED]
  docs/SECURITY_AUDIT.md → backend/app/api/tasks.py

## Import Cycles
- None detected.

## Communities (173 total, 28 thin omitted)

### Community 0 - "v1/farmers.py"
Cohesion: 0.17
Nodes (23): create(), _enforce_farmer_fpo_scope(), get_one(), get_whatsapp_invite(), list_all(), put, Session, UUID (+15 more)

### Community 1 - "Step-by-Step Production Runbook"
Cohesion: 0.10
Nodes (19): Check if price date exceeds staleness threshold., English (`en`) Template:, Environment Variables Reference, Meta WhatsApp Cloud API — Production Setup Checklist, Optional: Template Specification for `price_move_alert`, Prerequisites, Production Readiness Verification Sign-Off, Step 1: Create Meta Business Account (+11 more)

### Community 2 - "datetime"
Cohesion: 0.07
Nodes (59): asyncio, AggregationBatch, BatchItem, Base, AuditLog model — enterprise audit trail for operational mutations., TimestampMixin, Buyer and buyer requirement models — staff-mediated commercial demand., CropAlias model — maps raw, regional, and provider strings to canonical crops. (+51 more)

### Community 3 - "test_units.py"
Cohesion: 0.23
Nodes (13): convert_from_per_kg(), convert_to_per_kg(), Decimal, Unit conversion utilities for agricultural commodities., Convert a price from any unit to Rs/kg. Args: price: Price in the original unit…, Convert Rs/kg to another unit., Tests for unit conversions., test_convert_from_per_kg() (+5 more)

### Community 4 - "DbBotServices"
Cohesion: 0.07
Nodes (15): DbBotServices, Atomically claim notice sending lease for farmer. Return True if claim acquired., Record timestamp when first-contact DPDP notice was confirmed delivered., Release leased claim after send failure so future inbound messages can retry., Record timestamp when first-contact DPDP notice was sent (alias to…, Return latest weather advisory for district., Production implementation of BotServices using SQLAlchemy and PostgreSQL., Store opt-in/out with timestamp for DPDP audit compliance. (+7 more)

### Community 5 - "Harvest"
Cohesion: 0.08
Nodes (49): create_harvest(), _enforce_harvest_scope(), get_harvest(), get_harvest_aggregation(), list_harvests(), date, patch, Session (+41 more)

### Community 7 - "Farmer"
Cohesion: 0.17
Nodes (26): create(), _enforce_farmer_fpo_scope(), get_one(), get_whatsapp_invite(), list_all(), put, Session, UUID (+18 more)

### Community 8 - "test_supply_demand_services.py"
Cohesion: 0.07
Nodes (60): create(), _enforce_farm_scope(), _farm_to_response(), get_one(), get_yield_estimate(), import_csv(), list_all(), delete (+52 more)

### Community 9 - "typing"
Cohesion: 0.15
Nodes (17): ABC, MarketDataProvider, Base market data provider interface. All data source adapters inherit from this…, Abstract base class for market data providers., Check if this data source is currently accessible., CEDA Data Portal API provider (Ashoka University). Programmatic access to raw…, CEDA Agri-Market provider (Ashoka University). Parses the historical CSV data…, MandiPrices.co.in / Agmarknet web provider. Parses daily wholesale mandi prices… (+9 more)

### Community 10 - "PriceMoveAlertService"
Cohesion: 0.22
Nodes (9): PriceMoveAlertService, date, Decimal, Session, Calculate modal price change between latest price on/before target_date and…, Find opted-in, reachable farmers growing the specific crop., Verify whether an alert has already been sent to this farmer today (limit…, Detects modal price shifts >= threshold (default 5%) and dispatches alerts max… (+1 more)

### Community 11 - "post"
Cohesion: 0.11
Nodes (23): BackgroundTasks, Request, receive(), Check Meta's X-Hub-Signature-256 header (HMAC-SHA256 of the raw body)., verify_signature(), button_payload(), env(), FakeChannel (+15 more)

### Community 12 - "InMemoryServices"
Cohesion: 0.09
Nodes (24): WhatsAppSettings, Farmer, InMemoryServices, PriceInfo, make_services(), build_payload(), FailingChannel, MockChannel (+16 more)

### Community 13 - "seed_data"
Cohesion: 0.40
Nodes (5): db_session(), fixture, In-memory SQLite database session fixture., Seed base user, fpo, farmer, and crop., seed_data()

### Community 14 - "Crop"
Cohesion: 0.05
Nodes (66): get_commodity_detail(), list_commodities(), Session, UUID, Commodity registry API endpoints — Canonical commodity intelligence., List canonical crops with counts of varieties, aliases, source mappings, and…, Get rich commodity profile with varieties, aliases, source mappings, and active…, CropAlias (+58 more)

### Community 15 - "test_whatsapp_status_webhook.py"
Cohesion: 0.07
Nodes (43): get_status_service(), _status_service(), mask(), Transport-agnostic messaging types. Bot logic depends on these, not on WhatsApp., Mask a phone number for logs (phone numbers are personal data under DPDP)., StatusUpdate, Messaging package: transport-agnostic types and WhatsApp Cloud API adapter., WhatsApp Cloud API (Meta) adapter: webhook parsing, signature check, sending. (+35 more)

### Community 16 - "api/fpo.py"
Cohesion: 0.13
Nodes (37): create(), dashboard(), get_one(), list_all(), put, Session, FPO management endpoints., Get dashboard statistics for an FPO. (+29 more)

### Community 17 - "BotServices"
Cohesion: 0.07
Nodes (11): BotServices, ConvState, Protocol, Everything the bot needs from your app. Implement against your DB/services., Atomically record message_id; False if already seen (Meta retries webhooks)., Fetch open confirmed or candidate buyer requirements for farmer's crops/FPO., Store opt-in/out with a timestamp (consent evidence for DPDP / WhatsApp opt-in)., Atomically claim notice lease. Returns True only if claim was acquired. (+3 more)

### Community 18 - "getLatestPrices"
Cohesion: 0.18
Nodes (14): PricesPage(), resolveCropUnit(), MandiPricesTable(), load(), MandiPricesTableProps, PriceChart(), initCrops(), PriceChartProps (+6 more)

### Community 19 - "api/auth.py"
Cohesion: 0.20
Nodes (19): change_password(), get_me(), login(), Session, Authentication endpoints — register, login, refresh., Require the current password, then replace it before granting a normal session., Get current authenticated user's profile., Authenticate user and return JWT tokens. (+11 more)

### Community 20 - "test_ceda_api.py"
Cohesion: 0.14
Nodes (17): ceda_provider(), fixture, mock, Unit and contract tests for CEDA Data Portal API provider., Verify provider retries on 504 Gateway Timeout before failing., Verify circuit breaker trips after consecutive failures and fast-fails., Verify non-transient 4xx errors propagate immediately without retry and without…, Assert commodities endpoint returns list matching schema. (+9 more)

### Community 21 - "WeatherProvider"
Cohesion: 0.12
Nodes (12): NASAPowerProvider, Any, date, Fetch long-term weather history from NASA POWER., Fetch daily weather data from NASA POWER., Any, date, Fetch weather data from Open-Meteo API. (+4 more)

### Community 22 - "BotEngine"
Cohesion: 0.08
Nodes (31): Button, InboundMessage, MessageChannel, Protocol, BotEngine, normalize_phone(), WhatsApp ids look like 919876543210. Match on the last 10 digits (India-only…, Entry point for background tasks: never raises. (+23 more)

### Community 23 - "CEDAProvider"
Cohesion: 0.10
Nodes (18): CEDAProvider, date, Decimal, Parse a single CSV row into a PriceRecord., Parse CEDA historical CSV data for price backfill., Try multiple possible column names., Try multiple date formats., Parse CEDA CSV and return standardized price records. Expected CSV columns (may… (+10 more)

### Community 24 - "extract_features_for_series"
Cohesion: 0.10
Nodes (30): days_to_nearest_festival(), get_festival_features(), is_festival(), date, Tamil Nadu holiday/festival features for price prediction. Uses Python…, Check if a date is a known festival day., Days until the nearest festival within a window. Returns window+1 if none., Generate festival-related features for a given date. (+22 more)

### Community 25 - "admin_whatsapp.py"
Cohesion: 0.26
Nodes (11): get_admin_inbound(), get_whatsapp_usage(), Session, Admin endpoints for WhatsApp usage tracking, cost audits, and circuit breaker…, Get aggregated WhatsApp message usage, delivery rates, cost breakdown, and…, Get recent inbound WhatsApp messages for audit., InboundMessageItem, InboundMessageListResponse (+3 more)

### Community 26 - "Settings"
Cohesion: 0.21
Nodes (11): Application settings loaded from environment variables and .env file., Settings, Tests for production security enforcement in configuration., test_development_allows_default_secret_key(), test_production_accepts_strong_secret_key(), test_production_refuses_default_secret_key(), test_production_rejects_default_database_password(), test_production_rejects_demo_mode() (+3 more)

### Community 27 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 28 - "create_access_token"
Cohesion: 0.16
Nodes (15): create_access_token(), Create a short-lived access token., create_test_app(), Unit tests for authentication and authorization dependencies in app.api.deps., test_expired_token_returns_401(), test_invalid_token_returns_401(), test_require_role_authorized_returns_200(), test_require_role_insufficient_permission_returns_403() (+7 more)

### Community 29 - "TestClient"
Cohesion: 0.15
Nodes (7): TestClient, Authentication endpoint tests., TestLogin, TestProtectedRoutes, TestRefresh, TestRegister, TestRequiredPasswordChange

### Community 30 - "Market"
Cohesion: 0.04
Nodes (96): get_data_health(), purge_testing_data(), Session, Admin endpoints — manual ingestion trigger, system status., System-wide data health report: rows/market/day, calendar gaps, and outlier…, Manually trigger price data ingestion (admin only)., Trigger live weather forecast ingestion from Open-Meteo for a district or…, Purge synthetic/demo test data so only real ground-truth data remains. (+88 more)

### Community 31 - "DataSourceRegistry"
Cohesion: 0.08
Nodes (25): Bulk import mandi prices from CSV file., upload_csv_prices(), ManualProvider, date, Load bulk records from a local CSV file path., Handles manually-entered price data from FPO staff., Manual prices are entered via API, not fetched. This provider returns an empty…, Parse bulk price records from CSV text. (+17 more)

### Community 32 - "_get"
Cohesion: 0.17
Nodes (26): get_forecast(), Session, Legacy backward-compatible forecast endpoint delegating to ForecastingService., create_task(), delete_task(), _get(), list_tasks(), delete (+18 more)

### Community 33 - "package.json"
Cohesion: 0.05
Nodes (35): dependencies, clsx, lucide-react, next, react, react-dom, recharts, tailwind-merge (+27 more)

### Community 34 - "backtest_forecaster.py"
Cohesion: 0.19
Nodes (12): evaluate_series_rolling_origin(), main(), DataFrame, Path, Rolling-Origin Walk-Forward Backtest Harness and Model Promotion CLI. Evaluates…, Generate docs/FORECAST_BACKTEST.md report., Run walk-forward evaluation across all commodity series in dataset., Run rolling-origin backtest on a single (crop, market) time series. (+4 more)

### Community 35 - "verify_fpo_access"
Cohesion: 0.08
Nodes (65): Check if current user has authorization to access/modify a specific FPO tenant.…, verify_fpo_access(), _buyer_to_response(), create(), get_one(), get_requirement(), import_csv(), list_all() (+57 more)

### Community 36 - "farmers/page.tsx"
Cohesion: 0.12
Nodes (45): CATEGORIES, AdapterRow, AddFarmerForm, AddPlotForm, EMPTY_FORM, EMPTY_PLOT_FORM, Badge(), BadgeProps (+37 more)

### Community 37 - "main.py"
Cohesion: 0.11
Nodes (24): apscheduler_schedulers_blocking, get_wa_settings(), health_check(), lifespan(), main(), FPOLink TN — Background Worker Runs scheduled tasks in a separate container.…, Generate price forecasts using the active model for active crop/market pairs., Daily price digest sent to opted-in farmers at 07:30 IST (T4.2). (+16 more)

### Community 38 - "api.ts"
Cohesion: 0.05
Nodes (80): CommoditiesRegistryPage(), AdminPage(), BuyersPage(), FarmersPage(), MatchingPage(), FPOActionWorkspace(), FarmerInviteCard(), load() (+72 more)

### Community 39 - "v1/crops.py"
Cohesion: 0.16
Nodes (24): list_crops(), Session, Crop listing endpoints., List all configured crops., get_crop(), list_crop_varieties(), list_crops(), Session (+16 more)

### Community 40 - "_sqlite_pragmas"
Cohesion: 0.18
Nodes (8): _sqlite_pragmas(), compile_jsonb_sqlite(), compile_uuid_sqlite(), compiles, compile_jsonb_sqlite(), compile_uuid_sqlite(), compiles, listens_for

### Community 41 - "react"
Cohesion: 0.07
Nodes (47): ChangePasswordPage(), handleSubmit(), frontend_app_globals, inter, metadata, viewport, LoginPage(), handleSubmit() (+39 more)

### Community 42 - "arbitrage.py"
Cohesion: 0.13
Nodes (19): compute_uncertainty_score(), find_market_arbitrage(), get_default_spoilage_risk(), haversine_distance_km(), Session, UUID, Inter-District Market Arbitrage and Transport Net Realization Engine. Computes…, Compute multi-factor uncertainty score, discrete rating, and explanatory… (+11 more)

### Community 43 - "test_price_catchup.py"
Cohesion: 0.32
Nodes (11): price_run_missed(), True when the latest daily price slot passed without a completed statewide run.…, add_run(), fixture, Missed-run check behind the daily price catch-up on hosts that sleep (Render…, six_am_slot(), test_before_todays_slot_checks_yesterdays(), test_missed_when_last_run_was_yesterday() (+3 more)

### Community 44 - "check_market_coverage.py"
Cohesion: 0.27
Nodes (10): check_coverage(), main(), print_coverage_report(), Market price data coverage analyzer for FPOLink TN. Checks monthly price record…, Execute monthly coverage query across markets., Format and print coverage statistics and advisory., Tests for the market coverage audit script., test_check_coverage_query() (+2 more)

### Community 45 - "District"
Cohesion: 0.06
Nodes (53): DataSource, Block, District, Base, Geography models — State, District, Taluk, Block, Village hierarchy., State, Taluk, Village (+45 more)

### Community 46 - "bot.py"
Cohesion: 0.18
Nodes (14): crop_name(), detect_crop(), detect_intent(), format_price(), _match(), parse_qty(), Decimal, WhatsApp bot engine. Transport-agnostic: depends only on MessageChannel (send)… (+6 more)

### Community 47 - "WhatsApp Integration: Task List"
Cohesion: 0.07
Nodes (28): Checkpoint A: end-to-end from a real phone; CI green; no secrets in repo, Checkpoint B: harvest submitted by chat is visible to FPO staff, Checkpoint C: dry run with 3 test farmers, Checkpoint D: staging E2E with a real phone, Checkpoint E: Statewide Foundation Sign-Off, Checkpoint G: Agricultural Intelligence Sign-Off, Checkpoint H: Supply + Demand Network Sign-Off, FPOLink MVP Sprint — Tasks M1–M4 (+20 more)

### Community 48 - "PriceRecord"
Cohesion: 0.11
Nodes (24): PriceRecord, date, Standardized price record from any data source., Fetch price records for a crop in a district within a date range., date, Fetch prices from all available providers. Uses fallback chain: tries each…, Fetch from ALL available providers (not just first success)., clean_price_records() (+16 more)

### Community 49 - "forecasting.py"
Cohesion: 0.08
Nodes (34): compute_forecast_signal(), ForecastingService, load_price_series(), DataFrame, Session, UUID, Dual-Engine Agricultural Price Forecasting for FPOLink TN. Primary Engine:…, Dual-engine forecasting and signal generation service. (+26 more)

### Community 50 - "config.py"
Cohesion: 0.08
Nodes (29): OGDProvider, date, Open Government Data (data.gov.in) provider. Fetches daily wholesale mandi…, Case-tolerant field retriever., Fetch daily mandi prices from data.gov.in OGD API., Fetch prices from data.gov.in API., Parse an OGD API record into a PriceRecord., check_status() (+21 more)

### Community 54 - "test_retention.py"
Cohesion: 0.13
Nodes (26): Manually trigger DPDP retention purge., trigger_retention_purge(), ConversationState, Store active conversation state machines per WhatsApp ID with TTL., purge_conversation_state(), purge_inbound(), purge_outbound(), DPDP-compliant data retention purge for WhatsApp tables. Scheduled daily at… (+18 more)

### Community 61 - "schemas/__init__.py"
Cohesion: 0.14
Nodes (27): CommodityDetail, CommoditySummary, BaseModel, Commodity registry schemas., SourceMappingSummary, FPOLink Pydantic schemas package., MatchBreakdown, MatchCandidate (+19 more)

### Community 62 - "db"
Cohesion: 0.18
Nodes (10): admin_headers(), create_tables(), db(), _enable_whatsapp_for_legacy_bot_tests(), fixture, Create all tables before tests, drop after., WhatsApp ships disabled (Telegram is the farmer channel), but the dormant…, Provide a clean database session for each test. (+2 more)

### Community 65 - "v1/geography.py"
Cohesion: 0.13
Nodes (31): create_district(), create_state(), create_taluk(), create_village(), get_district(), list_districts(), list_states(), list_taluks_for_district() (+23 more)

### Community 66 - "Operational Playbook: Manual CEDA Backfill, Coverage Audit & External Feeds"
Cohesion: 0.22
Nodes (8): 1. Manual CEDA CSV Export & Ingestion, 2. CEDA Support Communication & API Key Extension, 3. Data.gov.in (OGD) Live API Key Setup, 4. Meta Test App Setup & Webhook Payload Capture (T0.3), Operational Playbook: Manual CEDA Backfill, Coverage Audit & External Feeds, Step 1: Download from CEDA Portal, Step 2: Ingest with Verified `--source ceda` Tag, Step 3: Run the Coverage Audit

### Community 67 - "FPOLink TN"
Cohesion: 0.11
Nodes (19): 1. Clone & Configure, 2. Deployment Requirements, 2. Launch Stack with Docker Compose, 3. Known Pilot Limitations & Boundaries, 3. Seed Reference Data, 4. Create the First Admin, API v1 Routing Matrix, Architecture Overview (+11 more)

### Community 68 - "Implementation Plan: WhatsApp Integration for FPOLink TN"
Cohesion: 0.12
Nodes (16): Agent Working Rules (paste at the top of every agent task), Constraints, Dates that matter, Implementation Plan: WhatsApp Integration for FPOLink TN, Later backlog (only if the pilot justifies it), Open Questions (need your answers), Overview, Phase 0: De-risk the external dependencies (start immediately, in parallel) (+8 more)

### Community 69 - "FakeChannel"
Cohesion: 0.33
Nodes (4): FakeChannel, anyio, Daily digest must abort immediately when circuit breaker is tripped., test_daily_digest_aborts_when_circuit_breaker_tripped()

### Community 70 - "Data Provenance & Fixture Verification Ledger"
Cohesion: 0.29
Nodes (6): 1. Fixture Inventory & Verification Status, 2. Sample Data Isolation Guarantee, 3. Guide: Ingesting Verified Real Mandi Data, A. Live Daily Ingestion (data.gov.in OGD Agmarknet), B. Historical Backfill (CEDA Ashoka University), Data Provenance & Fixture Verification Ledger

### Community 71 - "WhatsAppUsageService"
Cohesion: 0.16
Nodes (9): get_usage_service(), Session, Calculates monthly message volumes, applies configurable cost rates, and gates…, Parse YYYY-MM into year, month integers. Fallback to current UTC month., Evaluate whether monthly message caps or budget thresholds have been exceeded., Generate usage and cost report for the requested month., WhatsAppUsageService, GET /api/admin/whatsapp/usage enforces admin role and returns usage metrics. (+1 more)

### Community 72 - "1. Architectural Pillars"
Cohesion: 0.11
Nodes (18): 1.10 Statewide Telemetry Console & Commodity Registry UI, 1.11 Agricultural Intelligence & Forecasting Engine (v0.7), 1.1 Complete Administrative Geography Hierarchy, 1.2 Unified Agricultural Crop & Varietal Ontology, 1.3 Regulated Market Master Registry, 1.5 Explainable Data Quality Engine, 1.6 API v1 Unified Hierarchy, 1.8 Immutable Raw Ingestion Persistence & Replay Harness (+10 more)

### Community 73 - "test_inbound_sweep.py"
Cohesion: 0.13
Nodes (30): Log incoming WhatsApp webhook message IDs for deduplication / idempotency., WhatsAppInbound, At-least-once sweep: reprocess WhatsApp inbound messages stuck in 'received'.…, Find and increment retry on messages stuck in 'received' status. Messages that…, sweep_stuck_inbound(), At-least-once sweep for stuck inbound messages (T5.4)., run_inbound_sweep(), compile_jsonb_sqlite() (+22 more)

### Community 74 - "parse_webhook"
Cohesion: 0.14
Nodes (28): parse_status_updates(), parse_webhook(), Extract user messages. Delivery/read status callbacks yield an empty list., Extract message status updates (sent, delivered, read, failed)., load_fixture(), Parametrized contract tests verifying WhatsApp Cloud API fixtures against…, Verify read receipt status webhook parsing., Verify delivery failure callback parsing and error extraction. (+20 more)

### Community 77 - "fastapi_testclient"
Cohesion: 0.22
Nodes (8): Tests for Ingestion Center Telemetry and Control API (v1)., Verify paginated listing of ingestion runs., Verify retrieving detailed telemetry for a single run., Verify statewide coverage and freshness telemetry., test_get_ingestion_run_detail(), test_list_ingestion_runs(), test_statewide_freshness_endpoint(), fastapi_testclient

### Community 78 - "CEDAAPIProvider"
Cohesion: 0.12
Nodes (15): CEDAAPIProvider, Any, date, Execute HTTP request with short timeout, retries, and circuit breaker., Retrieve list of all commodities: [{"id": int, "name": str}]., Test if the configured API key is valid., Retrieve geographies: [{"state_id": int, "state_name": str, "districts": [...]}], Retrieve markets: POST /agmarknet/markets. (+7 more)

### Community 79 - "Production Hosting Guide: Oracle Cloud Always Free + Cloudflare Tunnel"
Cohesion: 0.08
Nodes (26): 1. Architecture & Cost Model, 2. Oracle Cloud VM Provisioning, 3. Host Initialization & Docker Installation, 4. Cloudflare Zero Trust Tunnel Setup, 5. Clone and Configure FPOLink, 6. Launch Production Stack, 7. Verification & Farmer Channel Wiring, 8. Automated Systemd Boot Service (+18 more)

### Community 80 - "backfill_ceda.py"
Cohesion: 0.12
Nodes (18): argparse, main(), CEDA Historical Data Backfill Script. Loads historical agricultural market…, get_waba_id(), list_templates(), main(), Path, CLI utility to register and check status of WhatsApp message templates with… (+10 more)

### Community 81 - "district-context.tsx"
Cohesion: 0.15
Nodes (13): DistrictItem, getDistricts(), DistrictContext, DistrictContextValue, DistrictProvider(), Overview, Phase M5 Execution Plan: Statewide Multi-Crop & District-Dynamic Experience with JetBrainsMono & Performance Optimization, Task M5.1: Typography Foundation with JetBrains Mono (+5 more)

### Community 82 - "calculate_quality_score"
Cohesion: 0.11
Nodes (18): calculate_quality_score(), Any, date, Decimal, Explainable Data Quality Scoring Service for Mandi Prices., Compute an explainable data quality score (0.0 to 100.0) with granular…, Checkpoint E: Statewide Platform Foundation Sign-Off, Detailed Task Specifications (+10 more)

### Community 83 - "markets.py"
Cohesion: 0.22
Nodes (16): get_market(), list_markets(), Session, UUID, Market API v1 endpoints — market registry and resolution., List markets with optional district and type filtering., Get single market by ID with its configured aliases., Resolve an incoming raw market name or code to a canonical Market. (+8 more)

### Community 84 - "Detailed Task Specifications"
Cohesion: 0.11
Nodes (18): Detailed Task Specifications, Executive Summary, Implementation Plan: Phase 11 — Agricultural Intelligence (v0.7 Architecture), Task 11.10: Checkpoint G Sign-Off & Documentation, Task 11.2: Feature Store Test Suite (`backend/tests/test_feature_store.py`), Task 11.3: LightGBM Quantile & Baseline Forecasting Engine (`backend/app/ml/forecasting.py`), Task 11.4: Signal Generation & Model Versioning, Task 11.5: Worker Scheduled Prediction Pipeline (+10 more)

### Community 85 - "v1/intelligence.py"
Cohesion: 0.10
Nodes (32): get_arbitrage_opportunities(), get_crop_forecast(), get_price_spreads(), Session, UUID, Agricultural Intelligence API v1: Forecasting, Arbitrage & Spread Analysis., Evaluate inter-district market arbitrage deducting estimated freight, handling,…, Analyze statewide price dispersion and identify highest/lowest reporting… (+24 more)

### Community 86 - "2. Gaps Identified & Remediated During Audit"
Cohesion: 0.14
Nodes (15): anyio, Verify /api/health returns 200 and db: ok when database engine succeeds., Verify /api/health returns 503 and db: error when database engine fails., Verify lifespan initializes Sentry when SENTRY_DSN is set., Verify lifespan skips Sentry when SENTRY_DSN is None or empty., Verify .env.example contains all critical Settings fields (T5.7 Nyquist check)., test_env_example_contains_all_critical_settings(), test_health_check_db_failure() (+7 more)

### Community 87 - "FPO"
Cohesion: 0.04
Nodes (82): FPO, Base, str, UserRole, hash_password(), Authentication service — password hashing with Argon2 via pwdlib., Hash a password using Argon2id., create_or_update_admin() (+74 more)

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
Cohesion: 0.12
Nodes (16): 1. Architecture, 2. Prerequisites, 3. Cloudflare Tunnel Setup, 4. Configuration, 5. Launch Stack, 6. Verification, 7. Operational Runbook & Maintenance, FPOLink TN — Production Deployment Guide (+8 more)

### Community 92 - "Detailed Task Specifications"
Cohesion: 0.14
Nodes (13): Detailed Task Specifications, Executive Summary, Implementation Plan: Phase 9 — Statewide Data Network (v0.6 Architecture), Task 9.10: Checkpoint F Statewide Data Network Sign-Off, Task 9.1: Reference Invariants & Automated Count Assertions, Task 9.2: Complete Regulated Market Master Registry, Task 9.3: External Source Mapping Models & Migration 0010, Task 9.4: Commodity Registry UI & Admin API (+5 more)

### Community 93 - "WhatsAppCloudChannel"
Cohesion: 0.14
Nodes (16): AsyncClient, Business-initiated message (e.g. daily digest). Template must be approved by…, Send template and return tuple of (success, meta_message_id)., WhatsAppCloudChannel, client(), Provide a test client using the shared test database session., anyio, mock (+8 more)

### Community 94 - "test_latest_price_and_dashboard_whitelist_real_sources_only"
Cohesion: 0.29
Nodes (8): anyio, fixture, Verify that latest_price and dashboard only return prices from whitelisted…, Verify that seed demo prices are never picked up by DbBotServices.latest_price., In-memory SQLite database factory for unit tests., test_db_factory(), test_latest_price_and_dashboard_whitelist_real_sources_only(), test_seed_script_prices_never_served_to_bot()

### Community 95 - "1. Emergency Messaging Kill Switches"
Cohesion: 0.10
Nodes (20): 1.1 Emergency WhatsApp Kill Switch (Dormant by default in MVP), 1.2 Emergency Telegram Kill Switch (Active Live Channel in MVP), 1. Emergency Messaging Kill Switches, 2. System Health Check, Expected Output:, FPOLink Operations Runbook, Health Endpoint Usage, How to Disable Telegram (+12 more)

### Community 96 - "Decisions Made in This Discussion"
Cohesion: 0.29
Nodes (7): D1: Deployment Strategy — Cloudflare Tunnel, D2: Meta Production Checklist, D3: Data Retention Policy, D5: Observability — Sentry Init + DB Health Check, D6: Ops Runbook — Kill Switch Procedure, D7: `.env.example` Update, Decisions Made in This Discussion

### Community 97 - "2. Locked Architectural Decisions"
Cohesion: 0.17
Nodes (11): 1. Vision & Roadmap Positioning, 2. Locked Architectural Decisions, 3. Scope Boundaries, D1: Dual-Engine Forecasting Architecture (LightGBM Quantile Regression + Robust Baseline), D3: Inter-District Arbitrage & Net Realized Margin Engine (`backend/app/services/arbitrage.py`), D5: Scheduled Autonomous Intelligence Worker, Deferred to Phase 13–15 (v0.8), In Scope (Phase 11) (+3 more)

### Community 98 - "2. Locked Decisions & Core Tenets"
Cohesion: 0.17
Nodes (11): 1. Vision & Architectural Transformation, 2. Locked Decisions & Core Tenets, 3. Explicitly Out of Scope for Phase 8, D2: Multi-Tenant RBAC & Organization Scoping, D3: Agricultural Crop Ontology & Canonical Alias Registry, D4: Market Registry & Canonical Market Aliases, D5: Ingestion Orchestration & Explainable Data Quality Framework, D6: API Versioning (v1) & Seamless Compatibility (+3 more)

### Community 99 - "ForecastAreaChart.tsx"
Cohesion: 0.18
Nodes (7): ForecastAreaChart, PriceHistoryChart, ForecastAreaChartProps, ForecastChartPoint, HistoryChartPoint, PriceHistoryChartProps, recharts

### Community 100 - "FastAPI"
Cohesion: 0.23
Nodes (9): get_buyers(), list_audit_logs(), Session, Audit API v1 endpoints — view system audit trails., List audit log records (admin only)., AuditLogListResponse, AuditLogResponse, BaseModel (+1 more)

### Community 101 - "Human Checkpoints Operational Guide (Checkpoints A, B, C, D)"
Cohesion: 0.18
Nodes (10): Checkpoint A: First End-to-End Inbound Message, Checkpoint B: Harvest Submission by Chat Visible to Staff, Checkpoint C: Proactive Daily Digest Dry Run (3 Test Farmers), Checkpoint D: Staging E2E behind Cloudflare Tunnel, Human Checkpoints Operational Guide (Checkpoints A, B, C, D), Prerequisites:, Verification Protocol (5 mins):, Verification Protocol (5 mins): (+2 more)

### Community 102 - "FPOLink TN: 2-Week Field Pilot Runbook (Final: Pilot)"
Cohesion: 0.20
Nodes (9): 1. Pilot Objectives & Key Results (OKRs), 2. Pre-Pilot Verification Checklist (Day -3 to Day 0), 3. Weekly Execution Timeline, 4. Daily Operational Telemetry & Monitoring Protocol, 5. Post-Pilot Evaluation & Go/No-Go Decision Matrix, Decision Pathways:, FPOLink TN: 2-Week Field Pilot Runbook (Final: Pilot), Week 1: Onboarding, Price Discovery & Harvest Flow (+1 more)

### Community 103 - "1. Resolution of Core Operational Questions"
Cohesion: 0.20
Nodes (9): 1. Resolution of Core Operational Questions, 2. Key Constraints & Compliance Fences, FPOLink TN: Pilot Specification & Open Decisions Resolution (T0.1), Q1: Bot Phone Number Allocation, Q2: Meta Business Manager & WABA Ownership, Q3: Pilot FPO & Cohort Selection, Q4: Harvest Submission Governance, Q5: Default Language & Localization (+1 more)

### Community 104 - "MandiPricesProvider"
Cohesion: 0.11
Nodes (16): MandiPricesProvider, date, Decimal, Load HTML live, falling back to the committed snapshot., Parse the HTML table into standardized PriceRecord instances., Convert '₹8,048' -> Decimal('8048')., Convert '25 Sep 2026' -> date(2026, 9, 25)., Fetch daily mandi prices from MandiPrices / Agmarknet portal. (+8 more)

### Community 105 - "test_telegram_bot.py"
Cohesion: 0.23
Nodes (20): map_command(), parse_update(), Translate '/price turmeric' or '/price@Fpo_Link_Bot' into engine text ('price…, Parse a Telegram Update into a TelegramUpdate. Returns None for ignorable…, _button(), _contact(), factory(), anyio (+12 more)

### Community 106 - ".validate_production_secrets"
Cohesion: 0.25
Nodes (7): 6. Network & CORS Origin Protection, model_validator, Codebase Assets to Reuse, Deferred Ideas (out of Phase 5 scope), Next Step, Phase 5 — Production Readiness: CONTEXT.md, Prior Decisions Carried Forward

### Community 108 - "jwt.py"
Cohesion: 0.31
Nodes (8): Get new access token using refresh token., refresh(), create_password_change_token(), create_refresh_token(), UUID, JWT service — token creation and verification using PyJWT., Create a long-lived refresh token., Create a short-lived token that can only complete a required password change.

### Community 109 - "Market Price Data Coverage & Readiness Audit (T0.5)"
Cohesion: 0.20
Nodes (9): 1. Executive Summary, 2. Coverage Audit Results (2026-10-04), 3. Modeling & Operational Implications, 4. Ashoka CEDA API Integration & Platform Fixes (2026-10-04), Banana Coverage (Erode District), CEDA Agmarknet Provider Status, Farmer Addition Crash Fix, Market Price Data Coverage & Readiness Audit (T0.5) (+1 more)

### Community 110 - "api/telegram.py"
Cohesion: 0.14
Nodes (20): get_client(), get_service(), public_base_url(), BackgroundTasks, Request, Telegram bot webhook (farmer channel). POST /api/telegram/webhook -> updates…, Point Telegram at this API and publish the command menu., receive() (+12 more)

### Community 111 - "getHealth"
Cohesion: 0.33
Nodes (8): WhatsAppPage(), AlertPanel(), buildAlerts(), AlertPanelProps, LiveAlert, getHealth(), getWhatsAppActivity(), getWhatsAppUsage()

### Community 112 - "3. Locked Architectural Decisions"
Cohesion: 0.22
Nodes (8): 1. Goal & Objectives, 3. Locked Architectural Decisions, 4. Scope Boundaries & Out of Scope, Decision 1: Database-Aware `verify_fpo_access`, Decision 3: Bulk Import & Tenant Boundaries, Decision 4: Production Bootstrap Security Standards, Decision 5: CORS Origin Policy Refinement, Phase M4: Tenant Isolation & Production Security Audits — Context & Locked Decisions

### Community 115 - "_get_price_on_date"
Cohesion: 0.12
Nodes (21): latest_prices(), list_markets(), price_anomalies(), price_history(), price_trend(), Session, Get latest prices for all crops in a district with optional crop and market…, Get price history for a crop in a market. (+13 more)

### Community 116 - "api/whatsapp.py"
Cohesion: 0.10
Nodes (21): _bot(), _channel(), get_bot(), get_channel(), get_whatsapp_activity(), Session, WhatsApp Cloud API webhook. GET /api/whatsapp/webhook -> Meta's one-time…, Staff dashboard monitor feed — returns real inbound messages and telemetry. (+13 more)

### Community 117 - "v1/matching.py"
Cohesion: 0.08
Nodes (49): confirm_match(), get_candidates(), list_matches(), _match_to_response(), Session, UUID, Semi-Automatic Demand-Supply Matching API endpoints., Record a suggested demand-supply match. (+41 more)

### Community 118 - "sys"
Cohesion: 0.09
Nodes (23): Run migrations in 'offline' mode. This configures the context with just a URL…, Run migrations in 'online' mode. In this scenario we need to create an Engine…, run_migrations_offline(), run_migrations_online(), Base, WeatherData, date, Weather ingestion service. (+15 more)

### Community 119 - "test_conversation_state_ttl"
Cohesion: 0.25
Nodes (8): anyio, fixture, Verify conversation state persistence and 30-minute TTL expiration., In-memory SQLite database factory for unit tests., Verify first_time returns True on first delivery, False on retries, and handles…, test_conversation_state_ttl(), test_db_factory(), test_first_time_atomic_dedup()

### Community 120 - "FPOLink TN — Phase 13: Supply + Demand Network (v0.8 Architecture Plan)"
Cohesion: 0.13
Nodes (14): 1. Locked Strategic Decisions, 3.1 Rule-Based Yield Estimator (`backend/app/services/yield_estimator.py`), 3.2 Semi-Automatic Matching Engine (`backend/app/services/matching_service.py`), 3. Business Logic & Core Algorithms, 4.1 Free Service Conversation Window (Inbound-First), 4.2 Gated Low-Cost Outbound Nudge (Only When Staff Confirms), 4. WhatsApp Zero-Cost Interaction Architecture, 5.1 Farm Plot Endpoints (`/api/v1/farms`) (+6 more)

### Community 121 - "User"
Cohesion: 0.09
Nodes (23): Dependency factory: restrict endpoint to specific roles. Automatically maps…, require_role(), get_ingestion_run(), list_ingestion_runs(), BaseModel, Session, UUID, Trigger a statewide or targeted price ingestion run. (+15 more)

### Community 122 - "normalise_phone"
Cohesion: 0.14
Nodes (9): Check whether a recipient is reachable or flagged as dead., format_phone_e164(), normalise_phone(), Phone number normalisation utilities for India / FPOLink., Format normalised phone to E.164 (+91...)., Normalise phone number to 10-digit Indian standard. Strips country codes (+91,…, Unit tests for phone normalisation, farmer consent, and bot models., TestBotModelsMetadata (+1 more)

### Community 123 - "ingest_ceda_live.py"
Cohesion: 0.14
Nodes (17): check_status(), main(), date, CEDA Agmarknet Live Ingestion & Authentication CLI Harness. Provides…, Verify OTP with Ashoka CEDA., Validate and write new CEDA_API_KEY into .env., Fetch live data from CEDA and ingest into PostgreSQL., Check connectivity and key validity against CEDA API. (+9 more)

### Community 124 - "FPOLink TN — Tenant Isolation & Production Security Audit Report"
Cohesion: 0.25
Nodes (7): 1. Executive Summary, 2. Multi-Tenant Role Hierarchy & RBAC Matrix, 4.1 Cryptographic Token Integrity, 4.2 Mandatory Password Rotation Boundary, 4. Token & Credential Security Lifecycle, 5. Production Admin Provisioning Governance, FPOLink TN — Tenant Isolation & Production Security Audit Report

### Community 125 - "FPOLink Technology Stack"
Cohesion: 0.14
Nodes (13): 1. Core Languages & Runtimes, 2. Backend Frameworks & Libraries, 3. Frontend Frameworks & UI Architecture, 4. Database Systems & Storage, 5. Development, Linting & CI/CD Tooling, Database & ORM, FPOLink Technology Stack, Framework & Routing (+5 more)

### Community 126 - "2. Tasks & Execution Sequence (Tracer-First)"
Cohesion: 0.22
Nodes (8): 1. Phase Overview, 2. Tasks & Execution Sequence (Tracer-First), Phase M4: Tenant Isolation & Production Security Audits — Implementation Plan, Task M4.3: Hardened Production Admin Provisioning, Task M4.4: CORS Origin Configuration Verification & Documentation, Task M4.5: Comprehensive Automated Security Test Suite, Task M4.6: Security Audit Report Documentation, Task M4.7: Regression Testing, Graph Sync & Git Commit

### Community 127 - "FPOLink External Integrations"
Cohesion: 0.15
Nodes (12): 1. Agricultural Mandi & Price Data Feeds, 2. Weather & Agrometeorology, 3. Messaging & Bot Gateways, 4. Monitoring & Telemetry, A. OGD India (Agmarknet Daily Mandi API), A. Telegram Bot API, B. CEDA Agri-Market Data Portal, B. WhatsApp Cloud API (Meta Graph API) (+4 more)

### Community 128 - "2. Test Suite Organization"
Cohesion: 0.15
Nodes (12): 1. Testing Framework & Tooling, 2. Test Suite Organization, 3. Running Tests, A. Authentication & Security (25 tests), B. Multi-Channel Messaging & Bots (74 tests), C. Ingestion, Parsers & Data Hygiene (42 tests), D. Core Domain & Business Logic (65 tests), E. Health, Retention & Platform Infrastructure (22 tests) (+4 more)

### Community 129 - "get_db"
Cohesion: 0.15
Nodes (16): get_price_lineage(), latest_prices(), price_history(), Session, UUID, quality_summary(), Statewide Prices API (v1) with quality score filtering and telemetry., Get the latest verified mandi prices across districts with optional quality… (+8 more)

### Community 130 - "telegram_bot.py"
Cohesion: 0.26
Nodes (7): TelegramUpdate, phone10(), Process one update. Never raises (runs as a background task)., Telegram front-end for the transport-agnostic BotEngine. Flow: 1. Unknown chat…, Link the chat to a farmer by phone. Returns (status, display) where status is…, TelegramBotService, secrets

### Community 131 - "deps.py"
Cohesion: 0.22
Nodes (14): get_current_user(), get_password_change_user(), _get_user_from_token(), Session, UUID, FastAPI dependencies for authentication, authorization, and multi-tenant…, Resolve an active user from a bearer token with the required token type., Extract a normal authenticated user, blocking accounts that must reset a… (+6 more)

### Community 132 - "import_farms_csv"
Cohesion: 0.24
Nodes (11): import_buyers_csv(), import_farms_csv(), parse_date(), date, Session, UUID, Import commercial buyers and optional procurement requirements from CSV text., Parse string to date with multiple format support. (+3 more)

### Community 133 - "1. Python & Backend Conventions"
Cohesion: 0.18
Nodes (10): 1. Python & Backend Conventions, 2. Frontend & Next.js Conventions, 3. Error Handling & Resilience Patterns, A. Next.js App Router & Server/Client Components, A. Type Hints & Pydantic Schemas, B. API Client & State Management, B. SQLAlchemy Models & Database Access, C. Authentication & Authorization (+2 more)

### Community 134 - "2. Locked Architectural Decisions"
Cohesion: 0.18
Nodes (10): 1. Goal & Objectives, 2. Locked Architectural Decisions, 3. Scope Boundaries & Out of Scope, Decision 1: Vehicle & Freight Presets, Decision 2: Per-Commodity Transit Spoilage Defaults, Decision 3: Line-Item Cost Structure, Decision 4: Like-for-Like Quality & Date Freshness Alignment, Decision 5: Multi-Factor Uncertainty Rating (+2 more)

### Community 135 - "README.md"
Cohesion: 0.27
Nodes (4): 1. Executive Summary, 2. Benchmark Evaluation Table, 3. Methodology & Guardrails, FPOLink TN — Price Forecasting Backtest & Model Validation Report

### Community 136 - "FPOLink TN — Inter-District Arbitrage & Transport Realization Specification"
Cohesion: 0.20
Nodes (9): 1. Executive Rationale & Defensibility Philosophy, 2. Mathematical Cost Model, 3. Vehicle Profile Configurations, 4. Commodity Perishability & Spoilage Matrix, 5. Multi-Factor Uncertainty Rubric, 6. Bilingual Advisory Disclaimers, Discrete Classification, FPOLink TN — Inter-District Arbitrage & Transport Realization Specification (+1 more)

### Community 137 - "FPOLink Technical Concerns & Architecture Watchpoints"
Cohesion: 0.20
Nodes (9): 1. Hosting & Infrastructure Constraints, 2. Upstream Data Feed Reliability, 3. Messaging Channel Considerations, 4. Privacy & Regulatory Compliance (DPDP Act), A. OGD & CEDA Gateway Timeouts, A. Render Free Tier Spin-Down, A. WhatsApp Cloud API Production Approval, B. Remote Database Latency During Bulk Operations (+1 more)

### Community 138 - "2. Tasks & Execution Sequence (Tracer-First)"
Cohesion: 0.22
Nodes (8): 1. Phase Overview, 2. Tasks & Execution Sequence (Tracer-First), Phase M3: Defensible Arbitrage & Transport Realization — Implementation Plan, Task M3.1: Upgrade Arbitrage Engine & Cost Realization Math (Tracer Slice), Task M3.3: Interactive UI Controls & Cost Visualizer, Task M3.4: Evaluation CLI Tool & Documentation Specification, Task M3.5: Automated Test Suite & Regression Verification, Task M3.6: Quality Checks & Git Commit

### Community 139 - "FPOLink TN — Product Roadmap"
Cohesion: 0.20
Nodes (9): Active Milestone: v0.9 — Cloud Hosting & Field Pilot, FPOLink TN — Product Roadmap, Future Milestone: v1.0 — Statewide Expansion & Voice Interface, Milestone Details, Milestone History & Status Overview, Milestone v0.5: Statewide Data Network, Milestone v0.6: Authentication & Management Dashboard, Milestone v0.7: Agricultural Intelligence & Multi-Channel Messaging (+1 more)

### Community 140 - "generate_erode_historical.py"
Cohesion: 0.29
Nodes (7): csv, math, get_daily_prices(), main(), date, Generate verified historical Erode Agmarknet dataset for 2026 pilot backfill.…, random

### Community 142 - "AggregationSummary.tsx"
Cohesion: 0.29
Nodes (7): AggregationSummary(), AggregationSummaryProps, BatchCard(), CROP_EMOJI, cropEmoji(), HarvestAggregation, HarvestBatch

### Community 143 - "tasks/page.tsx"
Cohesion: 0.39
Nodes (5): Task, TasksPage(), TelegramPage(), API_BASE, authFetch()

### Community 144 - "2. Core Subsystems & Data Pipelines"
Cohesion: 0.29
Nodes (6): 1. Architectural Style & Design Patterns, 2. Core Subsystems & Data Pipelines, 3. Security & Multitenancy Architecture, B. Transport-Agnostic Bot Engine, C. Supply & Demand Matching Engine, FPOLink System Architecture

### Community 145 - "2. Ingested Assets & Evidence"
Cohesion: 0.25
Nodes (7): 1. Onboarding Summary Overview, 2. Ingested Assets & Evidence, 3. Recommended Next Command, A. Codebase Architecture Map (`.planning/codebase/`), B. Core Planning Artifacts (`.planning/`), C. Live Cloud System Telemetry, FPOLink TN — GSD Onboarding Summary

### Community 146 - "FPOLink TN — Product Requirements Document (PRD)"
Cohesion: 0.25
Nodes (7): 1. Authentication & Security (AUTH), 2. Market Prices & Agricultural Intelligence (PRICE), 3. Multi-Channel Messaging & Farmer Chat (BOT), 4. Supply & Demand Matching (SUPPLY_DEMAND), 5. FPO Cooperative Operations (TASKS), 6. Infrastructure & Deployment (INFRA), FPOLink TN — Product Requirements Document (PRD)

### Community 147 - "AuditLog"
Cohesion: 0.22
Nodes (9): AuditLog, Base, log_audit_event(), Any, Session, UUID, Audit service — records operational mutations into immutable audit trail., Record an audit log entry. (+1 more)

### Community 150 - "2. Technical Decisions & Architectural Matrix"
Cohesion: 0.29
Nodes (6): 1. Executive Intent & Goals, 2. Technical Decisions & Architectural Matrix, Multi-Crop Dynamic Engine, Phase M5 Context: Statewide Multi-Crop & District-Dynamic Frontend Experience with JetBrainsMono & Modern Web Optimization, Statewide District Selection, Typography: JetBrains Mono + Noto Sans Tamil

### Community 151 - "status"
Cohesion: 0.47
Nodes (6): status(), 2.1 Farm / Plot Entity (`backend/app/models/farm.py`), 2.2 Buyer Entity (`backend/app/models/buyer.py`), 2.3 Buyer Requirement Entity (`backend/app/models/buyer.py`), 2.4 Supply Match Entity (`backend/app/models/supply_match.py` - NEW), 2. Data Model Evolution (Alembic Migration 0011)

### Community 152 - "FakeClient"
Cohesion: 0.33
Nodes (3): FakeClient, Records Bot API calls instead of hitting Telegram., test_channel_buttons_render_inline_keyboard()

### Community 153 - "Telegram bot (@Fpo_Link_Bot)"
Cohesion: 0.33
Nodes (5): Commands, Local dev (long polling), Production (Docker / Cloudflare Tunnel), Production (Render, webhook), Telegram bot (@Fpo_Link_Bot)

### Community 154 - "FPOLink TN — Project Specification"
Cohesion: 0.33
Nodes (5): 1. Executive Vision, 2. Core Entities & Stakeholders, 3. Technology Architecture Summary, 4. Key Constraints & Guiding Principles, FPOLink TN — Project Specification

### Community 155 - "vercel.json"
Cohesion: 0.33
Nodes (5): buildCommand, framework, installCommand, outputDirectory, $schema

### Community 156 - "3. Defense-in-Depth Isolation Implementation"
Cohesion: 0.33
Nodes (6): 3.1 Database-Aware `verify_fpo_access`, 3.2 Farmer Registry Scoping, 3.3 Task Board Tenant Scoping, 3.4 Harvest Aggregation & Lifecycle, 3.5 Demand & Supply Matching Scoping, 3. Defense-in-Depth Isolation Implementation

### Community 157 - "frontend/vercel.json"
Cohesion: 0.40
Nodes (4): buildCommand, framework, installCommand, $schema

### Community 158 - "FPOLink Project Status"
Cohesion: 0.50
Nodes (3): FPOLink Project Status, Next actions, Phase status

### Community 160 - "FPOLink TN — Current Workflow State"
Cohesion: 0.33
Nodes (5): 1. Project Overview, 2. Key Status Metrics, 3. Recent Session Accomplishments, 4. Immediate Next Steps, FPOLink TN — Current Workflow State

### Community 161 - "_jsonb_on_sqlite"
Cohesion: 0.67
Nodes (3): _jsonb_on_sqlite(), compiles, Local development on SQLite: store PostgreSQL JSONB columns as JSON text.

### Community 162 - "compile_jsonb_sqlite"
Cohesion: 0.67
Nodes (3): compile_jsonb_sqlite(), compile_uuid_sqlite(), compiles

### Community 163 - "compile_jsonb_sqlite"
Cohesion: 0.67
Nodes (3): compile_jsonb_sqlite(), compile_uuid_sqlite(), compiles

### Community 164 - "compile_jsonb_sqlite"
Cohesion: 0.67
Nodes (3): compile_jsonb_sqlite(), compile_uuid_sqlite(), compiles

### Community 165 - "compile_jsonb_sqlite"
Cohesion: 0.67
Nodes (3): compile_jsonb_sqlite(), compile_uuid_sqlite(), compiles

## Knowledge Gaps
- **481 isolated node(s):** `entrypoint.prod.sh script`, `entrypoint.sh script`, `CATEGORIES`, `AdapterRow`, `AddFarmerForm` (+476 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1500 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **28 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `v1/farmers.py`, `datetime`, `deps.py`, `import_farms_csv`, `Harvest`, `DbBotServices`, `Farmer`, `test_supply_demand_services.py`, `telegram_bot.py`, `seed_data`, `test_whatsapp_status_webhook.py`, `api/fpo.py`, `api/auth.py`, `BotEngine`, `status`, `admin_whatsapp.py`, `create_access_token`, `TestClient`, `Market`, `_get`, `verify_fpo_access`, `test_retention.py`, `db`, `v1/geography.py`, `WhatsAppUsageService`, `1. Architectural Pillars`, `FPO`, `FastAPI`, `test_telegram_bot.py`, `jwt.py`, `Market Price Data Coverage & Readiness Audit (T0.5)`, `api/telegram.py`, `api/whatsapp.py`, `v1/matching.py`, `sys`?**
  _High betweenness centrality (0.248) - this node is a cross-community bridge._
- **Why does `Farmer Addition Crash Fix` connect `Market Price Data Coverage & Readiness Audit (T0.5)` to `User`, `api.ts`?**
  _High betweenness centrality (0.159) - this node is a cross-community bridge._
- **Why does `formatApiError()` connect `api.ts` to `Market Price Data Coverage & Readiness Audit (T0.5)`?**
  _High betweenness centrality (0.148) - this node is a cross-community bridge._
- **Are the 111 inferred relationships involving `User` (e.g. with `get_data_health()` and `purge_testing_data()`) actually correct?**
  _`User` has 111 INFERRED edges - model-reasoned connections that need verification._
- **Are the 52 inferred relationships involving `Crop` (e.g. with `list_crops()` and `get_forecast()`) actually correct?**
  _`Crop` has 52 INFERRED edges - model-reasoned connections that need verification._
- **Are the 38 inferred relationships involving `Market` (e.g. with `get_data_health()` and `get_forecast()`) actually correct?**
  _`Market` has 38 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `Farmer` (e.g. with `create()` and `update()`) actually correct?**
  _`Farmer` has 46 INFERRED edges - model-reasoned connections that need verification._