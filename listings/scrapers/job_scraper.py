from .base import BaseScraper
import re
import time


class DevBgScraper(BaseScraper):

    def scrape_logic(self, page):
        original_url = self.url
        current_page = 1
        max_pages = 15

        while current_page <= max_pages:
            if current_page == 1:
                current_url = original_url
            else:
                if '?' in original_url:
                    current_url = f"{original_url}&_paged={current_page}"
                else:
                    base_url = original_url.rstrip('/')
                    current_url = f"{base_url}/page/{current_page}/"

            print(f"📄 [Dev.bg] Сканирам страница {current_page}: {current_url}")

            page.goto(current_url, wait_until='networkidle', timeout=30000)

            items = []
            job_cards = page.locator('div.job-list-item')
            count = job_cards.count()

            if count == 0:
                print("⚠ Не намирам обяви (job-list-item). Провери линка или класовете.")
                print(f"🏁 [Dev.bg] Няма повече обяви (достигнат край след Страница {current_page - 1}).")
                break

            print(f"🔎 Намерих {count} потенциални обяви за работа...")

            for i in range(count):
                try:
                    card = job_cards.nth(i)

                    link_tag = card.locator('a.overlay-link').first
                    if link_tag.count() == 0:
                        continue

                    href = link_tag.get_attribute('href')

                    title_tag = card.locator('h6.job-title').first
                    title = title_tag.inner_text().strip() if title_tag.count() > 0 else "Unknown Position"

                    company_tag = card.locator('.company-name').first
                    company = company_tag.inner_text().strip() if company_tag.count() > 0 else "Unknown Company"

                    location = "Unknown"
                    badge = card.locator('span.badge').first
                    if badge.count() > 0:
                        location = badge.inner_text().strip()

                    salary_min = None
                    image_url = ""

                    img_tag = card.locator('img[class*="company-logo"]').first
                    if img_tag.count() == 0:
                        img_tag = card.locator('img').first

                    if img_tag.count() > 0:
                        src = img_tag.get_attribute('data-lazy-src') or img_tag.get_attribute(
                            'data-src') or img_tag.get_attribute('src')
                        if src:
                            image_url = src

                    items.append({
                        'title': title,
                        'company': company,
                        'location': location,
                        'link': href,
                        'salary': salary_min,
                        'remote': 'Remote' in location or 'Hybrid' in location,
                        'image_url': image_url
                    })

                except Exception as e:
                    print(f"Error parsing job: {e}")
                    continue

            yield items
            current_page += 1
            time.sleep(2)