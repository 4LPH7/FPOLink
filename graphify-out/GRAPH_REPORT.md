# Graph Report - FPOLink  (2026-10-22)

## Corpus Check
- 353 files · ~209,698 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 23 file(s) not represented in the graph (top: (none) 15, .csv 3, .example 1)

## Summary
- 3314 nodes · 9192 edges · 160 communities (141 shown, 19 thin omitted)
- Extraction: 89% EXTRACTED · 11% INFERRED · 0% AMBIGUOUS · INFERRED: 967 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `4ca95a83`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- InMemoryServices
- Step-by-Step Production Runbook
- sqlalchemy
- test_units.py
- DbBotServices
- Farmer
- alembic
- api/farmers.py
- test_supply_demand_services.py
- typing
- main.py
- post
- test_whatsapp_onboarding.py
- FPO
- Variety
- database.py
- api/fpo.py
- BotServices
- getLatestPrices
- api/auth.py
- json
- WeatherProvider
- BotEngine
- CEDAProvider
- extract_features_for_series
- layout.tsx
- Settings
- compilerOptions
- create_access_token
- TestClient
- PriceRecord
- DataSourceRegistry
- User
- package.json
- commodities.py
- verify_fpo_access
- matching/page.tsx
- worker.py
- api.ts
- v1/crops.py
- test_whatsapp_price_alerts.py
- react
- datetime
- schemas/__init__.py
- check_market_coverage.py
- District
- bot.py
- WhatsApp Integration: Task List
- data_cleaning.py
- forecasting.py
- OGDProvider
- next.config.mjs
- postcss.config.mjs
- core/__init__.py
- pytest
- entrypoint.sh
- next-env.d.ts
- v1/matching.py
- BuyerRequirement
- v1/geography.py
- Operational Playbook: Manual CEDA Backfill, Coverage Audit & External Feeds
- FPOLink TN
- Implementation Plan: WhatsApp Integration for FPOLink TN
- test_whatsapp_daily_digest.py
- Data Provenance & Fixture Verification Ledger
- WhatsAppUsageService
- 1. Architectural Pillars
- test_inbound_sweep.py
- parse_webhook
- rules/graphify.md
- workflows/graphify.md
- test_ingestion_center_api.py
- CEDAAPIProvider
- Production Hosting Guide: Oracle Cloud Always Free + Cloudflare Tunnel
- register_whatsapp_templates.py
- farmers/page.tsx
- calculate_quality_score
- markets.py
- Detailed Task Specifications
- services/prices.py
- 2. Gaps Identified & Remediated During Audit
- hash_password
- components.json
- 3. Verify First Successful Requests
- 2. Locked Architectural Decisions
- FPOLink TN — Production Deployment Guide
- Detailed Task Specifications
- WhatsAppCloudChannel
- Crop
- 1. Emergency Messaging Kill Switches
- run_inbound_sweep
- 2. Locked Architectural Decisions
- 2. Locked Decisions & Core Tenets
- api/harvest.py
- get_db
- Human Checkpoints Operational Guide (Checkpoints A, B, C, D)
- FPOLink TN: 2-Week Field Pilot Runbook (Final: Pilot)
- 1. Resolution of Core Operational Questions
- MandiPricesProvider
- test_telegram_bot.py
- .validate_production_secrets
- Button
- dependencies
- Market Price Data Coverage & Readiness Audit (T0.5)
- api/telegram.py
- devDependencies
- 7. Automated Test Verification Matrix
- marketData.ts
- entrypoint.prod.sh
- api/prices.py
- test_whatsapp_wiring_and_killswitch.py
- find_candidate_matches_for_requirement
- admin.py
- messaging/telegram.py
- FPOLink TN — Phase 13: Supply + Demand Network (v0.8 Architecture Plan)
- v1/ingestion.py
- normalise_phone
- ingest_ceda_live.py
- FPOLink TN — Tenant Isolation & Production Security Audit Report
- FPOLink Technology Stack
- require_role
- FPOLink External Integrations
- 2. Test Suite Organization
- v1/prices.py
- TelegramBotService
- get_current_user
- import_farms_csv
- 1. Python & Backend Conventions
- 2. Locked Architectural Decisions
- README.md
- FPOLink TN — Inter-District Arbitrage & Transport Realization Specification
- FPOLink Technical Concerns & Architecture Watchpoints
- 2. Tasks & Execution Sequence (Tracer-First)
- FPOLink TN — Product Roadmap
- test_data_health.py
- TelegramChatChannel
- price.py
- tasks/page.tsx
- 2. Core Subsystems & Data Pipelines
- 2. Ingested Assets & Evidence
- FPOLink TN — Product Requirements Document (PRD)
- log_audit_event
- verify_meta_send.py
- test_worker_module_bootstraps_as_main
- 2. Technical Decisions & Architectural Matrix
- status
- _random_phone
- Telegram bot (@Fpo_Link_Bot)
- FPOLink TN — Project Specification
- vercel.json
- _get_admin_headers
- frontend/vercel.json
- FPOLink Project Status
- STRUCTURE.md

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

## Communities (160 total, 19 thin omitted)

### Community 0 - "InMemoryServices"
Cohesion: 0.10
Nodes (6): ConvState, InMemoryServices, Retrieve conversation state, returning None if expired beyond 30m TTL., anyio, Verify claim_notice only allows one concurrent sender, and failure leaves…, test_notice_atomic_claim_concurrency_and_retry()

### Community 1 - "Step-by-Step Production Runbook"
Cohesion: 0.10
Nodes (19): Check if price date exceeds staleness threshold., English (`en`) Template:, Environment Variables Reference, Meta WhatsApp Cloud API — Production Setup Checklist, Optional: Template Specification for `price_move_alert`, Prerequisites, Production Readiness Verification Sign-Off, Step 1: Create Meta Business Account (+11 more)

### Community 2 - "sqlalchemy"
Cohesion: 0.11
Nodes (32): Run migrations in 'offline' mode. This configures the context with just a URL…, Run migrations in 'online' mode. In this scenario we need to create an Engine…, run_migrations_offline(), run_migrations_online(), AggregationBatch, BatchItem, BatchStatus, Base (+24 more)

### Community 3 - "test_units.py"
Cohesion: 0.23
Nodes (13): convert_from_per_kg(), convert_to_per_kg(), Decimal, Unit conversion utilities for agricultural commodities., Convert a price from any unit to Rs/kg. Args: price: Price in the original unit…, Convert Rs/kg to another unit., Tests for unit conversions., test_convert_from_per_kg() (+5 more)

### Community 4 - "DbBotServices"
Cohesion: 0.05
Nodes (40): asyncio, _bot(), Farm, Base, DbBotServices, Decimal, Database implementation of BotServices protocol for FPOLink. Provides atomic…, Atomically claim notice sending lease for farmer. Return True if claim acquired. (+32 more)

