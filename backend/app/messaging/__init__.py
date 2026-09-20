"""Messaging package: transport-agnostic types and WhatsApp Cloud API adapter."""

from app.messaging.base import Button, InboundMessage, MessageChannel, mask
from app.messaging.whatsapp_cloud import (
    WhatsAppCloudChannel,
    parse_webhook,
    verify_signature,
)

__all__ = [
    "Button",
    "InboundMessage",
    "MessageChannel",
    "WhatsAppCloudChannel",
    "mask",
    "parse_webhook",
    "verify_signature",
]
