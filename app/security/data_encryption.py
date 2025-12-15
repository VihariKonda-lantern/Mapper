"""Data encryption utilities for sensitive data at rest."""
from typing import Any, Dict, Optional
from pathlib import Path
import base64
import json

try:
    from cryptography.fernet import Fernet
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    Fernet = None  # type: ignore

from core.exceptions import FileError


class DataEncryptor:
    """Encrypt/decrypt sensitive data."""
    
    def __init__(self, key: Optional[bytes] = None, password: Optional[str] = None):
        """
        Initialize encryptor.
        
        Args:
            key: Encryption key (Fernet key)
            password: Password to derive key from
        """
        if not CRYPTO_AVAILABLE:
            raise FileError("cryptography library not available", error_code="CRYPTO_NOT_AVAILABLE")
        
        if key:
            self.key = key
        elif password:
            self.key = self._derive_key(password)
        else:
            # Generate new key
            self.key = Fernet.generate_key()
        
        self.cipher = Fernet(self.key)
    
    def _derive_key(self, password: str, salt: Optional[bytes] = None) -> bytes:
        """Derive encryption key from password."""
        if salt is None:
            salt = b'default_salt_16b'  # In production, use random salt
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt(self, data: bytes) -> bytes:
        """
        Encrypt data.
        
        Args:
            data: Data to encrypt
        
        Returns:
            Encrypted data
        """
        return self.cipher.encrypt(data)
    
    def decrypt(self, encrypted_data: bytes) -> bytes:
        """
        Decrypt data.
        
        Args:
            encrypted_data: Encrypted data
        
        Returns:
            Decrypted data
        """
        return self.cipher.decrypt(encrypted_data)
    
    def encrypt_string(self, text: str) -> str:
        """Encrypt string and return base64-encoded result."""
        encrypted = self.encrypt(text.encode('utf-8'))
        return base64.b64encode(encrypted).decode('utf-8')
    
    def decrypt_string(self, encrypted_text: str) -> str:
        """Decrypt base64-encoded string."""
        encrypted_bytes = base64.b64decode(encrypted_text.encode('utf-8'))
        decrypted = self.decrypt(encrypted_bytes)
        return decrypted.decode('utf-8')
    
    def encrypt_file(self, input_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Encrypt file.
        
        Args:
            input_path: Path to input file
            output_path: Path to output file (default: input_path + .encrypted)
        
        Returns:
            Path to encrypted file
        """
        if output_path is None:
            output_path = input_path.with_suffix(input_path.suffix + '.encrypted')
        
        with open(input_path, 'rb') as f:
            data = f.read()
        
        encrypted = self.encrypt(data)
        
        with open(output_path, 'wb') as f:
            f.write(encrypted)
        
        return output_path
    
    def decrypt_file(self, input_path: Path, output_path: Optional[Path] = None) -> Path:
        """
        Decrypt file.
        
        Args:
            input_path: Path to encrypted file
            output_path: Path to output file
        
        Returns:
            Path to decrypted file
        """
        if output_path is None:
            output_path = input_path.with_suffix('').with_suffix(
                input_path.suffix.replace('.encrypted', '')
            )
        
        with open(input_path, 'rb') as f:
            encrypted = f.read()
        
        decrypted = self.decrypt(encrypted)
        
        with open(output_path, 'wb') as f:
            f.write(decrypted)
        
        return output_path
    
    def encrypt_dict(self, data: Dict[str, Any]) -> str:
        """Encrypt dictionary."""
        json_str = json.dumps(data)
        return self.encrypt_string(json_str)
    
    def decrypt_dict(self, encrypted_text: str) -> Dict[str, Any]:
        """Decrypt dictionary."""
        json_str = self.decrypt_string(encrypted_text)
        return json.loads(json_str)
    
    def save_key(self, key_path: Path) -> None:
        """Save encryption key to file."""
        with open(key_path, 'wb') as f:
            f.write(self.key)
    
    @classmethod
    def load_key(cls, key_path: Path) -> 'DataEncryptor':
        """Load encryption key from file."""
        with open(key_path, 'rb') as f:
            key = f.read()
        return cls(key=key)

