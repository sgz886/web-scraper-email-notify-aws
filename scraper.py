import requests
from bs4 import BeautifulSoup
from datetime import datetime
from utils import get_timestamp
import logging

logger = logging.getLogger(__name__)

class XiaomiEUScraper:
    def __init__(self, url):
        self.url = url
    
    def get_file_list(self):
        """
        访问网页并解析出文件列表
        返回格式: [{'filename': 'xxx.apk', 'url': 'xxx', 'date': 'yyyy-mm-dd'}]
        """
        try:
            response = requests.get(self.url)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            files_table = soup.find('table', id='files_list')
            tbody = files_table.find_next('tbody')
            
            if not files_table:
                logger.error(f"{get_timestamp()} - 找不到文件列表表格")
                return []
            
            files = []
            for row in tbody.find_all('tr'):
                content_of_interest = row.find_all('th')
                if content_of_interest:
                    filename = content_of_interest[0].find('span', class_='name').text.strip()
                    file_url = content_of_interest[0].find('a')['href']
                    # Extract date from filename and validate it
                    try:
                        date_str = filename.split('_')[-1].rsplit('.', 1)[0]  # XiaomiEUModule_2024.10.24.apk -> 2024.10.24
                        date_parts = date_str.split('.')
                        if len(date_parts) == 3:
                            year, month, day = date_parts
                            # Pad month and day with leading zeros if needed
                            month = month.zfill(2)
                            day = day.zfill(2)
                            date_str = f"{year}-{month}-{day}"
                            # Validate date by parsing it
                            datetime.strptime(date_str, '%Y-%m-%d')
                            date = f"{year}.{month}.{day}"  # Convert back to original format
                        else:
                            raise ValueError("Invalid date format")
                    except (ValueError, IndexError):
                        logger.warning(f"{get_timestamp()} - Could not extract valid date from filename: {filename}")
                        date = datetime.now().strftime('%Y.%m.%d')
                    
                    files.append({
                        'filename': filename,
                        'url': file_url,
                        'date': date
                    })
            
            return files
            
        except Exception as e:
            logger.error(f"{get_timestamp()} - 抓取文件列表时出错: {str(e)}")
            return [] 