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


class JobsBgScraper(BaseScraper):
    def scrape_items(self, soup):
        items = []
        containers = soup.find_all('div', class_='mdc-card')

        if not containers:
            return []

        print(f"🔎 [Jobs.bg] Намерих {len(containers)} потенциални обяви...")

        for container in containers:
            try:

                link_tag = container.find('a', class_='black-link-b')
                if not link_tag:
                    continue

                href = link_tag.get('href')
                if not href.startswith('http'):
                    href = 'https://www.jobs.bg/' + href.lstrip('/')


                title = link_tag.get('title')
                if not title:
                    title_div = container.find('div', class_='card-title')
                    title = title_div.get_text(strip=True) if title_div else "Неизвестна позиция"


                company_tag = container.find('div', class_='secondary-text')
                company = company_tag.get_text(strip=True) if company_tag else "Неизвестна компания"


                info_tag = container.find('div', class_='card-info')
                info_text = info_tag.get_text(strip=True) if info_tag else ""
                location = info_text.split(';')[0].strip() if info_text else "Неизвестна локация"
                info_lower = info_text.lower()
                is_remote = 'вкъщи' in info_lower or 'дистанционн' in info_lower or 'remote' in info_lower

                items.append({
                    'title': title,
                    'company': company,
                    'location': location,
                    'remote': is_remote,
                    'salary': 0.0,
                    'link': href
                })

            except Exception as e:
                print(f"Error parsing Jobs.bg ad: {e}")
                continue

        return items