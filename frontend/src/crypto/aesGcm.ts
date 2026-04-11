/**
 * Browser-side AES-GCM encryption — Web Crypto API.
 *
 * Wire format (matches Python backend CryptoService exactly):
 *   Key        — base64-encoded raw AES key (16, 24, or 32 bytes)
 *   Nonce/IV   — 12 random bytes per request, base64-encoded, sent separately
 *   Ciphertext — AES-GCM output (encrypted bytes + 16-byte auth tag), base64-encoded
 *
 * These map directly to the EncryptedPayload schema:
 *   { nonce: string; ciphertext: string }
 *
 * Backend equivalent:
 *   CryptoService.encrypt_message / CryptoService.decrypt_message
 *   in backend/app/crypto/crypto_service.py
 */

/** Must match backend NONCE_SIZE_BYTES = 12 */
const NONCE_SIZE = 12;

const enc = new TextEncoder();
const dec = new TextDecoder();

// ── Helpers ────────────────────────────────────────────────────────────────

/**
 * base64 → Uint8Array<ArrayBuffer>.
 * Uses `new Uint8Array(n)` (length constructor) so TypeScript 5.6+ types
 * the buffer as `ArrayBuffer`, not `ArrayBufferLike`, satisfying BufferSource.
 */
function b64ToBytes(b64: string): Uint8Array<ArrayBuffer> {
  const str = atob(b64);
  const bytes = new Uint8Array(str.length);
  for (let i = 0; i < str.length; i++) bytes[i] = str.charCodeAt(i);
  return bytes;
}

/** Uint8Array → base64 */
function bytesToB64(bytes: Uint8Array): string {
  return btoa(Array.from(bytes, (b) => String.fromCharCode(b)).join(""));
}

/** Import a raw base64 AES key, validating its decoded length. */
async function importKey(sharedKeyB64: string): Promise<CryptoKey> {
  const raw = b64ToBytes(sharedKeyB64);
  if (![16, 24, 32].includes(raw.byteLength)) {
    throw new Error(
      `AES key must decode to 16, 24, or 32 bytes — got ${raw.byteLength}. ` +
      `Check VITE_SHARED_KEY_BASE64.`,
    );
  }
  return crypto.subtle.importKey(
    "raw",
    raw,
    { name: "AES-GCM" },
    false,
    ["encrypt", "decrypt"],
  );
}

// ── Public API ─────────────────────────────────────────────────────────────

/** Matches the EncryptedPayload schema sent to / received from the backend. */
export type EncryptedPayload = {
  nonce: string;
  ciphertext: string;
};

/**
 * Encrypt plaintext with AES-GCM.
 *
 * Generates a fresh 12-byte IV per call.
 * Returns base64-encoded `{ nonce, ciphertext }` ready to POST to /api/v1/chat.
 */
export async function encryptText(
  sharedKeyB64: string,
  plaintext: string,
): Promise<EncryptedPayload> {
  const key = await importKey(sharedKeyB64);
  const nonce = crypto.getRandomValues(new Uint8Array(NONCE_SIZE));

  const ciphertext = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv: nonce },
    key,
    enc.encode(plaintext),
  );

  return {
    nonce: bytesToB64(nonce),
    ciphertext: bytesToB64(new Uint8Array(ciphertext)),
  };
}

/**
 * Decrypt an AES-GCM payload from the backend.
 *
 * Expects the same `{ nonce, ciphertext }` format produced by
 * `CryptoService.encrypt_message` on the Python side.
 */
export async function decryptText(
  sharedKeyB64: string,
  nonceB64: string,
  ciphertextB64: string,
): Promise<string> {
  const key = await importKey(sharedKeyB64);

  const plaintext = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv: b64ToBytes(nonceB64) },
    key,
    b64ToBytes(ciphertextB64),
  );

  return dec.decode(plaintext);
}
