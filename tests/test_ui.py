from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_playground_page_is_served():
    response = client.get("/")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/html")
    assert "Warehouse Outbound Invoice Agent" in response.text


def test_playground_script_is_served():
    response = client.get("/static/app.js")

    assert response.status_code == 200
    assert "/agent/chat" in response.text


def test_playground_is_not_part_of_the_api_schema():
    paths = client.get("/openapi.json").json()["paths"]

    assert "/" not in paths
