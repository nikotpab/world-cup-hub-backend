#!/bin/bash
set -e

echo "Running security audit on dependencies..."
# Instala pip-audit temporalmente para el check
pip install pip-audit

echo "Auditing requirements.txt..."
pip-audit -r requirements.txt

if [ $? -eq 0 ]; then
    echo "Sec audit passed successfully."
else
    echo "Sec audit failed. Vulnerabilities found!"
    exit 1
fi
