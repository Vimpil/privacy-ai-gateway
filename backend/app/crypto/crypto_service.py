import base64
import os

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

DEFAULT_SHARED_KEY_B64 = "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA="
NONCE_SIZE_BYTES = 12


def _decode_key(shared_key_b64: str) -> bytes:
    key = base64.b64decode(shared_key_b64)
    if len(key) not in (16, 24, 32):
        raise ValueError("GATEWAY_SHARED_KEY_BASE64 must decode to 16, 24, or 32 bytes")
    return key


def derive_key_from_passphrase(passphrase: str, salt_b64: str, iterations: int = 100_000) -> str:
    salt = base64.b64decode(salt_b64)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=max(100_000, iterations),
    )
    key_bytes = kdf.derive(passphrase.encode("utf-8"))
    return base64.b64encode(key_bytes).decode("utf-8")


def _get_default_key() -> bytes:
    shared_key_b64 = os.getenv("GATEWAY_SHARED_KEY_BASE64", DEFAULT_SHARED_KEY_B64)
    return _decode_key(shared_key_b64)


def encrypt(text: str) -> str:
    """Encrypt plaintext and return base64(iv + ciphertext_and_tag)."""
    key = _get_default_key()
    nonce = os.urandom(NONCE_SIZE_BYTES)
    ciphertext = AESGCM(key).encrypt(nonce, text.encode("utf-8"), None)
    payload = nonce + ciphertext
    return base64.b64encode(payload).decode("utf-8")


def decrypt(data: str) -> str:
    """Decrypt base64(iv + ciphertext_and_tag) payload back to plaintext."""
    key = _get_default_key()
    payload = base64.b64decode(data)
    if len(payload) <= NONCE_SIZE_BYTES:
        raise ValueError("Invalid payload: missing IV or ciphertext")
    nonce = payload[:NONCE_SIZE_BYTES]
    ciphertext = payload[NONCE_SIZE_BYTES:]
    plaintext = AESGCM(key).decrypt(nonce, ciphertext, None)
    return plaintext.decode("utf-8")


class CryptoService:
    @staticmethod
    def decrypt_message(shared_key_b64: str, nonce_b64: str, ciphertext_b64: str) -> str:
        key = _decode_key(shared_key_b64)
        nonce = base64.b64decode(nonce_b64)
        ciphertext = base64.b64decode(ciphertext_b64)
        plaintext = AESGCM(key).decrypt(nonce, ciphertext, None)
        return plaintext.decode("utf-8")

    @staticmethod
    def encrypt_message(shared_key_b64: str, plaintext: str) -> tuple[str, str]:
        key = _decode_key(shared_key_b64)
        nonce = os.urandom(NONCE_SIZE_BYTES)
        ciphertext = AESGCM(key).encrypt(nonce, plaintext.encode("utf-8"), None)
        return (
            base64.b64encode(nonce).decode("utf-8"),
            base64.b64encode(ciphertext).decode("utf-8"),
        )

