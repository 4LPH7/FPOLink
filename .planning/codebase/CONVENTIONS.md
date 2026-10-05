# FPOLink Development Conventions & Patterns

Code standards, architectural patterns, naming conventions, and style guidelines across backend and frontend.

---

## 1. Python & Backend Conventions

### A. Type Hints & Pydantic Schemas
- Every public function and endpoint MUST have complete type annotations (PEP 484 / 585 / 604).
- Request payloads and responses MUST use Pydantic v2 `BaseModel` classes defined in `backend/app/schemas/`.
- Never return raw database model dictionaries; serialize via Pydantic response models using `model_validate` or `from_attributes = True`.

### B. SQLAlchemy Models & Database Access
- Models inherit from `Base` and `TimestampMixin` (`created_at`, `updated_at`).
- Primary keys are uniformly `UUID` (`UUID(as_uuid=True)` or `UUID(as_uuid=False)` string representation).
- Foreign keys explicitly declare `ondelete` semantics (`CASCADE` or `SET NULL`).
- Database sessions are obtained via FastAPI dependency injection:
  ```python
  @router.get("/")
  def list_items(db: Session = Depends(get_db), current_user: User = Depends(require_role(["admin"]))):
      ...
  ```
- Always wrap database writes in transactional blocks; avoid lingering open sessions.

### C. Authentication & Authorization
- Use `require_role([...])` dependency to protect routes:
  ```python
  current_user: User = Depends(require_role(["admin", "fpo_staff"]))
  ```
- Passwords MUST be hashed using `hash_password(...)` via Passlib/Bcrypt.
- Enforce `password_change_required` checks on newly created staff/farmer users.

### D. Tamil-First Internationalization (i18n)
- Default user language preference is Tamil (`ta`), with English (`en`) supported as secondary.
- All bot conversational templates provide bilingual replies or automatic localized strings based on user preference.
- Aliases for crops, varieties, and markets are maintained in normalized lowercase tables (`CropAlias`, `VarietyAlias`, `MarketAlias`) to handle phonetic Tamil-English transliterations (e.g. `manjal`, `turmeric`, `மஞ்சள்`).

---

## 2. Frontend & Next.js Conventions

### A. Next.js App Router & Server/Client Components
- Place route pages in `frontend/app/<route>/page.tsx`.
- Mark components requiring client state, interactivity, or browser APIs with `"use client"` at the top.
- Keep layout components in `frontend/components/layout/` and primitives in `frontend/components/ui/`.

### B. API Client & State Management
- Never perform direct `fetch(...)` calls with hardcoded URLs.
- Always use the centralized client in `frontend/lib/api.ts`:
  ```typescript
  import { api } from "@/lib/api";
  const data = await api.get("/api/prices/latest");
  ```
- Token management (storage in `localStorage`, inclusion in `Authorization` header, and 401 handling) is encapsulated in `api.ts`.

### C. Styling & CSS
- Use utility classes with Tailwind CSS.
- Combine conditional classes using the `cn(...)` utility helper (`clsx` + `tailwind-merge`).
- Support responsive breakpoints (`sm:`, `md:`, `lg:`) for mobile-first farmer tablet & phone usage.

---

## 3. Error Handling & Resilience Patterns

- External HTTP calls to third-party feeds (CEDA, OGD, Open-Meteo) must specify explicit timeouts (e.g., `timeout=15`).
- Circuit breaker pattern is enforced for unstable external feeds to prevent blocking API workers during third-party downtime.
- Inbound webhook processing must acknowledge receipt quickly (HTTP 200/202) and execute heavy business logic asynchronously or via background tasks.
