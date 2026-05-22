"""
AWS Secrets Manager integration.

In production (App Runner / Lambda): secrets are injected as environment variables
directly by App Runner via "Secrets and variables" → link to Secrets Manager ARNs.
This module provides a helper for cases where you need to fetch a secret at runtime
(e.g., rotating credentials, one-off scripts).

Usage:
    from app.infrastructure.external.secrets_manager import get_secret
    value = get_secret("world-cup-hub/prod/DB_PASSWORD")
"""
import os
import json
import logging

logger = logging.getLogger(__name__)


def get_secret(secret_name: str, region: str = None) -> str:
    """
    Returns a secret value from AWS Secrets Manager.
    Falls back to os.environ if boto3 is unavailable or not in AWS.
    """
    region = region or os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
    try:
        import boto3
        from botocore.exceptions import ClientError

        client = boto3.client('secretsmanager', region_name=region)
        response = client.get_secret_value(SecretId=secret_name)
        secret = response.get('SecretString') or ''
        # If the secret is a JSON object, return its string representation
        try:
            parsed = json.loads(secret)
            if isinstance(parsed, dict) and len(parsed) == 1:
                return next(iter(parsed.values()))
            return secret
        except (json.JSONDecodeError, StopIteration):
            return secret
    except ImportError:
        logger.warning("boto3 not available — falling back to environment variable '%s'", secret_name)
        return os.environ.get(secret_name.split('/')[-1], '')
    except Exception as exc:
        logger.warning("Secrets Manager fetch failed for '%s': %s — falling back to env", secret_name, exc)
        return os.environ.get(secret_name.split('/')[-1], '')
