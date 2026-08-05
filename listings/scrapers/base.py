import types
from playwright.sync_api import sync_playwright


class BaseScraper:
    def __init__(self, url):
        self.url = url

    def scrape_logic(self, page):

        raise NotImplementedError("Subclasses must implement this method")

    def run(self):

        print(f"🚀 [BaseScraper] Инициализиране на Playwright двигател...")

        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=True)
                context = browser.new_context(
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                    viewport={'width': 1920, 'height': 1080}
                )
                page = context.new_page()

                results = self.scrape_logic(page)

                if isinstance(results, types.GeneratorType):
                    for item in results:
                        yield item
                else:
                    yield results

            except Exception as e:
                print(f"❌ [BaseScraper] Фатална грешка в браузърната сесия: {e}")
                yield []