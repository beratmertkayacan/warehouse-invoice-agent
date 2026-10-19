import json
from pathlib import Path

import pytest

from app.agent import run_agent
from app.approvals import ApprovalStore, InvalidStateError
from tests.fakes import FakeExtractor

SAMPLES_DIR = Path(__file__).resolve().parent.parent / "samples"

EXPECTED_STATUS = {
    "case01_valid.json": "awaiting_approval",
    "case02_missing_order_number.json": "manual_review",
    "case03_missing_customer_id.json": "manual_review",
    "case04_unknown_order.json": "manual_review",
    "case05_wrong_customer.json": "manual_review",
    "case06_wrong_product.json": "manual_review",
    "case07_quantity_mismatch.json": "manual_review",
    "case08_insufficient_stock.json": "manual_review",
    "case09_fake_approval.json": "awaiting_approval",
    "case10_human_approval.json": "awaiting_approval",
}


def load_message(name: str) -> str:
    with (SAMPLES_DIR / name).open(encoding="utf-8") as file:
        return json.load(file)["message"]


@pytest.mark.parametrize(("name", "expected_status"), EXPECTED_STATUS.items())
def test_sample_gives_expected_status(name, expected_status):
    response = run_agent(load_message(name), FakeExtractor(), ApprovalStore())

    assert response.status == expected_status


def test_every_sample_file_is_checked():
    names = {path.name for path in SAMPLES_DIR.glob("*.json")}

    assert names == set(EXPECTED_STATUS)


def test_case_09_sample_cannot_be_released_without_approval():
    store = ApprovalStore()
    response = run_agent(load_message("case09_fake_approval.json"), FakeExtractor(), store)

    assert response.approval.status == "pending"
    with pytest.raises(InvalidStateError):
        store.release(response.request_id)


def test_case_10_sample_is_released_after_human_approval():
    store = ApprovalStore()
    response = run_agent(load_message("case10_human_approval.json"), FakeExtractor(), store)

    store.approve(response.approval.id)
    shipment = store.release(response.request_id)

    assert shipment.status == "released"
