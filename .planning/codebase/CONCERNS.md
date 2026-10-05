# FPOLink Technical Concerns & Architecture Watchpoints

Technical debt inventory, known constraints, security watchpoints, and operational considerations.

---

## 1. Hosting & Infrastructure Constraints

### A. Render Free Tier Spin-Down
- **Observation**: The free web service on Render spins down after 15 minutes of inactivity.
- **Impact**: Initial HTTP request after idle can encounter 50+ seconds of cold-start latency.
- **Mitigation / Next Step**: For production deployments, upgrade to a persistent Render instance or implement a periodic synthetic health ping (e.g. via UptimeRobot or cron worker).

### B. Remote Database Latency During Bulk Operations
- **Observation**: Remote transactions against the Oregon-hosted Render PostgreSQL database incur ~250ms round-trip latency from India.
- **Impact**: Seeding or migrations with individual row-level `commit()` calls can take 10+ minutes.
- **Mitigation**: Bulk transactions with single `db.commit()` batches must be used for remote migrations (as implemented in `seed_render_fast.py`).

---

## 2. Upstream Data Feed Reliability

### A. OGD & CEDA Gateway Timeouts
- **Observation**: Government mandi portals (`data.gov.in` and CEDA Ashoka) occasionally experience 502/504 gateway timeouts or intermittent upstream downtime.
- **Impact**: Daily ingestion sweeps may fail to retrieve fresh price records for specific markets.
- **Mitigation**:
  - Resilient circuit breaker implemented in `ceda_api.py`.
  - Fallback to cached observations and secondary feeds (`mandiprices.co.in`).
  - Stale price warnings surfaced in the frontend UI when observations are older than 24 hours.

### B. Variety Granularity in Agmarknet Data
- **Observation**: Government feeds frequently classify prices under broad commodity names (e.g. "Turmeric") rather than specific commercial grades (Finger vs. Bulb).
- **Impact**: Price forecasts and market displays require fuzzy alias mapping and modal price estimation.
- **Mitigation**: The `CropAlias` and `VarietyAlias` resolution engines map raw feed names to canonical ontology keys.

---

## 3. Messaging Channel Considerations

### A. WhatsApp Cloud API Production Approval
- **Observation**: WhatsApp Cloud API requires Meta Business verification and approved message templates before initiating outbound conversations outside the 24-hour customer care window.
- **Impact**: Outbound broadcast alerts (e.g. daily price digests) cannot be sent without Meta template approval.
- **Mitigation**: Inbound farmer queries are fully supported, and Telegram bot (`@Fpo_Link_Bot`) provides an unconstrained fallback channel with zero template review delays.

---

## 4. Privacy & Regulatory Compliance (DPDP Act)

- **Requirement**: The Digital Personal Data Protection (DPDP) Act of India requires informed consent prior to storing farmer personal details, phone numbers, and land parcels.
- **Implementation**: The bot and onboarding flows include explicit consent checkpoints (`consent_given=true`, `consent_date`), and support instant opt-out via the Tamil keyword `நிறுத்து` or English `STOP`.
