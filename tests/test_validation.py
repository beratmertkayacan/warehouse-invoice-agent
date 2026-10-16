from app.models import InvoiceFields
from app.validation import validate_invoice


def valid_fields(**changes) -> InvoiceFields:
    fields = InvoiceFields(
        invoice_number="INV-1001",
        order_number="ORD-2001",
        warehouse_id="WH-IST-01",
        customer_id="CUST-1001",
        product_id="PROD-001",
        quantity=10,
        destination="Ankara",
    )
    return fields.model_copy(update=changes)


def test_valid_invoice_passes():
    result = validate_invoice(valid_fields())

    assert result.passed is True
    assert result.issues == []


def test_missing_order_number_fails():
    result = validate_invoice(valid_fields(order_number=None))

    assert result.passed is False
    assert result.issues == ["Missing required field: orderNumber"]


def test_missing_customer_id_fails():
    result = validate_invoice(valid_fields(customer_id=None))

    assert result.issues == ["Missing required field: customerId"]


def test_empty_text_counts_as_missing():
    result = validate_invoice(valid_fields(destination=""))

    assert result.issues == ["Missing required field: destination"]


def test_all_missing_fields_are_listed():
    result = validate_invoice(InvoiceFields())

    assert len(result.issues) == 7


def test_zero_quantity_fails():
    result = validate_invoice(valid_fields(quantity=0))

    assert result.issues == ["Quantity must be greater than zero"]


def test_unknown_order_fails():
    result = validate_invoice(valid_fields(order_number="ORD-9999"))

    assert result.issues == ["Unknown order: ORD-9999"]


def test_customer_mismatch_fails():
    result = validate_invoice(valid_fields(customer_id="CUST-1002"))

    assert result.passed is False
    assert result.issues == ["Customer mismatch: invoice has CUST-1002, order has CUST-1001"]


def test_product_mismatch_fails():
    result = validate_invoice(valid_fields(product_id="PROD-003"))

    assert result.issues == ["Product mismatch: invoice has PROD-003, order has PROD-001"]


def test_quantity_mismatch_fails():
    result = validate_invoice(valid_fields(quantity=12))

    assert result.issues == ["Quantity mismatch: invoice has 12, order has 10"]


def test_insufficient_stock_fails():
    fields = valid_fields(
        order_number="ORD-2002",
        customer_id="CUST-1002",
        product_id="PROD-002",
        quantity=8,
    )

    result = validate_invoice(fields)

    assert result.issues == ["Insufficient stock: requested 8, available 5 in WH-IST-01"]


def test_product_not_stocked_in_warehouse_fails():
    fields = valid_fields(
        order_number="ORD-2003",
        customer_id="CUST-1003",
        product_id="PROD-003",
        quantity=4,
        warehouse_id="WH-ANK-01",
    )

    result = validate_invoice(fields)

    assert result.issues == ["Insufficient stock: requested 4, available 0 in WH-ANK-01"]


def test_unknown_warehouse_fails():
    result = validate_invoice(valid_fields(warehouse_id="WH-XXX-99"))

    assert result.issues == ["Unknown warehouse: WH-XXX-99"]


def test_several_mismatches_are_reported_together():
    result = validate_invoice(valid_fields(customer_id="CUST-1002", quantity=12))

    assert len(result.issues) == 2


def test_fields_use_camel_case_in_json():
    fields = InvoiceFields.model_validate({"orderNumber": "ORD-2001", "quantity": 10})

    assert fields.order_number == "ORD-2001"
    assert fields.model_dump(exclude_none=True) == {"orderNumber": "ORD-2001", "quantity": 10}
