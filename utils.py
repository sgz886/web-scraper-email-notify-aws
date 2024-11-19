from datetime import datetime
from io import StringIO
import logging

# Global log buffer for email
log_buffer = StringIO()
log_handler = logging.StreamHandler(log_buffer)
log_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

def setup_logging():
    """Initialize logging configuration"""
    logging.basicConfig(level=logging.INFO)
    logging.getLogger().addHandler(log_handler)

def get_log_content():
    """Get current log content"""
    return log_buffer.getvalue()

def get_timestamp():
    """Return formatted timestamp string"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def emails_string_to_list(emails_string):
    if isinstance(emails_string, str):
        return [email.strip() for email in emails_string.split(',')]
    return ""

class AppError(Exception):
    def __init__(self, message, error_code=None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class EmailError(AppError):
    pass

class ScraperError(AppError):
    pass
