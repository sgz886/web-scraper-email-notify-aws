from botocore.exceptions import ClientError
from datetime import datetime
import logging.handlers
from util import emails_string_to_list, get_timestamp, get_log_content

logger = logging.getLogger(__name__)


class EmailSender:
    def __init__(self, ses, sender_recipient_addresses):
        # because of credential chain, there is no need to pass aws_credentials
        # read env then ~/.aws then Lambda environment
        self.ses = ses
        self.sender_email = sender_recipient_addresses['sender_email']
        self.new_file_recipient_emails = emails_string_to_list(sender_recipient_addresses['new_file_recipient_emails'])
        self.log_recipient_emails = emails_string_to_list(sender_recipient_addresses['log_recipient_emails'])

        self.is_sender_email_verified = self._check_email_verified(self.sender_email, 'sender')
        self.is_new_file_recipient_emails_verified = self._check_emails_verified(self.new_file_recipient_emails,
                                                                                 'new file recipient')
        self.is_log_recipient_emails_verified = self._check_emails_verified(self.log_recipient_emails, 'log recipient')

    def send_new_file_email(self, new_files):
        """send new file notification email"""
        subject = "new files detected"

        # build email content
        body_html = """
        <html>
        <head></head>
        <body>
            <h2>new files detected</h2>
            <ul>
        """

        for file in new_files:
            body_html += f"""
                <li>
                    <p>filename: {file['filename']}</p>
                    <p>download link: <a href="{file['url']}">{file['url']}</a></p>
                    <p>update date: {file['date']}</p>
                </li>
            """

        body_html += f"""
            </ul>
            <p>generated date: {get_timestamp()}</p>
        </body>
        </html>
        """

        try:
            type = 'new files'
            if self.is_sender_email_verified and self.is_new_file_recipient_emails_verified:
                value = self._ses_send_email(self.new_file_recipient_emails, subject, body_html, type)
                import time
                time.sleep(2)
                return value
            else:
                logger.error(f"{get_timestamp()} - {type} email send failed: sender or recipient verify failed")
                return False
        except ClientError as e:
            logger.error(f"{get_timestamp()} - {type} email send failed: {str(e)}")
            return False

    def send_log_email(self):
        """send program run log email"""

        # Check if today is Saturday (where weekday() returns 5 for Saturday), only send email on Saturdays
        if datetime.now().weekday() != 5:
            logger.info(f"{get_timestamp()} - Not Saturday, skipping log email")
            return True;

        # Get logs from global buffer
        log_content = get_log_content()
        last_line = log_content.strip().split('\n')[-1]
        new_file_message = last_line.split('-')[-1].strip()

        subject = "Crawler run log (AWS Lambda) - " + new_file_message
        body_html = f"""
        <html>
        <head></head>
        <body>
            <h2>Crawler from AWS Lambda run log</h2>
            <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">{log_content}</pre>
            <p>generated date: {get_timestamp()}</p>
        </body>
        </html>
        """

        try:
            type = 'logs'
            if self.is_sender_email_verified and self.is_log_recipient_emails_verified:
                return self._ses_send_email(self.log_recipient_emails, subject, body_html, type)
            else:
                logger.error(f"{get_timestamp()} - {type} email send failed: sender or recipient verify failed")
                return False
        except ClientError as e:
            logger.error(f"{get_timestamp()} - {type} email send failed: {str(e)}")
            return False

    def _ses_send_email(self, recipients, subject, body_html, type):
        try:
            response = self.ses.send_email(
                Source=self.sender_email,
                Destination={
                    'ToAddresses': recipients  # Now accepts a list of emails
                },
                Message={
                    'Subject': {
                        'Data': subject
                    },
                    'Body': {
                        'Html': {
                            'Data': body_html
                        }
                    }
                }
            )
            logger.info(f"{get_timestamp()} - {type} email send success: {response['MessageId']}")
            return True
        except ClientError as e:
            logger.error(f"{get_timestamp()} - {type} email send failed: {str(e)}")
            return False

    def _check_emails_verified(self, emails, role):
        for email in emails:
            if not self._check_email_verified(email, role):
                return False
        return True

    def _check_email_verified(self, email, role):
        """check if sender or recipient is verified in SES"""
        try:
            response = self.ses.get_identity_verification_attributes(Identities=[email])
            if email not in response['VerificationAttributes'] or \
                    response['VerificationAttributes'][email]['VerificationStatus'] != 'Success':
                logger.error(f"{get_timestamp()} - {role} email {email} is not verified in SES")
                return False
            return True
        except ClientError as e:
            logger.error(f"{get_timestamp()} - Failed to verify {role} email {email}: {str(e)}")
            return False
