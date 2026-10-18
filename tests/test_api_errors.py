import pytest
from fastapi.testclient import TestClient

from app.main import app, get_extractor
from tests.fakes import FakeExtractor

client = TestClient(app)


@pytest.fixture(autouse=True)
def fake_llm():
    app.dependency_overrides[get_extractor] = lambda: FakeExtractor()
    yield
    app.dependency_overrides.clear()


def test_invalid_field_returns_error_message():
    response = client.post("/agent/chat", json={"message": ""})

    assert response.status_code == 422
    assert response.json()["error"].startswith("Invalid request: message:")


def test_missing_body_returns_error_message():
    response = client.post("/agent/chat")

    assert response.status_code == 422
    assert response.json()["error"].startswith("Invalid request:")
