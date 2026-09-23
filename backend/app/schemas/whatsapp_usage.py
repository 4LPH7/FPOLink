"""WhatsApp usage and cost schemas (T4.4)."""

from pydantic import BaseModel, Field


class WhatsAppUsageSummary(BaseModel):
    month: str = Field(..., description="Reporting month in YYYY-MM format")
    total_messages: int = Field(..., description="Total outbound messages recorded")
    by_category: dict[str, int] = Field(
        default_factory=dict,
        description="Counts grouped by category (utility, service, marketing, authentication)",
    )
    by_status: dict[str, int] = Field(
        default_factory=dict,
        description="Counts grouped by status (sent, delivered, read, failed)",
    )
    delivery_rate_pct: float = Field(
        ..., description="Percentage of delivered/read out of final resolved messages"
    )
    estimated_cost_inr: float = Field(
        ..., description="Estimated cost in INR based on configured rates"
    )
    unreachable_recipients: int = Field(
        ..., description="Number of recipients flagged as unreachable"
    )
    monthly_cap: int = Field(..., description="Configured monthly send cap")
    monthly_budget_inr: float = Field(..., description="Configured monthly budget limit in INR")
    circuit_breaker_tripped: bool = Field(
        ..., description="Whether send limits have halted proactive messaging"
    )


class InboundMessageItem(BaseModel):
    message_id: str
    status: str
    retry_count: int
    received_at: str


class InboundMessageListResponse(BaseModel):
    messages: list[InboundMessageItem]
    total: int
