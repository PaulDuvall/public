#!/bin/bash

# Audit Trail Integrity System Runner

# Set up virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
else
    echo "Using existing virtual environment."
    source venv/bin/activate
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Check if AWS CLI is available
if command -v aws &> /dev/null; then
    echo "AWS CLI is available."
else
    echo "Warning: AWS CLI is not installed. S3 operations will be simulated."
fi

# Run the audit trail integrity demo
echo -e "\nRunning audit trail integrity process..."
python3 main.py demo --clean

echo -e "\nAudit trail processing complete."
echo "The virtual environment is activated. You can run 'deactivate' to exit it."
