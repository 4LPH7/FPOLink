# FPOLink TN: Pilot Specification & Open Decisions Resolution (T0.1)

This specification resolves the open architectural, operational, and organizational decisions required prior to launching the WhatsApp Cloud API integration and field pilot for FPOLink TN.

---

## 1. Resolution of Core Operational Questions

### Q1: Bot Phone Number Allocation
- **Decision**: A dedicated physical or virtual SIM registered exclusively for FPOLink TN (`+91 98765 43210` test placeholder / dedicated pilot number).
- **Rule**: The phone number must **never** be registered with the consumer or business WhatsApp mobile applications. Once a number is registered on the WhatsApp Cloud API (via Meta Business Manager), it operates headless and cannot coexist with an app installation.

### Q2: Meta Business Manager & WABA Ownership
- **Decision**: Primary ownership resides under the FPO entity (**Erode Turmeric Farmers Producer Company Limited**), with technical administration delegated to the development team via a **System User** with full WhatsApp Business Management permissions.
- **Rationale**:
  - Direct ownership by the registered agricultural cooperative satisfies Meta's Business Verification requirements (incorporation certificate, GSTIN, PAN, and utility bill matching business legal name).
  - Outbound utility message template approvals (`daily_price_digest`) achieve higher approval speed and retain compliance under DPDP Section 8 when sent from the verified cooperative entity.

### Q3: Pilot FPO & Cohort Selection
- **Selected Entity**: **Erode Turmeric Farmers Producer Co. Ltd** (Registration No: `TN-ERD-2024-FPO-01`).
- **Target District & Mandis**: Erode district mandis:
  - *Erode Mandi* (Semmampalayam)
  - *Perundurai Regulated Market*
  - *Gobichettipalayam Mandi*
- **Pilot Cohort**: 15 active turmeric and banana growers across Perundurai, Modakkurichi, and Kodumudi taluks.
- **Onboarding Method**: FPO staff provision farmer records in the staff dashboard (`/farmers`). Staff dispatch a single WhatsApp invite link (`https://wa.me/<BOT_PHONE>?text=Hi`).

### Q4: Harvest Submission Governance
- **Decision**: WhatsApp harvest submissions are received with status **`SUBMITTED`** and require staff review.
- **Workflow**:
  1. Farmer sends harvest details via WhatsApp interactive prompt: crop, estimated weight (in quintals/kg), grade (A/B/C), and expected harvest date.
  2. Bot issues an instant confirmation ticket with unique transaction reference (`wamid...`).
  3. FPO staff review the submission in the dashboard (`/farmers` or harvest table).
  4. Once staff verify quality or schedule logistics pickup, the status transitions to **`VERIFIED`** or **`SCHEDULED`**.
  5. Farmers are notified of status updates only if opted in to alerts.

### Q5: Default Language & Localization
- **Decision**: Default language is **Tamil (`ta`)** for all newly registered farmers.
- **Rationale**: 95%+ of member farmers in Erode district communicate and trade in Tamil.
- **Dynamic Switch**: Farmers can toggle their session language at any time by texting:
  - `ENGLISH` or `EN` -> switches interface and price alerts to English.
  - `TAMIL` or `TA` or `தமிழ்` -> reverts to Tamil.
- **Persistence**: Preference is stored in the `farmers.lang` column and reflected in outbound template calls.

### Q6: Tamil Copy Quality Review Board
- **Reviewers**:
  1. **Thiru. S. Murugesan** — FPO Lead Coordinator & Field Operations Director.
  2. **Tmt. K. Selvi** — Agricultural Extension Officer, Tamil Nadu Agricultural University (TNAU) Krishi Vigyan Kendra (KVK), Erode.
- **Mandate**: Review and certify all bot dialogue strings, error messages, and message templates (`daily_price_digest`) for native terminology accuracy (e.g., using *மஞ்சள்* for turmeric, *குவிண்டால்* for quintal, *மாதிரி விலை* for modal price).

---

## 2. Key Constraints & Compliance Fences

1. **DPDP Compliance (Digital Personal Data Protection Act, 2023)**:
   - Farmer phone numbers masked in logs and staff UI (`+91 98765 •••••`).
   - Strict retention limits enforced by daily automated worker job:
     - `whatsapp_inbound`: Purged after 7 days.
     - `conversation_state`: Purged after 24 hours.
     - `outbound_messages`: Retained 12 months for billing and cost auditing, then anonymized.
   - `STOP` / `நிறுத்து` commands must halt all proactive templates immediately and irrevocably until explicit re-opt-in.

2. **Cost Circuit Breakers**:
   - Monthly outbound send cap: 5,000 messages (default).
   - Rate limit: Max 30 inbound messages per farmer per 10 minutes to prevent loops.
   - Max 1 proactive price-change alert per farmer per day.
