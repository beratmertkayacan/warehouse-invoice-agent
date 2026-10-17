from pydantic.alias_generators import to_camel

from app.data_store import get_order, get_stock, get_warehouse
from app.models import InvoiceFields, ValidationResult

REQUIRED_FIELDS = [
    "invoice_number",
    "order_number",
    "warehouse_id",
    "customer_id",
    "product_id",
    "quantity",
    "destination",
]


def find_missing_fields(fields: InvoiceFields) -> list[str]:
    missing = []
    for name in REQUIRED_FIELDS:
        value = getattr(fields, name)
        if value is None or value == "":
            missing.append(to_camel(name))
    return missing


def validate_invoice(
    fields: InvoiceFields, tool_calls: list[str] | None = None
) -> ValidationResult:
    if tool_calls is None:
        tool_calls = []

    missing = find_missing_fields(fields)
    if missing:
        issues = [f"Missing required field: {name}" for name in missing]
        return ValidationResult(passed=False, issues=issues)

    if fields.quantity <= 0:
        return ValidationResult(passed=False, issues=["Quantity must be greater than zero"])

    tool_calls.append("get_order")
    order = get_order(fields.order_number)
    if order is None:
        return ValidationResult(passed=False, issues=[f"Unknown order: {fields.order_number}"])

    issues = []

    if fields.customer_id != order["customerId"]:
        issues.append(
            f"Customer mismatch: invoice has {fields.customer_id}, order has {order['customerId']}"
        )

    if fields.product_id != order["productId"]:
        issues.append(
            f"Product mismatch: invoice has {fields.product_id}, order has {order['productId']}"
        )

    if fields.quantity != order["quantity"]:
        issues.append(
            f"Quantity mismatch: invoice has {fields.quantity}, order has {order['quantity']}"
        )

    if get_warehouse(fields.warehouse_id) is None:
        issues.append(f"Unknown warehouse: {fields.warehouse_id}")
    else:
        tool_calls.append("get_stock")
        stock = get_stock(fields.warehouse_id, fields.product_id)
        available = stock["availableQuantity"] if stock else 0
        if fields.quantity > available:
            issues.append(
                f"Insufficient stock: requested {fields.quantity}, "
                f"available {available} in {fields.warehouse_id}"
            )

    return ValidationResult(passed=not issues, issues=issues)
