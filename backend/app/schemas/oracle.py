from pydantic import BaseModel


class EncryptedPayload(BaseModel):
    nonce: str
    ciphertext: str


class OracleRequest(BaseModel):
    encrypted: EncryptedPayload


class OracleResponse(BaseModel):
    encrypted: EncryptedPayload
    audit_hash: str

