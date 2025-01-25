from datetime import datetime, timedelta
import json
import logging
from util import get_timestamp

logger = logging.getLogger(__name__)


class DynamoDBHandler:
    def __init__(self, dynamodb, table_name):
        # because of credential chain, there is no need to pass aws_credentials
        # read env then ~/.aws then Lambda environment
        self.dynamodb = dynamodb
        self._create_table_if_not_exists(dynamodb, table_name)
        self.table = self.dynamodb.Table(table_name)

    def _create_table_if_not_exists(self, dynamodb, table_name):
        """Create DynamoDB table if it doesn't exist"""
        try:
            # Check if table exists first
            dynamodb.meta.client.describe_table(TableName=table_name)
            logger.info(f"{get_timestamp()} - Table {table_name} exists")
            return
        except dynamodb.meta.client.exceptions.ResourceNotFoundException:
            # Table doesn't exist, create it
            dynamodb.create_table(
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

    def deleteOldDbData(self):
        """At first day of a month, remove records older than 30 days using batch delete"""
        if datetime.now().day != 1:
            return
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

        response = self.table.query(KeyConditionExpression='record_type = :rt AND scan_date < :sd',
                                    ExpressionAttributeValues={':rt': 'SCAN_RESULT', ':sd': thirty_days_ago})

        items = response.get('Items', [])
        # limit batch operations to 25 items
        batch_size = 25
        for i in range(0, len(items), batch_size):
            batch_items = items[i:i + batch_size]
            request_items = {
                self.table.name: [
                    {
                        'DeleteRequest': {
                            'Key': {
                                'record_type': item['record_type'],
                                'scan_date': item['scan_date']
                            }
                        }
                    }
                    for item in batch_items
                ]
            }
            # Execute batch delete
            self.dynamodb.meta.client.batch_write_item(RequestItems=request_items)

        logger.info(f"{get_timestamp()} - Deleted {len(items)} old records")
