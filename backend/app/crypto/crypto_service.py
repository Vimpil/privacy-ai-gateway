import base64
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class CryptoService:
    @staticmethod
    def decrypt_message(shared_key_b64: str, nonce_b64: str, ciphertext_b64: str) -> str:
        key = base64.b64decode(shared_key_b64)
        nonce = base64.b64decode(nonce_b64)
        ciphertext = base64.b64decode(ciphertext_b64)
        plaintext = AESGCM(key).decrypt(nonce, ciphertext, None)
        return plaintext.decode("utf-8")

    @staticmethod
    def encrypt_message(shared_key_b64: str, plaintext: str) -> tuple[str, str]:
        key = base64.b64decode(shared_key_b64)
        nonce = os.urandom(12)
        ciphertext = AESGCM(key).encrypt(nonce, plaintext.encode("utf-8"), None)
        return (
            base64.b64encode(nonce).decode("utf-8"),
            base64.b64encode(ciphertext).decode("utf-8"),
        )

