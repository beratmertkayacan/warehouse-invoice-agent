from app.data_store import get_stock, get_warehouse
from app.models import Approval, ApprovalStatus, InvoiceFields, ShipmentRelease


class NotFoundError(Exception):
    pass


class InvalidStateError(Exception):
    pass


def prepare_shipment_summary(fields: InvoiceFields) -> str:
    stock = get_stock(fields.warehouse_id, fields.product_id)
    warehouse = get_warehouse(fields.warehouse_id)
    return (
        f"Ship {fields.quantity} x {stock['productName']} ({fields.product_id}) "
        f"from {warehouse['name']} to {fields.destination} "
        f"for customer {fields.customer_id}, order {fields.order_number}, "
        f"invoice {fields.invoice_number}."
    )


class ApprovalStore:
    def __init__(self) -> None:
        self._approvals: dict[str, Approval] = {}
        self._shipments: dict[str, ShipmentRelease] = {}

    def create(self, fields: InvoiceFields) -> Approval:
        number = len(self._approvals) + 1
        approval = Approval(
            id=f"APR-{number:03d}",
            request_id=f"REQ-{number:03d}",
            status="pending",
            summary=prepare_shipment_summary(fields),
            invoice=fields,
        )
        self._approvals[approval.id] = approval
        return approval

    def get(self, approval_id: str) -> Approval:
        approval = self._approvals.get(approval_id)
        if approval is None:
            raise NotFoundError(f"Approval not found: {approval_id}")
        return approval

    def approve(self, approval_id: str) -> Approval:
        return self._decide(approval_id, "approved")

    def reject(self, approval_id: str) -> Approval:
        return self._decide(approval_id, "rejected")

    def _decide(self, approval_id: str, new_status: ApprovalStatus) -> Approval:
        approval = self.get(approval_id)
        if approval.status != "pending":
            raise InvalidStateError(f"Approval {approval_id} is already {approval.status}")
        approval.status = new_status
        return approval

    def find_by_request(self, request_id: str) -> Approval:
        for approval in self._approvals.values():
            if approval.request_id == request_id:
                return approval
        raise NotFoundError(f"Request not found: {request_id}")

    def release(self, request_id: str) -> ShipmentRelease:
        approval = self.find_by_request(request_id)
        if approval.status != "approved":
            raise InvalidStateError(f"Release blocked: approval {approval.id} is {approval.status}")
        if request_id in self._shipments:
            raise InvalidStateError(f"Request {request_id} is already released")

        shipment = ShipmentRelease(
            status="released",
            shipment_id=f"SHIP-{5000 + len(self._shipments) + 1}",
            request_id=request_id,
        )
        self._shipments[request_id] = shipment
        return shipment
