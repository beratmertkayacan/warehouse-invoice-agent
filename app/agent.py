from typing import Protocol
from uuid import uuid4

from app.approvals import ApprovalStore
from app.grounding import drop_ungrounded_fields
from app.models import AgentResponse, ApprovalInfo, InvoiceFields, ToolCall
from app.validation import validate_invoice

APPROVAL_ANSWER = (
    "The document is complete and consistent. Human approval is required before shipment release."
)


class FieldExtractor(Protocol):
    def extract(self, text: str) -> InvoiceFields: ...


def new_session_id() -> str:
    return f"sess-{uuid4().hex[:8]}"


def run_agent(
    message: str,
    extractor: FieldExtractor,
    store: ApprovalStore,
    session_id: str | None = None,
) -> AgentResponse:
    session_id = session_id or new_session_id()
    fields, _ = drop_ungrounded_fields(extractor.extract(message), message)
    used_tools: list[str] = []

    validation = validate_invoice(fields, used_tools)
    if not validation.passed:
        return AgentResponse(
            session_id=session_id,
            answer="Manual review required: " + "; ".join(validation.issues),
            status="manual_review",
            extracted_fields=fields,
            validation=validation,
            tool_calls=[ToolCall(name=name) for name in used_tools],
        )

    approval = store.create(fields)
    used_tools.append("submit_for_human_approval")
    return AgentResponse(
        session_id=session_id,
        answer=APPROVAL_ANSWER,
        status="awaiting_approval",
        extracted_fields=fields,
        validation=validation,
        tool_calls=[ToolCall(name=name) for name in used_tools],
        approval=ApprovalInfo(id=approval.id, status=approval.status),
        request_id=approval.request_id,
    )
