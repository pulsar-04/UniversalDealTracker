from .base import BaseScraper
import re


class DevBgScraper(BaseScraper):
    def scrape_items(self, soup):
        items = []
        job_cards = soup.find_all('div', class_='job-list-item')

        if not job_cards:
            print("⚠ Не намирам обяви (job-list-item). Провери линка или класовете.")
            return []

        print(f"🔎 Намерих {len(job_cards)} потенциални обяви за работа...")

        for card in job_cards:
            try:
                link_tag = card.find('a', class_='overlay-link')
                if not link_tag:
                    continue

                href = link_tag.get('href')

                title_tag = card.find('h6', class_='job-title')
                title = title_tag.get_text(strip=True) if title_tag else "Unknown Position"

                company_tag = card.find(class_='company-name')
                company = company_tag.get_text(strip=True) if company_tag else "Unknown Company"

                location = "Unknown"
                badge = card.find('span', class_='badge')
                if badge:
                    location = badge.get_text(strip=True)

                salary_min = None

                image_url = ""

                img_tag = card.find('img', class_=re.compile(r'company-logo'))
                if not img_tag:
                    img_tag = card.find('img')

                if img_tag:
                    src = img_tag.get('data-lazy-src') or img_tag.get('data-src') or img_tag.get('src')
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

        return items

    def run(self):
        original_url = self.url
        page = 1
        max_pages = 15

        while page <= max_pages:
            print(f"📄 [Dev.bg] Сканирам страница {page}...")

            if page == 1:
                self.url = original_url
            else:
                if '?' in original_url:
                    self.url = f"{original_url}&_paged={page}"
                else:
                    base_url = original_url.rstrip('/')
                    self.url = f"{base_url}/page/{page}/"

            html = self.fetch_page()
            if not html:
                break

            soup = self.parse_html(html)
            items = self.scrape_items(soup)

            if not items:
                print(f"🏁 [Dev.bg] Няма повече обяви (достигнат край след Страница {page - 1}).")
                break

            yield items
            page += 1