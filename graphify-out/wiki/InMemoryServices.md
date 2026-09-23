# InMemoryServices

> God node · 30 connections · `backend/app/services/bot.py`

**Community:** [Community 1](Community_1.md)

## Connections by Relation

### calls
- test_bot_handles_send_failure_and_retries_notice() `EXTRACTED`
- test_t2_2_first_contact_notice() `EXTRACTED`
- test_t2_3_stop_from_any_state_clears_conversation() `EXTRACTED`
- test_harvest_chat_full_flow() `EXTRACTED`
- test_t2_3_tamil_niruthu_opt_out() `EXTRACTED`
- test_t2_4_unregistered_number_gets_zero_data() `EXTRACTED`
- test_harvest_retry_cap_resets_to_menu() `EXTRACTED`
- test_harvest_webhook_retry_idempotency() `EXTRACTED`
- test_media_unsupported_fallback() `EXTRACTED`
- test_rate_limiter() `EXTRACTED`
- make_services() `EXTRACTED`

### contains
- bot.py `EXTRACTED`

### imports
- test_whatsapp_harvest_flow.py `EXTRACTED`
- test_whatsapp_bot.py `EXTRACTED`
- test_whatsapp_onboarding.py `EXTRACTED`

### method
- .__init__() `EXTRACTED`
- .mark_notice_delivered() `EXTRACTED`
- .find_farmer() `EXTRACTED`
- .latest_price() `EXTRACTED`
- .mark_notice_sent() `EXTRACTED`
- .get_state() `EXTRACTED`
- .set_state() `EXTRACTED`
- .first_time() `EXTRACTED`
- .forecast_text() `EXTRACTED`
- .weather_text() `EXTRACTED`
- .submit_harvest() `EXTRACTED`
- .set_alerts() `EXTRACTED`
- .claim_notice() `EXTRACTED`
- .release_notice_claim() `EXTRACTED`

### uses
- test_notice_atomic_claim_concurrency_and_retry() `INFERRED`

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*