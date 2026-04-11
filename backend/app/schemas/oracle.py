from pydantic import BaseModel


class EncryptedPayload(BaseModel):
    nonce: str
    ciphertext: str


class OracleRequest(BaseModel):
    encrypted: EncryptedPayload
    request_id: str | None = None


class PublicApiContext(BaseModel):
    provider: str
    title: str
    summary: str
    url: str


class OracleResponse(BaseModel):
    encrypted: EncryptedPayload
    audit_hash: str
    public_api: PublicApiContext | None = None

