from typing import Literal

from pydantic import BaseModel, ConfigDict, Field
from pydantic.alias_generators import to_camel

ApprovalStatus = Literal["pending", "approved", "rejected"]
AgentStatus = Literal["manual_review", "awaiting_approval"]


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        serialize_by_alias=True,
    )


class InvoiceFields(CamelModel):
    invoice_number: str | None = None
    order_number: str | None = None
    warehouse_id: str | None = None
    customer_id: str | None = None
    product_id: str | None = None
    quantity: int | None = None
    destination: str | None = None
    requested_date: str | None = None
    notes: str | None = None


class ValidationResult(CamelModel):
    passed: bool
    issues: list[str]


class Approval(CamelModel):
    id: str
    request_id: str
    status: ApprovalStatus
    summary: str
    invoice: InvoiceFields
    shipment_id: str | None = None


class ShipmentRelease(CamelModel):
    status: Literal["released"]
    shipment_id: str
    request_id: str


class AgentRequest(CamelModel):
    session_id: str | None = None
    message: str = Field(min_length=1, max_length=5000)


class ToolCall(CamelModel):
    name: str


class ApprovalInfo(CamelModel):
    id: str
    status: ApprovalStatus
    summary: str


class AgentResponse(CamelModel):
    session_id: str
    answer: str
    status: AgentStatus
    extracted_fields: InvoiceFields
    validation: ValidationResult
    tool_calls: list[ToolCall]
    approval: ApprovalInfo | None = None
    request_id: str | None = None
