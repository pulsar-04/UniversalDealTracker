from .base import BaseScraper
import re


class MobileBgScraper(BaseScraper):
    def scrape_items(self, soup):
        items = []
        ad_links = soup.find_all('a', class_='title')

        if not ad_links:
            return []

        print(f"🔎 Намерих {len(ad_links)} потенциални връзки...")

        for link_tag in ad_links:
            try:

                href = link_tag.get('href')
                if href and not href.startswith('http'):
                    href = 'https:' + href


                if '/obiava' not in href:

                    continue


                title = link_tag.get_text(strip=True)


                price = 0
                parent_container = link_tag.find_parent('tr') or link_tag.find_parent('div')

                if parent_container:
                    price_tag = parent_container.find(class_='price')
                    if price_tag:
                        price_text = price_tag.get_text(separator=' ', strip=True)
                        match = re.search(r'\d[\d\s]*', price_text)

                        if match:
                            clean_price = match.group(0)
                            clean_price = re.sub(r'\s', '', clean_price)
                            if clean_price.isdigit():
                                price = int(clean_price)


                year = 2000
                info_text = parent_container.get_text() if parent_container else ""
                year_match = re.search(r'(19|20)\d{2}', info_text)
                if year_match:
                    year = int(year_match.group(0))

                items.append({
                    'title': title,
                    'price': price,
                    'link': href,
                    'year': year
                })

            except Exception as e:
                print(f"Error parsing ad: {e}")
                continue

        return items


class CarsBgScraper(BaseScraper):


    def scrape_items(self, soup):
        items = []


        containers = soup.find_all('div', class_='offer-item')

        if not containers:
            return []

        print(f"🔎 [Cars.bg] Намерих {len(containers)} обяви...")

        for container in containers:
            try:

                a_tag = container.find('a', href=re.compile(r'/offer/'))
                if not a_tag:
                    continue

                href = a_tag.get('href')
                if not href.startswith('http'):
                    href = 'https://www.cars.bg' + href



                title_tag = container.find('h5', class_='card__title')
                title = title_tag.get_text(strip=True) if title_tag else "Неизвестна обява"


                price = 0
                price_tag = container.find(class_=re.compile('price'))
                if price_tag:
                    price_text = price_tag.get_text(separator=' ', strip=True)

                    match = re.search(r'([\d,]+)', price_text)
                    if match:
                        clean_price = match.group(1).replace(',', '')
                        if clean_price.isdigit():
                            price = int(clean_price)


                year = 2000

                info_text = container.get_text()
                year_match = re.search(r'(19|20)\d{2}', info_text)
                if year_match:
                    year = int(year_match.group(0))

                items.append({
                    'title': title,
                    'price': price,
                    'link': href,
                    'year': year
                })

            except Exception as e:
                print(f"Error parsing Cars.bg ad: {e}")
                continue

        return items