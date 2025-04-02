# Audit Trail Integrity System

## Overview

This system ensures that application, system, and API logs are cryptographically signed and stored immutably to guarantee their authenticity, integrity, and non-repudiation. It implements key security controls for accountability and forensic analysis.

## Features

- 🔐 **Cryptographic Signing**: Uses RSA-2048 with SHA-256 for strong digital signatures
- 🧊 **Immutable Storage**: Configurable to use AWS S3 Glacier or Deep Archive with Vault Lock
- 🔍 **Integrity Verification**: Built-in tools to verify log authenticity
- 🔄 **Daily Processing**: Automated log rotation and processing workflow
- 🧹 **Data Sanitization**: Automatic redaction of sensitive information

## Architecture

The system consists of several components:

1. **AuditLogger**: Manages log generation with proper formatting, unique identifiers, and sanitization of sensitive data
2. **CryptographicProcessor**: Handles RSA key generation, file hashing, digital signatures, and verification
3. **StorageProcessor**: Manages secure upload to immutable storage (AWS S3 Glacier)
4. **AuditTrailProcessor**: Orchestrates the entire workflow and provides the main API

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/audit_trail_integrity.git
cd audit_trail_integrity

# Run the setup script
./run.sh
```

## Usage

### Command Line Interface

The system provides a command-line interface with several commands:

```bash
# Generate cryptographic keys
python3 main.py generate-keys

# Generate sample logs for testing
python3 main.py generate-samples --count 10

# Process logs for the current day
python3 main.py process

# Verify log integrity
python3 main.py verify --log-file path/to/logfile.log

# Run a full demonstration
python3 main.py demo --clean
```

### Integrating in Your Application

```python
from audit_trail import AuditTrailProcessor

# Initialize the processor
processor = AuditTrailProcessor()

# Log an API event
processor.log_api_event(
    api_endpoint="/api/users/123",
    user_id="user_abc",
    request_data={"action": "update", "fields": {"name": "John Doe"}},
    response_data={"status": "success"},
    status_code=200
)

# Process daily logs (e.g., call this from a scheduled job)
processor.process_daily_logs()
```

## Security Considerations

- **Private Key Protection**: The private key used for signing should be protected with proper access controls
- **Immutability Configuration**: AWS S3 Glacier Vault Lock should be configured for true immutability
- **Periodic Verification**: Implement regular integrity checks of archived logs
- **Access Control**: Limit access to log archives to essential personnel only
- **Key Rotation**: Consider implementing a key rotation policy for long-term deployments

## AWS Integration

The system integrates with AWS services for secure storage and management:

- **S3 Glacier**: For immutable, long-term storage of audit logs
- **IAM Roles**: For secure access control to S3 resources
- **CloudWatch**: Can be configured for monitoring and alerting (simulation mode available)
- **Parameter Store**: Can be used to store configuration securely (optional)

## Compliance

This implementation addresses requirements from:

- OWASP: Insufficient Logging & Monitoring
- ISO 42001:2023: Clause 9 (Monitoring)
- NIST AI RMF: Measure 4.1 (Monitor Behavior)
- EU AI Act: Article 14 (Human Oversight)
- GDPR: Article 5 (Principles of Processing)

## Metrics and Reporting

The system provides compliance metrics for:

- **Log Signing**: Percentage of logs that are cryptographically signed
- **Signing Algorithm**: Verification that SHA-256 or stronger is used
- **Immutable Storage**: Configuration check for proper S3 storage class
- **Integrity Verification**: Frequency and success rate of verification checks
- **Access Control**: Number of entities with write/delete access

## Dependencies

- Python 3.11 or higher
- boto3 (AWS SDK for Python)
- cryptography (for cryptographic operations)
- Additional dependencies listed in requirements.txt

## Development

### Directory Structure

```
audit_trail_integrity/
├── keys/                  # RSA key pair storage
├── logs/                  # Generated log files
├── signatures/            # Digital signatures for logs
├── audit_trail.py         # Main API module
├── config.py              # Configuration settings
├── log_collector.py       # Log collection functionality
├── log_signer.py          # Cryptographic signing functionality
├── main.py                # Command-line interface
├── requirements.txt       # Python dependencies
├── run.sh                 # Setup and execution script
└── s3_uploader.py         # AWS S3 upload functionality
```

### Testing

To run the system in test mode:

```bash
python3 main.py demo --clean
```

This will generate sample logs, process them, and verify their integrity without actually uploading to AWS S3.

## License

[Your License Here]
