#!/usr/bin/env python3
"""
Cryptographic signing functionality for the audit trail integrity system.

This module handles the cryptographic signing and verification of log files
to ensure their integrity and authenticity.
"""

import logging
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature

from config import Config
from log_collector import AuditLogger

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT
)
logger = logging.getLogger('audit_trail')

class CryptographicProcessor:
    """Handles cryptographic operations for log integrity."""
    
    @classmethod
    def generate_keys(cls) -> Tuple[bool, str]:
        """Generate RSA key pair for signing and verification.
        
        Returns:
            Tuple containing (success_flag, message)
        """
        try:
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=Config.RSA_KEY_SIZE
            )
            
            # Get the public key
            public_key = private_key.public_key()
            
            # Serialize the private key
            private_pem = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            # Serialize the public key
            public_pem = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # Save the keys to files
            with open(Config.get_private_key_path(), 'wb') as f:
                f.write(private_pem)
                
            with open(Config.get_public_key_path(), 'wb') as f:
                f.write(public_pem)
                
            return True, "Keys generated successfully."
        except Exception as e:
            return False, f"Error generating keys: {e}"
    
    @classmethod
    def calculate_sha256(cls, file_path: Union[str, Path]) -> Optional[str]:
        """Calculate SHA-256 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Hexadecimal string representation of the hash, or None if error
        """
        try:
            import hashlib
            
            if isinstance(file_path, str):
                file_path = Path(file_path)
                
            if not file_path.exists():
                logger.error(f"File not found for hashing: {file_path}")
                return None
                
            # Calculate hash
            sha256_hash = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
                    
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash: {e}")
            return None
    
    @classmethod
    def save_hash(cls, hash_value: str, hash_path: Path) -> bool:
        """Save a hash value to a file.
        
        Args:
            hash_value: Hash value to save
            hash_path: Path to save the hash to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            with open(hash_path, 'w') as f:
                f.write(hash_value)
                
            logger.info(f"SHA-256 hash saved to: {hash_path}")
            return True
        except Exception as e:
            logger.error(f"Error saving hash: {e}")
            return False
    
    @classmethod
    def sign_file(cls, file_path: Union[str, Path]) -> Optional[Path]:
        """Sign a file using the private key.
        
        Args:
            file_path: Path to the file to sign
            
        Returns:
            Path to the signature file if successful, None otherwise
        """
        try:
            # Ensure file_path is a Path object
            if isinstance(file_path, str):
                file_path = Path(file_path)
                
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return None
                
            # Read the file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
                
            # Sign the file content
            private_key = cls._load_private_key()
            if not private_key:
                return None
                
            # Sign with PKCS1v15 padding
            signature = private_key.sign(
                file_content,
                padding.PKCS1v15(),
                hashes.SHA256()
            )
            
            # Save the signature to a file
            signature_path = Path(f"{file_path}{Config.SIGNATURE_FILE_EXTENSION}")
            with open(signature_path, 'wb') as f:
                f.write(signature)
                
            logger.info(f"File signed successfully. Signature saved to: {signature_path}")
            logger.info(f"File size: {len(file_content)} bytes")
            logger.info(f"Signature size: {len(signature)} bytes")
            
            # Immediate verification to confirm the signature works
            verification_result = cls.verify_file(file_path, signature_path)
            if verification_result:
                logger.info(f"Immediate verification after signing: SUCCESS")
            else:
                logger.warning(f"Immediate verification after signing: FAILED - Check cryptographic implementation")
                
            return signature_path
        except Exception as e:
            logger.error(f"Error signing file: {e}")
            return None
            
    @classmethod
    def verify_file(cls, file_path: Union[str, Path], signature_path: Union[str, Path]) -> bool:
        """Verify a file's signature.
        
        Args:
            file_path: Path to the file to verify
            signature_path: Path to the signature file
            
        Returns:
            True if the signature is valid, False otherwise
        """
        try:
            # Ensure paths are Path objects
            if isinstance(file_path, str):
                file_path = Path(file_path)
            if isinstance(signature_path, str):
                signature_path = Path(signature_path)
                
            # Check if files exist
            if not file_path.exists():
                logger.error(f"File not found: {file_path}")
                return False
            if not signature_path.exists():
                logger.error(f"Signature file not found: {signature_path}")
                return False
                
            # Read the file and signature
            with open(file_path, 'rb') as f:
                file_content = f.read()
            with open(signature_path, 'rb') as f:
                signature = f.read()
                
            # Log file sizes for debugging
            logger.info(f"File size: {len(file_content)} bytes")
            logger.info(f"Signature size: {len(signature)} bytes")
                
            # Verify the signature
            public_key = cls._load_public_key()
            if not public_key:
                return False
                
            # Verify with PKCS1v15 padding
            try:
                public_key.verify(
                    signature,
                    file_content,
                    padding.PKCS1v15(),
                    hashes.SHA256()
                )
                logger.info(f"Signature verified successfully for {file_path}")
                return True
            except InvalidSignature as e:
                logger.error(f"Signature verification FAILED: {e} for {file_path}")
                return False
        except Exception as e:
            logger.error(f"Error verifying file: {e}")
            return False

    @staticmethod
    def _load_private_key() -> Optional[Any]:
        """Load the private key from the file."""
        private_key_path = Config.get_private_key_path()
        if not private_key_path.exists():
            logger.error(f"Private key not found at {private_key_path}")
            return None
            
        try:
            with open(private_key_path, "rb") as key_file:
                private_key = serialization.load_pem_private_key(
                    key_file.read(),
                    password=None
                )
            return private_key
        except Exception as e:
            logger.error(f"Error loading private key: {e}")
            return None

    @staticmethod
    def _load_public_key() -> Optional[Any]:
        """Load the public key from the file."""
        public_key_path = Config.get_public_key_path()
        if not public_key_path.exists():
            logger.error(f"Public key not found at {public_key_path}")
            return None
            
        try:
            with open(public_key_path, "rb") as key_file:
                public_key = serialization.load_pem_public_key(key_file.read())
            return public_key
        except Exception as e:
            logger.error(f"Error loading public key: {e}")
            return None


class AuditTrailProcessor:
    """Processes audit trail logs for signing and verification."""
    
    def __init__(self):
        """Initialize the audit trail processor."""
        self.audit_logger = AuditLogger()
        self.crypto = CryptographicProcessor
        
    def log_api_event(self, api_endpoint: str, user_id: str, request_data: Dict, response_data: Dict, status_code: int):
        """Log an API event with all relevant details.
        
        Args:
            api_endpoint: The API endpoint that was accessed
            user_id: ID of the user who made the request
            request_data: Dictionary containing request data
            response_data: Dictionary containing response data
            status_code: HTTP status code of the response
            
        Returns:
            The ID of the logged event
        """
        details = {
            "api_endpoint": api_endpoint,
            "request_data": self.audit_logger._sanitize_data(request_data),
            "response_status": status_code,
            "response_data": self.audit_logger._sanitize_data(response_data)
        }
        return self.audit_logger.log_event("api_request", details, user_id)
    
    def process_daily_logs(self):
        """Process, sign, and store logs for the current day.
        
        Returns:
            True if successful, False otherwise
        """
        log_path = self.audit_logger.log_path
        
        # Ensure all log data is flushed to disk
        for handler in logging.getLogger().handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()
        
        # Create a snapshot copy of the log file for signing
        snapshot_log_path = Path(f"{log_path}.snapshot")
        shutil.copy2(log_path, snapshot_log_path)
        
        logger.info(f"Created snapshot of log file for signing: {snapshot_log_path}")
        
        # 1. Calculate hash of the snapshot
        hash_value = self.crypto.calculate_sha256(snapshot_log_path)
        if not hash_value:
            return False
            
        # 2. Save hash to file
        hash_path = Path(f"{snapshot_log_path}{Config.HASH_FILE_EXTENSION}")
        if not self.crypto.save_hash(hash_value, hash_path):
            return False
            
        # 3. Sign the snapshot log file
        signature_path = self.crypto.sign_file(snapshot_log_path)
        if not signature_path:
            return False
            
        # Store the paths for verification
        self.snapshot_log_path = snapshot_log_path
        self.signature_path = signature_path
        
        success = True
        if success:
            logger.info("Log processing succeeded")
        else:
            logger.info("Log processing failed")
        return success
    
    def verify_logs(self, log_path: Path = None, signature_path: Path = None) -> bool:
        """Verify the integrity of a log file using its signature.
        
        Args:
            log_path: Path to the log file to verify
            signature_path: Path to the signature file
            
        Returns:
            True if verification is successful, False otherwise
        """
        # Use stored paths if not provided
        if log_path is None and hasattr(self, 'snapshot_log_path'):
            log_path = self.snapshot_log_path
        if signature_path is None and hasattr(self, 'signature_path'):
            signature_path = self.signature_path
            
        # Ensure log_path is a Path object
        if isinstance(log_path, str):
            log_path = Path(log_path)
            
        # Make sure we have the absolute path if log_path doesn't include the directory
        if not log_path.is_absolute() and str(log_path).count('/') == 0:
            log_path = Config.LOG_DIR / log_path
            
        if not log_path.exists():
            logger.error(f"Log file not found: {log_path}")
            return False
            
        # If signature path not provided, try to find it
        if signature_path is None:
            signature_path = Config.SIGNATURES_DIR / f"{log_path.name}{Config.SIGNATURE_FILE_EXTENSION}"
            
        if not signature_path.exists():
            logger.error(f"Signature file not found: {signature_path}")
            return False
                
        # Verify the file
        result = self.crypto.verify_file(log_path, signature_path)
        
        if result:
            logger.info(f"Verification successful: The log file {log_path.name} is authentic and unmodified")
        else:
            logger.error(f"Verification failed: The log file {log_path.name} may have been tampered with")
            
        return result
