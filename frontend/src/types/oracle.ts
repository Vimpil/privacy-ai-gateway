export type EncryptedPayload = {
  nonce: string;
  ciphertext: string;
};

export type OracleRequest = {
  encrypted: EncryptedPayload;
  request_id?: string;
    mode?: "ai" | "wikipedia_only";
};

export type PublicApiContext = {
  provider: string;
  title: string;
  summary: string;
  url: string;
};

export type OracleResponse = {
  encrypted: EncryptedPayload;
  audit_hash: string;
  public_api?: PublicApiContext;
};

