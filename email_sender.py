import boto3
from botocore.exceptions import ClientError
from config import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION
import logging
from io import StringIO
import logging.handlers
from datetime import datetime
from utils import emails_string_to_list, get_log_content, get_timestamp

logger = logging.getLogger(__name__)


class EmailSender:
    def __init__(self):
        self.ses = boto3.client(
            'ses',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION
        )

    def send_new_file_email(self, sender, recipients, new_files):
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
            recipients = emails_string_to_list(recipients)
            if self.check_sender_recipients_emails(sender, recipients):
                return self.ses_send_email(sender, recipients, subject, body_html, '新文件')
        except ClientError as e:
            logger.error(f"{get_timestamp()} - 新文件 邮件发送失败: {str(e)}")
            return False

    def send_log_email(self, sender, recipients):
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
            recipients = emails_string_to_list(recipients)
            if self.check_sender_recipients_emails(sender, recipients):
                return self.ses_send_email(sender, recipients, subject, body_html, '日志')
        except ClientError as e:
            logger.error(f"{get_timestamp()} - 日志 邮件发送失败: {str(e)}")
            return False

    def ses_send_email(self, sender, recipients, subject, body_html, type):
        try:
            response = self.ses.send_email(
                Source=sender,
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

    def check_sender_recipients_emails(self, sender, recipients):
        if not self.check_email_verified(sender, 'sender'):
                return False
        for recipient in recipients:
            if not self.check_email_verified(recipient, 'recipient'):
                return False
        return True
    
    def check_email_verified(self, email, role):
        """检查发送者和接收者是否在SES中验证"""
        try:
            response = self.ses.get_identity_verification_attributes(Identities=[email])
            if email not in response['VerificationAttributes'] or \
               response['VerificationAttributes'][email]['VerificationStatus'] != 'Success':
                logger.error(f"{get_timestamp()} - {role} email {email} is not verified in SES")
                return False
            return True
        except ClientError as e:
            logger.error(f"{get_timestamp()} - Failed to check {role} email verification: {str(e)}")
            return False
