from fastapi.testclient import TestClient

from app.main import app, store

client = TestClient(app)


def test_get_approval_returns_camel_case_json(valid_invoice):
    approval = store.create(valid_invoice)

    response = client.get(f"/approvals/{approval.id}")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "pending"
    assert body["requestId"] == approval.request_id
    assert body["invoice"]["orderNumber"] == "ORD-2001"


def test_get_unknown_approval_returns_404():
    response = client.get("/approvals/APR-999")

    assert response.status_code == 404
    assert response.json() == {"error": "Approval not found: APR-999"}


def test_human_approval_allows_release(valid_invoice):
    approval = store.create(valid_invoice)

    blocked = client.post(f"/shipments/{approval.request_id}/release")
    approved = client.post(f"/approvals/{approval.id}/approve")
    released = client.post(f"/shipments/{approval.request_id}/release")

    assert blocked.status_code == 409
    assert approved.json()["status"] == "approved"
    assert released.status_code == 200
    assert released.json()["status"] == "released"
    assert released.json()["shipmentId"].startswith("SHIP-")


def test_rejected_request_cannot_be_released(valid_invoice):
    approval = store.create(valid_invoice)

    client.post(f"/approvals/{approval.id}/reject")
    response = client.post(f"/shipments/{approval.request_id}/release")

    assert response.status_code == 409


def test_approving_twice_returns_409(valid_invoice):
    approval = store.create(valid_invoice)
    client.post(f"/approvals/{approval.id}/approve")

    response = client.post(f"/approvals/{approval.id}/approve")

    assert response.status_code == 409
