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


                items.append({
                    'title': title,
                    'company': company,
                    'location': location,
                    'link': href,
                    'salary': salary_min,
                    'remote': 'Remote' in location or 'Hybrid' in location  # Проста проверка
                })

            except Exception as e:
                print(f"Error parsing job: {e}")
                continue

        return items