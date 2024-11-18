import boto3
from botocore.exceptions import ClientError
from config import AWS_ACCESS_KEY, AWS_SECRET_KEY, AWS_REGION, SENDER_EMAIL
import logging
from io import StringIO
import logging.handlers
from datetime import datetime

logger = logging.getLogger(__name__)


class EmailSender:
    def __init__(self):
        self.ses = boto3.client(
            'ses',
            aws_access_key_id=AWS_ACCESS_KEY,
            aws_secret_access_key=AWS_SECRET_KEY,
            region_name=AWS_REGION
        )

        # Add log buffer
        self.log_buffer = StringIO()
        self.log_handler = logging.StreamHandler(self.log_buffer)
        self.log_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(self.log_handler)

    def check_email_verified(self, email, role):
        """检查发送者和接收者是否在SES中验证"""
        try:
            response = self.ses.get_identity_verification_attributes(Identities=[email])
            if SENDER_EMAIL not in response['VerificationAttributes'] or \
               response['VerificationAttributes'][SENDER_EMAIL]['VerificationStatus'] != 'Success':
                logger.error(f"{datetime.now().strftime(
                    '%Y-%m-%d %H:%M:%S')} - Sender email {SENDER_EMAIL} is not verified in SES")
                raise ValueError(
                    f"Sender email {SENDER_EMAIL} must be verified in SES")
        except ClientError as e:
            logger.error(f"{datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S')} - Failed to check sender email verification: {str(e)}")
            raise

    def send_new_file_notification(self, sender, recipients, new_files):
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

        body_html += """
            </ul>
        </body>
        </html>
        """

        try:
            # Verify all recipients are verified in sandbox mode
            for recipient in recipients if isinstance(recipients, list) else [recipients]:
                try:
                    self.ses.get_identity_verification_attributes(
                        Identities=[recipient.strip()]
                    )
                except ClientError:
                    logger.error(
                        f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - Recipient {recipient} is not verified in SES. Skipping.")
                    return False

            # Convert string to list if needed
            if isinstance(recipients, str):
                recipients = [email.strip() for email in recipients.split(',')]

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
            logger.info(f"{datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S')} - 新文件邮件发送成功: {response['MessageId']}")
            return True
        except ClientError as e:
            error_code = e.response['Error']['Code']
            error_msg = e.response['Error']['Message']
            logger.error(
                f"Email sending failed - Error {error_code}: {error_msg}")
            if error_code == 'MessageRejected':
                logger.error(
                    "{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} Email rejected - Check if sender/recipient are verified in sandbox mode")
            return False

    def send_log_email(self, sender, recipient):
        """发送程序运行日志邮件"""
        subject = "Xiaomi.eu Crawler 运行日志"

        # Get logs from buffer
        log_content = self.log_buffer.getvalue()

        body_html = f"""
        <html>
        <head></head>
        <body>
            <h2>程序运行日志</h2>
            <pre style="background-color: #f5f5f5; padding: 15px; border-radius: 5px;">{log_content}</pre>
        </body>
        </html>
        """

        try:
            response = self.ses.send_email(
                Source=sender,
                Destination={
                    'ToAddresses': [recipient]
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
            logger.info(f"{datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S')} - 日志邮件发送成功: {response['MessageId']}")
            return True
        except ClientError as e:
            logger.error(f"{datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S')} -  日志邮件发送失败: {str(e)}")
            return False
