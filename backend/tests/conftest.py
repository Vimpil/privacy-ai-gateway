import pytest

from app.core.config import get_settings

_TEST_KEY_B64 = "MDEyMzQ1Njc4OWFiY2RlZjAxMjM0NTY3ODlhYmNkZWY="


@pytest.fixture(autouse=True)
def force_test_gateway_key(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("GATEWAY_SHARED_KEY_BASE64", _TEST_KEY_B64)
    monkeypatch.setenv("ALLOW_INSECURE_DEV_KEY", "false")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()

