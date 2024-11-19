from scraper import XiaomiEUScraper
from db_handler import DynamoDBHandler
from email_sender import EmailSender
from config import Config
import logging
from utils import get_timestamp, setup_logging
from services import UpdateService

logger = logging.getLogger(__name__)


def main():
    setup_logging()
    service = create_app()
    service.check_new_files_and_send_email()
    service.send_log_email()

def create_app():
    config = Config()
    scraper = XiaomiEUScraper(config.URL)
    db_handler = DynamoDBHandler(config.aws_credentials, config.TABLE_NAME)
    email_sender = EmailSender(config.aws_credentials, config.sender_recipient_addresses)

    return UpdateService(scraper, db_handler, email_sender)

if __name__ == "__main__":
    main()
