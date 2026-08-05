from .base import BaseScraper
import re
import time


class MobileBgScraper(BaseScraper):

    def scrape_logic(self, page):
        current_url = self.url
        page.goto(current_url, wait_until='networkidle', timeout=30000)

        while True:
            print(f"🌍 Зареждам страница: {page.url}")

            items = []
            ad_links = page.locator('a.title')
            count = ad_links.count()

            print(f"🔎 Намерих {count} потенциални връзки...")
            if count == 0:
                break

            for i in range(count):
                try:
                    link_locator = ad_links.nth(i)
                    href = link_locator.get_attribute('href')

                    if not href:
                        continue
                    if not href.startswith('http'):
                        href = 'https:' + href
                    if '/obiava' not in href:
                        continue

                    title = link_locator.inner_text().strip()

                    parent = link_locator.locator(
                        "xpath=ancestor::tr | ancestor::div[contains(concat(' ', normalize-space(@class), ' '), ' item ')]").first

                    image_url = ""
                    price = 0
                    year = 2000

                    if parent.count() > 0:
                        img = parent.locator('img.pic').first
                        if img.count() == 0:
                            img = parent.locator('img').first

                        if img.count() > 0:
                            src = img.get_attribute('src')
                            if src:
                                image_url = 'https:' + src if src.startswith('//') else src

                        price_tag = parent.locator('.price').first
                        if price_tag.count() > 0:
                            price_text = price_tag.inner_text()
                            match = re.search(r'\d[\d\s]*', price_text)
                            if match:
                                clean_price = re.sub(r'\s', '', match.group(0))
                                if clean_price.isdigit():
                                    price = int(clean_price)

                        info_text = parent.inner_text()
                        year_match = re.search(r'(19|20)\d{2}', info_text)
                        if year_match:
                            year = int(year_match.group(0))

                    items.append({
                        'title': title,
                        'price': price,
                        'link': href,
                        'year': year,
                        'image_url': image_url
                    })

                except Exception as e:
                    print(f"Error parsing ad: {e}")
                    continue

            yield items

            next_btn = page.locator('a.saveSlink.next').first
            if next_btn.count() > 0:
                next_url = next_btn.get_attribute('href')
                if next_url:
                    if next_url.startswith('//'):
                        current_url = 'https:' + next_url
                    elif next_url.startswith('/'):
                        current_url = 'https://www.mobile.bg' + next_url
                    else:
                        current_url = next_url

                    page.goto(current_url, wait_until='domcontentloaded')
                    time.sleep(2)
                else:
                    break
            else:
                print(f"✅ Край! Достигната е последната страница.")
                break


class CarsBgScraper(BaseScraper):

    def scrape_logic(self, page):
        original_url = self.url
        current_page = 1

        while True:
            current_url = original_url if current_page == 1 else f"{original_url}{'&' if '?' in original_url else '?'}page={current_page}"

            print(f"🌍 [Cars.bg] Зареждам страница {current_page}: {current_url}")
            page.goto(current_url, wait_until='networkidle', timeout=30000)

            items = []
            containers = page.locator('div.offer-item')
            count = containers.count()

            print(f"🔎 [Cars.bg] Намерих {count} обяви...")
            if count == 0:
                print("🏁 [Cars.bg] Няма повече обяви (достигнат край).")
                break

            for i in range(count):
                try:
                    container = containers.nth(i)

                    a_tag = container.locator('a[href*="/offer/"]').first
                    if a_tag.count() == 0:
                        continue

                    href = a_tag.get_attribute('href')
                    if not href:
                        continue
                    if not href.startswith('http'):
                        href = 'https://www.cars.bg' + href

                    title_tag = container.locator('h5.card__title').first
                    title = title_tag.inner_text().strip() if title_tag.count() > 0 else "Неизвестна обява"

                    image_url = ""
                    media_div = container.locator('div[class*="mdc-card__media"]').first
                    if media_div.count() > 0:
                        style_str = media_div.get_attribute('style')
                        if style_str:
                            match = re.search(r"url\(['\"]?(.*?)['\"]?\)", style_str)
                            if match:
                                image_url = match.group(1)

                    price = 0
                    price_tag = container.locator('[class*="price"]').first
                    if price_tag.count() > 0:
                        price_text = price_tag.inner_text()
                        match = re.search(r'([\d,]+)', price_text)
                        if match:
                            clean_price = match.group(1).replace(',', '')
                            if clean_price.isdigit():
                                price = int(clean_price)

                    year = 2000
                    info_text = container.inner_text()
                    year_match = re.search(r'(19|20)\d{2}', info_text)
                    if year_match:
                        year = int(year_match.group(0))

                    items.append({
                        'title': title,
                        'price': price,
                        'link': href,
                        'year': year,
                        'image_url': image_url
                    })

                except Exception as e:
                    print(f"Error parsing Cars.bg ad: {e}")
                    continue

            yield items
            time.sleep(2)
            current_page += 1