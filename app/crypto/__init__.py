"""
Encryption and cryptography modules.

AES-256 encryption, key management, and secure backup functionality.
"""

try:
    from app.crypto.encryption import EncryptionManager, KeyManager  # noqa: F401

    __all__ = ["EncryptionManager", "KeyManager"]
except ImportError:
    # cryptography not installed
    __all__ = []
