#!/usr/bin/env python3
# audit_trail.py
# Ensures system, application, and API logs are cryptographically signed
# and stored immutably to guarantee their authenticity, integrity, and non-repudiation

import logging
import hashlib
import os
import json
import datetime
import time
import uuid
import boto3
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple, Union
from botocore.exceptions import ClientError
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.exceptions import InvalidSignature

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("audit_trail")

# Configuration
class Config:
    # Paths and file naming
    LOG_DIR = Path("logs")
    SIGNATURES_DIR = Path("signatures")
    LOG_FILENAME_BASE = "api_log"
    LOG_FILE_EXTENSION = ".log"
    HASH_FILE_EXTENSION = ".sha256"
    SIGNATURE_FILE_EXTENSION = ".sig"
    
    # Keys for cryptographic signing
    KEYS_DIR = Path("keys")
    PRIVATE_KEY_FILENAME = "private_key.pem"
    PUBLIC_KEY_FILENAME = "public_key.pem"
    
    # AWS S3 configuration - use simulation mode by default to avoid errors
    S3_SIMULATION_MODE = True
    S3_BUCKET_NAME = "audit-trail-archive"  # This would be your actual bucket name in production
    S3_PREFIX = "audit-logs/"
    S3_STORAGE_CLASS = "GLACIER"  # or "DEEP_ARCHIVE" for longer retention
    
    # Log retention and verification
    VERIFICATION_INTERVAL_DAYS = 30  # Verify logs every 30 days
    
    @classmethod
    def ensure_directories(cls):
        """Ensure all necessary directories exist."""
        cls.LOG_DIR.mkdir(exist_ok=True, parents=True)
        cls.SIGNATURES_DIR.mkdir(exist_ok=True, parents=True)
        cls.KEYS_DIR.mkdir(exist_ok=True, parents=True)
        
    @classmethod
    def get_private_key_path(cls) -> Path:
        return cls.KEYS_DIR / cls.PRIVATE_KEY_FILENAME
    
    @classmethod
    def get_public_key_path(cls) -> Path:
        return cls.KEYS_DIR / cls.PUBLIC_KEY_FILENAME


class AuditLogger:
    """Handles the generation and management of secure audit logs."""
    
    def __init__(self):
        Config.ensure_directories()
        self.log_path = self._get_log_path()
        self.file_handler = None
        self._setup_file_handler()
        
    def _get_log_path(self) -> Path:
        """Generate a log path using the current date."""
        today = datetime.date.today().strftime("%Y-%m-%d")
        return Config.LOG_DIR / f"{Config.LOG_FILENAME_BASE}_{today}{Config.LOG_FILE_EXTENSION}"
    
    def _setup_file_handler(self):
        """Set up a file handler for the logger."""
        self.file_handler = logging.FileHandler(self.log_path)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        self.file_handler.setFormatter(file_formatter)
        
        # Remove any existing file handlers and add our new handler
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            if isinstance(handler, logging.FileHandler):
                root_logger.removeHandler(handler)
        root_logger.addHandler(self.file_handler)
    
    def finalize_log(self):
        """Flush and remove the file handler to finalize the log file."""
        if self.file_handler:
            self.file_handler.flush()
            logging.getLogger().removeHandler(self.file_handler)
            self.file_handler.close()
            self.file_handler = None
            logger.info(f"Log file {self.log_path} finalized for signing.")
    
    def log_event(self, event_type: str, details: Dict[str, Any], user_id: Optional[str] = None):
        """Log an audit event with a unique event ID."""
        event_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        event_data = {
            "event_id": event_id,
            "timestamp": timestamp,
            "event_type": event_type,
            "details": details
        }
        
        if user_id:
            event_data["user_id"] = user_id
            
        logger.info(f"AUDIT: {json.dumps(event_data)}")
        return event_id


