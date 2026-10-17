import pytest

from app.approvals import ApprovalStore
from app.models import InvoiceFields
from tests.fakes import FakeExtractor


@pytest.fixture
def valid_invoice() -> InvoiceFields:
    return InvoiceFields(
        invoice_number="INV-1001",
        order_number="ORD-2001",
        warehouse_id="WH-IST-01",
        customer_id="CUST-1001",
        product_id="PROD-001",
        quantity=10,
        destination="Ankara",
    )


@pytest.fixture
def extractor() -> FakeExtractor:
    return FakeExtractor()


@pytest.fixture
def store() -> ApprovalStore:
    return ApprovalStore()