### Community 5 - "Farmer"
Cohesion: 0.08
Nodes (47): Buyer and buyer requirement models — staff-mediated commercial demand., Farmer, Base, Harvest, HarvestGrade, HarvestStatus, Base, str (+39 more)

### Community 7 - "api/farmers.py"
Cohesion: 0.10
Nodes (48): create(), _enforce_farmer_fpo_scope(), get_one(), get_whatsapp_invite(), list_all(), put, Session, UUID (+40 more)

### Community 8 - "test_supply_demand_services.py"
Cohesion: 0.07
Nodes (60): create(), _enforce_farm_scope(), _farm_to_response(), get_one(), get_yield_estimate(), import_csv(), list_all(), delete (+52 more)

### Community 9 - "typing"
Cohesion: 0.07
Nodes (34): ABC, MarketDataProvider, date, Base market data provider interface. All data source adapters inherit from this…, Abstract base class for market data providers., Fetch price records for a crop in a district within a date range., Check if this data source is currently accessible., CEDA Data Portal API provider (Ashoka University). Programmatic access to raw… (+26 more)

### Community 10 - "main.py"
Cohesion: 0.15
Nodes (11): get_buyers(), list_crops(), Session, Crop listing endpoints., List all configured crops., health_check(), contextlib, FastAPI (+3 more)

### Community 11 - "post"
Cohesion: 0.16
Nodes (22): BackgroundTasks, Request, receive(), Check Meta's X-Hub-Signature-256 header (HMAC-SHA256 of the raw body)., verify_signature(), parse_qty(), button_payload(), post() (+14 more)

