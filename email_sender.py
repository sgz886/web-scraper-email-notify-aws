import boto3
from botocore.exceptions import ClientError
import logging
from io import StringIO
import logging.handlers
from datetime import datetime
from utils import emails_string_to_list, get_log_content, get_timestamp

logger = logging.getLogger(__name__)


class EmailSender:
    def __init__(self, sender_recipient_addresses):
        # because of credential chain, there is no need to pass aws_credentials
        # read env then ~/.aws then Lambda environment
        self.ses = boto3.client('ses')
        self.sender_email = sender_recipient_addresses['sender_email']
        self.new_file_recipient_emails = emails_string_to_list(sender_recipient_addresses['new_file_recipient_emails'])
        self.log_recipient_emails = emails_string_to_list(sender_recipient_addresses['log_recipient_emails'])

        self.is_sender_email_verified = self._check_email_verified(self.sender_email, 'sender')
        self.is_new_file_recipient_emails_verified = self._check_emails_verified(self.new_file_recipient_emails, 'new file recipient')
        self.is_log_recipient_emails_verified = self._check_emails_verified(self.log_recipient_emails, 'log recipient')

    def send_new_file_email(self, new_files):
        """发送新文件通知邮件"""
        subject = "检测到新的Xiaomi.eu文件更新"

        # 构建邮件内容
        body_html = """
        <html>
        <head></head>
        <body>
            <h2>检测到以下新文件：</h2>
            <ul>
        """

        for file in new_files:
            body_html += f"""
                <li>
                    <p>文件名：{file['filename']}</p>
                    <p>下载链接：<a href="{file['url']}">{file['url']}</a></p>
                    <p>更新日期：{file['date']}</p>
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
                return self._ses_send_email(self.new_file_recipient_emails, subject, body_html, type)
            else:
                logger.error(f"{get_timestamp()} - {type} 邮件发送失败: 发送者或接收者 verify failed")
                return False
        except ClientError as e:
            logger.error(f"{get_timestamp()} - {type} 邮件发送失败: {str(e)}")
            return False

    def send_log_email(self):
        """发送程序运行日志邮件"""
        subject = "Xiaomi.eu Crawler 运行日志"

        # Get logs from global buffer
        log_content = get_log_content()

        body_html = f"""
        <html>
        <head></head>
        <body>
            <h2>程序运行日志</h2>
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
                logger.error(f"{get_timestamp()} - {type} 邮件发送失败: 发送者或接收者 verify failed")
                return False
        except ClientError as e:
            logger.error(f"{get_timestamp()} - {type} 邮件发送失败: {str(e)}")
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
            logger.info(f"{get_timestamp()} - {type} 邮件发送成功: {response['MessageId']}")
            return True
        except ClientError as e:
            logger.error(f"{get_timestamp()} - {type} 邮件发送失败: {str(e)}")
            return False

    def _check_emails_verified(self, emails, role):
        for email in emails:
            if not self._check_email_verified(email, role):
                return False
        return True

    def _check_email_verified(self, email, role):
        """检查发送者和接收者是否在SES中验证"""
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
