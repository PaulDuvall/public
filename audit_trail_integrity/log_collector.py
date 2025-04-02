#!/usr/bin/env python3
"""
Log collection functionality for the audit trail integrity system.

This module handles the collection and formatting of audit logs for API events.
"""

import json
import uuid
import logging
import datetime
from typing import Dict, Any, Optional
from pathlib import Path

from config import Config

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT
)
logger = logging.getLogger('audit_trail')

class AuditLogger:
    """Handles the collection and formatting of audit logs."""
    
    def __init__(self):
        """Initialize the audit logger."""
        self.log_path = self._get_log_path()
        self._setup_file_handler()
    
    def _get_log_path(self) -> Path:
        """Get the path to the log file for the current date."""
        today = datetime.date.today()
        return Config.get_log_path_for_date(today)
    
    def _setup_file_handler(self) -> None:
        """Set up the file handler for logging."""
        file_handler = logging.FileHandler(self.log_path)
        file_handler.setLevel(getattr(logging, Config.LOG_LEVEL))
        file_handler.setFormatter(logging.Formatter(Config.LOG_FORMAT))
        
        # Add the file handler to the logger
        logger.addHandler(file_handler)
    
    def log_event(self, event_type: str, details: Dict[str, Any], user_id: str) -> str:
        """Log an event with the specified details.
        
        Args:
            event_type: Type of the event (e.g., 'api_request', 'login')
            details: Dictionary containing event details
            user_id: ID of the user associated with the event
            
        Returns:
            The ID of the logged event
        """
        event_id = str(uuid.uuid4())
        timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
        
        log_entry = {
            "event_id": event_id,
            "timestamp": timestamp,
            "event_type": event_type,
            "details": details,
            "user_id": user_id
        }
        
        # Log the event
        logger.info(f"AUDIT: {json.dumps(log_entry)}")
        
        return event_id
    
    def _sanitize_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sanitize sensitive data in the log entry.
        
        Args:
            data: Dictionary containing data to sanitize
            
        Returns:
            Sanitized data dictionary
        """
        if not isinstance(data, dict):
            return data
            
        sanitized = {}
        sensitive_fields = ["password", "token", "api_key", "secret", "credential"]
        
        for key, value in data.items():
            if isinstance(value, dict):
                sanitized[key] = self._sanitize_data(value)
            elif any(sensitive in key.lower() for sensitive in sensitive_fields):
                sanitized[key] = "[REDACTED]"
            else:
                sanitized[key] = value
                
        return sanitized


def generate_sample_logs(count: int = 10) -> tuple[Path, bool, Any]:
    """Generate sample logs for demonstration purposes.
    
    Args:
        count: Number of sample logs to generate
        
    Returns:
        Tuple containing (log_path, success_flag, processor_instance)
    """
    from log_signer import AuditTrailProcessor
    import time
    import uuid
    
    processor = AuditTrailProcessor()
    
    # Log some sample API events
    for _ in range(count):
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
        time.sleep(0.1)  # Small delay to separate logs
    
    # Close the file handler to ensure all data is written to disk
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.FileHandler):
            handler.flush()
            handler.close()
    
    # Process the generated logs
    log_path = processor.audit_logger.log_path
    result = processor.process_daily_logs()
    
    # Return the log path, processing result, and processor instance
    return log_path, result, processor
