"""
Encryption service for sensitive data (HIPAA compliance)
"""
import base64
import hashlib
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from app.core.config import settings


class EncryptionService:
    """Handle encryption/decryption of sensitive data"""

    def __init__(self):
        # Derive encryption key from secret
        self._fernet = self._create_fernet()

    def _create_fernet(self) -> Fernet:
        """Create Fernet instance from secret key"""
        # Use PBKDF2 to derive a proper key from the secret
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b"firefly_salt_v1",  # In production, use a proper salt
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(settings.SECRET_KEY.encode()))
        return Fernet(key)

    def encrypt(self, plaintext: str) -> str:
        """Encrypt sensitive text data"""
        if not plaintext:
            return ""
        encrypted = self._fernet.encrypt(plaintext.encode())
        return base64.urlsafe_b64encode(encrypted).decode()

    def decrypt(self, ciphertext: str) -> str:
        """Decrypt encrypted text data"""
        if not ciphertext:
            return ""
        try:
            encrypted = base64.urlsafe_b64decode(ciphertext.encode())
            decrypted = self._fernet.decrypt(encrypted)
            return decrypted.decode()
        except Exception:
            return ""

    @staticmethod
    def hash_sensitive_data(data: str) -> str:
        """Create one-way hash for sensitive data (for searching)"""
        return hashlib.sha256(
            (data + settings.SECRET_KEY).encode()
        ).hexdigest()


# Singleton instance
encryption_service = EncryptionService()
