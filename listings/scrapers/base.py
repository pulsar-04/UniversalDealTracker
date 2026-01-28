import requests
from bs4 import BeautifulSoup
import time


class BaseScraper:
    """
    Това е абстрактен клас. Той не знае КАКВО търсим (коли или работа),
    но знае КАК да достъпи интернет и да вземе HTML-а.
    """

    def __init__(self, url):
        self.url = url
        # User-Agent е нашата "фалшива лична карта".
        # Без нея сайтовете виждат, че сме скрипт и ни блокират.
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept-Language': 'en-US,en;q=0.9,bg;q=0.8',
        }

    def fetch_page(self):
        print(f"Connecting to {self.url}...")
        try:
            time.sleep(1)
            response = requests.get(self.url, headers=self.headers, timeout=10)
            response.raise_for_status()

            # --- НОВО: Оправяме кирилицата ---
            # Казваме на requests да използва кодировката, която сайтът реално подава
            response.encoding = response.apparent_encoding

            return response.text
        except requests.exceptions.RequestException as e:
            print(f"❌ Error fetching page: {e}")
            return None

    def parse_html(self, html_content):
        """
        Превръща текста в 'супа' (обект), в която можем да търсим тагове.
        """
        return BeautifulSoup(html_content, 'html.parser')

    def run(self):
        """
        Главният метод, който оркестрира всичко.
        """
        html = self.fetch_page()
        if not html:
            return []

        soup = self.parse_html(html)
        items = self.scrape_items(soup)  # Този метод ще се дефинира в дъщерните класове
        print(f"✅ Found {len(items)} items.")
        return items

    def scrape_items(self, soup):
        """
        Този метод е празен тук. Дъщерните класове (CarScraper, JobScraper)
        СА ДЛЪЖНИ да го пренапишат със своята логика.
        """
        raise NotImplementedError("Subclasses must implement scrape_items()!")