class CryptographicProcessor:
    """Handles cryptographic operations for log integrity."""
    
    @staticmethod
    def generate_keys() -> Tuple[bool, str]:
        """Generate RSA key pair if they don't exist."""
        private_key_path = Config.get_private_key_path()
        public_key_path = Config.get_public_key_path()
        
        # Check if keys already exist
        if private_key_path.exists() and public_key_path.exists():
            return True, "Keys already exist"
        
        try:
            # Import cryptography library
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            
            # Serialize private key
            private_key_bytes = private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            # Serialize public key
            public_key = private_key.public_key()
            public_key_bytes = public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            
            # Write keys to files
            with open(private_key_path, 'wb') as f:
                f.write(private_key_bytes)
                
            with open(public_key_path, 'wb') as f:
                f.write(public_key_bytes)
                
            return True, "Keys generated successfully"
            
        except Exception as e:
            return False, f"Error generating keys: {str(e)}"
    
    @staticmethod
    def calculate_sha256(filepath: Path) -> Optional[str]:
        """Calculate the SHA-256 hash of a file."""
        if not filepath.exists():
            logger.error(f"File not found for hashing: {filepath}")
            return None
            
        sha256_hash = hashlib.sha256()
        try:
            with open(filepath, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.error(f"Error calculating hash for {filepath}: {str(e)}")
            return None
    
    @staticmethod
    def save_hash(hash_value: str, hash_filepath: Path) -> bool:
        """Save the hash value to a file."""
        try:
            with open(hash_filepath, "w") as f:
                f.write(hash_value)
            logger.info(f"SHA-256 hash saved to: {hash_filepath}")
            return True
        except Exception as e:
            logger.error(f"Error saving hash to {hash_filepath}: {str(e)}")
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
            from cryptography.hazmat.primitives import serialization
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
            from cryptography.hazmat.primitives import serialization
            with open(public_key_path, "rb") as key_file:
                public_key = serialization.load_pem_public_key(key_file.read())
            return public_key
        except Exception as e:
            logger.error(f"Error loading public key: {e}")
            return None


class StorageProcessor:
    """Handles secure storage of logs and signatures."""
    
    def __init__(self):
        self.s3_client = boto3.client('s3')
    
    def upload_to_s3(self, local_path: Path, key_prefix: str = "") -> bool:
        """Upload a file to S3 with Glacier storage class."""
        if not local_path.exists():
            logger.error(f"File not found for upload: {local_path}")
            return False
            
        try:
            s3_key = f"{Config.S3_PREFIX}{key_prefix}{local_path.name}"
            
            if Config.S3_SIMULATION_MODE:
                logger.info(f"SIMULATION: Would upload {local_path} to s3://{Config.S3_BUCKET_NAME}/{s3_key}")
                logger.info(f"SIMULATION: Using storage class: {Config.S3_STORAGE_CLASS}")
                return True
            
            self.s3_client.upload_file(
                str(local_path),
                Config.S3_BUCKET_NAME,
                s3_key,
                ExtraArgs={
                    'StorageClass': Config.S3_STORAGE_CLASS,
                    'ServerSideEncryption': 'AES256'
                }
            )
            
            logger.info(f"Successfully uploaded {local_path} to s3://{Config.S3_BUCKET_NAME}/{s3_key}")
            return True
            
        except ClientError as e:
            logger.error(f"Error uploading to S3: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error during S3 upload: {str(e)}")
            return False


class AuditTrailProcessor:
    """Main class that orchestrates the audit trail process."""
    
    def __init__(self):
        self.audit_logger = AuditLogger()
        self.crypto = CryptographicProcessor()
        self.storage = StorageProcessor()
        
    def log_api_event(self, api_endpoint: str, user_id: str, request_data: Dict, 
                      response_data: Dict, status_code: int):
        """Log an API event with all relevant details."""
        details = {
            "api_endpoint": api_endpoint,
            "request_data": self._sanitize_data(request_data),
            "response_status": status_code,
            "response_data": self._sanitize_data(response_data)
        }
        
        return self.audit_logger.log_event("api_request", details, user_id)
    
    def _sanitize_data(self, data: Dict) -> Dict:
        """Remove sensitive information from data before logging."""
        sanitized = data.copy() if data else {}
        sensitive_keys = ['password', 'token', 'secret', 'key', 'authorization',
                          'credit_card', 'ssn', 'social_security']
        
        def _redact_sensitive(obj):
            if isinstance(obj, dict):
                for k, v in list(obj.items()):
                    if any(sensitive in k.lower() for sensitive in sensitive_keys):
                        obj[k] = "[REDACTED]"
                    else:
                        _redact_sensitive(v)
            elif isinstance(obj, list):
                for item in obj:
                    _redact_sensitive(item)
        
        _redact_sensitive(sanitized)
        return sanitized
    
    def process_daily_logs(self):
        """Process, sign, and store logs for the current day."""
        log_path = self.audit_logger.log_path
        
        # Ensure all log data is flushed to disk
        for handler in logging.getLogger().handlers:
            if isinstance(handler, logging.FileHandler):
                handler.flush()
        
        # Create a snapshot copy of the log file for signing
        import shutil
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
            
        # 4. Upload log, hash, and signature to S3
        date_prefix = datetime.date.today().strftime("%Y/%m/%d/")
        upload_results = [
            self.storage.upload_to_s3(snapshot_log_path, date_prefix),
            self.storage.upload_to_s3(hash_path, date_prefix),
            self.storage.upload_to_s3(signature_path, date_prefix)
        ]
        
        # Store the paths for verification
        self.snapshot_log_path = snapshot_log_path
        self.signature_path = signature_path
        
        success = all(upload_results)
        if success:
            logger.info("Log processing succeeded")
        else:
            logger.info("Log processing failed")
        return success
    
    def verify_logs(self, log_path: Path = None, signature_path: Path = None) -> bool:
        """Verify the integrity of a log file using its signature."""
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


def generate_sample_logs():
    """Generate sample logs for demonstration purposes."""
    processor = AuditTrailProcessor()
    
    for _ in range(10):
        endpoint = f"/api/users/{uuid.uuid4()}"
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        
        request_data = {
            "action": "update",
            "fields": {"name": "John Doe", "email": "john@example.com"},
            "token": "secret_token_123"
        }
        
        response_data = {
            "status": "success",
            "updated_fields": ["name", "email"]
        }
        
        processor.log_api_event(endpoint, user_id, request_data, response_data, 200)
        time.sleep(0.1)
    
    # Close the file handler to ensure all data is written to disk
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.FileHandler):
            handler.flush()
            handler.close()
    
    # Process the generated logs
    log_path = processor.audit_logger.log_path
    result = processor.process_daily_logs()
    
    # Return both the log path and the processing result, as well as the processor instance
    return log_path, result, processor


