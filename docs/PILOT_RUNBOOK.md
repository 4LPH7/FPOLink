# FPOLink TN: 2-Week Field Pilot Runbook (Final: Pilot)

This runbook guides FPO leadership, agronomy field staff, and technical operators through conducting the initial 2-week live field pilot with 10–20 turmeric and banana farmers in Erode district, Tamil Nadu.

---

## 1. Pilot Objectives & Key Results (OKRs)

- **Target Cohort**: 15 active farmer members from **Erode Turmeric Farmers Producer Co. Ltd** across Perundurai, Modakkurichi, and Kodumudi.
- **Duration**: 14 calendar days.
- **Success Criteria**:
  1. **Engagement**: At least 70% (11/15) of enrolled farmers interact with the bot weekly (price query or harvest entry).
  2. **Reply Reliability**: At least 98% of scripted Telegram price and harvest interactions receive the expected bot response during the test set.
  3. **Data Accuracy**: 100% of price queries return actual Erode Regulated Market modal prices with accurate dates.
  4. **Cost Ceiling**: Pilot messaging stays within the approved Telegram/hosting budget; record any paid infrastructure separately from messaging.
  5. **DPDP Compliance**: Zero unmasked PII logged in application traces; 100% immediate honoring of `STOP` requests.

---

## 2. Pre-Pilot Verification Checklist (Day -3 to Day 0)

- [ ] Checkpoint A passed: Test Telegram `/start`, `/price turmeric`, `"விலை"`, and duplicate webhook delivery handling.
- [ ] Checkpoint B passed: Test harvest entry workflow; record appears on `/farmers` dashboard.
- [ ] Checkpoint C passed: Test Telegram `/stop` and `/alerts` behavior with internal staff accounts; verify opted-out farmers do not receive any enabled proactive channel messages.
- [ ] Checkpoint D passed: Staging stack running on HTTPS with valid SSL; `/api/health` returns `200 OK`.
- [ ] Telegram staff page at `/telegram` reports the bot configured and webhook registered.
- [ ] Database seeded with active crops (Turmeric, Banana, Coconut) and Erode district mandis.
- [ ] Tamil copy certified by FPO Review Board (Thiru. S. Murugesan & Tmt. K. Selvi).

---

## 3. Weekly Execution Timeline

### Week 1: Onboarding, Price Discovery & Harvest Flow
- **Day 1 (Monday)**:
  - FPO staff register the 15 farmer profiles via dashboard (`/farmers`) with name, village, taluk, phone number, and primary crop.
  - Staff share the Telegram bot link (`https://t.me/Fpo_Link_Bot`) with each farmer.
  - Farmer receives first-contact notice explaining service and DPDP consent terms.
- **Days 2–4 (Tuesday–Thursday)**:
  - Farmers test `/price turmeric`, `விலை`, or interactive buttons in Telegram.
  - Field coordinators encourage farmers to query current rates before selling at local mandis.
- **Day 5 (Friday)**:
  - Harvest simulation: Farmers test submitting upcoming harvest batches (e.g., 20 quintals Turmeric Grade A).
  - FPO manager reviews incoming entries on staff dashboard.
- **Day 7 (Sunday)**:
  - Week 1 Telemetry Review: Inspect `/telegram` bot and webhook status, review API logs for failed updates, and record active farmer count and dropped/retried interactions.

### Week 2: Repeat Use, Data Freshness & Opt-Out
- **Day 8 (Monday)**:
  - Confirm the 06:00 IST price-ingestion job completed and the displayed observation dates are current for pilot markets.
- **Days 9–12 (Tuesday–Friday)**:
  - Monitor daily ingestion health on `/admin` and ask participating farmers to repeat price lookups and harvest updates.
- **Day 13 (Saturday)**:
  - Test `/stop` with 2 selected volunteer farmers; confirm no proactive notifications are sent after opt-out.
- **Day 14 (Sunday)**:
  - Pilot Conclusion & Data Tally.

---

## 4. Daily Operational Telemetry & Monitoring Protocol

Every morning during the pilot (08:00 IST), the technical operator performs a 3-minute health check:

1. **Check System Health**:
   ```bash
   curl -s https://api.yourfpo.org/api/health | jq .
   ```
   Ensure `"status": "ok"` and `"db": "ok"`.

2. **Verify Data Ingestion and Farmer Channel**:
   ```bash
   docker compose exec backend python -c "
   from app.database import SessionLocal
   from app.models.market_price import MarketPrice
   db = SessionLocal()
   print(db.query(MarketPrice).order_by(MarketPrice.price_date.desc()).first())
   "
   ```

3. **Check Inbound Error Logs**:
   - Access `https://app.yourfpo.org/telegram` and confirm the webhook is registered.
   - Review backend logs for `telegram update` failures and follow up on any farmer report of a missing response.

4. **Monitor Operating Cost**:
   - Record hosting and any paid API cost against the approved pilot budget.

---

## 5. Post-Pilot Evaluation & Go/No-Go Decision Matrix

At the conclusion of Day 14, the FPO executive committee reviews the pilot scorecard:

| Metric | Target | Actual | Evaluation |
|---|---|---|---|
| Farmer Participation Rate | ≥ 70% (11/15) | — | PASS / FAIL |
| Total Harvest Inquiries Logged | ≥ 10 | — | PASS / FAIL |
| Scripted Telegram Reply Reliability | ≥ 98% | — | PASS / FAIL |
| Farmer Satisfaction (Tamil Usability) | ≥ 4.0 / 5.0 | — | PASS / FAIL |
| Total Pilot Cost | Within approved budget | — | PASS / FAIL |

### Decision Pathways:
- **EXPAND**: If all 5 criteria pass, proceed to onboarding all 200+ FPO cooperative members and connect multi-FPO district routing.
- **ADJUST**: If Tamil wording caused confusion or harvest parsing had errors, implement copy revisions and speech-to-text voice input before expanding.
- **STOP**: If farmers prefer traditional phone calls or data freshness cannot be maintained, invoke the Telegram kill switch (`TELEGRAM_ENABLED=false`) and reassess strategy.
