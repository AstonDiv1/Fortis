import json
import os
import base64
import hashlib
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

VAULT_FILE = os.path.join(os.path.expanduser("~"), ".fortis.vault")
SALT_SIZE = 32
NONCE_SIZE = 12
ITERATIONS = 390000


def _derive_key(password: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=ITERATIONS,
        backend=default_backend(),
    )
    return kdf.derive(password.encode())


def vault_exists() -> bool:
    return os.path.exists(VAULT_FILE)


def create_vault(master_password: str) -> bool:
    """Create a new empty vault with the given master password."""
    salt = os.urandom(SALT_SIZE)
    key = _derive_key(master_password, salt)
    aesgcm = AESGCM(key)
    nonce = os.urandom(NONCE_SIZE)
    data = json.dumps([]).encode()
    ciphertext = aesgcm.encrypt(nonce, data, None)
    with open(VAULT_FILE, "wb") as f:
        f.write(salt + nonce + ciphertext)
    return True


def load_vault(master_password: str):
    """Load and decrypt vault. Returns list of entries or None if wrong password."""
    try:
        with open(VAULT_FILE, "rb") as f:
            raw = f.read()
        salt = raw[:SALT_SIZE]
        nonce = raw[SALT_SIZE:SALT_SIZE + NONCE_SIZE]
        ciphertext = raw[SALT_SIZE + NONCE_SIZE:]
        key = _derive_key(master_password, salt)
        aesgcm = AESGCM(key)
        plaintext = aesgcm.decrypt(nonce, ciphertext, None)
        return json.loads(plaintext.decode())
    except Exception:
        return None


def save_vault(master_password: str, entries: list) -> bool:
    """Encrypt and save vault entries."""
    try:
        with open(VAULT_FILE, "rb") as f:
            raw = f.read()
        salt = raw[:SALT_SIZE]
        key = _derive_key(master_password, salt)
        aesgcm = AESGCM(key)
        nonce = os.urandom(NONCE_SIZE)
        data = json.dumps(entries, ensure_ascii=False).encode()
        ciphertext = aesgcm.encrypt(nonce, data, None)
        with open(VAULT_FILE, "wb") as f:
            f.write(salt + nonce + ciphertext)
        return True
    except Exception:
        return False


def delete_vault():
    if os.path.exists(VAULT_FILE):
        os.remove(VAULT_FILE)
