"""WhatsApp Cloud API (Meta) adapter: webhook parsing, signature check, sending."""

from __future__ import annotations

import hashlib
import hmac
import logging

import httpx

from app.messaging.base import Button, InboundMessage, StatusUpdate, mask

log = logging.getLogger("whatsapp")

MAX_TEXT = 4096  # WhatsApp text body limit
MAX_BUTTONS = 3  # reply buttons per message
MAX_BUTTON_TITLE = 20


def verify_signature(app_secret: str, raw_body: bytes, header: str | None) -> bool:
    """Check Meta's X-Hub-Signature-256 header (HMAC-SHA256 of the raw body)."""
    if not app_secret or not header or not header.startswith("sha256="):
        return False  # an empty secret would let anyone forge a valid signature
    expected = hmac.new(app_secret.encode(), raw_body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, header.removeprefix("sha256="))


def parse_webhook(payload: dict) -> list[InboundMessage]:
    """Extract user messages. Delivery/read status callbacks yield an empty list."""
    out: list[InboundMessage] = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            names = {
                c.get("wa_id", ""): c.get("profile", {}).get("name", "")
                for c in value.get("contacts", [])
            }
            for m in value.get("messages", []):
                wa_id = m.get("from", "")
                kind, text = "unsupported", ""
                mtype = m.get("type")
                if mtype == "text":
                    kind, text = "text", m.get("text", {}).get("body", "")
                elif mtype == "interactive":
                    inter = m.get("interactive", {})
                    if inter.get("type") == "button_reply":
                        kind, text = "button", inter["button_reply"].get("id", "")
                    elif inter.get("type") == "list_reply":
                        kind, text = "list", inter["list_reply"].get("id", "")
                elif mtype in (
                    "audio",
                    "voice",
                    "image",
                    "document",
                    "video",
                    "sticker",
                    "location",
                    "contacts",
                ):
                    kind = mtype
                out.append(InboundMessage(m.get("id", ""), wa_id, kind, text, names.get(wa_id, "")))
    return out


def parse_status_updates(payload: dict) -> list[StatusUpdate]:
    """Extract message status updates (sent, delivered, read, failed)."""
    out: list[StatusUpdate] = []
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            value = change.get("value", {})
            for s in value.get("statuses", []):
                meta_id = s.get("id", "")
                recipient_id = s.get("recipient_id", "")
                status = s.get("status", "")
                timestamp = str(s.get("timestamp", ""))
                errors = s.get("errors")
                if meta_id and status:
                    out.append(
                        StatusUpdate(
                            meta_message_id=meta_id,
                            recipient_id=recipient_id,
                            status=status,
                            timestamp=timestamp,
                            errors=errors,
                        )
                    )
    return out


class WhatsAppCloudChannel:
    def __init__(
        self,
        access_token: str,
        phone_number_id: str,
        api_version: str,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._url = f"https://graph.facebook.com/{api_version}/{phone_number_id}/messages"
        self._headers = {"Authorization": f"Bearer {access_token}"}
        self._client = client or httpx.AsyncClient(timeout=10)
        self.last_sent_message_id: str | None = None

    async def _post(self, to: str, payload: dict) -> bool:
        body = {"messaging_product": "whatsapp", "to": to, **payload}
        self.last_sent_message_id = None
        try:
            resp = await self._client.post(self._url, json=body, headers=self._headers)
        except httpx.TimeoutException:
            log.warning("WhatsApp send timeout to %s", mask(to))
            raise
        except httpx.HTTPError:
            log.exception("WhatsApp send error to %s", mask(to))
            return False
        if resp.status_code >= 400:
            # Never log the token; body may say why (template not approved, window closed...)
            log.error("WhatsApp send %s to %s: %s", resp.status_code, mask(to), resp.text[:300])
            return False
        try:
            data = resp.json()
            messages = data.get("messages", [])
            if messages and isinstance(messages, list):
                self.last_sent_message_id = messages[0].get("id")
        except Exception:
            pass
        return True

    async def send_text(self, to: str, body: str) -> bool:
        return await self._post(to, {"type": "text", "text": {"body": body[:MAX_TEXT]}})

    async def send_buttons(self, to: str, body: str, buttons: list[Button]) -> bool:
        rows = [
            {"type": "reply", "reply": {"id": b.id, "title": b.title[:MAX_BUTTON_TITLE]}}
            for b in buttons[:MAX_BUTTONS]
        ]
        return await self._post(
            to,
            {
                "type": "interactive",
                "interactive": {
                    "type": "button",
                    "body": {"text": body[:1024]},
                    "action": {"buttons": rows},
                },
            },
        )

    async def send_template(self, to: str, name: str, lang: str, params: list[str]) -> bool:
        """Business-initiated message (e.g. daily digest). Template must be approved by Meta."""
        components = []
        if params:
            components.append(
                {"type": "body", "parameters": [{"type": "text", "text": p} for p in params]}
            )
        return await self._post(
            to,
            {
                "type": "template",
                "template": {"name": name, "language": {"code": lang}, "components": components},
            },
        )

    async def send_template_with_id(
        self, to: str, name: str, lang: str, params: list[str]
    ) -> tuple[bool, str | None]:
        """Send template and return tuple of (success, meta_message_id)."""
        ok = await self.send_template(to, name, lang, params)
        return ok, self.last_sent_message_id

