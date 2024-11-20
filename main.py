from scraper import XiaomiEUScraper
from db_handler import DynamoDBHandler
from email_sender import EmailSender
from config import Config
from utils import setup_logging
from services import UpdateService


def main():
    setup_logging()
    service = create_app()
    service.check_new_files_and_send_email()
    service.send_log_email()

def create_app():
    config = Config()
    scraper = XiaomiEUScraper(config.URL)
    db_handler = DynamoDBHandler(config.TABLE_NAME)
    email_sender = EmailSender(config.sender_recipient_addresses)

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
    main()
