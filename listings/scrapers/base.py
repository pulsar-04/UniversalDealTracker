import time
import cloudscraper
from bs4 import BeautifulSoup


class BaseScraper:
    def __init__(self, url):
        self.url = url

        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'bg-BG,bg;q=0.9,en-US;q=0.8,en;q=0.7',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
        }

    def fetch_page(self):
        print(f"Connecting to {self.url}...")
        try:
            time.sleep(2)

            scraper = cloudscraper.create_scraper(
                browser={
                    'browser': 'chrome',
                    'platform': 'windows',
                    'mobile': False
                }
            )


            response = scraper.get(self.url, headers=self.headers, timeout=15)
            response.raise_for_status()

            response.encoding = response.apparent_encoding
            return response.text

        except Exception as e:
            print(f"❌ Error fetching page: {e}")
            return None

    def parse_html(self, html_content):
        return BeautifulSoup(html_content, 'html.parser')

    def scrape_items(self, soup):
        raise NotImplementedError("Subclasses must implement this method")

    def run(self):
        html = self.fetch_page()
        if not html:
            return []
        soup = self.parse_html(html)
        return self.scrape_items(soup)