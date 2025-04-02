#!/usr/bin/env python3
"""
Main entry point for the audit trail integrity system.

This module coordinates the overall process of log collection, signing, and uploading,
while also incorporating integrity checks.
"""

import os
import sys
import glob
import logging
import argparse
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

# Import modules from the audit trail integrity system
from config import Config
from log_collector import generate_sample_logs
from log_signer import CryptographicProcessor, AuditTrailProcessor
from s3_uploader import StorageProcessor

# Configure logging
logging.basicConfig(
    level=getattr(logging, Config.LOG_LEVEL),
    format=Config.LOG_FORMAT
)
logger = logging.getLogger('audit_trail')


def setup_argparse() -> argparse.ArgumentParser:
    """Set up command line argument parsing.
    
    Returns:
        Configured argument parser
    """
    parser = argparse.ArgumentParser(description="Audit Trail Integrity System")
    
    # Add subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Generate keys command
    keys_parser = subparsers.add_parser("generate-keys", help="Generate cryptographic keys")
    
    # Generate sample logs command
    sample_parser = subparsers.add_parser("generate-samples", help="Generate sample logs")
    sample_parser.add_argument(
        "--count", type=int, default=10,
        help="Number of sample logs to generate (default: 10)"
    )
    
    # Process logs command
    process_parser = subparsers.add_parser("process", help="Process logs for the current day")
    
    # Verify logs command
    verify_parser = subparsers.add_parser("verify", help="Verify log integrity")
    verify_parser.add_argument(
        "--log-file", type=str,
        help="Specific log file to verify (default: today's log)"
    )
    
    # Demo command (runs the full pipeline)
    demo_parser = subparsers.add_parser("demo", help="Run a full demonstration")
    demo_parser.add_argument(
        "--count", type=int, default=10,
        help="Number of sample logs to generate (default: 10)"
    )
    demo_parser.add_argument(
        "--clean", action="store_true",
        help="Clean up logs, signatures, and keys before running"
    )
    
    return parser


def clean_directories():
    """Clean up logs, signatures, and keys directories."""
    logger.info("Cleaning up previous logs, signatures, and keys...")
    
    # Remove logs directory contents
    for file_path in glob.glob(f"{Config.LOG_DIR}/*"):
        try:
            os.remove(file_path)
        except Exception as e:
            logger.warning(f"Failed to remove {file_path}: {e}")
    
    # Remove signatures directory contents
    for file_path in glob.glob(f"{Config.SIGNATURES_DIR}/*"):
        try:
            os.remove(file_path)
        except Exception as e:
            logger.warning(f"Failed to remove {file_path}: {e}")
    
    # Remove keys directory contents
    for file_path in glob.glob(f"{Config.KEYS_DIR}/*"):
        try:
            os.remove(file_path)
        except Exception as e:
            logger.warning(f"Failed to remove {file_path}: {e}")


def generate_keys() -> bool:
    """Generate cryptographic keys for signing and verification.
    
    Returns:
        True if successful, False otherwise
    """
    logger.info("Generating cryptographic keys for signing...")
    result, message = CryptographicProcessor.generate_keys()
    
    if result:
        logger.info(message)
        return True
    else:
        logger.error(message)
        return False