### Community 12 - "test_whatsapp_onboarding.py"
Cohesion: 0.13
Nodes (18): WhatsAppSettings, PriceInfo, build_payload(), FailingChannel, MockChannel, post_webhook(), TestClient, Tests for WhatsApp Phase 2: Onboarding, Identity, Consent, and Scoping (T2.1 -… (+10 more)

### Community 13 - "FPO"
Cohesion: 0.06
Nodes (40): FastAPI dependencies for authentication, authorization, and multi-tenant…, FPO, Base, Base, SupplyMatch, str, UserRole, Telegram front-end for the transport-agnostic BotEngine. Flow: 1. Unknown chat… (+32 more)

### Community 14 - "Variety"
Cohesion: 0.06
Nodes (44): CropSourceMapping, Base, External Source-to-Canonical Entity Mappings. Eliminates pure fuzzy matching by…, VarietySourceMapping, Base, Variety model — crop varieties with grades and maturity., Variety, _clean_str() (+36 more)

### Community 15 - "database.py"
Cohesion: 0.06
Nodes (58): get_status_service(), WhatsApp Cloud API webhook. GET /api/whatsapp/webhook -> Meta's one-time…, _status_service(), init_sqlite_schema(), _jsonb_on_sqlite(), compiles, Local development on SQLite: store PostgreSQL JSONB columns as JSON text., Create all tables directly on SQLite (Alembic migrations target PostgreSQL). (+50 more)

### Community 16 - "api/fpo.py"
Cohesion: 0.14
Nodes (35): create(), dashboard(), get_one(), list_all(), put, Session, FPO management endpoints., Get dashboard statistics for an FPO. (+27 more)

### Community 17 - "BotServices"
Cohesion: 0.08
Nodes (11): BotServices, Decimal, Protocol, Everything the bot needs from your app. Implement against your DB/services., Atomically record message_id; False if already seen (Meta retries webhooks)., Fetch open confirmed or candidate buyer requirements for farmer's crops/FPO., Store opt-in/out with a timestamp (consent evidence for DPDP / WhatsApp opt-in)., Atomically claim notice lease. Returns True only if claim was acquired. (+3 more)

### Community 18 - "getLatestPrices"
Cohesion: 0.10
Nodes (22): PricesPage(), resolveCropUnit(), MandiPricesTable(), load(), MandiPricesTableProps, PriceChart(), initCrops(), PriceChartProps (+14 more)

### Community 19 - "api/auth.py"
Cohesion: 0.15
Nodes (25): change_password(), get_me(), login(), Session, Authentication endpoints — register, login, refresh., Require the current password, then replace it before granting a normal session., Get new access token using refresh token., Get current authenticated user's profile. (+17 more)

### Community 20 - "json"
Cohesion: 0.07
Nodes (34): client(), create_tables(), _enable_whatsapp_for_legacy_bot_tests(), fixture, Create all tables before tests, drop after., WhatsApp ships disabled (Telegram is the farmer channel), but the dormant…, Provide a test client using the shared test database session., ceda_provider() (+26 more)

### Community 21 - "WeatherProvider"
Cohesion: 0.12
Nodes (12): NASAPowerProvider, Any, date, Fetch long-term weather history from NASA POWER., Fetch daily weather data from NASA POWER., Any, date, Fetch weather data from Open-Meteo API. (+4 more)

### Community 22 - "BotEngine"
Cohesion: 0.11
Nodes (21): InboundMessage, BotEngine, Farmer, normalize_phone(), WhatsApp ids look like 919876543210. Match on the last 10 digits (India-only…, Entry point for background tasks: never raises., Match farmer by last 10 digits of phone., build_payload() (+13 more)

### Community 23 - "CEDAProvider"
Cohesion: 0.10
Nodes (18): CEDAProvider, date, Decimal, Parse a single CSV row into a PriceRecord., Parse CEDA historical CSV data for price backfill., Try multiple possible column names., Try multiple date formats., Parse CEDA CSV and return standardized price records. Expected CSV columns (may… (+10 more)

### Community 24 - "extract_features_for_series"
Cohesion: 0.10
Nodes (32): days_to_nearest_festival(), get_festival_features(), is_festival(), date, Tamil Nadu holiday/festival features for price prediction. Uses Python…, Check if a date is a known festival day., Days until the nearest festival within a window. Returns window+1 if none., Generate festival-related features for a given date. (+24 more)

### Community 25 - "layout.tsx"
Cohesion: 0.29
Nodes (5): frontend_app_globals, inter, metadata, viewport, Providers()

### Community 26 - "Settings"
Cohesion: 0.12
Nodes (18): Application settings loaded from environment variables and .env file., Settings, Tests for production security enforcement in configuration., test_development_allows_default_secret_key(), test_production_accepts_strong_secret_key(), test_production_refuses_default_secret_key(), test_production_rejects_default_database_password(), test_production_rejects_demo_mode() (+10 more)

### Community 27 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 28 - "create_access_token"
Cohesion: 0.16
Nodes (15): create_access_token(), Create a short-lived access token., create_test_app(), Unit tests for authentication and authorization dependencies in app.api.deps., test_expired_token_returns_401(), test_invalid_token_returns_401(), test_require_role_authorized_returns_200(), test_require_role_insufficient_permission_returns_403() (+7 more)

### Community 29 - "TestClient"
Cohesion: 0.15
Nodes (7): TestClient, Authentication endpoint tests., TestLogin, TestProtectedRoutes, TestRefresh, TestRegister, TestRequiredPasswordChange

### Community 30 - "PriceRecord"
Cohesion: 0.06
Nodes (55): argparse, PriceRecord, Standardized price record from any data source., IngestionRun, IngestionLog, Base, Base, Raw ingest model — stores raw JSONB payloads for replay. (+47 more)

### Community 31 - "DataSourceRegistry"
Cohesion: 0.13
Nodes (11): DataSourceRegistry, date, Manages data source providers with fallback chain. Priority: OGD (live API) →…, Get provider by source name., Fetch prices from all available providers. Uses fallback chain: tries each…, Fetch from ALL available providers (not just first success)., Session, Verify MandiPricesProvider is registered in fallback chain. (+3 more)

### Community 32 - "User"
Cohesion: 0.17
Nodes (27): create_task(), delete_task(), _get(), list_tasks(), delete, patch, Session, UUID (+19 more)

### Community 33 - "package.json"
Cohesion: 0.06
Nodes (26): ForecastAreaChart, PriceHistoryChart, ForecastAreaChartProps, ForecastChartPoint, HistoryChartPoint, PriceHistoryChartProps, name, private (+18 more)

### Community 34 - "commodities.py"
Cohesion: 0.25
Nodes (12): get_commodity_detail(), list_commodities(), Session, UUID, Commodity registry API endpoints — Canonical commodity intelligence., List canonical crops with counts of varieties, aliases, source mappings, and…, Get rich commodity profile with varieties, aliases, source mappings, and active…, CommodityDetail (+4 more)

### Community 35 - "verify_fpo_access"
Cohesion: 0.10
Nodes (46): UUID, Check if current user has authorization to access/modify a specific FPO tenant.…, verify_fpo_access(), _buyer_to_response(), create(), get_one(), get_requirement(), import_csv() (+38 more)

### Community 36 - "matching/page.tsx"
Cohesion: 0.14
Nodes (39): CATEGORIES, AdapterRow, Badge(), BadgeProps, Button, ButtonProps, Card, CardContent (+31 more)

### Community 37 - "worker.py"
Cohesion: 0.12
Nodes (22): apscheduler_schedulers_blocking, Manually trigger DPDP retention purge., trigger_retention_purge(), M2.4: fill actual_price/error on forecast_log rows whose target date has passed., score_forecasts(), purge_inbound(), Delete whatsapp_inbound rows older than *retention_days*., main() (+14 more)

### Community 38 - "api.ts"
Cohesion: 0.05
Nodes (80): CommoditiesRegistryPage(), AdminPage(), BuyersPage(), MatchingPage(), FPOActionWorkspace(), WhatsAppPage(), AggregationSummary(), AggregationSummaryProps (+72 more)

### Community 39 - "v1/crops.py"
Cohesion: 0.20
Nodes (20): get_crop(), list_crop_varieties(), list_crops(), Session, UUID, Crop API v1 endpoints — agricultural ontology and resolution., Resolve an incoming raw string (e.g. from mandi feed or chat) to a canonical…, List crops in the agricultural ontology. (+12 more)

### Community 40 - "test_whatsapp_price_alerts.py"
Cohesion: 0.19
Nodes (12): alert_db(), compile_jsonb_sqlite(), compile_uuid_sqlite(), FakeChannel, anyio, compiles, fixture, Tests for T4.3: Price-move alerts (>= 5% threshold) and max 1 alert per farmer… (+4 more)

### Community 41 - "react"
Cohesion: 0.08
Nodes (43): ChangePasswordPage(), handleSubmit(), LoginPage(), handleSubmit(), FooterProps, LanguageSwitcher(), NavbarProps, apiIsHealthy() (+35 more)

### Community 42 - "datetime"
Cohesion: 0.06
Nodes (57): Crop model — agricultural crop ontology., MarketPrice, Base, Market price model — daily commodity prices from various sources., Market model — normalized market locations., compute_uncertainty_score(), find_market_arbitrage(), get_default_spoilage_risk() (+49 more)

### Community 43 - "schemas/__init__.py"
Cohesion: 0.31
Nodes (11): FPOLink Pydantic schemas package., ArbitrageOpportunity, ArbitrageResponse, ForecastPoint, ForecastResponse, BaseModel, Pydantic schemas for Agricultural Intelligence API v1., SpreadPoint (+3 more)

### Community 44 - "check_market_coverage.py"
Cohesion: 0.24
Nodes (11): check_coverage(), main(), print_coverage_report(), Market price data coverage analyzer for FPOLink TN. Checks monthly price record…, Execute monthly coverage query across markets., Format and print coverage statistics and advisory., Tests for the market coverage audit script., test_check_coverage_query() (+3 more)

### Community 45 - "District"
Cohesion: 0.07
Nodes (47): CropAlias, Base, DataSource, Data Quality and Ingestion Telemetry Models., Block, District, Base, Geography models — State, District, Taluk, Block, Village hierarchy. (+39 more)

### Community 46 - "bot.py"
Cohesion: 0.29
Nodes (10): crop_name(), detect_crop(), detect_intent(), format_price(), _match(), WhatsApp bot engine. Transport-agnostic: depends only on MessageChannel (send)…, _tokens(), test_intent_and_crop_detection() (+2 more)

### Community 47 - "WhatsApp Integration: Task List"
Cohesion: 0.07
Nodes (28): Checkpoint A: end-to-end from a real phone; CI green; no secrets in repo, Checkpoint B: harvest submitted by chat is visible to FPO staff, Checkpoint C: dry run with 3 test farmers, Checkpoint D: staging E2E with a real phone, Checkpoint E: Statewide Foundation Sign-Off, Checkpoint G: Agricultural Intelligence Sign-Off, Checkpoint H: Supply + Demand Network Sign-Off, FPOLink MVP Sprint — Tasks M1–M4 (+20 more)

### Community 48 - "data_cleaning.py"
Cohesion: 0.16
Nodes (17): clean_price_records(), detect_anomaly_mad(), _normalize_record(), Decimal, Data cleaning utilities for market price data., Clean and validate a list of price records., Validate a price record., Normalize a price record. (+9 more)

### Community 49 - "forecasting.py"
Cohesion: 0.08
Nodes (37): get_forecast(), Session, Legacy backward-compatible forecast endpoint delegating to ForecastingService., compute_forecast_signal(), ForecastingService, load_price_series(), DataFrame, Session (+29 more)

### Community 50 - "OGDProvider"
Cohesion: 0.09
Nodes (25): OGDProvider, date, Case-tolerant field retriever., Fetch daily mandi prices from data.gov.in OGD API., Fetch prices from data.gov.in API., Parse an OGD API record into a PriceRecord., check_status(), load_fixture_records() (+17 more)

### Community 54 - "pytest"
Cohesion: 0.13
Nodes (20): ConversationState, Store active conversation state machines per WhatsApp ID with TTL., purge_conversation_state(), purge_outbound(), DPDP-compliant data retention purge for WhatsApp tables. Scheduled daily at…, Delete stale conversation_state rows older than *ttl_hours*., Delete outbound_messages older than *retention_months*., Unit tests for phone normalisation, farmer consent, and bot models. (+12 more)

### Community 61 - "v1/matching.py"
Cohesion: 0.15
Nodes (29): confirm_match(), get_candidates(), list_matches(), _match_to_response(), Session, UUID, Semi-Automatic Demand-Supply Matching API endpoints., Record a suggested demand-supply match. (+21 more)

### Community 62 - "BuyerRequirement"
Cohesion: 0.14
Nodes (28): Buyer, BuyerRequirement, Base, create_buyer(), create_buyer_requirement(), delete_buyer(), get_buyer(), get_buyer_requirement() (+20 more)

### Community 65 - "v1/geography.py"
Cohesion: 0.13
Nodes (31): create_district(), create_state(), create_taluk(), create_village(), get_district(), list_districts(), list_states(), list_taluks_for_district() (+23 more)

### Community 66 - "Operational Playbook: Manual CEDA Backfill, Coverage Audit & External Feeds"
Cohesion: 0.22
Nodes (8): 1. Manual CEDA CSV Export & Ingestion, 2. CEDA Support Communication & API Key Extension, 3. Data.gov.in (OGD) Live API Key Setup, 4. Meta Test App Setup & Webhook Payload Capture (T0.3), Operational Playbook: Manual CEDA Backfill, Coverage Audit & External Feeds, Step 1: Download from CEDA Portal, Step 2: Ingest with Verified `--source ceda` Tag, Step 3: Run the Coverage Audit

### Community 67 - "FPOLink TN"
Cohesion: 0.09
Nodes (21): Evaluate un-scored past predictions against ground truth actual observations., 1. Clone & Configure, 1. Verified Workflows, 2. Deployment Requirements, 2. Launch Stack with Docker Compose, 3. Known Pilot Limitations & Boundaries, 3. Seed Reference Data, 4. Create the First Admin (+13 more)

### Community 68 - "Implementation Plan: WhatsApp Integration for FPOLink TN"
Cohesion: 0.12
Nodes (16): Agent Working Rules (paste at the top of every agent task), Constraints, Dates that matter, Implementation Plan: WhatsApp Integration for FPOLink TN, Later backlog (only if the pilot justifies it), Open Questions (need your answers), Overview, Phase 0: De-risk the external dependencies (start immediately, in parallel) (+8 more)

### Community 69 - "test_whatsapp_daily_digest.py"
Cohesion: 0.11
Nodes (19): DailyDigestService, date, Session, Check if an outbound message of template has already been logged today., Fetch distinct active crop names for farmer, falling back to default crops., Executes the daily 07:30 IST price digest to opted-in farmers with strict…, Run daily price digest for all eligible farmers. Guarantees: 1. Checks circuit…, compile_jsonb_sqlite() (+11 more)

### Community 70 - "Data Provenance & Fixture Verification Ledger"
Cohesion: 0.29
Nodes (6): 1. Fixture Inventory & Verification Status, 2. Sample Data Isolation Guarantee, 3. Guide: Ingesting Verified Real Mandi Data, A. Live Daily Ingestion (data.gov.in OGD Agmarknet), B. Historical Backfill (CEDA Ashoka University), Data Provenance & Fixture Verification Ledger

### Community 71 - "WhatsAppUsageService"
Cohesion: 0.05
Nodes (41): get_admin_inbound(), get_usage_service(), get_whatsapp_usage(), Session, Admin endpoints for WhatsApp usage tracking, cost audits, and circuit breaker…, Get aggregated WhatsApp message usage, delivery rates, cost breakdown, and…, Get recent inbound WhatsApp messages for audit., InboundMessageItem (+33 more)

### Community 72 - "1. Architectural Pillars"
Cohesion: 0.11
Nodes (18): 1.10 Statewide Telemetry Console & Commodity Registry UI, 1.11 Agricultural Intelligence & Forecasting Engine (v0.7), 1.1 Complete Administrative Geography Hierarchy, 1.2 Unified Agricultural Crop & Varietal Ontology, 1.3 Regulated Market Master Registry, 1.5 Explainable Data Quality Engine, 1.6 API v1 Unified Hierarchy, 1.8 Immutable Raw Ingestion Persistence & Replay Harness (+10 more)

### Community 73 - "test_inbound_sweep.py"
Cohesion: 0.14
Nodes (27): Log incoming WhatsApp webhook message IDs for deduplication / idempotency., WhatsAppInbound, Atomically record message_id; returns False if already seen (Meta retries…, At-least-once sweep: reprocess WhatsApp inbound messages stuck in 'received'.…, Find and increment retry on messages stuck in 'received' status. Messages that…, sweep_stuck_inbound(), compile_jsonb_sqlite(), compile_uuid_sqlite() (+19 more)

### Community 74 - "parse_webhook"
Cohesion: 0.17
Nodes (24): parse_webhook(), Extract user messages. Delivery/read status callbacks yield an empty list., load_fixture(), Parametrized contract tests verifying WhatsApp Cloud API fixtures against…, Verify read receipt status webhook parsing., Verify delivery failure callback parsing and error extraction., Load JSON fixture file., Verify parsing of English text message 'PRICE'. (+16 more)

### Community 77 - "test_ingestion_center_api.py"
Cohesion: 0.25
Nodes (7): Tests for Ingestion Center Telemetry and Control API (v1)., Verify paginated listing of ingestion runs., Verify retrieving detailed telemetry for a single run., Verify statewide coverage and freshness telemetry., test_get_ingestion_run_detail(), test_list_ingestion_runs(), test_statewide_freshness_endpoint()

### Community 78 - "CEDAAPIProvider"
Cohesion: 0.12
Nodes (15): CEDAAPIProvider, Any, date, Execute HTTP request with short timeout, retries, and circuit breaker., Retrieve list of all commodities: [{"id": int, "name": str}]., Test if the configured API key is valid., Retrieve geographies: [{"state_id": int, "state_name": str, "districts": [...]}], Retrieve markets: POST /agmarknet/markets. (+7 more)

### Community 79 - "Production Hosting Guide: Oracle Cloud Always Free + Cloudflare Tunnel"
Cohesion: 0.08
Nodes (26): 1. Architecture & Cost Model, 2. Oracle Cloud VM Provisioning, 3. Host Initialization & Docker Installation, 4. Cloudflare Zero Trust Tunnel Setup, 5. Clone and Configure FPOLink, 6. Launch Production Stack, 7. Verification & Farmer Channel Wiring, 8. Automated Systemd Boot Service (+18 more)

### Community 80 - "register_whatsapp_templates.py"
Cohesion: 0.13
Nodes (17): get_waba_id(), list_templates(), main(), Path, CLI utility to register and check status of WhatsApp message templates with…, Retrieve WhatsApp Business Account ID or fall back to Phone Number ID., Fetch and display all registered templates in the WABA., Submit templates defined in JSON file to Meta Graph API for approval. (+9 more)

### Community 81 - "farmers/page.tsx"
Cohesion: 0.12
Nodes (25): AddFarmerForm, AddPlotForm, EMPTY_FORM, EMPTY_PLOT_FORM, FarmersPage(), FarmerInviteCard(), load(), FarmerInviteCardProps (+17 more)

### Community 82 - "calculate_quality_score"
Cohesion: 0.11
Nodes (18): calculate_quality_score(), Any, date, Decimal, Explainable Data Quality Scoring Service for Mandi Prices., Compute an explainable data quality score (0.0 to 100.0) with granular…, Checkpoint E: Statewide Platform Foundation Sign-Off, Detailed Task Specifications (+10 more)

### Community 83 - "markets.py"
Cohesion: 0.22
Nodes (16): get_market(), list_markets(), Session, UUID, Market API v1 endpoints — market registry and resolution., List markets with optional district and type filtering., Get single market by ID with its configured aliases., Resolve an incoming raw market name or code to a canonical Market. (+8 more)

### Community 84 - "Detailed Task Specifications"
Cohesion: 0.11
Nodes (18): Detailed Task Specifications, Executive Summary, Implementation Plan: Phase 11 — Agricultural Intelligence (v0.7 Architecture), Task 11.10: Checkpoint G Sign-Off & Documentation, Task 11.2: Feature Store Test Suite (`backend/tests/test_feature_store.py`), Task 11.3: LightGBM Quantile & Baseline Forecasting Engine (`backend/app/ml/forecasting.py`), Task 11.4: Signal Generation & Model Versioning, Task 11.5: Worker Scheduled Prediction Pipeline (+10 more)

### Community 85 - "services/prices.py"
Cohesion: 0.12
Nodes (27): get_real_price_sources(), get_source_priority(), is_real_source(), Constants and utilities for verified market price data sources. Guarantees that…, Dynamically return verified price sources based on environment and DEMO_MODE.…, Return True if source is in the real verified price sources whitelist., Return priority rank for source (lower = higher priority). Unknown sources…, Retrieve newest available price for crop in district, with state fallback.… (+19 more)

### Community 86 - "2. Gaps Identified & Remediated During Audit"
Cohesion: 0.12
Nodes (17): anyio, Verify /api/health returns 200 and db: ok when database engine succeeds., Verify /api/health returns 503 and db: error when database engine fails., Verify lifespan initializes Sentry when SENTRY_DSN is set., Verify lifespan skips Sentry when SENTRY_DSN is None or empty., Verify .env.example contains all critical Settings fields (T5.7 Nyquist check)., test_env_example_contains_all_critical_settings(), test_health_check_db_failure() (+9 more)

### Community 87 - "hash_password"
Cohesion: 0.12
Nodes (23): hash_password(), Authentication service — password hashing with Argon2 via pwdlib., Hash a password using Argon2id., Verify a password against its Argon2id hash., verify_password(), create_or_update_admin(), main(), Bootstrap / provision the initial FPOLink administrator account. Reads… (+15 more)

### Community 88 - "components.json"
Cohesion: 0.12
Nodes (16): aliases, components, hooks, lib, ui, utils, rsc, $schema (+8 more)

### Community 89 - "3. Verify First Successful Requests"
Cohesion: 0.12
Nodes (15): 1. Backend Health Probe, 1. Prerequisites, 2. Statewide Districts Probe (v1), 2. Step-by-Step Setup, 2. Verified Crops Feed, 3. Latest Verified Mandi Prices (v1), 3. Staff Web Dashboard, 3. Verify First Successful Requests (+7 more)

### Community 90 - "2. Locked Architectural Decisions"
Cohesion: 0.12
Nodes (15): 1. Vision & Roadmap Positioning, 2. Locked Architectural Decisions, 3. Scope Boundaries, D1: Reference-Data Invariant Assertions & CI Protection, D2: Comprehensive Regulated Market Master Registry, D3: Source-Specific External Identifier Mappings (Zero-Fuzzy Priority), D4: Commodity Registry UI & Administrative Portal, D5: Reproducible Raw Ingestion Persistence & Replayability (+7 more)

### Community 91 - "FPOLink TN — Production Deployment Guide"
Cohesion: 0.12
Nodes (16): 1. Architecture, 2. Prerequisites, 3. Cloudflare Tunnel Setup, 4. Configuration, 5. Launch Stack, 6. Verification, 7. Operational Runbook & Maintenance, FPOLink TN — Production Deployment Guide (+8 more)

### Community 92 - "Detailed Task Specifications"
Cohesion: 0.14
Nodes (13): Detailed Task Specifications, Executive Summary, Implementation Plan: Phase 9 — Statewide Data Network (v0.6 Architecture), Task 9.10: Checkpoint F Statewide Data Network Sign-Off, Task 9.1: Reference Invariants & Automated Count Assertions, Task 9.2: Complete Regulated Market Master Registry, Task 9.3: External Source Mapping Models & Migration 0010, Task 9.4: Commodity Registry UI & Admin API (+5 more)

### Community 93 - "WhatsAppCloudChannel"
Cohesion: 0.17
Nodes (11): AsyncClient, _channel(), get_channel(), get_wa_settings(), Business-initiated message (e.g. daily digest). Template must be approved by…, Send template and return tuple of (success, meta_message_id)., WhatsAppCloudChannel, Price-move alerts sent to opted-in farmers at 07:45 IST (T4.3). (+3 more)

### Community 94 - "Crop"
Cohesion: 0.06
Nodes (49): get_arbitrage_opportunities(), get_crop_forecast(), get_price_spreads(), Session, UUID, Agricultural Intelligence API v1: Forecasting, Arbitrage & Spread Analysis., Evaluate inter-district market arbitrage deducting estimated freight, handling,…, Analyze statewide price dispersion and identify highest/lowest reporting… (+41 more)

### Community 95 - "1. Emergency Messaging Kill Switches"
Cohesion: 0.10
Nodes (20): 1.1 Emergency WhatsApp Kill Switch (Dormant by default in MVP), 1.2 Emergency Telegram Kill Switch (Active Live Channel in MVP), 1. Emergency Messaging Kill Switches, 2. System Health Check, Expected Output:, FPOLink Operations Runbook, Health Endpoint Usage, How to Disable Telegram (+12 more)

### Community 96 - "run_inbound_sweep"
Cohesion: 0.18
Nodes (11): At-least-once sweep for stuck inbound messages (T5.4)., run_inbound_sweep(), Verify app.worker.run_inbound_sweep runs without error., test_worker_run_inbound_sweep(), D1: Deployment Strategy — Cloudflare Tunnel, D2: Meta Production Checklist, D4: At-Least-Once Processing Sweep, D5: Observability — Sentry Init + DB Health Check (+3 more)

### Community 97 - "2. Locked Architectural Decisions"
Cohesion: 0.17
Nodes (11): 1. Vision & Roadmap Positioning, 2. Locked Architectural Decisions, 3. Scope Boundaries, D1: Dual-Engine Forecasting Architecture (LightGBM Quantile Regression + Robust Baseline), D3: Inter-District Arbitrage & Net Realized Margin Engine (`backend/app/services/arbitrage.py`), D5: Scheduled Autonomous Intelligence Worker, Deferred to Phase 13–15 (v0.8), In Scope (Phase 11) (+3 more)

### Community 98 - "2. Locked Decisions & Core Tenets"
Cohesion: 0.17
Nodes (11): 1. Vision & Architectural Transformation, 2. Locked Decisions & Core Tenets, 3. Explicitly Out of Scope for Phase 8, D2: Multi-Tenant RBAC & Organization Scoping, D3: Agricultural Crop Ontology & Canonical Alias Registry, D4: Market Registry & Canonical Market Aliases, D5: Ingestion Orchestration & Explainable Data Quality Framework, D6: API Versioning (v1) & Seamless Compatibility (+3 more)

### Community 99 - "api/harvest.py"
Cohesion: 0.16
Nodes (22): create_harvest(), _enforce_harvest_scope(), get_harvest(), get_harvest_aggregation(), list_harvests(), date, patch, Session (+14 more)

### Community 100 - "get_db"
Cohesion: 0.17
Nodes (13): list_audit_logs(), Session, Audit API v1 endpoints — view system audit trails., List audit log records (admin only)., get_db(), Session, FastAPI dependency that provides a database session., AuditLog (+5 more)

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
Cohesion: 0.12
Nodes (15): MandiPricesProvider, date, Decimal, Parse the HTML table into standardized PriceRecord instances., Convert '₹8,048' -> Decimal('8048')., Convert '25 Sep 2026' -> date(2026, 9, 25)., Fetch daily mandi prices from MandiPrices / Agmarknet portal., Fetch prices for a crop and district. (+7 more)

### Community 105 - "test_telegram_bot.py"
Cohesion: 0.21
Nodes (17): _contact(), factory(), FakeClient, anyio, fixture, Telegram channel: parsing, linking/auto-registration, command routing, harvest…, Records Bot API calls instead of hitting Telegram., _svc() (+9 more)

### Community 106 - ".validate_production_secrets"
Cohesion: 0.14
Nodes (12): 6. Network & CORS Origin Protection, model_validator, 1. Project Overview, 2. Key Status Metrics, 3. Recent Session Accomplishments, 4. Immediate Next Steps, FPOLink TN — Current Workflow State, Codebase Assets to Reuse (+4 more)

### Community 107 - "Button"
Cohesion: 0.08
Nodes (13): Button, MessageChannel, Protocol, Messaging package: transport-agnostic types and WhatsApp Cloud API adapter., MockChannel, In-memory channel that records all outbound messages sent by BotEngine., MockChannel, Mock WhatsApp channel capturing outgoing messages. (+5 more)

### Community 108 - "dependencies"
Cohesion: 0.25
Nodes (8): dependencies, clsx, lucide-react, next, react, react-dom, recharts, tailwind-merge

### Community 109 - "Market Price Data Coverage & Readiness Audit (T0.5)"
Cohesion: 0.20
Nodes (9): 1. Executive Summary, 2. Coverage Audit Results (2026-10-04), 3. Modeling & Operational Implications, 4. Ashoka CEDA API Integration & Platform Fixes (2026-10-04), Banana Coverage (Erode District), CEDA Agmarknet Provider Status, Farmer Addition Crash Fix, Market Price Data Coverage & Readiness Audit (T0.5) (+1 more)

### Community 110 - "api/telegram.py"
Cohesion: 0.16
Nodes (14): get_client(), get_service(), public_base_url(), Telegram bot webhook (farmer channel). POST /api/telegram/webhook -> updates…, Point Telegram at this API and publish the command menu., register_webhook(), _service(), set_webhook() (+6 more)

### Community 111 - "devDependencies"
Cohesion: 0.25
Nodes (8): devDependencies, autoprefixer, postcss, tailwindcss, @types/node, @types/react, @types/react-dom, typescript

### Community 112 - "7. Automated Test Verification Matrix"
Cohesion: 0.13
Nodes (19): _create_test_fpo(), _create_test_user(), An FPO staff user cannot view, update, or delete tasks belonging to another FPO., Authentication rejects expired, corrupted, or signature-mismatched tokens., Users with password_change_required cannot access protected APIs until password…, Verify CORS_ORIGIN_REGEX matches project Vercel previews but blocks attacker…, FPO staff cannot import buyers or requirements for another FPO., Verify that wildcard '*' CORS origin is strictly forbidden in production. (+11 more)

### Community 115 - "api/prices.py"
Cohesion: 0.15
Nodes (17): latest_prices(), list_markets(), price_anomalies(), price_history(), price_trend(), Session, Price endpoints — latest prices, history, trends, anomalies., Bulk import mandi prices from CSV file. (+9 more)

### Community 116 - "test_whatsapp_wiring_and_killswitch.py"
Cohesion: 0.12
Nodes (15): get_bot(), Return active BotEngine or raise 503 if WhatsApp is disabled via kill switch., Unit tests for WhatsApp bot wiring, settings validation, and kill switch., When WHATSAPP_ENABLED is False, both GET and POST webhooks return 503., get_bot() returns an active BotEngine when enabled., test_get_bot_dependency_wired(), test_kill_switch_returns_503(), Design notes (+7 more)

### Community 117 - "find_candidate_matches_for_requirement"
Cohesion: 0.20
Nodes (18): compute_proximity_score(), confirm_match_by_staff(), create_or_suggest_match(), find_candidate_matches_for_requirement(), _get_district_lat_lon(), get_supply_demand_summary(), Decimal, Session (+10 more)

### Community 118 - "admin.py"
Cohesion: 0.11
Nodes (21): get_data_health(), purge_testing_data(), Session, Admin endpoints — manual ingestion trigger, system status., System-wide data health report: rows/market/day, calendar gaps, and outlier…, Manually trigger price data ingestion (admin only)., Trigger live weather forecast ingestion from Open-Meteo for a district or…, Purge synthetic/demo test data so only real ground-truth data remains. (+13 more)

### Community 119 - "messaging/telegram.py"
Cohesion: 0.15
Nodes (15): BackgroundTasks, Request, receive(), webhook_secret(), derive_webhook_secret(), map_command(), parse_update(), Telegram Bot API adapter: update parsing, webhook secret check, and sending.… (+7 more)

### Community 120 - "FPOLink TN — Phase 13: Supply + Demand Network (v0.8 Architecture Plan)"
Cohesion: 0.13
Nodes (14): 1. Locked Strategic Decisions, 3.1 Rule-Based Yield Estimator (`backend/app/services/yield_estimator.py`), 3.2 Semi-Automatic Matching Engine (`backend/app/services/matching_service.py`), 3. Business Logic & Core Algorithms, 4.1 Free Service Conversation Window (Inbound-First), 4.2 Gated Low-Cost Outbound Nudge (Only When Staff Confirms), 4. WhatsApp Zero-Cost Interaction Architecture, 5.1 Farm Plot Endpoints (`/api/v1/farms`) (+6 more)

### Community 121 - "v1/ingestion.py"
Cohesion: 0.20
Nodes (13): get_ingestion_run(), get_statewide_freshness(), list_ingestion_runs(), BaseModel, Session, UUID, Ingestion Center Telemetry and Control API (v1)., Get statewide coverage and freshness telemetry across all 38 districts. (+5 more)

### Community 122 - "normalise_phone"
Cohesion: 0.21
Nodes (6): Check whether a recipient is reachable or flagged as dead., format_phone_e164(), normalise_phone(), Format normalised phone to E.164 (+91...)., Normalise phone number to 10-digit Indian standard. Strips country codes (+91,…, TestPhoneNormalisation

### Community 123 - "ingest_ceda_live.py"
Cohesion: 0.21
Nodes (13): check_status(), main(), date, CEDA Agmarknet Live Ingestion & Authentication CLI Harness. Provides…, Verify OTP with Ashoka CEDA., Validate and write new CEDA_API_KEY into .env., Fetch live data from CEDA and ingest into PostgreSQL., Check connectivity and key validity against CEDA API. (+5 more)

### Community 124 - "FPOLink TN — Tenant Isolation & Production Security Audit Report"
Cohesion: 0.14
Nodes (13): 1. Executive Summary, 2. Multi-Tenant Role Hierarchy & RBAC Matrix, 3.1 Database-Aware `verify_fpo_access`, 3.2 Farmer Registry Scoping, 3.3 Task Board Tenant Scoping, 3.4 Harvest Aggregation & Lifecycle, 3.5 Demand & Supply Matching Scoping, 3. Defense-in-Depth Isolation Implementation (+5 more)

### Community 125 - "FPOLink Technology Stack"
Cohesion: 0.14
Nodes (13): 1. Core Languages & Runtimes, 2. Backend Frameworks & Libraries, 3. Frontend Frameworks & UI Architecture, 4. Database Systems & Storage, 5. Development, Linting & CI/CD Tooling, Database & ORM, FPOLink Technology Stack, Framework & Routing (+5 more)

### Community 126 - "require_role"
Cohesion: 0.15
Nodes (11): Dependency factory: restrict endpoint to specific roles. Automatically maps…, require_role(), 1. Phase Overview, 2. Tasks & Execution Sequence (Tracer-First), Phase M4: Tenant Isolation & Production Security Audits — Implementation Plan, Task M4.1: Database-Aware Multi-Tenant Scoping (`verify_fpo_access`), Task M4.3: Hardened Production Admin Provisioning, Task M4.4: CORS Origin Configuration Verification & Documentation (+3 more)

### Community 127 - "FPOLink External Integrations"
Cohesion: 0.15
Nodes (12): 1. Agricultural Mandi & Price Data Feeds, 2. Weather & Agrometeorology, 3. Messaging & Bot Gateways, 4. Monitoring & Telemetry, A. OGD India (Agmarknet Daily Mandi API), A. Telegram Bot API, B. CEDA Agri-Market Data Portal, B. WhatsApp Cloud API (Meta Graph API) (+4 more)

### Community 128 - "2. Test Suite Organization"
Cohesion: 0.15
Nodes (12): 1. Testing Framework & Tooling, 2. Test Suite Organization, 3. Running Tests, A. Authentication & Security (25 tests), B. Multi-Channel Messaging & Bots (74 tests), C. Ingestion, Parsers & Data Hygiene (42 tests), D. Core Domain & Business Logic (65 tests), E. Health, Retention & Platform Infrastructure (22 tests) (+4 more)

### Community 129 - "v1/prices.py"
Cohesion: 0.23
Nodes (11): get_price_lineage(), latest_prices(), price_history(), Session, UUID, quality_summary(), Statewide Prices API (v1) with quality score filtering and telemetry., Get the latest verified mandi prices across districts with optional quality… (+3 more)

### Community 130 - "TelegramBotService"
Cohesion: 0.33
Nodes (5): TelegramUpdate, phone10(), Process one update. Never raises (runs as a background task)., Link the chat to a farmer by phone. Returns (status, display) where status is…, TelegramBotService

### Community 131 - "get_current_user"
Cohesion: 0.29
Nodes (11): get_current_user(), get_password_change_user(), _get_user_from_token(), Session, Resolve an active user from a bearer token with the required token type., Extract a normal authenticated user, blocking accounts that must reset a…, Accept only the restricted, short-lived token used for a required password…, decode_token() (+3 more)

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
Cohesion: 0.20
Nodes (9): 1. Phase Overview, 2. Tasks & Execution Sequence (Tracer-First), Phase M3: Defensible Arbitrage & Transport Realization — Implementation Plan, Task M3.1: Upgrade Arbitrage Engine & Cost Realization Math (Tracer Slice), Task M3.2: Extend API Schemas & REST Endpoint, Task M3.3: Interactive UI Controls & Cost Visualizer, Task M3.4: Evaluation CLI Tool & Documentation Specification, Task M3.5: Automated Test Suite & Regression Verification (+1 more)

### Community 139 - "FPOLink TN — Product Roadmap"
Cohesion: 0.20
Nodes (9): Active Milestone: v0.9 — Cloud Hosting & Field Pilot, FPOLink TN — Product Roadmap, Future Milestone: v1.0 — Statewide Expansion & Voice Interface, Milestone Details, Milestone History & Status Overview, Milestone v0.5: Statewide Data Network, Milestone v0.6: Authentication & Management Dashboard, Milestone v0.7: Agricultural Intelligence & Multi-Channel Messaging (+1 more)

### Community 140 - "test_data_health.py"
Cohesion: 0.25
Nodes (5): DataQualityEvent, Base, Tests for Data Health endpoint, CSV upload, query filters, and variety…, test_data_health_authenticated(), test_prices_latest_crop_and_market_filters()

### Community 142 - "price.py"
Cohesion: 0.43
Nodes (7): ManualPriceEntry, MarketPriceResponse, PriceHistoryPoint, PriceHistoryResponse, PriceTrend, BaseModel, QualitySummaryResponse

### Community 143 - "tasks/page.tsx"
Cohesion: 0.39
Nodes (5): Task, TasksPage(), TelegramPage(), API_BASE, authFetch()

### Community 144 - "2. Core Subsystems & Data Pipelines"
Cohesion: 0.25
Nodes (7): 1. Architectural Style & Design Patterns, 2. Core Subsystems & Data Pipelines, 3. Security & Multitenancy Architecture, A. Price Ingestion & Normalization Pipeline, B. Transport-Agnostic Bot Engine, C. Supply & Demand Matching Engine, FPOLink System Architecture

### Community 145 - "2. Ingested Assets & Evidence"
Cohesion: 0.25
Nodes (7): 1. Onboarding Summary Overview, 2. Ingested Assets & Evidence, 3. Recommended Next Command, A. Codebase Architecture Map (`.planning/codebase/`), B. Core Planning Artifacts (`.planning/`), C. Live Cloud System Telemetry, FPOLink TN — GSD Onboarding Summary

### Community 146 - "FPOLink TN — Product Requirements Document (PRD)"
Cohesion: 0.25
Nodes (7): 1. Authentication & Security (AUTH), 2. Market Prices & Agricultural Intelligence (PRICE), 3. Multi-Channel Messaging & Farmer Chat (BOT), 4. Supply & Demand Matching (SUPPLY_DEMAND), 5. FPO Cooperative Operations (TASKS), 6. Infrastructure & Deployment (INFRA), FPOLink TN — Product Requirements Document (PRD)

### Community 147 - "log_audit_event"
Cohesion: 0.29
Nodes (7): log_audit_event(), Any, Session, UUID, Record an audit log entry., Test recording an audit log event and querying via API., test_audit_logging_and_api()

### Community 148 - "verify_meta_send.py"
Cohesion: 0.38
Nodes (6): main(), CLI utility to verify Meta WhatsApp Cloud API outbound transmission (T0.2).…, Send text message directly to Meta WhatsApp Cloud API., Send pre-approved utility template to Meta WhatsApp Cloud API., send_direct_text(), send_test_template()

### Community 150 - "2. Technical Decisions & Architectural Matrix"
Cohesion: 0.29
Nodes (6): 1. Executive Intent & Goals, 2. Technical Decisions & Architectural Matrix, Multi-Crop Dynamic Engine, Phase M5 Context: Statewide Multi-Crop & District-Dynamic Frontend Experience with JetBrainsMono & Modern Web Optimization, Statewide District Selection, Typography: JetBrains Mono + Noto Sans Tamil

### Community 151 - "status"
Cohesion: 0.47
Nodes (6): status(), 2.1 Farm / Plot Entity (`backend/app/models/farm.py`), 2.2 Buyer Entity (`backend/app/models/buyer.py`), 2.3 Buyer Requirement Entity (`backend/app/models/buyer.py`), 2.4 Supply Match Entity (`backend/app/models/supply_match.py` - NEW), 2. Data Model Evolution (Alembic Migration 0011)

### Community 152 - "_random_phone"
Cohesion: 0.33
Nodes (6): _random_phone(), Generate a valid 10-digit numeric phone number., Journey 1: Administrator creation -> login -> required password rotation ->…, Journey 2: Farmer registration -> consent capture -> harvest logging., test_journey_admin_bootstrap_and_password_rotation(), test_journey_farmer_registration_consent_and_harvest()

### Community 153 - "Telegram bot (@Fpo_Link_Bot)"
Cohesion: 0.33
Nodes (5): Commands, Local dev (long polling), Production (Docker / Cloudflare Tunnel), Production (Render, webhook), Telegram bot (@Fpo_Link_Bot)

### Community 154 - "FPOLink TN — Project Specification"
Cohesion: 0.33
Nodes (5): 1. Executive Vision, 2. Core Entities & Stakeholders, 3. Technology Architecture Summary, 4. Key Constraints & Guiding Principles, FPOLink TN — Project Specification

### Community 155 - "vercel.json"
Cohesion: 0.33
Nodes (5): buildCommand, framework, installCommand, outputDirectory, $schema

### Community 156 - "_get_admin_headers"
Cohesion: 0.40
Nodes (5): _get_admin_headers(), Verify /api/fpos/ and /api/v1/fpos/ return compatible responses., Verify /api/farmers/{fpo_id} and /api/v1/farmers/{fpo_id} work equivalently., test_farmers_compatibility(), test_fpos_compatibility()

### Community 157 - "frontend/vercel.json"
Cohesion: 0.40
Nodes (4): buildCommand, framework, installCommand, $schema

### Community 158 - "FPOLink Project Status"
Cohesion: 0.50
Nodes (3): FPOLink Project Status, Next actions, Phase status

## Knowledge Gaps
- **481 isolated node(s):** `entrypoint.prod.sh script`, `entrypoint.sh script`, `CATEGORIES`, `AdapterRow`, `AddFarmerForm` (+476 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1496 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **19 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `User` connect `User` to `sqlalchemy`, `get_current_user`, `import_farms_csv`, `Farmer`, `DbBotServices`, `api/farmers.py`, `test_supply_demand_services.py`, `TelegramBotService`, `FPO`, `database.py`, `api/fpo.py`, `api/auth.py`, `log_audit_event`, `status`, `create_access_token`, `TestClient`, `_get_admin_headers`, `verify_fpo_access`, `worker.py`, `test_whatsapp_price_alerts.py`, `datetime`, `District`, `v1/matching.py`, `v1/geography.py`, `test_whatsapp_daily_digest.py`, `WhatsAppUsageService`, `1. Architectural Pillars`, `hash_password`, `Crop`, `api/harvest.py`, `get_db`, `test_telegram_bot.py`, `Market Price Data Coverage & Readiness Audit (T0.5)`, `api/telegram.py`, `7. Automated Test Verification Matrix`, `find_candidate_matches_for_requirement`, `admin.py`, `v1/ingestion.py`, `require_role`?**
  _High betweenness centrality (0.213) - this node is a cross-community bridge._
- **Why does `Farmer Addition Crash Fix` connect `Market Price Data Coverage & Readiness Audit (T0.5)` to `User`, `api.ts`?**
  _High betweenness centrality (0.127) - this node is a cross-community bridge._
- **Why does `formatApiError()` connect `api.ts` to `Market Price Data Coverage & Readiness Audit (T0.5)`?**
  _High betweenness centrality (0.124) - this node is a cross-community bridge._
- **Are the 111 inferred relationships involving `User` (e.g. with `get_data_health()` and `purge_testing_data()`) actually correct?**
  _`User` has 111 INFERRED edges - model-reasoned connections that need verification._
- **Are the 52 inferred relationships involving `Crop` (e.g. with `list_crops()` and `get_forecast()`) actually correct?**
  _`Crop` has 52 INFERRED edges - model-reasoned connections that need verification._
- **Are the 38 inferred relationships involving `Market` (e.g. with `get_data_health()` and `get_forecast()`) actually correct?**
  _`Market` has 38 INFERRED edges - model-reasoned connections that need verification._
- **Are the 46 inferred relationships involving `Farmer` (e.g. with `create()` and `update()`) actually correct?**
  _`Farmer` has 46 INFERRED edges - model-reasoned connections that need verification._