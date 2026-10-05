# FPOLink Technology Stack

Comprehensive inventory of languages, runtimes, frameworks, libraries, database systems, and development tooling.

---

## 1. Core Languages & Runtimes

| Layer | Technology | Version | Purpose |
|---|---|---|---|
| **Backend Runtime** | Python | 3.12+ | Core API service, bot engines, background workers, ML forecasting |
| **Frontend Runtime** | Node.js | 18+ / 20+ | Next.js server & frontend application build runtime |
| **Backend Language** | Python | 3.12 | Strongly typed with PEP 484/585/604 type annotations |
| **Frontend Language** | TypeScript | 5.x | Strict-mode typing across Next.js App Router and components |

---

## 2. Backend Frameworks & Libraries

### Web API & Core Architecture
- **FastAPI** (`^0.110.0`): High-performance asynchronous REST API framework
- **Uvicorn** (`^0.28.0`): ASGI server implementation with standard workers
- **Pydantic v2** (`^2.6.0`): Strict data parsing, validation schemas, and environment settings (`pydantic-settings`)
- **PyJWT** (`^2.8.0`): JWT token issuance, verification, refresh, and role claim encoding
- **Passlib** (`^1.7.4`) with **Bcrypt / Argon2**: Secure password hashing with salt

### Database & ORM
- **PostgreSQL**: Primary relational datastore (production on Render managed Postgres, local dev on PostgreSQL 16)
- **SQLAlchemy** (`^2.0.28`): Declarative 2.0 ORM with typed mappings and SessionLocal pattern
- **Psycopg 3** (`psycopg[binary] ^3.1.18`): Modern PostgreSQL driver supporting both sync and async execution
- **Alembic** (`^1.13.1`): Database schema migrations (latest version: `0013_fpo_tasks`)

### Machine Learning & Analytics
- **LightGBM** (`^4.3.0`): Gradient boosted decision trees for price forecasting
- **Scikit-learn** (`^1.4.1`): Preprocessing, evaluation metrics, and fallback models
- **Pandas** (`^2.2.1`): Time series manipulation, data cleaning, and feature engineering
- **NumPy** (`^1.26.4`): Numerical routines and MAD (Median Absolute Deviation) anomaly detection

### Networking & Messaging
- **HTTPX** (`^0.27.0`): Asynchronous and synchronous HTTP client for upstream data feeds and Telegram API
- **Requests** (`^2.31.0`): Synchronous HTTP client for external weather and price ingest APIs
- **APScheduler** (`^3.10.4`): Background scheduled worker execution for daily ingestion and sweeps
- **Respx** (`^0.23.1`): HTTP mock client for pytest suites

---

## 3. Frontend Frameworks & UI Architecture

### Framework & Routing
- **Next.js** (`14.2+`): React framework utilizing the App Router architecture (`frontend/app/`)
- **React** (`^18.2.0`): Component model with React Server Components (RSC) and Client Components

### Styling & Design System
- **Tailwind CSS** (`^3.4.1`): Utility-first CSS framework configured with custom tokens
- **PostCSS** & **Autoprefixer**: CSS build pipeline
- **Lucide React** (`^0.359.0`): Clean, accessible iconography
- **clsx** & **tailwind-merge**: Dynamic class string combination (`cn` helper)
- **Radix UI Primitives**: Accessible headless UI primitives for dialogs, dropdowns, and tabs

### Visualization & State
- **Recharts** (`^2.12.0`): Responsive SVG charting for price history and forecasts
- **Native Fetch Client** (`frontend/lib/api.ts`): Centralized auth token management, auto-refresh, and API proxy routing

---

## 4. Database Systems & Storage

| System | Role | Configuration |
|---|---|---|
| **Render PostgreSQL** | Production Primary | Managed PostgreSQL `16`, SSL required, 43 tables migrated |
| **Local PostgreSQL** | Development Primary | `localhost:5432`, database `fpolink` |
| **SQLite (In-Memory)** | Fast Unit Tests | Ephemeral in-memory SQLite for high-speed deterministic test suites |

---

## 5. Development, Linting & CI/CD Tooling

- **Pytest** (`^8.1.0`): Test runner with plugins `pytest-asyncio`, `pytest-mock`, `pytest-cov`, `respx`
- **Ruff / Black**: Code style and linting enforcement
- **Graphify**: Persistent AST knowledge graph and community detection (`graphify-out/`)
- **GitHub Actions**: Automated CI pipeline running lint, backend tests, and frontend build checks
- **Docker & Docker Compose**: Containerized multi-service deployment specs (`docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile`)