def verify_sample_logs(log_path: Path):
    """Verify the sample logs."""
    processor = AuditTrailProcessor()
    logger.info(f"Verifying log file: {log_path}")
    signature_path = Config.SIGNATURES_DIR / f"{log_path.name}{Config.SIGNATURE_FILE_EXTENSION}"
    logger.info(f"Using signature file: {signature_path}")
    
    if not log_path.exists():
        logger.error(f"Log file does not exist: {log_path}")
        return False
    if not signature_path.exists():
        logger.error(f"Signature file does not exist: {signature_path}")
        return False
        
    return processor.verify_logs(log_path, signature_path)


if __name__ == "__main__":
    # Generate keys if they don't exist
    key_result, key_message = CryptographicProcessor.generate_keys()
    if not key_result:
        logger.error(f"Key generation failed: {key_message}")
        exit(1)
        
    # Generate and process sample logs
    logger.info("Generating sample logs...")
    log_path, process_result, processor = generate_sample_logs()
    
    if not process_result:
        logger.error("Failed to process logs properly")
        exit(1)
    
    # Use the snapshot path from the processor for verification
    logger.info("Verifying logs...")
    verify_result = processor.verify_logs(processor.snapshot_log_path, processor.signature_path)
    
    # Final status
    if verify_result:
        logger.info("Audit trail integrity verification successful")
    else:
        logger.error("Audit trail integrity verification failed")
        
    logger.info("Audit trail processing complete")
    
    # Clean up snapshot files
    import glob
    for snapshot_file in glob.glob("logs/*.snapshot*"):
        try:
            Path(snapshot_file).unlink()
            logger.debug(f"Removed temporary file: {snapshot_file}")
        except Exception as e:
            logger.warning(f"Failed to remove temporary file {snapshot_file}: {e}")
