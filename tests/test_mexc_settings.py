from src.app.infrastructure.exchange.mexc.settings import MexcSettings


def test_mexc_settings_strip_whitespace_from_secrets(monkeypatch):
    monkeypatch.setenv("MEXC_API_KEY", "mx0vgluicGPyka9vwO\r\n")
    monkeypatch.setenv("MEXC_SECRET_KEY", "secret-value\n")

    settings = MexcSettings()

    assert settings.api_key == "mx0vgluicGPyka9vwO"
    assert settings.api_secret == "secret-value"
