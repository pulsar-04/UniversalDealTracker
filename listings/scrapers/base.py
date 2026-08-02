from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright


class BaseScraper:
    def __init__(self, url):
        self.url = url

    def fetch_page(self):
        print(f"🌍 Вдигане на браузър и свързване към {self.url}...")
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)

                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                page = context.new_page()

                page.goto(self.url, wait_until='networkidle', timeout=30000)

                html_content = page.content()
                browser.close()

                return html_content

        except Exception as e:
            print(f"❌ Error fetching page with Playwright: {e}")
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