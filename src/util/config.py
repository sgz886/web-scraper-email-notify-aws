from dotenv import load_dotenv
import os
import boto3
import logging
from .helper import get_timestamp

IS_LOCAL = os.getenv('AWS_LAMBDA_FUNCTION_NAME') is None  # True if running locally
logger = logging.getLogger(__name__)


class Config:
    def __init__(self):
        if IS_LOCAL:
            load_dotenv()  # Only load .env file in local environment
        self._load_config()

    def _load_config(self):
        self.AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
        self.AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
        self.AWS_REGION = os.getenv('AWS_REGION', 'ap-southeast-2')
        self.SENDER_EMAIL = os.getenv('SENDER_EMAIL')
        self.NEW_FILE_RECIPIENT_EMAILS = os.getenv('NEW_FILE_RECIPIENT_EMAILS')
        self.LOG_RECIPIENT_EMAILS = os.getenv('LOG_RECIPIENT_EMAILS')
        self.TABLE_NAME = os.getenv('TABLE_NAME')
        self.URL = os.getenv('URL')

    @property
    def sender_recipient_addresses(self):
        return {
            'sender_email': self.SENDER_EMAIL,
            'new_file_recipient_emails': self.NEW_FILE_RECIPIENT_EMAILS,
            'log_recipient_emails': self.LOG_RECIPIENT_EMAILS,
        }

    # don't use following AWS Secrets Manager, use environment variables instead
    def _get_secret(self, secret_name):
        """Get secret from AWS Secrets Manager"""
        try:
            session = boto3.session.Session()
            client = session.client(
                service_name='secretsmanager',
                region_name=self.AWS_REGION
            )
            response = client.get_secret_value(SecretId=secret_name)
            return response['SecretString']
        except Exception as e:
            logger.warning(f"{get_timestamp()} - Could not get secret from AWS Secrets Manager in {self.AWS_REGION}: {str(e)}")
            return None
