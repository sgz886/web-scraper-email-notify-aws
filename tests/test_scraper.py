import pytest
import requests
import requests_mock

from src.scraper import XiaomiEUScraper

DATE = '2024.01.01'
FILENAME = f'XiaomiEUModule_{DATE}.apk'

HTML_CONTENT = f"""
    <table id="files_list">
        <tbody>
            <tr>
                <th>
                    <span class="name">{FILENAME}</span>
                    <a href="/download/{FILENAME}"></a>
                </th>
            </tr>
        </tbody>
    </table>
    """


@pytest.fixture
def scraper_real():
    return XiaomiEUScraper("https://example.com")

def test_get_file_list_success(scraper_real):
    with requests_mock.Mocker() as m:
        m.get(scraper_real.url, text=HTML_CONTENT)
        files = scraper_real.get_file_list()

        assert len(files) == 1
        assert files[0]['filename'] == FILENAME
        assert files[0]['date'] == DATE


def test_get_file_list_invalid_html(scraper_real):
    with requests_mock.Mocker() as m:
        m.get(scraper_real.url, text="<html>Invalid HTML</html>")
        files = scraper_real.get_file_list()
        assert len(files) == 0


def test_get_file_list_network_error(scraper_real):
    with requests_mock.Mocker() as m:
        m.get(scraper_real.url, exc=requests.exceptions.ConnectionError)
        files = scraper_real.get_file_list()
        assert len(files) == 0
