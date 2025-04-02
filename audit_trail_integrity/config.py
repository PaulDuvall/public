#!/usr/bin/env python3
"""
Configuration settings for the audit trail integrity system.

This module centralizes all configuration settings for the audit trail integrity system,
including file paths, AWS settings, and cryptographic parameters.
"""

import os
from pathlib import Path

class Config:
    """Configuration settings for the audit trail integrity system."""
    
    # Directory paths
    BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
    LOG_DIR = BASE_DIR / "logs"
    SIGNATURES_DIR = BASE_DIR / "signatures"
    KEYS_DIR = BASE_DIR / "keys"
    
    # Ensure directories exist
    LOG_DIR.mkdir(exist_ok=True)
    SIGNATURES_DIR.mkdir(exist_ok=True)
    KEYS_DIR.mkdir(exist_ok=True)
    
    # File extensions
    SIGNATURE_FILE_EXTENSION = ".sig"
    HASH_FILE_EXTENSION = ".sha256"
    
    # Key file names
    PRIVATE_KEY_FILENAME = "private_key.pem"
    PUBLIC_KEY_FILENAME = "public_key.pem"
    
    # AWS S3 settings
    S3_BUCKET_NAME = "audit-trail-archive"
    S3_PREFIX = "audit-logs"
    S3_STORAGE_CLASS = "GLACIER"
    
    # Logging settings
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_LEVEL = "INFO"
    LOG_FILENAME_FORMAT = "api_log_%Y-%m-%d.log"
    
    # Cryptographic settings
    RSA_KEY_SIZE = 2048
    HASH_ALGORITHM = "sha256"
    
    @classmethod
    def get_private_key_path(cls):
        """Get the path to the private key file."""
        return cls.KEYS_DIR / cls.PRIVATE_KEY_FILENAME
    
    @classmethod
    def get_public_key_path(cls):
        """Get the path to the public key file."""
        return cls.KEYS_DIR / cls.PUBLIC_KEY_FILENAME
    
    @classmethod
    def get_log_path_for_date(cls, date):
        """Get the log path for a specific date."""
        filename = date.strftime(cls.LOG_FILENAME_FORMAT)
        return cls.LOG_DIR / filename
