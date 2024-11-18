from scraper import XiaomiEUScraper
from db_handler import DynamoDBHandler
from email_sender import EmailSender
from config import URL, SENDER_EMAIL, NEW_FILE_RECIPIENT_EMAILS, LOG_RECIPIENT_EMAIL
import logging
from datetime import datetime
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main():
    """主函数"""
    logger.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 启动文件监控服务...")

    # 初始化邮件发送器
    email_sender = EmailSender()

    try:
        # 首次运行立即检查一次
        check_update_and_send_email(email_sender)
    finally:
        # 无论是否发生错误，都发送运行日志
        email_sender.send_log_email(SENDER_EMAIL, LOG_RECIPIENT_EMAIL)
        pass


def check_update_and_send_email(email_sender):
    """检查更新并发送通知"""
    logger.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 开始检查更新...")

    # 初始化组件
    scraper = XiaomiEUScraper(URL)
    db_handler = DynamoDBHandler()
    # email_sender = EmailSender()

    # 确保数据库表存在
    db_handler.create_table_if_not_exists()

    # 获取当前文件列表
    current_files = scraper.get_file_list()
    if not current_files:
        logger.error("获取当前文件列表失败")
        return

    # 获取上次扫描结果
    last_files = db_handler.get_last_scan_result()

    # 比较文件列表
    new_files = []
    current_filenames = {f['filename'] for f in current_files}
    last_filenames = {f['filename'] for f in last_files}

    if current_filenames != last_filenames:
        new_files = [f for f in current_files if f['filename']
                     not in last_filenames]

        if new_files:
            logger.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 发现 {len(new_files)} 个新文件")
            # 发送new file 邮件通知
            email_sender.send_new_file_notification(
                SENDER_EMAIL, NEW_FILE_RECIPIENT_EMAILS, new_files)
    else:
        logger.info(f"{datetime.now().strftime('%Y-%m-%d %H:%M:%S')} - 没有发现新文件")
    # 保存新的扫描结果
    db_handler.save_scan_result(current_files)
    # 发送new file 邮件通知 todo delete when sucess
    email_sender.send_new_file_notification(SENDER_EMAIL, NEW_FILE_RECIPIENT_EMAILS, new_files)


if __name__ == "__main__":
    main()
