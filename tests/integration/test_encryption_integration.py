"""
Integration tests for encryption module.
"""

import pytest
from pathlib import Path
import tempfile


def test_encryption_import():
    """Test encryption module can be imported."""
    try:
        from app.crypto.encryption import EncryptionManager, KeyManager
        assert EncryptionManager is not None
        assert KeyManager is not None
    except ImportError:
        pytest.skip("Cryptography not installed")


def test_encryption_basic_workflow():
    """Test basic encryption workflow."""
    try:
        from app.crypto.encryption import EncryptionManager
    except ImportError:
        pytest.skip("Cryptography not installed")
        return

    # Create encryption manager with password
    manager = EncryptionManager(password="test_password_123")

    # Test data encryption
    plaintext = b"This is a test message for encryption"
    nonce, ciphertext = manager.encrypt_data(plaintext)

    assert len(nonce) == 12  # AES-GCM nonce size
    assert ciphertext != plaintext
    assert len(ciphertext) > 0

    # Test decryption
    decrypted = manager.decrypt_data(nonce, ciphertext)
    assert decrypted == plaintext
