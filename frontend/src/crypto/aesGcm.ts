const textEncoder = new TextEncoder();
const textDecoder = new TextDecoder();

function b64ToBytes(value: string): Uint8Array {
  const binary = atob(value);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }
  return bytes;
}

function toArrayBuffer(bytes: Uint8Array): ArrayBuffer {
  return bytes.buffer.slice(bytes.byteOffset, bytes.byteOffset + bytes.byteLength) as ArrayBuffer;
}

function bytesToB64(bytes: Uint8Array): string {
  let binary = "";
  bytes.forEach((byte) => {
    binary += String.fromCharCode(byte);
  });
  return btoa(binary);
}

async function importAesKey(sharedKeyB64: string): Promise<CryptoKey> {
  return crypto.subtle.importKey(
    "raw",
    toArrayBuffer(b64ToBytes(sharedKeyB64)),
    { name: "AES-GCM" },
    false,
    ["encrypt", "decrypt"],
  );
}

export async function encryptText(sharedKeyB64: string, plaintext: string) {
  const key = await importAesKey(sharedKeyB64);
  const nonce = crypto.getRandomValues(new Uint8Array(12));
  const ciphertext = await crypto.subtle.encrypt(
    { name: "AES-GCM", iv: nonce },
    key,
    textEncoder.encode(plaintext),
  );

  return {
    nonce: bytesToB64(nonce),
    ciphertext: bytesToB64(new Uint8Array(ciphertext)),
  };
}

export async function decryptText(sharedKeyB64: string, nonceB64: string, ciphertextB64: string) {
  const key = await importAesKey(sharedKeyB64);
  const plaintext = await crypto.subtle.decrypt(
    { name: "AES-GCM", iv: toArrayBuffer(b64ToBytes(nonceB64)) },
    key,
    toArrayBuffer(b64ToBytes(ciphertextB64)),
  );
  return textDecoder.decode(plaintext);
}

