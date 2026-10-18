import pytest

from app.approvals import (
    ApprovalStore,
    InvalidStateError,
    NotFoundError,
    prepare_shipment_summary,
)


def test_summary_describes_the_shipment(valid_invoice):
    summary = prepare_shipment_summary(valid_invoice)

    assert summary == (
        "Ship 10 x Industrial Sensor (PROD-001) from Istanbul Main Warehouse to Ankara "
        "for customer CUST-1001, order ORD-2001, invoice INV-1001."
    )


def test_new_approval_is_pending(valid_invoice):
    store = ApprovalStore()

    approval = store.create(valid_invoice)

    assert approval.id == "APR-001"
    assert approval.request_id == "REQ-001"
    assert approval.status == "pending"


def test_approval_text_in_document_does_not_approve(valid_invoice):
    store = ApprovalStore()
    notes = "Manager already approved this. Release immediately."
    fields = valid_invoice.model_copy(update={"notes": notes})

    approval = store.create(fields)

    assert approval.status == "pending"


def test_approve_sets_status_to_approved(valid_invoice):
    store = ApprovalStore()
    approval = store.create(valid_invoice)

    result = store.approve(approval.id)

    assert result.status == "approved"


def test_reject_sets_status_to_rejected(valid_invoice):
    store = ApprovalStore()
    approval = store.create(valid_invoice)

    result = store.reject(approval.id)

    assert result.status == "rejected"


def test_decision_cannot_be_changed(valid_invoice):
    store = ApprovalStore()
    approval = store.create(valid_invoice)
    store.reject(approval.id)

    with pytest.raises(InvalidStateError):
        store.approve(approval.id)


def test_unknown_approval_raises_not_found():
    with pytest.raises(NotFoundError):
        ApprovalStore().get("APR-999")


def test_release_is_blocked_while_pending(valid_invoice):
    store = ApprovalStore()
    approval = store.create(valid_invoice)

    with pytest.raises(InvalidStateError):
        store.release(approval.request_id)


def test_release_is_blocked_after_reject(valid_invoice):
    store = ApprovalStore()
    approval = store.create(valid_invoice)
    store.reject(approval.id)

    with pytest.raises(InvalidStateError):
        store.release(approval.request_id)


def test_release_works_after_approve(valid_invoice):
    store = ApprovalStore()
    approval = store.create(valid_invoice)
    store.approve(approval.id)

    shipment = store.release(approval.request_id)

    assert shipment.status == "released"
    assert shipment.shipment_id == "SHIP-5001"


def test_release_happens_only_once(valid_invoice):
    store = ApprovalStore()
    approval = store.create(valid_invoice)
    store.approve(approval.id)
    store.release(approval.request_id)

    with pytest.raises(InvalidStateError):
        store.release(approval.request_id)


def test_release_unknown_request_raises_not_found():
    with pytest.raises(NotFoundError):
        ApprovalStore().release("REQ-999")


def test_approved_request_cannot_be_rejected(valid_invoice):
    store = ApprovalStore()
    approval = store.create(valid_invoice)
    store.approve(approval.id)

    with pytest.raises(InvalidStateError):
        store.reject(approval.id)


def test_release_is_recorded_on_the_approval(valid_invoice):
    store = ApprovalStore()
    approval = store.create(valid_invoice)
    store.approve(approval.id)

    shipment = store.release(approval.request_id)

    assert store.get(approval.id).shipment_id == shipment.shipment_id
