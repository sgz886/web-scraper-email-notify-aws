import boto3
from datetime import datetime
import json
from config import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, TABLE_NAME
import logging
from utils import get_timestamp

logger = logging.getLogger(__name__)


class DynamoDBHandler:
    def __init__(self):
        self.dynamodb = boto3.resource(
            'dynamodb',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION
        )
        self.table = self.dynamodb.Table(TABLE_NAME)

    def create_table_if_not_exists(self):
        """Create DynamoDB table if it doesn't exist"""
        try:
            # Check if table exists first
            self.dynamodb.meta.client.describe_table(TableName=TABLE_NAME)
            logger.info(f"{get_timestamp()} - Table {TABLE_NAME} already exists")
            return
        except self.dynamodb.meta.client.exceptions.ResourceNotFoundException:
            # Table doesn't exist, create it
            self.dynamodb.create_table(
                TableName=TABLE_NAME,
                KeySchema=[
                    {'AttributeName': 'record_type', 'KeyType': 'HASH'},
                    {'AttributeName': 'scan_date', 'KeyType': 'RANGE'}
                ],
                AttributeDefinitions=[
                    {'AttributeName': 'record_type', 'AttributeType': 'S'},
                    {'AttributeName': 'scan_date', 'AttributeType': 'S'}
                ],
                ProvisionedThroughput={
                    'ReadCapacityUnits': 5,
                    'WriteCapacityUnits': 5
                }
            )
            logger.info(f"{get_timestamp()} - Table {TABLE_NAME} created successfully")

    def save_scraper_result(self, files):
        """Save scan result to DynamoDB"""
        try:
            scan_date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            self.table.put_item(
                Item={
                    'record_type': 'SCAN_RESULT',
                    'scan_date': scan_date,
                    'files': json.dumps(files)
                }
            )
            return True
        except Exception as e:
            logger.error(f"{get_timestamp()} - Error saving scan result: {str(e)}")
            return False

    def get_last_scraper_result(self):
        """Get the most recent result"""
        try:
            response = self.table.query(
                KeyConditionExpression='record_type = :rt',
                ExpressionAttributeValues={
                    ':rt': 'SCAN_RESULT'
                },
                Limit=1,
                ScanIndexForward=False
            )
            items = response.get('Items', [])
            if items:
                return json.loads(items[0]['files'])
            return []
        except Exception as e:
            logger.error(f"{get_timestamp()} - Error getting last scan result: {str(e)}")
            return []
