import os, struct, hashlib
from Crypto.Cipher import AES, PKCS1_OAEP
from Crypto.PublicKey import RSA
from Crypto.Util.Padding import pad, unpad

def derive_mask(key: bytes, length: int) -> bytes:
    """Derives a pseudorandom mask using iterative SHA-256 to obfuscate ciphertext."""
    mask = b""
    counter = 0
    while len(mask) < length:
        counter += 1
        data = key + struct.pack('>I', counter)
        mask += hashlib.sha256(data).digest()
    return mask[:length]

class UniqueEncryptionSystem:
    def __init__(self, rsa_key: RSA.RsaKey = None):
        if rsa_key is None:
            self.rsa_key = RSA.generate(2048)
        else:
            self.rsa_key = rsa_key
        self.public_key = self.rsa_key.publickey()
        self.rsa_cipher_enc = PKCS1_OAEP.new(self.public_key)
        self.rsa_cipher_dec = PKCS1_OAEP.new(self.rsa_key)

    def encrypt(self, plaintext: str) -> dict:
        plaintext_bytes = plaintext.encode('utf-8')
        padded_plaintext = pad(plaintext_bytes, AES.block_size)
        aes_key = os.urandom(32) # AES-256 key
        iv = os.urandom(AES.block_size)
        cipher_aes = AES.new(aes_key, AES.MODE_CBC, iv)
        aes_ciphertext = cipher_aes.encrypt(padded_plaintext)
        nonce = os.urandom(16)
        combined_key = aes_key + nonce
        mask = derive_mask(combined_key, len(aes_ciphertext))
        obfuscated_ciphertext = bytes(b ^ m for b, m in zip(aes_ciphertext, mask))
        key_blob = aes_key + nonce + iv
        rsa_encrypted_key = self.rsa_cipher_enc.encrypt(key_blob)
        return {
            'rsa_encrypted_key': rsa_encrypted_key,
            'obfuscated_ciphertext': obfuscated_ciphertext
        }

    def decrypt(self, encrypted_data: dict) -> str:
        rsa_encrypted_key = encrypted_data['rsa_encrypted_key']
        obfuscated_ciphertext = encrypted_data['obfuscated_ciphertext']
        key_blob = self.rsa_cipher_dec.decrypt(rsa_encrypted_key)
        aes_key = key_blob[:32]
        nonce = key_blob[32:48]
        iv = key_blob[48:64]
        combined_key = aes_key + nonce
        mask = derive_mask(combined_key, len(obfuscated_ciphertext))
        aes_ciphertext = bytes(b ^ m for b, m in zip(obfuscated_ciphertext, mask))
        cipher_aes = AES.new(aes_key, AES.MODE_CBC, iv)
        padded_plaintext = cipher_aes.decrypt(aes_ciphertext)
        plaintext_bytes = unpad(padded_plaintext, AES.block_size)
        return plaintext_bytes.decode('utf-8')