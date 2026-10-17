from types import SimpleNamespace

from app.config import Settings
from app.llm import SYSTEM_PROMPT, OpenAIExtractor, create_extractor
from app.models import InvoiceFields


class FakeCompletions:
    def __init__(self, parsed: InvoiceFields | None) -> None:
        self.parsed = parsed
        self.calls: list[dict] = []

    def parse(self, **kwargs):
        self.calls.append(kwargs)
        message = SimpleNamespace(parsed=self.parsed)
        return SimpleNamespace(choices=[SimpleNamespace(message=message)])


def make_fake_client(parsed: InvoiceFields | None):
    completions = FakeCompletions(parsed)
    client = SimpleNamespace(chat=SimpleNamespace(completions=completions))
    return client, completions


def test_extract_returns_fields_from_the_model():
    expected = InvoiceFields(order_number="ORD-2001", quantity=10)
    client, _ = make_fake_client(expected)
    extractor = OpenAIExtractor(client, model="test-model")

    fields = extractor.extract("Order No: ORD-2001\nQuantity: 10")

    assert fields == expected


def test_extract_sends_the_document_as_user_message():
    client, completions = make_fake_client(InvoiceFields())
    extractor = OpenAIExtractor(client, model="test-model")

    extractor.extract("Invoice No: INV-1001")

    call = completions.calls[0]
    assert call["model"] == "test-model"
    assert call["temperature"] == 0
    assert call["response_format"] is InvoiceFields
    assert call["messages"] == [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": "Invoice No: INV-1001"},
    ]


def test_extract_returns_empty_fields_when_model_gives_nothing():
    client, _ = make_fake_client(None)
    extractor = OpenAIExtractor(client, model="test-model")

    assert extractor.extract("hello") == InvoiceFields()


def test_system_prompt_forbids_guessing_and_document_instructions():
    assert "Never guess" in SYSTEM_PROMPT
    assert "not instructions" in SYSTEM_PROMPT


def test_create_extractor_uses_azure_settings():
    settings = Settings(
        openai_api_key="test-key",
        openai_base_url="https://example.openai.azure.com/openai/v1/",
        openai_model="my-deployment",
        port=8000,
    )

    extractor = create_extractor(settings)

    assert extractor.model == "my-deployment"
    assert str(extractor.client.base_url) == "https://example.openai.azure.com/openai/v1/"