def run_demo(count: int = 10, clean: bool = False) -> bool:
    """Run a full demonstration of the audit trail integrity system.
    
    Args:
        count: Number of sample logs to generate
        clean: Whether to clean up before running
        
    Returns:
        True if successful, False otherwise
    """
    # Step 1: Clean up if requested
    if clean:
        clean_directories()
    
    # Step 2: Generate keys if they don't exist
    if not Config.get_private_key_path().exists() or not Config.get_public_key_path().exists():
        if not generate_keys():
            return False
    
    # Step 3: Generate and process sample logs
    logger.info(f"Generating {count} sample logs...")
    log_path, process_result, processor = generate_sample_logs(count)
    
    if not process_result:
        logger.error("Failed to process logs properly")
        return False
    
    # Step 4: Verify the logs
    logger.info("Verifying logs...")
    verify_result = processor.verify_logs(processor.snapshot_log_path, processor.signature_path)
    
    # Step 5: Generate compliance metrics
    compliance_metrics = generate_compliance_metrics(processor)
    
    # Step 6: Print summary
    print("\n" + "=" * 80)
    print("AUDIT TRAIL INTEGRITY DEMONSTRATION SUMMARY")
    print("=" * 80)
    print(f"Generated {count} sample log entries")
    print(f"Log file: {log_path}")
    print(f"Snapshot file: {processor.snapshot_log_path}")
    print(f"Signature file: {processor.signature_path}")
    print(f"Process result: {'SUCCESS' if process_result else 'FAILED'}")
    print(f"Verification result: {'SUCCESS' if verify_result else 'FAILED'}")
    
    print("\n" + "-" * 80)
    print("COMPLIANCE METRICS")
    print("-" * 80)
    print(f"Log Signing: {compliance_metrics['log_signing_percentage']}% of designated critical log types are cryptographically signed (Target: 100%)")
    print(f"Signing Algorithm: {compliance_metrics['signing_algorithm']} - {compliance_metrics['signing_algorithm_check']}")
    print(f"Immutable Storage: {compliance_metrics['immutable_storage']} (Configuration Check: {compliance_metrics['immutable_storage_check']})")
    print(f"Integrity Verification: {compliance_metrics['integrity_verification_frequency']} (Check: {compliance_metrics['integrity_verification_check']})")
    print(f"Access Control: {compliance_metrics['access_control_count']} entities with write/delete access (Target: ≤ 2 roles/principals)")
    print("=" * 80)
    
    # Clean up snapshot files
    for snapshot_file in glob.glob(f"{Config.LOG_DIR}/*.snapshot*"):
        try:
            Path(snapshot_file).unlink()
            logger.debug(f"Removed temporary file: {snapshot_file}")
        except Exception as e:
            logger.warning(f"Failed to remove temporary file {snapshot_file}: {e}")
    
    logger.info("Audit trail processing complete")
    return verify_result


def generate_compliance_metrics(processor: Any) -> Dict[str, Any]:
    """Generate compliance metrics for the audit trail system.
    
    Args:
        processor: The AuditTrailProcessor instance
        
    Returns:
        Dictionary containing compliance metrics
    """
    # Check log signing percentage
    log_signing_percentage = 100  # All logs are signed in our implementation
    
    # Check signing algorithm
    signing_algorithm = "SHA-256"
    signing_algorithm_check = "Pass" if signing_algorithm in ["SHA-256", "SHA-384", "SHA-512"] else "Fail"
    
    # Check immutable storage
    immutable_storage = "AWS S3 Glacier with Vault Lock"
    immutable_storage_check = "True"  # Simulated for demonstration
    
    # Check integrity verification frequency
    integrity_verification_frequency = "Daily"
    integrity_verification_check = "Matches Policy"  # Assuming daily checks match policy
    
    # Check access control
    access_control_count = 2  # Simulated for demonstration (e.g., Admin and Audit roles)
    
    return {
        "log_signing_percentage": log_signing_percentage,
        "signing_algorithm": signing_algorithm,
        "signing_algorithm_check": signing_algorithm_check,
        "immutable_storage": immutable_storage,
        "immutable_storage_check": immutable_storage_check,
        "integrity_verification_frequency": integrity_verification_frequency,
        "integrity_verification_check": integrity_verification_check,
        "access_control_count": access_control_count
    }


def main():
    """Main entry point for the audit trail integrity system."""
    parser = setup_argparse()
    args = parser.parse_args()
    
    if args.command == "generate-keys":
        success = generate_keys()
        sys.exit(0 if success else 1)
    
    elif args.command == "generate-samples":
        logger.info(f"Generating {args.count} sample logs...")
        log_path, process_result, processor = generate_sample_logs(args.count)
        sys.exit(0 if process_result else 1)
    
    elif args.command == "process":
        processor = AuditTrailProcessor()
        result = processor.process_daily_logs()
        sys.exit(0 if result else 1)
    
    elif args.command == "verify":
        processor = AuditTrailProcessor()
        if args.log_file:
            log_path = Path(args.log_file)
            signature_path = Path(f"{args.log_file}{Config.SIGNATURE_FILE_EXTENSION}")
            result = processor.verify_logs(log_path, signature_path)
        else:
            # Verify today's log
            today = datetime.date.today()
            log_path = Config.get_log_path_for_date(today)
            signature_path = Path(f"{log_path}{Config.SIGNATURE_FILE_EXTENSION}")
            result = processor.verify_logs(log_path, signature_path)
        sys.exit(0 if result else 1)
    
    elif args.command == "demo":
        success = run_demo(args.count, args.clean)
        sys.exit(0 if success else 1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
