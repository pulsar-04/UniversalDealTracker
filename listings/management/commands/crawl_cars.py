import logging
import types
from django.core.management.base import BaseCommand
from listings.scrapers.car_scraper import MobileBgScraper, CarsBgScraper
from listings.models import CarListing, Search, PriceHistory
from listings.tasks import send_deal_email_task
from django.conf import settings

logger = logging.getLogger('scrapers')


class Command(BaseCommand):
    help = 'Scrapes cars based on saved Searches in database'

    def handle(self, *args, **kwargs):
        searches = Search.objects.filter(category='car', is_paused=False)

        if not searches.exists():
            logger.warning("No searches found in database! Go to Admin and add one.")
            return

        logger.info(f"Found {searches.count()} active searches. Starting job...")

        for search in searches:
            logger.info(f"--> Processing: {search.title} [Playwright Engine]")

            if 'mobile.bg' in search.url:
                scraper = MobileBgScraper(search.url)
            elif 'cars.bg' in search.url:
                scraper = CarsBgScraper(search.url)
            else:
                logger.error(f"   [Грешка] Неподдържан сайт в линка: {search.url}")
                continue

            results = scraper.run()

            if isinstance(results, types.GeneratorType):
                pages = results
            else:
                pages = [results] if results else []

            saved_count = 0
            is_first_run = not search.is_initial_scan_done

            for page_items in pages:
                if not page_items:
                    continue

                for item in page_items:
                    try:
                        car = CarListing.objects.filter(url=item['link']).first()
                        new_price = item['price']

                        if not car:
                            car = CarListing.objects.create(
                                url=item['link'],
                                title=item['title'],
                                price=new_price,
                                year=item['year'],
                                category='car',
                                brand=search.brand if search.brand else 'Unknown',
                                model=search.model if search.model else 'Unknown',
                                kilometers=0,
                                fuel_type='Unknown',
                                image_url=item.get('image_url')
                            )
                            saved_count += 1

                            if new_price:
                                PriceHistory.objects.create(listing=car, price=new_price)

                            if not is_first_run and search.user.email and hasattr(search.user,
                                                                                  'profile') and search.user.profile.receive_emails:
                                subject = f"🚀 DealTracker: Нова обява за {search.title}"
                                message = f"Здравей, {search.user.username}!\n\nРоботът откри нова обява:\n🚗 {item['title']}\n💰 {item['price']} лв\n\nЛинк: {item['link']}"
                                send_deal_email_task.delay(
                                    subject,
                                    message,
                                    settings.DEFAULT_FROM_EMAIL,
                                    [search.user.email]
                                )

                        else:
                            old_price = car.price
                            car.title = item['title']
                            car.price = new_price
                            if item.get('image_url'):
                                car.image_url = item.get('image_url')
                            car.save()

                            if old_price != new_price and new_price:
                                PriceHistory.objects.create(listing=car, price=new_price)
                                logger.warning(f"   [Price Change] {car.title}: {old_price} -> {new_price}")

                    except Exception as e:
                        logger.error(f"Error saving car: {e}", exc_info=True)

            logger.info(f"   Saved {saved_count} new cars for '{search.title}'")

            if is_first_run:
                search.is_initial_scan_done = True
                search.save()
                logger.info(f"   [Muted] Initial scan completed. Future updates will trigger emails.")