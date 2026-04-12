/** Browser-side AES-GCM crypto with PBKDF2-derived session key. */

const NONCE_SIZE = 12;
const SALT_SIZE = 16;
const PBKDF2_ITERATIONS = 100_000;
const SALT_STORAGE_KEY = "cipher-oracle-session-salt";

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

function getSessionSaltB64(): string {
  const fromStorage = window.localStorage.getItem(SALT_STORAGE_KEY);
  if (fromStorage) return fromStorage;
  const salt = bytesToB64(crypto.getRandomValues(new Uint8Array(SALT_SIZE)));
  window.localStorage.setItem(SALT_STORAGE_KEY, salt);
  return salt;
}

async function deriveKey(passphrase: string, saltB64: string, iterations = PBKDF2_ITERATIONS): Promise<CryptoKey> {
  const passphraseKey = await crypto.subtle.importKey(
    "raw",
    enc.encode(passphrase),
    { name: "PBKDF2" },
    false,
    ["deriveKey"],
  );

  return crypto.subtle.deriveKey(
    {
      name: "PBKDF2",
      salt: b64ToBytes(saltB64),
      iterations: Math.max(PBKDF2_ITERATIONS, iterations),
      hash: "SHA-256",
    },
    passphraseKey,
    { name: "AES-GCM", length: 256 },
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

export type KdfContext = {
  salt: string;
  iterations: number;
};

/**
 * Encrypt plaintext with AES-GCM.
 *
 * Generates a fresh 12-byte IV per call.
 * Returns base64-encoded `{ nonce, ciphertext }` ready to POST to /api/v1/chat.
 */
export async function encryptText(
  passphrase: string,
  plaintext: string,
): Promise<{ encrypted: EncryptedPayload; kdf: KdfContext }> {
  if (passphrase.trim().length < 8) {
    throw new Error("Passphrase must be at least 8 characters.");
  }
  const salt = getSessionSaltB64();
  const key = await deriveKey(passphrase, salt, PBKDF2_ITERATIONS);
  const nonce = crypto.getRandomValues(new Uint8Array(NONCE_SIZE));

  const ciphertext = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv: nonce },
    key,
    enc.encode(plaintext),
  );

  return {
    encrypted: {
      nonce: bytesToB64(nonce),
      ciphertext: bytesToB64(new Uint8Array(ciphertext)),
    },
    kdf: {
      salt,
      iterations: PBKDF2_ITERATIONS,
    },
  };
}

/**
 * Decrypt an AES-GCM payload from the backend.
 *
 * Expects the same `{ nonce, ciphertext }` format produced by
 * `CryptoService.encrypt_message` on the Python side.
 */
export async function decryptText(
  passphrase: string,
  nonceB64: string,
  ciphertextB64: string,
  kdf: KdfContext,
): Promise<string> {
  const key = await deriveKey(passphrase, kdf.salt, kdf.iterations);

  const plaintext = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv: b64ToBytes(nonceB64) },
    key,
    b64ToBytes(ciphertextB64),
  );

  return dec.decode(plaintext);
}
