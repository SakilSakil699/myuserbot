"""
🔐 Session Vault — Locked Session Protocol
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Kya karta hai:
  • Session string ko Fernet (AES-128) se encrypt karta hai
  • Encryption key = SHA256(VAULT_KEY)
  • Stolen session sirf tumhare bot pe kaam karegi
  • Plain session kabhi disk pe plain text me nahi likhta

Kaise use kare:
  from core.session_vault import SessionVault
  vault = SessionVault()
  locked = vault.lock("BQACAg...plain_session")
  unlocked = vault.unlock(locked)
"""

import os
import base64
import hashlib

from cryptography.fernet import Fernet, InvalidToken


class SessionVaultError(Exception):
    """Vault-specific errors."""
    pass


class SessionVault:
    """Encrypts / decrypts session strings using VAULT_KEY."""

    # Fernet tokens always start with this prefix
    TOKEN_PREFIX = "gAAAAA"

    def __init__(self, master_key: str = None):
        """
        master_key: string used to derive encryption key.
        If None, reads VAULT_KEY from environment / config.
        """
        if master_key is None:
            # Try config first, then env
            try:
                from config import VAULT_KEY as _cfg_key
                master_key = _cfg_key
            except Exception:
                master_key = os.getenv("VAULT_KEY", "")

        if not master_key:
            raise SessionVaultError(
                "VAULT_KEY missing! Add it to .env file.\n"
                "Example: VAULT_KEY=my-strong-32-char-random-string-here"
            )

        if len(master_key) < 16:
            raise SessionVaultError(
                "VAULT_KEY too short! Use at least 32 characters.\n"
                "Generate one: openssl rand -base64 32"
            )

        self._master = master_key
        self._fernet = self._build_fernet(master_key)

    # ─────────────────────────────────────────────
    #  Key derivation
    # ─────────────────────────────────────────────
    @staticmethod
    def _build_fernet(master_key: str) -> Fernet:
        """Derive Fernet key from master key via SHA256."""
        digest = hashlib.sha256(master_key.encode("utf-8")).digest()
        fernet_key = base64.urlsafe_b64encode(digest)
        return Fernet(fernet_key)

    # ─────────────────────────────────────────────
    #  Core operations
    # ─────────────────────────────────────────────
    def lock(self, plain_session: str) -> str:
        """
        Encrypt a plain session string.
        Returns encrypted string (starts with 'gAAAAA').
        """
        if not plain_session:
            raise SessionVaultError("Cannot lock empty session.")

        # Already encrypted? Return as-is
        if self.is_locked(plain_session):
            return plain_session

        try:
            encrypted = self._fernet.encrypt(plain_session.encode("utf-8"))
            return encrypted.decode("utf-8")
        except Exception as e:
            raise SessionVaultError(f"Encryption failed: {e}")

    def unlock(self, encrypted_session: str) -> str:
        """
        Decrypt an encrypted session string.
        Raises SessionVaultError if tampered / wrong key.
        """
        if not encrypted_session:
            raise SessionVaultError("Cannot unlock empty session.")

        # Already plain? Return as-is
        if not self.is_locked(encrypted_session):
            return encrypted_session

        try:
            decrypted = self._fernet.decrypt(encrypted_session.encode("utf-8"))
            return decrypted.decode("utf-8")
        except InvalidToken:
            raise SessionVaultError(
                "Invalid token! Either:\n"
                "  1. Wrong VAULT_KEY\n"
                "  2. Session was tampered with\n"
                "  3. Different machine encrypted it"
            )
        except Exception as e:
            raise SessionVaultError(f"Decryption failed: {e}")

    # ─────────────────────────────────────────────
    #  Helpers
    # ─────────────────────────────────────────────
    @classmethod
    def is_locked(cls, value: str) -> bool:
        """Check if a string is a Fernet token."""
        return bool(value) and value.startswith(cls.TOKEN_PREFIX)

    @classmethod
    def auto_unlock(cls, value: str) -> str:
        """
        Smart helper — auto-detect and decrypt if needed.
        Useful in config.py for SESSION_STRING.
        """
        if not value:
            return value
        if not cls.is_locked(value):
            return value
        return cls().unlock(value)


# ─────────────────────────────────────────────
#  CLI test: python -m core.session_vault
# ─────────────────────────────────────────────
if __name__ == "__main__":
    import sys

    print("═" * 60)
    print("🔐 Session Vault — Test")
    print("═" * 60)

    try:
        vault = SessionVault()
    except SessionVaultError as e:
        print(f"❌ {e}")
        print("\n👉 Add VAULT_KEY to .env first:")
        print("   VAULT_KEY=" + base64.urlsafe_b64encode(os.urandom(32)).decode())
        sys.exit(1)

    # Generate test session
    test = "BQACAgUAAxkBAAIC_TEST_SESSION_STRING_1234567890"

    print(f"\n📝 Original : {test[:40]}...")

    locked = vault.lock(test)
    print(f"🔐 Locked   : {locked[:40]}...")

    unlocked = vault.unlock(locked)
    print(f"🔓 Unlocked : {unlocked[:40]}...")

    if unlocked == test:
        print("\n✅ SUCCESS — Vault working perfectly!")
    else:
        print("\n❌ FAILED — Data mismatch!")
        sys.exit(1)

    print("\n💡 Generate strong VAULT_KEY:")
    print(f"   {base64.urlsafe_b64encode(os.urandom(32)).decode()}")
    print("═" * 60)
