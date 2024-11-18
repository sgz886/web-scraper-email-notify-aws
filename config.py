from dotenv import load_dotenv
import os
import boto3
import logging

logger = logging.getLogger(__name__)


def get_secret(secret_name):
    """Get secret from AWS Secrets Manager"""
    try:
        session = boto3.session.Session()
        client = session.client(
            service_name='secretsmanager',
            region_name=os.getenv('AWS_REGION', 'ap-southeast-1')
        )
        response = client.get_secret_value(SecretId=secret_name)
        return response['SecretString']
    except Exception as e:
        logger.warning(f"Could not get secret from AWS: {str(e)}")
        return None


# Try to load from .env file first
load_dotenv()

# Configuration settings
URL = "https://sourceforge.net/projects/xiaomi-eu-multilang-miui-roms/files/xiaomi.eu/Xiaomi.eu-app/"
CHECK_TIME = "02:00"

# Try to get credentials from AWS Secrets Manager first, fall back to env vars
secret = get_secret('xiaomi_eu_crawler_secrets')
if secret:
    import json
    secrets_dict = json.loads(secret)
    AWS_ACCESS_KEY = secrets_dict.get('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = secrets_dict.get('AWS_SECRET_KEY')
    SENDER_EMAIL = secrets_dict.get('SENDER_EMAIL')
    NEW_FILE_RECIPIENT_EMAILS = secrets_dict.get('NEW_FILE_RECIPIENT_EMAILS')
    LOG_RECIPIENT_EMAIL = secrets_dict.get('LOG_RECIPIENT_EMAIL')
else:
    # Fall back to environment variables
    AWS_ACCESS_KEY = os.getenv('AWS_ACCESS_KEY')
    AWS_SECRET_KEY = os.getenv('AWS_SECRET_KEY')
    SENDER_EMAIL = os.getenv('SENDER_EMAIL')
    NEW_FILE_RECIPIENT_EMAILS = os.getenv('NEW_FILE_RECIPIENT_EMAILS')
    LOG_RECIPIENT_EMAIL = os.getenv('LOG_RECIPIENT_EMAIL')
AWS_REGION = os.getenv('AWS_REGION')
TABLE_NAME = 'xiaomi_eu_files'
