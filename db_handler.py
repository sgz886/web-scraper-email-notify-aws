import boto3
from datetime import datetime
import json
import logging
from utils import get_timestamp

logger = logging.getLogger(__name__)


class DynamoDBHandler:
    def __init__(self, table_name):
        # because of credential chain, there is no need to pass aws_credentials
        # read env then ~/.aws then Lambda environment
        self.dynamodb = boto3.resource('dynamodb')
        self.create_table_if_not_exists(table_name)
        self.table = self.dynamodb.Table(table_name)

    def create_table_if_not_exists(self, table_name):
        """Create DynamoDB table if it doesn't exist"""
        try:
            # Check if table exists first
            self.dynamodb.meta.client.describe_table(TableName=table_name)
            logger.info(f"{get_timestamp()} - Table {table_name} exists")
            return
        except self.dynamodb.meta.client.exceptions.ResourceNotFoundException:
            # Table doesn't exist, create it
            self.dynamodb.create_table(
                TableName=table_name,
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
            logger.info(f"{get_timestamp()} - Table {table_name} created successfully")

    def save_scraper_result(self, files):
        """Save latest files result to DynamoDB"""
        try:
            scan_date = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            self.table.put_item(
                Item={
                    'record_type': 'SCAN_RESULT',
                    'scan_date': scan_date,
                    'files': json.dumps(files)
                }
            )
            logger.info(f"{get_timestamp()} - save latest records to db table {self.table.name} successfully")
            logger.info(f"{get_timestamp()} - file content: {files}")
            return True
        except Exception as e:
            logger.error(f"{get_timestamp()} - Error saving new files to DB")
            logger.error(f"{get_timestamp()} - file content: {files}")
            logger.error(f"{get_timestamp()} - Error message: {str(e)}")
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
