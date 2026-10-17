import re

from pydantic.alias_generators import to_camel

from app.models import InvoiceFields
from app.validation import REQUIRED_FIELDS


def appears_in_text(value: str, text: str) -> bool:
    pattern = rf"(?<!\w){re.escape(value)}(?!\w)"
    return re.search(pattern, text, flags=re.IGNORECASE) is not None


def drop_ungrounded_fields(fields: InvoiceFields, text: str) -> tuple[InvoiceFields, list[str]]:
    changes = {}
    dropped = []
    for name in REQUIRED_FIELDS:
        value = getattr(fields, name)
        if value is None:
            continue
        if not appears_in_text(str(value), text):
            changes[name] = None
            dropped.append(to_camel(name))
    return fields.model_copy(update=changes), dropped
