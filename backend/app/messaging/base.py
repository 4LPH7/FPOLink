"""Transport-agnostic messaging types. Bot logic depends on these, not on WhatsApp."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class InboundMessage:
    message_id: str  # WhatsApp message id (wamid...), used for dedup
    wa_id: str  # sender phone, digits only, e.g. "919876543210"
    kind: str  # "text" | "button" | "list" | "unsupported"
    text: str = ""  # text body, or the id of the tapped button / list row
    profile_name: str = ""


@dataclass(frozen=True)
class Button:
    id: str
    title: str  # WhatsApp limit: 20 characters


class MessageChannel(Protocol):
    async def send_text(self, to: str, body: str) -> None: ...

    async def send_buttons(self, to: str, body: str, buttons: list[Button]) -> None: ...

    async def send_template(self, to: str, name: str, lang: str, params: list[str]) -> None: ...


def mask(wa_id: str) -> str:
    """Mask a phone number for logs (phone numbers are personal data under DPDP)."""
    if len(wa_id) <= 6:
        return "***"
    return wa_id[:3] + "*" * (len(wa_id) - 5) + wa_id[-2:]
