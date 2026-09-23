# DbBotServices

> God node · 43 connections · `backend/app/services/db_bot_services.py`

**Community:** [Community 4](Community_4.md)

## Connections by Relation

### contains
- db_bot_services.py `EXTRACTED`

### imports
- test_whatsapp_harvest_flow.py `EXTRACTED`
- test_db_bot_services.py `EXTRACTED`
- test_source_safety.py `EXTRACTED`
- api/whatsapp.py `EXTRACTED`

### method
- .submit_harvest() `EXTRACTED`
- .set_state() `EXTRACTED`
- .mark_notice_delivered() `EXTRACTED`
- .mark_notice_sent() `EXTRACTED`
- .latest_price() `EXTRACTED`
- .is_price_stale() `EXTRACTED`
- .get_state() `EXTRACTED`
- .first_time() `EXTRACTED`
- .find_farmer() `EXTRACTED`
- .release_notice_claim() `EXTRACTED`
- .forecast_text() `EXTRACTED`
- .weather_text() `EXTRACTED`
- .set_alerts() `EXTRACTED`
- .claim_notice() `EXTRACTED`
- .__init__() `EXTRACTED`

### rationale_for
- Production implementation of BotServices using SQLAlchemy and PostgreSQL. `EXTRACTED`

### uses
- [User](User.md) `INFERRED`
- [Farmer](Farmer.md) `INFERRED`
- [Crop](Crop.md) `INFERRED`
- [MarketPrice](MarketPrice.md) `INFERRED`
- [Farmer](Farmer.md) `INFERRED`
- Market `INFERRED`
- Harvest `INFERRED`
- HarvestGrade `INFERRED`
- ConvState `INFERRED`
- PriceInfo `INFERRED`
- WeatherData `INFERRED`
- ConversationState `INFERRED`
- test_db_bot_services_submit_harvest_persistence() `INFERRED`
- test_latest_price_and_dashboard_whitelist_real_sources_only() `INFERRED`
- WhatsAppInbound `INFERRED`
- test_find_farmer_by_phone() `INFERRED`
- test_latest_price_and_staleness() `INFERRED`
- test_seed_script_prices_never_served_to_bot() `INFERRED`
- test_conversation_state_ttl() `INFERRED`
- Prediction `INFERRED`
- *…and 2 more `uses` connection(s) not listed (lowest-degree first to go)*

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*