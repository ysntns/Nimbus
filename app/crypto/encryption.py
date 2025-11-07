"""
Encryption Module - AES-256 encryption for backup files

Provides secure encryption and decryption functionality using AES-256-GCM.
"""

import os
import hashlib
from pathlib import Path
from typing import Optional, Tuple
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
from loguru import logger


class EncryptionManager:
    """Manages encryption and decryption operations."""

    # AES-256 requires 32 bytes key
    KEY_SIZE = 32

    # PBKDF2 iterations for key derivation
    KDF_ITERATIONS = 100000

    # Nonce size for AES-GCM
    NONCE_SIZE = 12

    def __init__(self, password: Optional[str] = None, key_file: Optional[Path] = None):
        """Initialize encryption manager.

        Args:
            password: Password for encryption (will derive key)
            key_file: Path to key file (alternative to password)
        """
        self.key: Optional[bytes] = None

        if password:
            # Derive key from password
            self.key = self._derive_key_from_password(password)
        elif key_file and key_file.exists():
            # Load key from file
            self.key = self._load_key_from_file(key_file)

        logger.info("Encryption manager initialized")

    def _derive_key_from_password(self, password: str, salt: Optional[bytes] = None) -> bytes:
        """Derive encryption key from password using PBKDF2.

        Args:
            password: User password
            salt: Salt for key derivation (generated if not provided)

        Returns:
            Derived encryption key
        """
        if salt is None:
            salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=self.KEY_SIZE,
            salt=salt,
            iterations=self.KDF_ITERATIONS,
            backend=default_backend()
        )

        key = kdf.derive(password.encode('utf-8'))
        logger.debug(f"Key derived from password using PBKDF2 ({self.KDF_ITERATIONS} iterations)")

        return key

    def _load_key_from_file(self, key_file: Path) -> bytes:
        """Load encryption key from file.

        Args:
            key_file: Path to key file

        Returns:
            Encryption key
        """
        try:
            with open(key_file, 'rb') as f:
                key = f.read()

            if len(key) != self.KEY_SIZE:
                raise ValueError(f"Invalid key size: {len(key)} bytes (expected {self.KEY_SIZE})")

            logger.info(f"Encryption key loaded from {key_file}")
            return key

        except Exception as e:
            logger.error(f"Failed to load key from {key_file}: {e}")
            raise

    def save_key_to_file(self, key_file: Path, key: Optional[bytes] = None):
        """Save encryption key to file.

        Args:
            key_file: Path to save key
            key: Key to save (uses current key if not provided)
        """
        key_to_save = key or self.key

        if not key_to_save:
            raise ValueError("No key available to save")

        try:
            key_file.parent.mkdir(parents=True, exist_ok=True)

            # Write key with restricted permissions
            with open(key_file, 'wb') as f:
                f.write(key_to_save)

            # Set file permissions to 600 (read/write for owner only)
            os.chmod(key_file, 0o600)

            logger.info(f"Encryption key saved to {key_file}")

        except Exception as e:
            logger.error(f"Failed to save key to {key_file}: {e}")
            raise

    def generate_key(self) -> bytes:
        """Generate a new random encryption key.

        Returns:
            Generated encryption key
        """
        key = os.urandom(self.KEY_SIZE)
        self.key = key
        logger.info("New encryption key generated")
        return key

    def encrypt_data(self, data: bytes, associated_data: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """Encrypt data using AES-256-GCM.

        Args:
            data: Data to encrypt
            associated_data: Additional authenticated data (not encrypted)

        Returns:
            Tuple of (nonce, ciphertext)
        """
        if not self.key:
            raise ValueError("No encryption key available")

        # Generate random nonce
        nonce = os.urandom(self.NONCE_SIZE)

        # Create cipher
        cipher = AESGCM(self.key)

        # Encrypt data
        ciphertext = cipher.encrypt(nonce, data, associated_data)

        logger.debug(f"Encrypted {len(data)} bytes of data")

        return nonce, ciphertext

    def decrypt_data(self, nonce: bytes, ciphertext: bytes, associated_data: Optional[bytes] = None) -> bytes:
        """Decrypt data using AES-256-GCM.

        Args:
            nonce: Nonce used for encryption
            ciphertext: Encrypted data
            associated_data: Additional authenticated data

        Returns:
            Decrypted data
        """
        if not self.key:
            raise ValueError("No encryption key available")

        # Create cipher
        cipher = AESGCM(self.key)

        # Decrypt data
        try:
            plaintext = cipher.decrypt(nonce, ciphertext, associated_data)
            logger.debug(f"Decrypted {len(plaintext)} bytes of data")
            return plaintext

        except Exception as e:
            logger.error(f"Decryption failed: {e}")
            raise ValueError("Decryption failed - invalid key or corrupted data")

    def encrypt_file(self, input_file: Path, output_file: Path, chunk_size: int = 64 * 1024):
        """Encrypt a file.

        Args:
            input_file: Path to input file
            output_file: Path to output encrypted file
            chunk_size: Size of chunks to read/write
        """
        if not self.key:
            raise ValueError("No encryption key available")

        try:
            # Generate nonce
            nonce = os.urandom(self.NONCE_SIZE)

            # Create cipher
            cipher = AESGCM(self.key)

            # Read input file
            with open(input_file, 'rb') as f:
                plaintext = f.read()

            # Encrypt
            ciphertext = cipher.encrypt(nonce, plaintext, None)

            # Write output file (nonce + ciphertext)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'wb') as f:
                f.write(nonce)
                f.write(ciphertext)

            logger.info(f"Encrypted file: {input_file} -> {output_file}")

        except Exception as e:
            logger.error(f"File encryption failed: {e}")
            raise

    def decrypt_file(self, input_file: Path, output_file: Path):
        """Decrypt a file.

        Args:
            input_file: Path to encrypted file
            output_file: Path to output decrypted file
        """
        if not self.key:
            raise ValueError("No encryption key available")

        try:
            # Read encrypted file
            with open(input_file, 'rb') as f:
                nonce = f.read(self.NONCE_SIZE)
                ciphertext = f.read()

            # Create cipher
            cipher = AESGCM(self.key)

            # Decrypt
            plaintext = cipher.decrypt(nonce, ciphertext, None)

            # Write output file
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'wb') as f:
                f.write(plaintext)

            logger.info(f"Decrypted file: {input_file} -> {output_file}")

        except Exception as e:
            logger.error(f"File decryption failed: {e}")
            raise

    def get_file_hash(self, file_path: Path) -> str:
        """Calculate SHA-256 hash of a file.

        Args:
            file_path: Path to file

        Returns:
            Hex string of file hash
        """
        sha256 = hashlib.sha256()

        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)

        return sha256.hexdigest()


