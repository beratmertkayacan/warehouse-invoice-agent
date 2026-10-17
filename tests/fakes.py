from app.models import InvoiceFields

LABELS = {
    "invoice no": "invoice_number",
    "order no": "order_number",
    "warehouse": "warehouse_id",
    "customer": "customer_id",
    "product": "product_id",
    "quantity": "quantity",
    "destination": "destination",
}

VALID_LINES = {
    "Invoice No": "INV-1001",
    "Order No": "ORD-2001",
    "Warehouse": "WH-IST-01",
    "Customer": "CUST-1001",
    "Product": "PROD-001",
    "Quantity": "10",
    "Destination": "Ankara",
}


class FakeExtractor:
    def extract(self, text: str) -> InvoiceFields:
        values = {}
        for line in text.splitlines():
            label, _, value = line.partition(":")
            name = LABELS.get(label.strip().lower())
            if name and value.strip():
                values[name] = value.strip()
        return InvoiceFields(**values)


def make_document(
    changes: dict[str, str | None] | None = None,
    note: str = "Please prepare this shipment.",
) -> str:
    lines = dict(VALID_LINES)
    for label, value in (changes or {}).items():
        if value is None:
            lines.pop(label)
        else:
            lines[label] = value
    text = "\n".join(f"{label}: {value}" for label, value in lines.items())
    return f"{text}\nDocument text: {note}"
