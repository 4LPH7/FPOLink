# FPOLink Pilot: Pitch and Onboarding (1 page each)

For FPO coordinators and the promoters who fund them. Detailed schedule and go/no-go rules: `docs/PILOT_RUNBOOK.md`.

## Pitch

**Problem.** Members sell to whoever comes to the gate, without knowing what nearby markets pay.

**What FPOLink does (free for the 14-day pilot):**
1. Farmers message a Telegram bot in Tamil with a crop name (for example `தக்காளி`) and get today's mandi price. If another market within 150 km pays clearly more after transport, the reply names it and the extra ₹ per quintal. The figure is an estimate.
2. Farmers report a harvest in a few taps (crop, kg, grade). Staff see all members' harvests in one list, ready to pool for a buyer.
3. Staff get a dashboard with farmers, harvests, buyer demand and tasks.

**What we ask.** 1 coordinator and about 10 farmers for 14 days, and a 15-minute call at the end.

**What we measure** (shared with you at the end):
- farmers who used it in week 2 (target: at least 6 of 10)
- kg of harvest reported and pooled
- how often the "better market" line was shown, and how many farmers say they acted on it
- ₹ per quintal gained versus the local price, from farmers who acted

**After the pilot.** If it saved members money, a subscription per FPO (roughly ₹1,000-2,500 a month, to be tested with you) or one fee for a promoter covering many FPOs. No ads, and farmer data is never sold.

## Onboarding (about 30 minutes)

1. **Staff login.** We create the coordinator's dashboard account. First login forces a new password.
2. **Add farmers** on `/farmers` (name, village, taluk, phone, crops). Phones must be 10-digit mobile numbers.
3. **Farmers join.** Each farmer opens `@Fpo_Link_Bot` in Telegram, taps Start, and shares their contact. A phone not on your list is told to ask the FPO.
4. **First messages to try:** send a crop name; `HARVEST`; `FORECAST`; `MENU`. Language: `/lang ta` or `/lang en`.
5. **Consent.** Farmers see the data-protection notice on first contact; `STOP` turns alerts off at any time (DPDP Act).
6. **Support.** Problems go to the pilot contact (add name and number here before the pilot starts).

## Before sending this
- A native Tamil speaker should read the bot's Tamil replies (`T["ta"]` in `backend/app/services/bot.py`).
- Fill in the pilot contact above.
- Check `/api/health` and today's date on `/prices` the morning the pilot starts.