class KeyManager:
    """Manages encryption keys and passwords."""

    def __init__(self, keys_dir: Path):
        """Initialize key manager.

        Args:
            keys_dir: Directory to store keys
        """
        self.keys_dir = keys_dir
        self.keys_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Key manager initialized (keys dir: {keys_dir})")

    def generate_and_save_key(self, key_name: str) -> Path:
        """Generate and save a new encryption key.

        Args:
            key_name: Name for the key file

        Returns:
            Path to saved key file
        """
        manager = EncryptionManager()
        key = manager.generate_key()

        key_file = self.keys_dir / f"{key_name}.key"
        manager.save_key_to_file(key_file, key)

        logger.info(f"Generated and saved key: {key_file}")
        return key_file

    def list_keys(self) -> list:
        """List all available keys.

        Returns:
            List of key file paths
        """
        keys = list(self.keys_dir.glob("*.key"))
        logger.debug(f"Found {len(keys)} keys in {self.keys_dir}")
        return keys

    def delete_key(self, key_name: str):
        """Delete an encryption key.

        Args:
            key_name: Name of key to delete
        """
        key_file = self.keys_dir / f"{key_name}.key"

        if key_file.exists():
            key_file.unlink()
            logger.info(f"Deleted key: {key_file}")
        else:
            logger.warning(f"Key not found: {key_file}")
