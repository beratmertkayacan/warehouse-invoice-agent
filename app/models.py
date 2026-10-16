from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelModel(BaseModel):
    model_config = ConfigDict(
        alias_generator=to_camel,
        validate_by_name=True,
        serialize_by_alias=True,
    )


class InvoiceFields(CamelModel):
    invoice_number: str | None = None
    order_number: str | None = None
    warehouse_id: str | None = None
    customer_id: str | None = None
    product_id: str | None = None
    quantity: int | None = None
    destination: str | None = None
    requested_date: str | None = None
    notes: str | None = None


class ValidationResult(CamelModel):
    passed: bool
    issues: list[str]
