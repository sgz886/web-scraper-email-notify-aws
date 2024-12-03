import pytest

from src.util import Config
from src.service import UpdateService
from src.util import get_timestamp
import logging

logger = logging.getLogger(__name__)


@pytest.fixture
def config():
    return Config()


@pytest.fixture
def scraper_mock(mocker, current_files):
    mock_scraper = mocker.Mock()
    mock_scraper.get_file_list.return_value = current_files
    return mock_scraper


@pytest.fixture
def dynamodb_mock(mocker, old_files):
    # create a mock handler
    mock_handler = mocker.Mock()
    mock_handler.create_table_if_not_exists.return_value = None
    mock_handler.save_scraper_result.return_value = True
    mock_handler.get_last_scraper_result.return_value = old_files
    return mock_handler


@pytest.fixture
def email_mock(mocker):
    mock_sender = mocker.Mock()

    # Mock _ses_send_email with logging
    def mock_ses_send_email(*args, **kwargs):
        type = kwargs.get('type') or args[3]
        logger.info(f"{get_timestamp()} - {type} mock email send success")
        return True
    mock_sender._check_email_verified.return_value = True
    mock_sender._ses_send_email = mock_ses_send_email
    return mock_sender


# @pytest.fixture
# def email_sender(config, mocker):
#     # Create real EmailSender instance
#     from src.notification import EmailSender
#     sender = EmailSender(config.sender_recipient_addresses)

#     # Only mock the internal SES calls
#     # sender._check_email_verified = lambda *args, **kwargs: True
#     # sender._ses_send_email = lambda *args, **kwargs: True
#     mocker.patch.object(sender, '_check_email_verified', return_value=True)
#     sender._ses_send_email = mocker.Mock(return_value=True)
#     return sender


@pytest.fixture
def update_service(scraper_mock, dynamodb_mock, email_mock):
    return UpdateService(scraper_mock, dynamodb_mock, email_mock)


@pytest.fixture
def old_files():
    return [
        {
            'filename': 'file_2024.01.02.apk',
            'url': 'https://example.com/file2.apk',
            'date': '2024.01.02'
        },
        {
            'filename': 'file_2024.01.01.apk',
            'url': 'https://example.com/file1.apk',
            'date': '2024.01.01'
        }
    ]


@pytest.fixture
def current_files():
    return [
        {
            'filename': 'file_2024.01.03.apk',
            'url': 'https://example.com/file3.apk',
            'date': '2024.01.03'
        },
        {
            'filename': 'file_2024.01.02.apk',
            'url': 'https://example.com/file2.apk',
            'date': '2024.01.02'
        },
        {
            'filename': 'file_2024.01.01.apk',
            'url': 'https://example.com/file1.apk',
            'date': '2024.01.01'
        }
    ]
