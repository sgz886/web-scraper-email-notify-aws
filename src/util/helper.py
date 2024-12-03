from datetime import datetime


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
