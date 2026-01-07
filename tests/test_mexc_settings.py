import os

import pytest

from src.app.infrastructure.exchange.mexc.settings import MexcSettings


@pytest.mark.parametrize("secret_env_var", ["MEXC_SECRET_KEY", "MEXC_API_SECRET"])
def test_mexc_settings_accepts_secret_alias(monkeypatch, secret_env_var):
    monkeypatch.delenv("MEXC_SECRET_KEY", raising=False)
    monkeypatch.delenv("MEXC_API_SECRET", raising=False)
    monkeypatch.setenv("MEXC_API_KEY", "alias-key")
    monkeypatch.setenv(secret_env_var, "alias-secret")

    settings = MexcSettings()

    assert settings.api_key == "alias-key"
    assert settings.api_secret == "alias-secret"
