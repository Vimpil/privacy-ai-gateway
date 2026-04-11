import base64

import pytest

from app.crypto.crypto_service import decrypt, encrypt


def test_encrypt_decrypt_round_trip(monkeypatch: pytest.MonkeyPatch) -> None:
    key_b64 = base64.b64encode(b"1" * 32).decode("utf-8")
    monkeypatch.setenv("GATEWAY_SHARED_KEY_BASE64", key_b64)

    payload = encrypt("hello cipher oracle")
    result = decrypt(payload)

    assert isinstance(payload, str)
    assert result == "hello cipher oracle"


def test_decrypt_rejects_invalid_payload(monkeypatch: pytest.MonkeyPatch) -> None:
    key_b64 = base64.b64encode(b"1" * 32).decode("utf-8")
    monkeypatch.setenv("GATEWAY_SHARED_KEY_BASE64", key_b64)

    invalid_payload = base64.b64encode(b"short").decode("utf-8")
    with pytest.raises(ValueError):
        decrypt(invalid_payload)

