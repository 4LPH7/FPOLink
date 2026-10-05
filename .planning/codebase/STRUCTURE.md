# FPOLink Codebase Structure & Directory Map

Layout of the repository, key modules, entry points, and directory responsibilities.

```
FPOLink/
├── backend/                         # FastAPI backend service
│   ├── alembic/                     # Database migrations
│   │   ├── env.py                   # Alembic environment runner
│   │   └── versions/                # 14 migration revisions (0001 to 0013_fpo_tasks)
│   ├── app/                         # Core application package
│   │   ├── api/                     # REST API routers
│   │   │   ├── admin.py             # Ingestion triggers and system administration
│   │   │   ├── auth.py              # Login, token refresh, password changes, me
│   │   │   ├── buyers.py            # Buyer registry & procurement requirements
│   │   │   ├── crops.py             # Crop reference listings
│   │   │   ├── deps.py              # Auth & RBAC FastAPI dependencies
│   │   │   ├── farmers.py           # Farmer CRUD & profile management
│   │   │   ├── fpo.py               # FPO management & dashboard statistics
│   │   │   ├── harvest.py           # Harvest submission & status transitions
│   │   │   ├── matching.py          # Supply & demand matching workflow
│   │   │   ├── prices.py            # Mandi prices, history, trends, anomalies
│   │   │   ├── tasks.py             # FPO operational task management
│   │   │   ├── telegram.py          # Telegram bot webhook & administration
│   │   │   ├── v1/                  # Extended API v1 (commodities, geography, intel)
│   │   │   └── whatsapp.py          # WhatsApp Cloud API webhooks & verification
│   │   ├── models/                  # SQLAlchemy 2.0 ORM models
│   │   │   ├── base.py              # Base declarative model & TimestampMixin
│   │   │   ├── buyer.py             # Buyer & Requirement models
│   │   │   ├── crop.py              # Crop master model
│   │   │   ├── crop_alias.py        # Regional multilingual crop aliases
│   │   │   ├── farm.py              # Farmer land plot definitions
│   │   │   ├── farmer.py            # Farmer profile model
│   │   │   ├── fpo.py               # Farmer Producer Organization model
│   │   │   ├── geography.py         # State, District, Taluk, Village hierarchy
│   │   │   ├── harvest.py           # Farmer harvest batch records
│   │   │   ├── market.py            # Mandi / Regulated market model
│   │   │   ├── market_alias.py      # Market aliases for scraper matching
│   │   │   ├── market_price.py      # Canonical market price observations
│   │   │   ├── supply_match.py      # Buyer-Plot matched allocations
│   │   │   ├── task.py              # FPO tasks & assignments
│   │   │   ├── user.py              # User authentication & RBAC model
│   │   │   └── whatsapp.py          # Outbound logs, conversation state, usage
│   │   ├── schemas/                 # Pydantic v2 DTO schemas
│   │   │   ├── auth.py, buyer.py, crop.py, farmer.py, fpo.py, ...
│   │   ├── services/                # Business logic & domain services
│   │   │   ├── agricultural_intelligence.py # Forecasting & Haversine distance
│   │   │   ├── bot.py               # Transport-agnostic BotEngine
│   │   │   ├── ceda_api.py          # CEDA Ashoka API client
│   │   │   ├── data_cleaning.py     # MAD outlier & hygiene checks
│   │   │   ├── ingestion.py         # Multi-source ingestion orchestrator
│   │   │   ├── matching.py          # Matching engine for supply & demand
│   │   │   ├── parsers/             # Feed-specific parsers (OGD, CEDA, MandiPrices)
│   │   │   ├── telegram_bot.py      # Telegram bot service wrapper
│   │   │   ├── weather_service.py   # Open-Meteo weather client
│   │   │   ├── whatsapp.py          # WhatsApp Cloud client & templates
│   │   │   └── yield_estimator.py   # Plot yield forecasting algorithm
│   │   ├── messaging/               # Chat transport adapters
│   │   │   └── telegram.py          # Telegram HTTP client & command mapping
│   │   ├── config.py                # Pydantic Settings & environment validation
│   │   ├── database.py              # SQLAlchemy engine & session factory
│   │   ├── main.py                  # FastAPI application entry point & lifespan
│   │   └── worker.py                # Scheduled background worker loop
│   ├── scripts/                     # Operational & database seeding scripts
│   │   ├── provision_admin.py       # Admin account creation / credentials sync
│   │   ├── seed.py                  # Pilot FPO, farmers, and synthetic demo prices
│   │   ├── seed_render_fast.py      # Batch transaction seeder for remote DBs
│   │   ├── seed_statewide_foundation.py # Statewide 38 districts, markets, crops
│   │   ├── seed_supply_demand.py    # Buyers, plots, and demand matching pilot
│   │   └── telegram_poll.py         # Local Telegram bot polling runner
│   └── tests/                       # Pytest test suite (228 automated tests)
│
├── frontend/                        # Next.js 14 App Router frontend
│   ├── app/                         # App Router pages (16 routes)
│   │   ├── layout.tsx, page.tsx     # Root layout & landing page
│   │   ├── login/page.tsx           # Multi-role authentication page
│   │   ├── dashboard/page.tsx       # FPO executive dashboard
│   │   ├── prices/page.tsx          # Real-time mandi price explorer
│   │   ├── forecasts/page.tsx       # ML price forecast charts
│   │   ├── harvests/page.tsx        # Farmer harvest logs & aggregation
│   │   ├── buyers/page.tsx          # Verified buyers & procurement demands
│   │   ├── matching/page.tsx        # AI supply-demand matching interface
│   │   ├── tasks/page.tsx           # Operational task board for FPO staff
│   │   ├── telegram/page.tsx        # Telegram bot live connection manager
│   │   ├── farmers/page.tsx         # Farmer roster & onboarding
│   │   └── settings/page.tsx        # FPO settings & language toggle
│   ├── components/                  # Reusable UI component library
│   │   ├── ui/                      # Base buttons, cards, modals, tables
│   │   ├── layout/                  # Sidebar, header, navigation, language switch
│   │   └── charts/                  # Recharts wrappers for prices & forecasts
│   ├── lib/                         # Client utilities
│   │   ├── api.ts                   # Centralized API fetcher with token handling
│   │   └── utils.ts                 # CSS class merger and formatters
│   ├── package.json                 # Next.js dependencies and scripts
│   └── next.config.mjs              # Next.js configuration and proxy rewrites
│
├── docs/                            # Documentation, guides, runbooks
├── graphify-out/                    # AST knowledge graph, communities, wiki
└── render.yaml                      # Render Blueprint deployment definition
```
