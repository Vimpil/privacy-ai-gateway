from pydantic import BaseModel, Field


class EncryptedPayload(BaseModel):
    nonce: str = Field(min_length=8, max_length=256)
    ciphertext: str = Field(min_length=8, max_length=65535)


class OracleRequest(BaseModel):
    encrypted: EncryptedPayload
    request_id: str | None = Field(default=None, min_length=8, max_length=128)


class PublicApiContext(BaseModel):
    provider: str
    title: str
    summary: str
    url: str


class OracleResponse(BaseModel):
    encrypted: EncryptedPayload
    audit_hash: str
    public_api: PublicApiContext | None = None

