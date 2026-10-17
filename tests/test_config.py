from app.config import DEFAULT_BASE_URL, DEFAULT_MODEL, load_settings

SETTING_NAMES = ["OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_MODEL", "PORT"]


def test_settings_read_environment_variables(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://example.openai.azure.com/openai/v1/")
    monkeypatch.setenv("OPENAI_MODEL", "my-deployment")
    monkeypatch.setenv("PORT", "9000")

    settings = load_settings()

    assert settings.openai_api_key == "test-key"
    assert settings.openai_base_url == "https://example.openai.azure.com/openai/v1/"
    assert settings.openai_model == "my-deployment"
    assert settings.port == 9000


def test_settings_use_defaults_when_values_are_missing(monkeypatch):
    for name in SETTING_NAMES:
        monkeypatch.delenv(name, raising=False)

    settings = load_settings()

    assert settings.openai_api_key == ""
    assert settings.openai_base_url == DEFAULT_BASE_URL
    assert settings.openai_model == DEFAULT_MODEL
    assert settings.port == 8000


def test_empty_base_url_falls_back_to_default(monkeypatch):
    monkeypatch.setenv("OPENAI_BASE_URL", "")

    assert load_settings().openai_base_url == DEFAULT_BASE_URL
