#!/usr/bin/env python3
"""
AWS S3 upload functionality for the audit trail integrity system.

This module handles the secure upload of log files, hash files, and signatures to AWS S3.
"""

import logging
import datetime
from pathlib import Path
from typing import Optional, Union

import boto3
from botocore.exceptions import ClientError

from config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT
)
logger = logging.getLogger('audit_trail')

class StorageProcessor:
    """Handles storage operations for audit logs and signatures."""
    
    def __init__(self, simulate: bool = True):
        """Initialize the storage processor.
        
        Args:
            simulate: If True, simulate uploads instead of actually performing them
        """
        self.simulate = simulate
        self.s3_client = self._get_s3_client()
    
    def _get_s3_client(self):
        """Get an S3 client."""
        try:
            return boto3.client('s3')
        except Exception as e:
            logger.error(f"Error creating S3 client: {e}")
            return None
    
    def upload_to_s3(self, file_path: Union[str, Path], date_prefix: str = "") -> bool:
        """Upload a file to S3.
        
        Args:
            file_path: Path to the file to upload
            date_prefix: Optional date prefix for the S3 key
            
        Returns:
            True if successful or simulated, False otherwise
        """
        if isinstance(file_path, str):
            file_path = Path(file_path)
            
        if not file_path.exists():
            logger.error(f"File not found for upload: {file_path}")
            return False
            
        # Construct the S3 key
        s3_key = f"{Config.S3_PREFIX}/{date_prefix}{file_path.name}"
        
        if self.simulate:
            logger.info(f"SIMULATION: Would upload {file_path} to s3://{Config.S3_BUCKET_NAME}/{s3_key}")
            logger.info(f"SIMULATION: Using storage class: {Config.S3_STORAGE_CLASS}")
            return True
            
        try:
            # Upload the file to S3
            self.s3_client.upload_file(
                str(file_path),
                Config.S3_BUCKET_NAME,
                s3_key,
                ExtraArgs={
                    'StorageClass': Config.S3_STORAGE_CLASS
                }
            )
            
            logger.info(f"Uploaded {file_path} to s3://{Config.S3_BUCKET_NAME}/{s3_key}")
            return True
        except ClientError as e:
            logger.error(f"Error uploading to S3: {e}")
            return False
    
    def download_from_s3(self, s3_key: str, local_path: Union[str, Path]) -> bool:
        """Download a file from S3.
        
        Args:
            s3_key: S3 key of the file to download
            local_path: Local path to save the file to
            
        Returns:
            True if successful, False otherwise
        """
        if isinstance(local_path, str):
            local_path = Path(local_path)
            
        # Ensure the parent directory exists
        local_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.simulate:
            logger.info(f"SIMULATION: Would download s3://{Config.S3_BUCKET_NAME}/{s3_key} to {local_path}")
            return True
            
        try:
            # Download the file from S3
            self.s3_client.download_file(
                Config.S3_BUCKET_NAME,
                s3_key,
                str(local_path)
            )
            
            logger.info(f"Downloaded s3://{Config.S3_BUCKET_NAME}/{s3_key} to {local_path}")
            return True
        except ClientError as e:
            logger.error(f"Error downloading from S3: {e}")
            return False
    
    def list_logs_for_date_range(self, start_date: datetime.date, end_date: datetime.date) -> list:
        """List all logs within a date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of S3 keys matching the date range
        """
        if self.simulate:
            logger.info(f"SIMULATION: Would list logs from {start_date} to {end_date}")
            return []
            
        try:
            # Construct the prefix for the date range
            prefix = f"{Config.S3_PREFIX}/"
            
            # List objects in the S3 bucket with the specified prefix
            response = self.s3_client.list_objects_v2(
                Bucket=Config.S3_BUCKET_NAME,
                Prefix=prefix
            )
            
            # Filter objects by date
            matching_keys = []
            for obj in response.get('Contents', []):
                key = obj['Key']
                # Extract the date from the key (assuming format YYYY/MM/DD/filename)
                key_parts = key.split('/')
                if len(key_parts) >= 4:
                    try:
                        year = int(key_parts[1])
                        month = int(key_parts[2])
                        day = int(key_parts[3])
                        log_date = datetime.date(year, month, day)
                        
                        if start_date <= log_date <= end_date:
                            matching_keys.append(key)
                    except (ValueError, IndexError):
                        continue
            
            return matching_keys
        except ClientError as e:
            logger.error(f"Error listing logs from S3: {e}")
            return []
