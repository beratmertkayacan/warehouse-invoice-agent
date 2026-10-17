from app.grounding import appears_in_text, drop_ungrounded_fields
from app.models import InvoiceFields

DOCUMENT = (
    "Invoice No: INV-1001\n"
    "Order No: ORD-2001\n"
    "Warehouse: WH-IST-01\n"
    "Customer: CUST-1001\n"
    "Product: PROD-001\n"
    "Quantity: 10\n"
    "Destination: Ankara"
)


def test_value_in_text_is_found():
    assert appears_in_text("ORD-2001", DOCUMENT)


def test_match_ignores_case():
    assert appears_in_text("ankara", DOCUMENT)


def test_part_of_a_longer_value_is_not_a_match():
    assert not appears_in_text("100", DOCUMENT)


def test_grounded_fields_are_kept(valid_invoice):
    fields, dropped = drop_ungrounded_fields(valid_invoice, DOCUMENT)

    assert fields == valid_invoice
    assert dropped == []


def test_invented_value_is_removed(valid_invoice):
    text = DOCUMENT.replace("Order No: ORD-2001\n", "")

    fields, dropped = drop_ungrounded_fields(valid_invoice, text)

    assert fields.order_number is None
    assert dropped == ["orderNumber"]


def test_optional_fields_are_not_checked(valid_invoice):
    fields = valid_invoice.model_copy(update={"notes": "Urgent delivery"})

    result, dropped = drop_ungrounded_fields(fields, DOCUMENT)

    assert result.notes == "Urgent delivery"
    assert dropped == []


def test_missing_values_stay_missing():
    fields, dropped = drop_ungrounded_fields(InvoiceFields(), DOCUMENT)

    assert fields == InvoiceFields()
    assert dropped == []
