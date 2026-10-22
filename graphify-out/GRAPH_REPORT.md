# Graph Report - FPOLink  (2026-10-22)

## Corpus Check
- 354 files · ~211,304 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 23 file(s) not represented in the graph (top: (none) 15, .csv 3, .example 1)

## Summary
- 3352 nodes · 9293 edges · 180 communities (153 shown, 27 thin omitted)
- Extraction: 90% EXTRACTED · 10% INFERRED · 0% AMBIGUOUS · INFERRED: 975 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `3468a176`
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
- farms.py
- datetime
- User
- test_whatsapp_bot.py
- bot.py
- Farmer
- Variety
- api/whatsapp.py
- api/fpo.py
- BotServices
- getLatestPrices
- api/auth.py
- json
- WeatherService
- BotEngine
- ._parse_row
- extract_features_for_series
- test_supply_demand_services.py
- Settings
- compilerOptions
- test_auth_deps.py
- TestClient
- MarketPrice
- run_backfill
- _get
- package.json
- backtest_forecaster.py
- verify_fpo_access
- matching/page.tsx
- main.py
- api.ts
- v1/crops.py
- compile_jsonb_sqlite
- react
- test_arbitrage_enhancements.py
- test_price_catchup.py
- commodities.py
- Market
- telegram_bot.py
- WhatsApp Integration: Task List
- data_cleaning.py
- forecasting.py
- config.py
- next.config.mjs
- postcss.config.mjs
- core/__init__.py
- worker.py
- entrypoint.sh
- next-env.d.ts
- schemas/__init__.py
- os
- v1/geography.py
- Operational Playbook: Manual CEDA Backfill, Coverage Audit & External Feeds
- FPOLink TN
- Implementation Plan: WhatsApp Integration for FPOLink TN
- test_daily_digest_full_flow_with_crop_matching_and_freshness
- Data Provenance & Fixture Verification Ledger
- test_whatsapp_usage_and_circuit_breaker.py
- 1. Architectural Pillars
- test_inbound_sweep.py
- parse_webhook
- rules/graphify.md
- workflows/graphify.md
- api/harvest.py
- CEDAAPIProvider
- Production Hosting Guide: Oracle Cloud Always Free + Cloudflare Tunnel
- sys
- farmers/page.tsx
- Detailed Task Specifications
- markets.py
- Detailed Task Specifications
- v1/intelligence.py
- lifespan
- Farm
- components.json
- 3. Verify First Successful Requests
- MarketAlias
- FPOLink TN — Production Deployment Guide
- Detailed Task Specifications
- test_send_buttons_contract
- test_latest_price_and_dashboard_whitelist_real_sources_only
- 1. Emergency Messaging Kill Switches
- Decisions Made in This Discussion
- 2. Locked Architectural Decisions
- 2. Locked Decisions & Core Tenets
- Crop
- FastAPI
- Human Checkpoints Operational Guide (Checkpoints A, B, C, D)
- FPOLink TN: 2-Week Field Pilot Runbook (Final: Pilot)
- 1. Resolution of Core Operational Questions
- MandiPricesProvider
- test_telegram_bot.py
- .validate_production_secrets
- MockChannel
- messaging/telegram.py
- Market Price Data Coverage & Readiness Audit (T0.5)
- api/telegram.py
- yield_estimator.py
- require_role
- marketData.ts
- entrypoint.prod.sh
- services/prices.py
- test_whatsapp_wiring_and_killswitch.py
- v1/matching.py
- days_to_nearest_festival
- test_conversation_state_ttl
- FPOLink TN — Phase 13: Supply + Demand Network (v0.8 Architecture Plan)
- v1/ingestion.py
- resolve_market
- ingest_ceda_live.py
- 2. Gaps Identified & Remediated During Audit
- FPOLink Technology Stack
- db
- FPOLink External Integrations
- 2. Test Suite Organization
- DailyDigestService
- TelegramBotService
- deps.py
- import_farms_csv
- 2. Frontend & Next.js Conventions
- 2. Locked Architectural Decisions
- README.md
- FPOLink TN — Inter-District Arbitrage & Transport Realization Specification
- FPOLink Technical Concerns & Architecture Watchpoints
- 2. Tasks & Execution Sequence (Tracer-First)
- FPOLink TN — Product Roadmap
- test_price_drop_triggers_downward_alert
- TelegramChatChannel
- price.py
- tasks/page.tsx
- 2. Core Subsystems & Data Pipelines
- 2. Ingested Assets & Evidence
- FPOLink TN — Product Requirements Document (PRD)
- calculate_quality_score
- TelegramClient
- test_worker_module_bootstraps_as_main
- 2. Technical Decisions & Architectural Matrix
- dependencies
- devDependencies
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
- layout.tsx
- compile_jsonb_sqlite
- .fetch_prices
- .use_psycopg3
- init_sqlite_schema
- BatchStatus
- .score_past_forecasts
- test_production_refuses_missing_whatsapp_secrets
- test_production_allows_disabled_whatsapp_without_secrets
- test_production_accepts_valid_whatsapp_secrets
- _random_phone
- 2. System Health Check
- .fetch_all
- get_whatsapp_activity
- compile_jsonb_sqlite
- compile_jsonb_sqlite
- _sqlite_pragmas

## God Nodes (most connected - your core abstractions)
1. `User` - 187 edges
2. `Crop` - 131 edges
3. `Market` - 104 edges
4. `Farmer` - 96 edges
5. `MarketPrice` - 93 edges
6. `FPO` - 78 edges
7. `DbBotServices` - 78 edges
8. `_get()` - 75 edges
9. `UserRole` - 74 edges
10. `District` - 69 edges

## Surprising Connections (you probably didn't know these)
- `3.1 Database-Aware `verify_fpo_access`` --references--> `verify_fpo_access()`  [INFERRED]
  docs/SECURITY_AUDIT.md → backend/app/api/deps.py
- `Step 2: Route Hostnames` --references--> `dashboard()`  [INFERRED]
  docs/HOSTING.md → backend/app/api/fpo.py
- `3.4 Harvest Aggregation & Lifecycle` --references--> `_enforce_harvest_scope()`  [INFERRED]
  docs/SECURITY_AUDIT.md → backend/app/api/harvest.py
- `3.3 Task Board Tenant Scoping` --references--> `_scoped()`  [INFERRED]
  docs/SECURITY_AUDIT.md → backend/app/api/tasks.py
- `Task M3.2: Extend API Schemas & REST Endpoint` --references--> `get_arbitrage_opportunities()`  [INFERRED]
  .planning/phases/M3-PLAN.md → backend/app/api/v1/intelligence.py

## Import Cycles
- None detected.

## Communities (180 total, 27 thin omitted)

### Community 0 - "InMemoryServices"
Cohesion: 0.07
Nodes (20): ConvState, Farmer, InMemoryServices, build_payload(), MockChannel, post_webhook(), TestClient, T3.2: Complete multi-step conversational harvest flow. (+12 more)

