# FPOLink TN: 2-Week Field Pilot Runbook (Final: Pilot)

This runbook guides FPO leadership, agronomy field staff, and technical operators through conducting the initial 2-week live field pilot with 10–20 turmeric and banana farmers in Erode district, Tamil Nadu.

---

## 1. Pilot Objectives & Key Results (OKRs)

- **Target Cohort**: 15 active farmer members from **Erode Turmeric Farmers Producer Co. Ltd** across Perundurai, Modakkurichi, and Kodumudi.
- **Duration**: 14 calendar days.
- **Success Criteria**:
  1. **Engagement**: At least 70% (11/15) of enrolled farmers interact with the bot weekly (price query or harvest entry).
  2. **Delivery Reliability**: > 98% successful delivery rate on `daily_price_digest` utility templates.
  3. **Data Accuracy**: 100% of price queries return actual Erode Regulated Market modal prices with accurate dates.
  4. **Cost Ceiling**: Total pilot WhatsApp messaging cost < ₹250 (utilizing free tier allowances where applicable).
  5. **DPDP Compliance**: Zero unmasked PII logged in application traces; 100% immediate honoring of `STOP` requests.

---

## 2. Pre-Pilot Verification Checklist (Day -3 to Day 0)

- [ ] Checkpoint A passed: Test inbound `"PRICE"` and `"விலை"` from test phone; duplicate delivery ignored.
- [ ] Checkpoint B passed: Test harvest entry workflow; record appears on `/farmers` dashboard.
- [ ] Checkpoint C passed: Dry run of `send_daily_digests()` to 3 internal staff numbers; `STOP` keyword halts messages.
- [ ] Checkpoint D passed: Staging stack running on HTTPS with valid SSL; `/api/health` returns `200 OK`.
- [ ] Database seeded with active crops (Turmeric, Banana, Coconut) and Erode district mandis.
- [ ] Tamil copy certified by FPO Review Board (Thiru. S. Murugesan & Tmt. K. Selvi).

---

## 3. Weekly Execution Timeline

### Week 1: Onboarding, Price Discovery & Harvest Flow
- **Day 1 (Monday)**:
  - FPO staff register the 15 farmer profiles via dashboard (`/farmers`) with name, village, taluk, phone number, and primary crop.
  - Staff dispatch SMS or WhatsApp invitation link (`https://wa.me/<BOT_NUMBER>?text=Hi`).
  - Farmer receives first-contact notice explaining service and DPDP consent terms.
- **Days 2–4 (Tuesday–Thursday)**:
  - Farmers test price lookup commands: `PRICE`, `விலை`, or interactive buttons.
  - Field coordinators encourage farmers to query current rates before selling at local mandis.
- **Day 5 (Friday)**:
  - Harvest simulation: Farmers test submitting upcoming harvest batches (e.g., 20 quintals Turmeric Grade A).
  - FPO manager reviews incoming entries on staff dashboard.
- **Day 7 (Sunday)**:
  - Week 1 Telemetry Review: Inspect `/whatsapp` activity dashboard; record active count and any dropped webhooks.

### Week 2: Automated Proactive Digests & Price-Move Alerts
- **Day 8 (Monday)**:
  - Enable 07:30 IST daily digest cron in `fpolink-worker`.
  - Opted-in farmers automatically receive morning price summary for their enrolled crops.
- **Days 9–12 (Tuesday–Friday)**:
  - Monitor daily ingestion health on `/admin` at 06:15 IST (OGD and Agmarknet feeds).
  - Test threshold price-move alerts if market price fluctuates by > ₹5/kg.
- **Day 13 (Saturday)**:
  - Test opt-out flow with 2 selected volunteer farmers texting `"STOP"`.
  - Confirm worker skips opted-out numbers on Sunday morning digest.
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

2. **Verify Morning Digest Dispatch**:
   ```bash
   docker compose exec backend python -c "
   from app.database import SessionLocal
   from app.models.whatsapp import OutboundMessage
   from datetime import date
   db = SessionLocal()
   count = db.query(OutboundMessage).filter(OutboundMessage.category == 'digest').count()
   print(f'Total digests sent to date: {count}')
   "
   ```

3. **Check Inbound Error Logs**:
   - Access `https://app.yourfpo.org/whatsapp` (or local staff dashboard).
   - Review table for any rows with `status = 'failed'` or `retry_count > 0`.

4. **Monitor Outbound Cost**:
   - Check month-to-date estimated cost widget. Confirm expenditure is well within monthly limits.

---

## 5. Post-Pilot Evaluation & Go/No-Go Decision Matrix

At the conclusion of Day 14, the FPO executive committee reviews the pilot scorecard:

| Metric | Target | Actual | Evaluation |
|---|---|---|---|
| Farmer Participation Rate | ≥ 70% (11/15) | — | PASS / FAIL |
| Total Harvest Inquiries Logged | ≥ 10 | — | PASS / FAIL |
| Message Delivery Rate | ≥ 98% | — | PASS / FAIL |
| Farmer Satisfaction (Tamil Usability) | ≥ 4.0 / 5.0 | — | PASS / FAIL |
| Total Cost incurred | < ₹250 | — | PASS / FAIL |

### Decision Pathways:
- **EXPAND**: If all 5 criteria pass, proceed to onboarding all 200+ FPO cooperative members and connect multi-FPO district routing.
- **ADJUST**: If Tamil wording caused confusion or harvest parsing had errors, implement copy revisions and speech-to-text voice input before expanding.
- **STOP**: If farmers prefer traditional phone calls or data freshness cannot be maintained, invoke kill switch (`WHATSAPP_ENABLED=false`) and reassess strategy.
