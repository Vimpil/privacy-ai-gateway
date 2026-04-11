export type EncryptedPayload = {
  nonce: string;
  ciphertext: string;
};

export type OracleRequest = {
  encrypted: EncryptedPayload;
  request_id?: string;
};

export type OracleResponse = {
  encrypted: EncryptedPayload;
  audit_hash: string;
};