### Community 1 - "Step-by-Step Production Runbook"
Cohesion: 0.10
Nodes (19): Check if price date exceeds staleness threshold., English (`en`) Template:, Environment Variables Reference, Meta WhatsApp Cloud API — Production Setup Checklist, Optional: Template Specification for `price_move_alert`, Prerequisites, Production Readiness Verification Sign-Off, Step 1: Create Meta Business Account (+11 more)

### Community 2 - "sqlalchemy"
Cohesion: 0.10
Nodes (35): asyncio, AggregationBatch, BatchItem, Base, AuditLog model — enterprise audit trail for operational mutations., Buyer and buyer requirement models — staff-mediated commercial demand., Crop model — agricultural crop ontology., Farm plot model — discrete agricultural plots per farmer. (+27 more)

### Community 3 - "test_units.py"
Cohesion: 0.23
Nodes (13): convert_from_per_kg(), convert_to_per_kg(), Decimal, Unit conversion utilities for agricultural commodities., Convert a price from any unit to Rs/kg. Args: price: Price in the original unit…, Convert Rs/kg to another unit., Tests for unit conversions., test_convert_from_per_kg() (+5 more)

### Community 4 - "DbBotServices"
Cohesion: 0.06
Nodes (18): DbBotServices, Decimal, Atomically claim notice sending lease for farmer. Return True if claim acquired., Record timestamp when first-contact DPDP notice was confirmed delivered., Release leased claim after send failure so future inbound messages can retry., Record timestamp when first-contact DPDP notice was sent (alias to…, Active crops as {name: (English, Tamil, words farmers may use)} for the bot., Return latest weather advisory for district. (+10 more)

### Community 5 - "test_harvest_service_and_api.py"
Cohesion: 0.11
Nodes (36): Harvest, HarvestGrade, HarvestStatus, Base, str, HarvestCreate, Pydantic schemas for harvest submission, updates, and listings., create_harvest() (+28 more)

### Community 6 - "alembic"
Cohesion: 0.04
Nodes (7): alembic, Run migrations in 'offline' mode. This configures the context with just a URL…, Run migrations in 'online' mode. In this scenario we need to create an Engine…, run_migrations_offline(), run_migrations_online(), logging_config, sqlalchemy_dialects

### Community 7 - "api/farmers.py"
Cohesion: 0.08
Nodes (54): create(), _enforce_farmer_fpo_scope(), get_one(), get_whatsapp_invite(), list_all(), put, Session, UUID (+46 more)

### Community 8 - "farms.py"
Cohesion: 0.10
Nodes (46): create(), _enforce_farm_scope(), _farm_to_response(), get_one(), get_yield_estimate(), import_csv(), list_all(), delete (+38 more)

### Community 9 - "datetime"
Cohesion: 0.06
Nodes (50): ABC, MarketDataProvider, Base market data provider interface. All data source adapters inherit from this…, Abstract base class for market data providers., Check if this data source is currently accessible., CEDA Data Portal API provider (Ashoka University). Programmatic access to raw…, CEDAProvider, CEDA Agri-Market provider (Ashoka University). Parses the historical CSV data… (+42 more)

### Community 10 - "User"
Cohesion: 0.12
Nodes (25): Base, str, User, UserRole, hash_password(), Hash a password using Argon2id., Seed Supply and Demand Network for Erode Pilot (Phase 13 / v0.8) Populates: 1.…, seed_supply_demand() (+17 more)

### Community 11 - "test_whatsapp_bot.py"
Cohesion: 0.11
Nodes (22): parse_qty(), button_payload(), CropAwareServices, FakeChannel, make_services(), post(), InMemoryServices plus the optional crop list and selling advice., test_alerts_opt_in_and_out() (+14 more)

### Community 12 - "bot.py"
Cohesion: 0.09
Nodes (28): WhatsAppSettings, detect_crop(), detect_intent(), _match(), PriceInfo, WhatsApp bot engine. Transport-agnostic: depends only on MessageChannel (send)…, _tokens(), env() (+20 more)

### Community 13 - "Farmer"
Cohesion: 0.09
Nodes (30): Farmer, Base, FPO, Base, _development_password(), FPOLink TN — Database Seed Script (v2) Uses Argon2 hashing (pwdlib) and…, Seed the database with initial reference data., seed_data() (+22 more)

### Community 14 - "Variety"
Cohesion: 0.08
Nodes (36): CropAlias, Base, CropAlias model — maps raw, regional, and provider strings to canonical crops., VarietySourceMapping, Base, VarietyAlias model — maps variety names and codes to canonical varieties., VarietyAlias, Base (+28 more)

### Community 15 - "api/whatsapp.py"
Cohesion: 0.05
Nodes (55): AsyncClient, _channel(), get_channel(), get_status_service(), get_wa_settings(), BackgroundTasks, Request, WhatsApp Cloud API webhook. GET /api/whatsapp/webhook -> Meta's one-time… (+47 more)

### Community 16 - "api/fpo.py"
Cohesion: 0.13
Nodes (37): create(), dashboard(), get_one(), list_all(), put, Session, FPO management endpoints., Get dashboard statistics for an FPO. (+29 more)

### Community 17 - "BotServices"
Cohesion: 0.07
Nodes (13): BotServices, Decimal, Protocol, Everything the bot needs from your app. Implement against your DB/services., Atomically record message_id; False if already seen (Meta retries webhooks)., Fetch open confirmed or candidate buyer requirements for farmer's crops/FPO., Optional: {crop: (English name, Tamil name, words farmers use)} beyond the…, Optional: one line on where the crop sells better after transport costs. (+5 more)

### Community 18 - "getLatestPrices"
Cohesion: 0.10
Nodes (22): PricesPage(), resolveCropUnit(), MandiPricesTable(), load(), MandiPricesTableProps, PriceChart(), initCrops(), PriceChartProps (+14 more)

### Community 19 - "api/auth.py"
Cohesion: 0.15
Nodes (29): change_password(), get_me(), login(), Session, Authentication endpoints — register, login, refresh., Require the current password, then replace it before granting a normal session., Get new access token using refresh token., Get current authenticated user's profile. (+21 more)

### Community 20 - "json"
Cohesion: 0.15
Nodes (16): mock, Unit and contract tests for CEDA Data Portal API provider., Verify provider retries on 504 Gateway Timeout before failing., Verify circuit breaker trips after consecutive failures and fast-fails., Verify non-transient 4xx errors propagate immediately without retry and without…, Assert commodities endpoint returns list matching schema., Assert geographies endpoint returns state and district hierarchy., Assert prices endpoint posts exact schema and converts quintal to kg. (+8 more)

### Community 21 - "WeatherService"
Cohesion: 0.09
Nodes (23): NASAPowerProvider, Any, date, Fetch long-term weather history from NASA POWER., Fetch daily weather data from NASA POWER., Any, date, Fetch weather data from Open-Meteo API. (+15 more)

### Community 22 - "BotEngine"
Cohesion: 0.11
Nodes (17): Button, InboundMessage, MessageChannel, Protocol, Messaging package: transport-agnostic types and WhatsApp Cloud API adapter., BotEngine, crop_name(), format_price() (+9 more)

### Community 23 - "._parse_row"
Cohesion: 0.10
Nodes (11): date, Decimal, Parse a single CSV row into a PriceRecord., Try multiple possible column names., Try multiple date formats., Parse CEDA CSV and return standardized price records. Expected CSV columns (may…, Find a CEDA CSV file matching the crop/district., date (+3 more)

### Community 24 - "extract_features_for_series"
Cohesion: 0.15
Nodes (18): extract_features_for_series(), get_latest_feature_vector(), DataFrame, Agricultural Feature Store Engine for FPOLink TN. Extracts tabular feature…, Generate the single inference feature vector for the most recent observation to…, Transform historical price observations into an ML feature matrix. Args: df:…, Unit tests for the Agricultural Feature Store engine., Verify single-row feature vector generation for live inference. (+10 more)

### Community 25 - "test_supply_demand_services.py"
Cohesion: 0.16
Nodes (27): post_requirement(), Post a commercial crop procurement requirement., BuyerCreate, BuyerRequirementCreate, BuyerRequirementUpdate, create_buyer(), create_buyer_requirement(), delete_buyer() (+19 more)

### Community 26 - "Settings"
Cohesion: 0.21
Nodes (11): Application settings loaded from environment variables and .env file., Settings, Tests for production security enforcement in configuration., test_development_allows_default_secret_key(), test_production_accepts_strong_secret_key(), test_production_refuses_default_secret_key(), test_production_rejects_default_database_password(), test_production_rejects_demo_mode() (+3 more)

### Community 27 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 28 - "test_auth_deps.py"
Cohesion: 0.27
Nodes (9): create_test_app(), Unit tests for authentication and authorization dependencies in app.api.deps., test_expired_token_returns_401(), test_invalid_token_returns_401(), test_require_role_authorized_returns_200(), test_require_role_insufficient_permission_returns_403(), test_require_role_unauthenticated_returns_401(), test_unauthenticated_request_returns_401() (+1 more)

### Community 29 - "TestClient"
Cohesion: 0.17
Nodes (5): TestClient, TestLogin, TestProtectedRoutes, TestRefresh, TestRegister

### Community 30 - "MarketPrice"
Cohesion: 0.04
Nodes (85): get_data_health(), purge_testing_data(), Session, Admin endpoints — manual ingestion trigger, system status., Manually trigger DPDP retention purge., System-wide data health report: rows/market/day, calendar gaps, and outlier…, Manually trigger price data ingestion (admin only)., Trigger live weather forecast ingestion from Open-Meteo for a district or… (+77 more)

### Community 31 - "run_backfill"
Cohesion: 0.20
Nodes (8): Load bulk records from a local CSV file path., Parse bulk price records from CSV text., generate_gap_report(), main(), date, Execute backfill and print gap report., Analyze date continuity and print a mandi observation gap report., run_backfill()

### Community 32 - "_get"
Cohesion: 0.20
Nodes (23): create_task(), delete_task(), _get(), list_tasks(), delete, patch, Session, UUID (+15 more)

### Community 33 - "package.json"
Cohesion: 0.06
Nodes (26): ForecastAreaChart, PriceHistoryChart, ForecastAreaChartProps, ForecastChartPoint, HistoryChartPoint, PriceHistoryChartProps, name, private (+18 more)

### Community 34 - "backtest_forecaster.py"
Cohesion: 0.19
Nodes (12): evaluate_series_rolling_origin(), main(), DataFrame, Path, Rolling-Origin Walk-Forward Backtest Harness and Model Promotion CLI. Evaluates…, Generate docs/FORECAST_BACKTEST.md report., Run walk-forward evaluation across all commodity series in dataset., Run rolling-origin backtest on a single (crop, market) time series. (+4 more)

### Community 35 - "verify_fpo_access"
Cohesion: 0.12
Nodes (38): Check if current user has authorization to access/modify a specific FPO tenant.…, verify_fpo_access(), _buyer_to_response(), create(), get_one(), get_requirement(), import_csv(), list_all() (+30 more)

### Community 36 - "matching/page.tsx"
Cohesion: 0.14
Nodes (39): CATEGORIES, AdapterRow, Badge(), BadgeProps, Button, ButtonProps, Card, CardContent (+31 more)

### Community 37 - "main.py"
Cohesion: 0.22
Nodes (6): get_buyers(), health_check(), contextlib, fastapi_middleware_cors, fastapi_middleware_gzip, fastapi_responses

### Community 38 - "api.ts"
Cohesion: 0.05
Nodes (80): CommoditiesRegistryPage(), AdminPage(), BuyersPage(), MatchingPage(), FPOActionWorkspace(), WhatsAppPage(), AggregationSummary(), AggregationSummaryProps (+72 more)

### Community 39 - "v1/crops.py"
Cohesion: 0.16
Nodes (24): list_crops(), Session, Crop listing endpoints., List all configured crops., get_crop(), list_crop_varieties(), list_crops(), Session (+16 more)

### Community 40 - "compile_jsonb_sqlite"
Cohesion: 0.67
Nodes (3): compile_jsonb_sqlite(), compile_uuid_sqlite(), compiles

### Community 41 - "react"
Cohesion: 0.08
Nodes (43): ChangePasswordPage(), handleSubmit(), LoginPage(), handleSubmit(), FooterProps, LanguageSwitcher(), NavbarProps, apiIsHealthy() (+35 more)

### Community 42 - "test_arbitrage_enhancements.py"
Cohesion: 0.06
Nodes (43): compute_uncertainty_score(), find_market_arbitrage(), get_default_spoilage_risk(), haversine_distance_km(), market_coordinates(), Session, UUID, Inter-District Market Arbitrage and Transport Net Realization Engine. Computes… (+35 more)

### Community 43 - "test_price_catchup.py"
Cohesion: 0.32
Nodes (11): price_run_missed(), True when the latest daily price slot passed without a completed statewide run.…, add_run(), fixture, Missed-run check behind the daily price catch-up on hosts that sleep (Render…, six_am_slot(), test_before_todays_slot_checks_yesterdays(), test_missed_when_last_run_was_yesterday() (+3 more)

### Community 44 - "commodities.py"
Cohesion: 0.11
Nodes (24): get_commodity_detail(), list_commodities(), Session, UUID, Commodity registry API endpoints — Canonical commodity intelligence., List canonical crops with counts of varieties, aliases, source mappings, and…, Get rich commodity profile with varieties, aliases, source mappings, and active…, CropSourceMapping (+16 more)

### Community 45 - "Market"
Cohesion: 0.11
Nodes (36): get_statewide_freshness(), Get statewide coverage and freshness telemetry across all 38 districts., TimestampMixin, DataSource, Block, District, Base, Geography models — State, District, Taluk, Block, Village hierarchy. (+28 more)

### Community 46 - "telegram_bot.py"
Cohesion: 0.11
Nodes (21): Authentication service — password hashing with Argon2 via pwdlib., Telegram front-end for the transport-agnostic BotEngine. Flow: 1. Unknown chat…, create_or_update_admin(), main(), Bootstrap / provision the initial FPOLink administrator account. Reads…, Create or update admin account idempotently with production password hardening., main(), Interactively provision an administrator using the shared hardened bootstrap. (+13 more)

### Community 47 - "WhatsApp Integration: Task List"
Cohesion: 0.07
Nodes (28): Checkpoint A: end-to-end from a real phone; CI green; no secrets in repo, Checkpoint B: harvest submitted by chat is visible to FPO staff, Checkpoint C: dry run with 3 test farmers, Checkpoint D: staging E2E with a real phone, Checkpoint E: Statewide Foundation Sign-Off, Checkpoint G: Agricultural Intelligence Sign-Off, Checkpoint H: Supply + Demand Network Sign-Off, FPOLink MVP Sprint — Tasks M1–M4 (+20 more)

### Community 48 - "data_cleaning.py"
Cohesion: 0.16
Nodes (17): clean_price_records(), detect_anomaly_mad(), _normalize_record(), Decimal, Data cleaning utilities for market price data., Clean and validate a list of price records., Validate a price record., Normalize a price record. (+9 more)

### Community 49 - "forecasting.py"
Cohesion: 0.09
Nodes (33): compute_forecast_signal(), ForecastingService, load_price_series(), DataFrame, Session, UUID, Dual-Engine Agricultural Price Forecasting for FPOLink TN. Primary Engine:…, Dual-engine forecasting and signal generation service. (+25 more)

### Community 50 - "config.py"
Cohesion: 0.08
Nodes (28): check_status(), load_fixture_records(), main(), date, Path, Open Government Data (data.gov.in) Ingestion CLI Harness. Provides programmatic…, Check configuration and connectivity for OGD., Parse records from a local JSON fixture using OGDProvider's record parser. (+20 more)

### Community 54 - "worker.py"
Cohesion: 0.07
Nodes (43): apscheduler_schedulers_blocking, ConversationState, OutboundMessage, Base, WhatsApp bot models for message idempotency, conversation state, and outbound…, Store active conversation state machines per WhatsApp ID with TTL., Log outbound messages sent via Meta Cloud API for auditing, status updates, and…, purge_conversation_state() (+35 more)

### Community 61 - "schemas/__init__.py"
Cohesion: 0.27
Nodes (15): FPOLink Pydantic schemas package., MatchBreakdown, MatchCandidate, MatchCandidateListResponse, MatchConfirmRequest, MatchCreate, MatchListResponse, MatchResponse (+7 more)

### Community 62 - "os"
Cohesion: 0.24
Nodes (9): admin_headers(), create_tables(), _enable_whatsapp_for_legacy_bot_tests(), fixture, Test configuration and fixtures., Create all tables before tests, drop after., WhatsApp ships disabled (Telegram is the farmer channel), but the dormant…, Provision a trusted admin identity for tests of protected operations. (+1 more)

### Community 65 - "v1/geography.py"
Cohesion: 0.13
Nodes (31): create_district(), create_state(), create_taluk(), create_village(), get_district(), list_districts(), list_states(), list_taluks_for_district() (+23 more)

### Community 66 - "Operational Playbook: Manual CEDA Backfill, Coverage Audit & External Feeds"
Cohesion: 0.22
Nodes (8): 1. Manual CEDA CSV Export & Ingestion, 2. CEDA Support Communication & API Key Extension, 3. Data.gov.in (OGD) Live API Key Setup, 4. Meta Test App Setup & Webhook Payload Capture (T0.3), Operational Playbook: Manual CEDA Backfill, Coverage Audit & External Feeds, Step 1: Download from CEDA Portal, Step 2: Ingest with Verified `--source ceda` Tag, Step 3: Run the Coverage Audit

### Community 67 - "FPOLink TN"
Cohesion: 0.12
Nodes (16): 1. Clone & Configure, 2. Launch Stack with Docker Compose, 3. Seed Reference Data, 4. Create the First Admin, API v1 Routing Matrix, Architecture Overview, Data Provenance & Live Data Verification, Database Schema & Migrations (+8 more)

### Community 68 - "Implementation Plan: WhatsApp Integration for FPOLink TN"
Cohesion: 0.12
Nodes (16): Agent Working Rules (paste at the top of every agent task), Constraints, Dates that matter, Implementation Plan: WhatsApp Integration for FPOLink TN, Later backlog (only if the pilot justifies it), Open Questions (need your answers), Overview, Phase 0: De-risk the external dependencies (start immediately, in parallel) (+8 more)

### Community 69 - "test_daily_digest_full_flow_with_crop_matching_and_freshness"
Cohesion: 0.22
Nodes (8): digest_db(), FakeChannel, anyio, fixture, Daily digest must abort immediately when circuit breaker is tripped., Daily digest matches farmer crops, sends only fresh prices, and logs outbound…, test_daily_digest_aborts_when_circuit_breaker_tripped(), test_daily_digest_full_flow_with_crop_matching_and_freshness()

### Community 70 - "Data Provenance & Fixture Verification Ledger"
Cohesion: 0.29
Nodes (6): 1. Fixture Inventory & Verification Status, 2. Sample Data Isolation Guarantee, 3. Guide: Ingesting Verified Real Mandi Data, A. Live Daily Ingestion (data.gov.in OGD Agmarknet), B. Historical Backfill (CEDA Ashoka University), Data Provenance & Fixture Verification Ledger

### Community 71 - "test_whatsapp_usage_and_circuit_breaker.py"
Cohesion: 0.08
Nodes (31): get_admin_inbound(), get_usage_service(), get_whatsapp_usage(), Session, Admin endpoints for WhatsApp usage tracking, cost audits, and circuit breaker…, Get aggregated WhatsApp message usage, delivery rates, cost breakdown, and…, Get recent inbound WhatsApp messages for audit., Track recipient delivery health and mark unreachable numbers after repeated… (+23 more)

### Community 72 - "1. Architectural Pillars"
Cohesion: 0.07
Nodes (27): AuditLog, Base, log_audit_event(), Any, Session, UUID, Audit service — records operational mutations into immutable audit trail., Record an audit log entry. (+19 more)

### Community 73 - "test_inbound_sweep.py"
Cohesion: 0.18
Nodes (22): Log incoming WhatsApp webhook message IDs for deduplication / idempotency., WhatsAppInbound, At-least-once sweep: reprocess WhatsApp inbound messages stuck in 'received'.…, Find and increment retry on messages stuck in 'received' status. Messages that…, sweep_stuck_inbound(), DummyChannel, anyio, fixture (+14 more)

### Community 74 - "parse_webhook"
Cohesion: 0.16
Nodes (25): parse_webhook(), Extract user messages. Delivery/read status callbacks yield an empty list., test_status_only_payload_is_ignored(), load_fixture(), Parametrized contract tests verifying WhatsApp Cloud API fixtures against…, Verify read receipt status webhook parsing., Verify delivery failure callback parsing and error extraction., Load JSON fixture file. (+17 more)

### Community 77 - "api/harvest.py"
Cohesion: 0.16
Nodes (22): create_harvest(), _enforce_harvest_scope(), get_harvest(), get_harvest_aggregation(), list_harvests(), date, patch, Session (+14 more)

### Community 78 - "CEDAAPIProvider"
Cohesion: 0.11
Nodes (17): CEDAAPIProvider, Any, date, Execute HTTP request with short timeout, retries, and circuit breaker., Retrieve list of all commodities: [{"id": int, "name": str}]., Test if the configured API key is valid., Retrieve geographies: [{"state_id": int, "state_name": str, "districts": [...]}], Retrieve markets: POST /agmarknet/markets. (+9 more)

### Community 79 - "Production Hosting Guide: Oracle Cloud Always Free + Cloudflare Tunnel"
Cohesion: 0.08
Nodes (26): 1. Architecture & Cost Model, 2. Oracle Cloud VM Provisioning, 3. Host Initialization & Docker Installation, 4. Cloudflare Zero Trust Tunnel Setup, 5. Clone and Configure FPOLink, 6. Launch Production Stack, 7. Verification & Farmer Channel Wiring, 8. Automated Systemd Boot Service (+18 more)

### Community 80 - "sys"
Cohesion: 0.08
Nodes (30): argparse, main(), CEDA Historical Data Backfill Script. Loads historical agricultural market…, check_coverage(), main(), print_coverage_report(), Market price data coverage analyzer for FPOLink TN. Checks monthly price record…, Execute monthly coverage query across markets. (+22 more)

### Community 81 - "farmers/page.tsx"
Cohesion: 0.12
Nodes (25): AddFarmerForm, AddPlotForm, EMPTY_FORM, EMPTY_PLOT_FORM, FarmersPage(), FarmerInviteCard(), load(), FarmerInviteCardProps (+17 more)

### Community 82 - "Detailed Task Specifications"
Cohesion: 0.17
Nodes (11): Checkpoint E: Statewide Platform Foundation Sign-Off, Detailed Task Specifications, Executive Summary, Implementation Plan: Phase 8 — Statewide Platform Foundation (v0.5 Architecture), Task 8.2: Agricultural Ontology & Canonical Crop/Variety Registry with Aliases, Task 8.3: Market Master Registry & Canonical Market Aliases, Task 8.4: Multi-Tenant RBAC, Organization Scoping & Audit Logging, Task 8.6: API v1 Routing & Compatibility Shims (+3 more)

### Community 83 - "markets.py"
Cohesion: 0.22
Nodes (16): get_market(), list_markets(), Session, UUID, Market API v1 endpoints — market registry and resolution., List markets with optional district and type filtering., Get single market by ID with its configured aliases., Resolve an incoming raw market name or code to a canonical Market. (+8 more)

### Community 84 - "Detailed Task Specifications"
Cohesion: 0.11
Nodes (18): Detailed Task Specifications, Executive Summary, Implementation Plan: Phase 11 — Agricultural Intelligence (v0.7 Architecture), Task 11.10: Checkpoint G Sign-Off & Documentation, Task 11.2: Feature Store Test Suite (`backend/tests/test_feature_store.py`), Task 11.3: LightGBM Quantile & Baseline Forecasting Engine (`backend/app/ml/forecasting.py`), Task 11.4: Signal Generation & Model Versioning, Task 11.5: Worker Scheduled Prediction Pipeline (+10 more)

### Community 85 - "v1/intelligence.py"
Cohesion: 0.17
Nodes (21): get_arbitrage_opportunities(), get_crop_forecast(), get_price_spreads(), Session, UUID, Agricultural Intelligence API v1: Forecasting, Arbitrage & Spread Analysis., Evaluate inter-district market arbitrage deducting estimated freight, handling,…, Analyze statewide price dispersion and identify highest/lowest reporting… (+13 more)

### Community 86 - "lifespan"
Cohesion: 0.21
Nodes (11): lifespan(), anyio, Verify /api/health returns 200 and db: ok when database engine succeeds., Verify /api/health returns 503 and db: error when database engine fails., Verify lifespan initializes Sentry when SENTRY_DSN is set., Verify lifespan skips Sentry when SENTRY_DSN is None or empty., test_health_check_db_failure(), test_health_check_success() (+3 more)

### Community 87 - "Farm"
Cohesion: 0.07
Nodes (43): Buyer, BuyerRequirement, Base, Farm, Base, get_supply_demand_summary(), Aggregate total standing acreage, estimated yield, harvest stock, and…, Journey 4: Buyer requirement -> supply match -> staff follow-up task. (+35 more)

### Community 88 - "components.json"
Cohesion: 0.12
Nodes (16): aliases, components, hooks, lib, ui, utils, rsc, $schema (+8 more)

### Community 89 - "3. Verify First Successful Requests"
Cohesion: 0.12
Nodes (15): 1. Backend Health Probe, 1. Prerequisites, 2. Statewide Districts Probe (v1), 2. Step-by-Step Setup, 2. Verified Crops Feed, 3. Latest Verified Mandi Prices (v1), 3. Staff Web Dashboard, 3. Verify First Successful Requests (+7 more)

### Community 90 - "MarketAlias"
Cohesion: 0.08
Nodes (23): MarketAlias, Base, Test GET and POST /api/v1/markets endpoints., test_api_v1_markets_resolve(), A. Price Ingestion & Normalization Pipeline, 1. Python & Backend Conventions, A. Type Hints & Pydantic Schemas, B. SQLAlchemy Models & Database Access (+15 more)

### Community 91 - "FPOLink TN — Production Deployment Guide"
Cohesion: 0.12
Nodes (16): 1. Architecture, 2. Prerequisites, 3. Cloudflare Tunnel Setup, 4. Configuration, 5. Launch Stack, 6. Verification, 7. Operational Runbook & Maintenance, FPOLink TN — Production Deployment Guide (+8 more)

### Community 92 - "Detailed Task Specifications"
Cohesion: 0.14
Nodes (13): Detailed Task Specifications, Executive Summary, Implementation Plan: Phase 9 — Statewide Data Network (v0.6 Architecture), Task 9.10: Checkpoint F Statewide Data Network Sign-Off, Task 9.1: Reference Invariants & Automated Count Assertions, Task 9.2: Complete Regulated Market Master Registry, Task 9.3: External Source Mapping Models & Migration 0010, Task 9.4: Commodity Registry UI & Admin API (+5 more)

### Community 93 - "test_send_buttons_contract"
Cohesion: 0.29
Nodes (10): client(), Provide a test client using the shared test database session., anyio, mock, Assert exact JSON payload and headers for text messages., Assert exact JSON for interactive buttons, max 3 buttons, and 20 char title…, Assert exact JSON for business-initiated templates with body parameters., test_send_buttons_contract() (+2 more)

### Community 94 - "test_latest_price_and_dashboard_whitelist_real_sources_only"
Cohesion: 0.29
Nodes (8): anyio, fixture, Verify that latest_price and dashboard only return prices from whitelisted…, Verify that seed demo prices are never picked up by DbBotServices.latest_price., In-memory SQLite database factory for unit tests., test_db_factory(), test_latest_price_and_dashboard_whitelist_real_sources_only(), test_seed_script_prices_never_served_to_bot()

### Community 95 - "1. Emergency Messaging Kill Switches"
Cohesion: 0.14
Nodes (14): 1.1 Emergency WhatsApp Kill Switch (Dormant by default in MVP), 1.2 Emergency Telegram Kill Switch (Active Live Channel in MVP), 1. Emergency Messaging Kill Switches, Expected Output:, How to Disable Telegram, How to Disable WhatsApp, How to Verify the Kill Switch Is Active, Re-Enabling Procedure (+6 more)

### Community 96 - "Decisions Made in This Discussion"
Cohesion: 0.29
Nodes (7): D1: Deployment Strategy — Cloudflare Tunnel, D2: Meta Production Checklist, D3: Data Retention Policy, D5: Observability — Sentry Init + DB Health Check, D6: Ops Runbook — Kill Switch Procedure, D7: `.env.example` Update, Decisions Made in This Discussion

### Community 97 - "2. Locked Architectural Decisions"
Cohesion: 0.17
Nodes (11): 1. Vision & Roadmap Positioning, 2. Locked Architectural Decisions, 3. Scope Boundaries, D1: Dual-Engine Forecasting Architecture (LightGBM Quantile Regression + Robust Baseline), D3: Inter-District Arbitrage & Net Realized Margin Engine (`backend/app/services/arbitrage.py`), D5: Scheduled Autonomous Intelligence Worker, Deferred to Phase 13–15 (v0.8), In Scope (Phase 11) (+3 more)

### Community 98 - "2. Locked Decisions & Core Tenets"
Cohesion: 0.17
Nodes (11): 1. Vision & Architectural Transformation, 2. Locked Decisions & Core Tenets, 3. Explicitly Out of Scope for Phase 8, D2: Multi-Tenant RBAC & Organization Scoping, D3: Agricultural Crop Ontology & Canonical Alias Registry, D4: Market Registry & Canonical Market Aliases, D5: Ingestion Orchestration & Explainable Data Quality Framework, D6: API Versioning (v1) & Seamless Compatibility (+3 more)

### Community 99 - "Crop"
Cohesion: 0.11
Nodes (17): get_forecast(), Session, Legacy backward-compatible forecast endpoint delegating to ForecastingService., Crop, Base, Test Crop model with category, seasonality, perishability, and units., test_crop_ontology_expansion(), fixture (+9 more)

### Community 100 - "FastAPI"
Cohesion: 0.21
Nodes (11): list_audit_logs(), Session, Audit API v1 endpoints — view system audit trails., List audit log records (admin only)., get_db(), Session, FastAPI dependency that provides a database session., AuditLogListResponse (+3 more)

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
Cohesion: 0.21
Nodes (17): _contact(), factory(), FakeClient, anyio, fixture, Telegram channel: parsing, linking/auto-registration, command routing, harvest…, Records Bot API calls instead of hitting Telegram., _svc() (+9 more)

### Community 106 - ".validate_production_secrets"
Cohesion: 0.25
Nodes (7): 6. Network & CORS Origin Protection, model_validator, Codebase Assets to Reuse, Deferred Ideas (out of Phase 5 scope), Next Step, Phase 5 — Production Readiness: CONTEXT.md, Prior Decisions Carried Forward

### Community 108 - "messaging/telegram.py"
Cohesion: 0.15
Nodes (15): BackgroundTasks, Request, receive(), webhook_secret(), derive_webhook_secret(), map_command(), parse_update(), Telegram Bot API adapter: update parsing, webhook secret check, and sending.… (+7 more)

### Community 109 - "Market Price Data Coverage & Readiness Audit (T0.5)"
Cohesion: 0.20
Nodes (9): 1. Executive Summary, 2. Coverage Audit Results (2026-10-04), 3. Modeling & Operational Implications, 4. Ashoka CEDA API Integration & Platform Fixes (2026-10-04), Banana Coverage (Erode District), CEDA Agmarknet Provider Status, Farmer Addition Crash Fix, Market Price Data Coverage & Readiness Audit (T0.5) (+1 more)

### Community 110 - "api/telegram.py"
Cohesion: 0.18
Nodes (17): get_client(), get_service(), public_base_url(), Telegram bot webhook (farmer channel). POST /api/telegram/webhook -> updates…, Point Telegram at this API and publish the command menu., register_webhook(), _service(), set_webhook() (+9 more)

### Community 111 - "yield_estimator.py"
Cohesion: 0.17
Nodes (14): estimate_crop_yield(), estimate_farm_yield(), get_irrigation_factor(), get_soil_factor(), date, Session, UUID, Rule-Based Yield Estimator for Tamil Nadu Agricultural Commodities. Estimates… (+6 more)

### Community 112 - "require_role"
Cohesion: 0.09
Nodes (19): Dependency factory: restrict endpoint to specific roles. Automatically maps…, require_role(), 1. Goal & Objectives, 3. Locked Architectural Decisions, 4. Scope Boundaries & Out of Scope, Decision 1: Database-Aware `verify_fpo_access`, Decision 3: Bulk Import & Tenant Boundaries, Decision 4: Production Bootstrap Security Standards (+11 more)

### Community 115 - "services/prices.py"
Cohesion: 0.06
Nodes (54): latest_prices(), list_markets(), price_anomalies(), price_history(), price_trend(), Session, Price endpoints — latest prices, history, trends, anomalies., Bulk import mandi prices from CSV file. (+46 more)

### Community 116 - "test_whatsapp_wiring_and_killswitch.py"
Cohesion: 0.12
Nodes (15): _bot(), get_bot(), Return active BotEngine or raise 503 if WhatsApp is disabled via kill switch., Unit tests for WhatsApp bot wiring, settings validation, and kill switch., When WHATSAPP_ENABLED is False, both GET and POST webhooks return 503., get_bot() returns an active BotEngine when enabled., test_get_bot_dependency_wired(), test_kill_switch_returns_503() (+7 more)

### Community 117 - "v1/matching.py"
Cohesion: 0.12
Nodes (32): confirm_match(), get_candidates(), list_matches(), _match_to_response(), Session, UUID, Semi-Automatic Demand-Supply Matching API endpoints., Record a suggested demand-supply match. (+24 more)

### Community 118 - "days_to_nearest_festival"
Cohesion: 0.27
Nodes (12): days_to_nearest_festival(), get_festival_features(), is_festival(), date, Tamil Nadu holiday/festival features for price prediction. Uses Python…, Check if a date is a known festival day., Days until the nearest festival within a window. Returns window+1 if none., Generate festival-related features for a given date. (+4 more)

### Community 119 - "test_conversation_state_ttl"
Cohesion: 0.25
Nodes (8): anyio, fixture, Verify conversation state persistence and 30-minute TTL expiration., In-memory SQLite database factory for unit tests., Verify first_time returns True on first delivery, False on retries, and handles…, test_conversation_state_ttl(), test_db_factory(), test_first_time_atomic_dedup()

### Community 120 - "FPOLink TN — Phase 13: Supply + Demand Network (v0.8 Architecture Plan)"
Cohesion: 0.13
Nodes (14): 1. Locked Strategic Decisions, 3.1 Rule-Based Yield Estimator (`backend/app/services/yield_estimator.py`), 3.2 Semi-Automatic Matching Engine (`backend/app/services/matching_service.py`), 3. Business Logic & Core Algorithms, 4.1 Free Service Conversation Window (Inbound-First), 4.2 Gated Low-Cost Outbound Nudge (Only When Staff Confirms), 4. WhatsApp Zero-Cost Interaction Architecture, 5.1 Farm Plot Endpoints (`/api/v1/farms`) (+6 more)

### Community 121 - "v1/ingestion.py"
Cohesion: 0.23
Nodes (11): get_ingestion_run(), list_ingestion_runs(), BaseModel, Session, UUID, Ingestion Center Telemetry and Control API (v1)., Trigger a statewide or targeted price ingestion run., Get paginated history of ingestion runs with telemetry metrics. (+3 more)

### Community 122 - "resolve_market"
Cohesion: 0.18
Nodes (12): _clean_str(), Session, UUID, Market canonicalization resolver service., Normalize input string: strip, lowercase, collapse whitespace., Resolve any raw mandi string or code to a canonical Market entity. Precedence:…, resolve_market(), Verify Stage 0 deterministic external ID resolution for regulated markets. (+4 more)

### Community 123 - "ingest_ceda_live.py"
Cohesion: 0.21
Nodes (13): check_status(), main(), date, CEDA Agmarknet Live Ingestion & Authentication CLI Harness. Provides…, Verify OTP with Ashoka CEDA., Validate and write new CEDA_API_KEY into .env., Fetch live data from CEDA and ingest into PostgreSQL., Check connectivity and key validity against CEDA API. (+5 more)

### Community 124 - "2. Gaps Identified & Remediated During Audit"
Cohesion: 0.17
Nodes (12): At-least-once sweep for stuck inbound messages (T5.4)., run_inbound_sweep(), Verify .env.example contains all critical Settings fields (T5.7 Nyquist check)., test_env_example_contains_all_critical_settings(), Verify app.worker.run_inbound_sweep runs without error., test_worker_run_inbound_sweep(), Verify app.worker.run_data_retention executes without error., test_worker_run_data_retention() (+4 more)

### Community 125 - "FPOLink Technology Stack"
Cohesion: 0.14
Nodes (13): 1. Core Languages & Runtimes, 2. Backend Frameworks & Libraries, 3. Frontend Frameworks & UI Architecture, 4. Database Systems & Storage, 5. Development, Linting & CI/CD Tooling, Database & ORM, FPOLink Technology Stack, Framework & Routing (+5 more)

### Community 126 - "db"
Cohesion: 0.20
Nodes (6): Retrieve newest available price for crop in district, with state fallback.…, Newest verified (MarketPrice, market name) for a crop: the district, else the…, One line on whether a nearby market pays clearly more after transport., Return the 7-day price outlook for a crop (stored prediction, else computed…, db(), Provide a clean database session for each test.

### Community 127 - "FPOLink External Integrations"
Cohesion: 0.15
Nodes (12): 1. Agricultural Mandi & Price Data Feeds, 2. Weather & Agrometeorology, 3. Messaging & Bot Gateways, 4. Monitoring & Telemetry, A. OGD India (Agmarknet Daily Mandi API), A. Telegram Bot API, B. CEDA Agri-Market Data Portal, B. WhatsApp Cloud API (Meta Graph API) (+4 more)

### Community 128 - "2. Test Suite Organization"
Cohesion: 0.15
Nodes (12): 1. Testing Framework & Tooling, 2. Test Suite Organization, 3. Running Tests, A. Authentication & Security (25 tests), B. Multi-Channel Messaging & Bots (74 tests), C. Ingestion, Parsers & Data Hygiene (42 tests), D. Core Domain & Business Logic (65 tests), E. Health, Retention & Platform Infrastructure (22 tests) (+4 more)

### Community 129 - "DailyDigestService"
Cohesion: 0.25
Nodes (7): DailyDigestService, date, Session, Check if an outbound message of template has already been logged today., Fetch distinct active crop names for farmer, falling back to default crops., Executes the daily 07:30 IST price digest to opted-in farmers with strict…, Run daily price digest for all eligible farmers. Guarantees: 1. Checks circuit…

### Community 130 - "TelegramBotService"
Cohesion: 0.33
Nodes (5): TelegramUpdate, phone10(), Process one update. Never raises (runs as a background task)., Link the chat to a farmer by phone. Returns (status, display) where status is…, TelegramBotService

### Community 131 - "deps.py"
Cohesion: 0.12
Nodes (21): get_current_user(), get_password_change_user(), _get_user_from_token(), Session, UUID, FastAPI dependencies for authentication, authorization, and multi-tenant…, Resolve an active user from a bearer token with the required token type., Extract a normal authenticated user, blocking accounts that must reset a… (+13 more)

### Community 132 - "import_farms_csv"
Cohesion: 0.24
Nodes (11): import_buyers_csv(), import_farms_csv(), parse_date(), date, Session, UUID, Import commercial buyers and optional procurement requirements from CSV text., Parse string to date with multiple format support. (+3 more)

### Community 133 - "2. Frontend & Next.js Conventions"
Cohesion: 0.29
Nodes (6): 2. Frontend & Next.js Conventions, 3. Error Handling & Resilience Patterns, A. Next.js App Router & Server/Client Components, B. API Client & State Management, C. Styling & CSS, FPOLink Development Conventions & Patterns

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
Cohesion: 0.20
Nodes (9): 1. Phase Overview, 2. Tasks & Execution Sequence (Tracer-First), Phase M3: Defensible Arbitrage & Transport Realization — Implementation Plan, Task M3.1: Upgrade Arbitrage Engine & Cost Realization Math (Tracer Slice), Task M3.2: Extend API Schemas & REST Endpoint, Task M3.3: Interactive UI Controls & Cost Visualizer, Task M3.4: Evaluation CLI Tool & Documentation Specification, Task M3.5: Automated Test Suite & Regression Verification (+1 more)

### Community 139 - "FPOLink TN — Product Roadmap"
Cohesion: 0.20
Nodes (9): Active Milestone: v0.9 — Cloud Hosting & Field Pilot, FPOLink TN — Product Roadmap, Future Milestone: v1.0 — Statewide Expansion & Voice Interface, Milestone Details, Milestone History & Status Overview, Milestone v0.5: Statewide Data Network, Milestone v0.6: Authentication & Management Dashboard, Milestone v0.7: Agricultural Intelligence & Multi-Channel Messaging (+1 more)

### Community 140 - "test_price_drop_triggers_downward_alert"
Cohesion: 0.24
Nodes (8): alert_db(), FakeChannel, anyio, fixture, A price drop >= 5% triggers an alert with direction 'Drop' / 'சரிவு'., Price swings >= 5% trigger an alert, swings < 5% do not, and max 1…, test_price_drop_triggers_downward_alert(), test_price_move_alert_triggers_at_5_percent_and_respects_daily_limit()

### Community 142 - "price.py"
Cohesion: 0.43
Nodes (7): ManualPriceEntry, MarketPriceResponse, PriceHistoryPoint, PriceHistoryResponse, PriceTrend, BaseModel, QualitySummaryResponse

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

### Community 147 - "calculate_quality_score"
Cohesion: 0.29
Nodes (7): calculate_quality_score(), Any, date, Decimal, Explainable Data Quality Scoring Service for Mandi Prices., Compute an explainable data quality score (0.0 to 100.0) with granular…, Task 8.5: Statewide Market Ingestion & Explainable Quality Scoring Framework

### Community 150 - "2. Technical Decisions & Architectural Matrix"
Cohesion: 0.29
Nodes (6): 1. Executive Intent & Goals, 2. Technical Decisions & Architectural Matrix, Multi-Crop Dynamic Engine, Phase M5 Context: Statewide Multi-Crop & District-Dynamic Frontend Experience with JetBrainsMono & Modern Web Optimization, Statewide District Selection, Typography: JetBrains Mono + Noto Sans Tamil

### Community 151 - "dependencies"
Cohesion: 0.25
Nodes (8): dependencies, clsx, lucide-react, next, react, react-dom, recharts, tailwind-merge

### Community 152 - "devDependencies"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

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

### Community 163 - "layout.tsx"
Cohesion: 0.29
Nodes (5): frontend_app_globals, inter, metadata, viewport, Providers()

### Community 164 - "compile_jsonb_sqlite"
Cohesion: 0.67
Nodes (3): compile_jsonb_sqlite(), compile_uuid_sqlite(), compiles

### Community 165 - ".fetch_prices"
Cohesion: 0.27
Nodes (4): date, Fetch price records for a crop in a district within a date range., date, Manual prices are entered via API, not fetched. This provider returns an empty…

### Community 169 - ".score_past_forecasts"
Cohesion: 0.33
Nodes (5): Evaluate un-scored past predictions against ground truth actual observations., 1. Verified Workflows, 2. Deployment Requirements, 3. Known Pilot Limitations & Boundaries, What Works Today

### Community 173 - "_random_phone"
Cohesion: 0.33
Nodes (6): _random_phone(), Generate a valid 10-digit numeric phone number., Journey 1: Administrator creation -> login -> required password rotation ->…, Journey 2: Farmer registration -> consent capture -> harvest logging., test_journey_admin_bootstrap_and_password_rotation(), test_journey_farmer_registration_consent_and_harvest()

### Community 174 - "2. System Health Check"
Cohesion: 0.33
Nodes (6): 2. System Health Check, FPOLink Operations Runbook, Health Endpoint Usage, Quick Reference Links, Response Statuses, Triage Steps if Health Check is Degraded

### Community 175 - ".fetch_all"
Cohesion: 0.40
Nodes (3): date, Fetch prices from all available providers. Uses fallback chain: tries each…, Fetch from ALL available providers (not just first success).

### Community 176 - "get_whatsapp_activity"
Cohesion: 0.67
Nodes (3): get_whatsapp_activity(), Session, Staff dashboard monitor feed — returns real inbound messages and telemetry.

### Community 177 - "compile_jsonb_sqlite"
Cohesion: 0.67
Nodes (3): compile_jsonb_sqlite(), compile_uuid_sqlite(), compiles

### Community 178 - "compile_jsonb_sqlite"
Cohesion: 0.67
Nodes (3): compile_jsonb_sqlite(), compile_uuid_sqlite(), compiles

## Knowledge Gaps
- **481 isolated node(s):** `entrypoint.prod.sh script`, `entrypoint.sh script`, `CATEGORIES`, `AdapterRow`, `AddFarmerForm` (+476 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1512 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **27 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `sqlalchemy`, `deps.py`, `import_farms_csv`, `DbBotServices`, `TelegramBotService`, `api/farmers.py`, `farms.py`, `test_harvest_service_and_api.py`, `test_price_drop_triggers_downward_alert`, `Farmer`, `api/whatsapp.py`, `api/fpo.py`, `api/auth.py`, `BotEngine`, `test_supply_demand_services.py`, `test_auth_deps.py`, `MarketPrice`, `_get`, `verify_fpo_access`, `Market`, `telegram_bot.py`, `get_whatsapp_activity`, `schemas/__init__.py`, `os`, `v1/geography.py`, `test_daily_digest_full_flow_with_crop_matching_and_freshness`, `test_whatsapp_usage_and_circuit_breaker.py`, `1. Architectural Pillars`, `api/harvest.py`, `Farm`, `FastAPI`, `test_telegram_bot.py`, `Market Price Data Coverage & Readiness Audit (T0.5)`, `api/telegram.py`, `require_role`, `v1/matching.py`, `v1/ingestion.py`?**
  _High betweenness centrality (0.207) - this node is a cross-community bridge._
- **Why does `Farmer Addition Crash Fix` connect `Market Price Data Coverage & Readiness Audit (T0.5)` to `User`, `api.ts`?**
  _High betweenness centrality (0.122) - this node is a cross-community bridge._
- **Why does `formatApiError()` connect `api.ts` to `Market Price Data Coverage & Readiness Audit (T0.5)`?**
  _High betweenness centrality (0.120) - this node is a cross-community bridge._
- **Are the 111 inferred relationships involving `User` (e.g. with `get_data_health()` and `purge_testing_data()`) actually correct?**
  _`User` has 111 INFERRED edges - model-reasoned connections that need verification._
- **Are the 52 inferred relationships involving `Crop` (e.g. with `list_crops()` and `get_forecast()`) actually correct?**
  _`Crop` has 52 INFERRED edges - model-reasoned connections that need verification._
- **Are the 39 inferred relationships involving `Market` (e.g. with `get_data_health()` and `get_forecast()`) actually correct?**
  _`Market` has 39 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `Farmer` (e.g. with `create()` and `update()`) actually correct?**
  _`Farmer` has 46 INFERRED edges - model-reasoned connections that need verification._