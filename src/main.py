import boto3
from scraper import XiaomiEUScraper
from data import DynamoDBHandler
from notification import EmailSender
from util import Config, setup_logging
from service import UpdateService


def create_app():
    config = Config()
    scraper = XiaomiEUScraper(config.URL)
    db_handler = DynamoDBHandler(boto3.resource('dynamodb'),config.TABLE_NAME)
    email_sender = EmailSender(boto3.client('ses'), config.sender_recipient_addresses)

    return UpdateService(scraper, db_handler, email_sender)


def lambda_handler(event, context):
    setup_logging()
    service = create_app()
    service.check_new_files_and_send_email()
    service.send_log_email()
    return {
        'statusCode': 200,
        'body': 'Successfully executed'
    }


if __name__ == "__main__":
    lambda_handler(None, None)
