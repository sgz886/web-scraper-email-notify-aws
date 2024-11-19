import logging

from utils import ScraperError, get_timestamp


logger = logging.getLogger(__name__)


class UpdateService:
    def __init__(self, scraper, db_handler, email_sender):
        self.scraper = scraper
        self.db_handler = db_handler
        self.email_sender = email_sender

    def check_new_files_and_send_email(self):
        try:
            current_files = self.scraper.get_file_list()
            if not current_files:
                raise ScraperError(f"{get_timestamp()} - get 0 files from URL, check URL {self.scraper.url}")
            
            last_files_in_db = self.db_handler.get_last_scraper_result()
            new_files = self._compare_files_to_get_new(current_files, last_files_in_db)
            if new_files:
                logger.info(f"{get_timestamp()} - 发现 {len(new_files)} 个新文件, prepare to send email")
                self._send_notification_email(new_files)
            else:
                logger.info(f"{get_timestamp()} - 没有新文件, 不发送邮件")
        except Exception as e:
            logger.error(f"{get_timestamp()} - Service error: {str(e)}")

    def _compare_files_to_get_new(self, current_files, old_files):
        """Compare files by filename and return new"""
        old_filenames = {f['filename'] for f in old_files}  # Convert to set for O(1) lookup
        return [f for f in current_files if f['filename'] not in old_filenames]

    def _send_notification_email(self, new_files):
        self.email_sender.send_new_file_email(new_files)

    def send_log_email(self):
        self.email_sender.send_log_email()
