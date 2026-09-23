# Community 11

> 29 nodes · cohesion 0.14

## Key Concepts

- **test_whatsapp_bot.py** (46 connections) — `backend/tests/test_whatsapp_bot.py`
- **post()** (20 connections) — `backend/tests/test_whatsapp_bot.py`
- **text_payload()** (11 connections) — `backend/tests/test_whatsapp_bot.py`
- **receive()** (9 connections) — `backend/app/api/whatsapp.py`
- **parse_webhook()** (8 connections) — `backend/app/messaging/whatsapp_cloud.py`
- **verify_signature()** (7 connections) — `backend/app/messaging/whatsapp_cloud.py`
- **env()** (6 connections) — `backend/tests/test_whatsapp_bot.py`
- **make_services()** (5 connections) — `backend/tests/test_whatsapp_bot.py`
- **button_payload()** (4 connections) — `backend/tests/test_whatsapp_bot.py`
- **test_harvest_flow_end_to_end()** (4 connections) — `backend/tests/test_whatsapp_bot.py`
- **test_alerts_opt_in_and_out()** (3 connections) — `backend/tests/test_whatsapp_bot.py`
- **test_cancel_clears_state()** (3 connections) — `backend/tests/test_whatsapp_bot.py`
- **test_duplicate_delivery_processed_once()** (3 connections) — `backend/tests/test_whatsapp_bot.py`
- **test_menu_button_tap_triggers_price()** (3 connections) — `backend/tests/test_whatsapp_bot.py`
- **test_menu_has_three_buttons()** (3 connections) — `backend/tests/test_whatsapp_bot.py`
- **test_price_reply_in_tamil_uses_quintal()** (3 connections) — `backend/tests/test_whatsapp_bot.py`
- **test_price_single_crop_english()** (3 connections) — `backend/tests/test_whatsapp_bot.py`
- **test_rejects_bad_or_missing_signature()** (3 connections) — `backend/tests/test_whatsapp_bot.py`
- **test_status_only_payload_is_ignored()** (3 connections) — `backend/tests/test_whatsapp_bot.py`
- **test_unregistered_number_gets_generic_reply()** (3 connections) — `backend/tests/test_whatsapp_bot.py`
- **test_empty_app_secret_never_verifies()** (2 connections) — `backend/tests/test_whatsapp_bot.py`
- **Check Meta's X-Hub-Signature-256 header (HMAC-SHA256 of the raw body).** (1 connections) — `backend/app/messaging/whatsapp_cloud.py`
- **Extract user messages. Delivery/read status callbacks yield an empty list.** (1 connections) — `backend/app/messaging/whatsapp_cloud.py`
- **fixture** (1 connections)
- **test_invalid_json_with_valid_signature_is_400()** (1 connections) — `backend/tests/test_whatsapp_bot.py`
- *... and 4 more nodes in this community*

## Relationships

- [Community 22](Community_22.md) (11 shared connections)
- [Community 13](Community_13.md) (10 shared connections)
- [Community 14](Community_14.md) (6 shared connections)
- [Community 1](Community_1.md) (5 shared connections)
- [Community 12](Community_12.md) (4 shared connections)
- [Community 19](Community_19.md) (3 shared connections)
- [Community 3](Community_3.md) (2 shared connections)
- [Community 9](Community_9.md) (2 shared connections)
- [Community 10](Community_10.md) (1 shared connections)
- [Community 46](Community_46.md) (1 shared connections)
- [Community 7](Community_7.md) (1 shared connections)
- [Community 16](Community_16.md) (1 shared connections)

## Source Files

- `backend/app/api/whatsapp.py`
- `backend/app/messaging/whatsapp_cloud.py`
- `backend/tests/test_whatsapp_bot.py`

## Audit Trail

- EXTRACTED: 101 (97%)
- INFERRED: 3 (3%)
- AMBIGUOUS: 0 (0%)

---

*Part of the graphify knowledge wiki. See [index](index.md) to navigate.*