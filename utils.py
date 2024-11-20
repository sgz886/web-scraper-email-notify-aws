from datetime import datetime
from io import StringIO
import logging
import sys


def setup_logging():
    """Initialize logging configuration"""
    root = logging.getLogger()
    root.setLevel(logging.INFO)
    
    # Clear any default handlers created by lambda
    if root.handlers:
        for handler in root.handlers:
            root.removeHandler(handler)
    
    # Create handlers for both outputs
    handlers = [
        logging.StreamHandler(StringIO()),   # For email
        logging.StreamHandler(sys.stdout),  # For CloudWatch
    ]
    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # Configure all handlers
    for handler in handlers:
        handler.setFormatter(formatter)
        root.addHandler(handler)

def get_log_content():
    root = logging.getLogger()
    string_io_handler = root.handlers[0]    # email is the first handler
    return string_io_handler.stream.getvalue()

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
