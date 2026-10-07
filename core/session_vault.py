"""
Locked Session Protocol
- Encrypts session string with VAULT_KEY
- Stolen session useless on other tools
- Auto-detects tampering
"""
import base64
import hashlib
import os
from cryptography.fernet import Fernet, InvalidToken

class SessionVault:
    def __init__(self, master_key=None):
        self.master_key = master_key or os.getenv("VAULT_KEY", "")
        if not self.master_key:
            raise ValueError("VAULT_KEY environment variable required!")
    
    def _fernet(self):
        key = base64.urlsafe_b64encode(
            hashlib.sha256(self.master_key.encode()).digest()
        )
        return Fernet(key)

    def lock(self, session_string):
        """Encrypt session string."""
        return self._fernet().encrypt(session_string.encode()).decode()

    def unlock(self, encrypted):
        """Decrypt session string. Raises if tampered."""
        try:
            return self._fernet().decrypt(encrypted.encode()).decode()
        except InvalidToken:
            raise ValueError("Session tampered or wrong VAULT_KEY!")