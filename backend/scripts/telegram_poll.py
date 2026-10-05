"""Run the Telegram bot with long polling (local development, no public URL needed).

    cd backend && TELEGRAM_BOT_TOKEN=... python scripts/telegram_poll.py

Polling and webhooks are mutually exclusive: this script deletes any registered webhook.
On Render the API registers the webhook again on its next start.
"""

import asyncio
import logging
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.api.telegram import _service, get_client  # noqa: E402
from app.config import settings  # noqa: E402
from app.messaging.telegram import BOT_COMMANDS, parse_update  # noqa: E402

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("telegram.poll")


async def main() -> None:
    if not settings.TELEGRAM_BOT_TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN is not set")
    client = get_client()
    me = await client.call("getMe")
    if not me:
        raise SystemExit("Telegram rejected the token (getMe failed)")
    await client.call("deleteWebhook", {"drop_pending_updates": False})
    await client.call("setMyCommands", {"commands": BOT_COMMANDS})
    log.info("Polling as @%s - press Ctrl+C to stop", me["username"])
    svc = _service()
    offset = None
    while True:
        payload = {"timeout": 30, "allowed_updates": ["message", "callback_query"]}
        if offset is not None:
            payload["offset"] = offset
        updates = await client.call("getUpdates", payload, timeout=40) or []
        for raw in updates:
            offset = raw["update_id"] + 1
            update = parse_update(raw)
            if update is not None:
                await svc.handle_update(update)
        if not updates:
            await asyncio.sleep(0.5)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
