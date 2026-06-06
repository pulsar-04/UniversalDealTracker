from django.core.management.base import BaseCommand
from listings.scrapers.car_scraper import MobileBgScraper, CarsBgScraper
from listings.models import CarListing, Search
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Scrapes cars based on saved Searches in database'

    def handle(self, *args, **kwargs):
        searches = Search.objects.filter(category='car')

        if not searches.exists():
            self.stdout.write(self.style.WARNING("No searches found in database! Go to Admin and add one."))
            return

        self.stdout.write(f"Found {searches.count()} active searches. Starting job...")

        for search in searches:
            self.stdout.write(f"--> Processing: {search.title}")

            if 'mobile.bg' in search.url:
                scraper = MobileBgScraper(search.url)
            elif 'cars.bg' in search.url:
                scraper = CarsBgScraper(search.url)
            else:
                self.stdout.write(self.style.ERROR(f"   [Грешка] Неподдържан сайт в линка: {search.url}"))
                continue
            # ------------------------------------------------------
            items = scraper.run()

            if not items:
                self.stdout.write(self.style.WARNING(f"   No items found for {search.title}"))
                continue

            saved_count = 0

            is_first_run = not search.is_initial_scan_done

            for item in items:
                try:
                    obj, created = CarListing.objects.update_or_create(
                        url=item['link'],
                        defaults={
                            'title': item['title'],
                            'price': item['price'],
                            'year': item['year'],
                            'category': 'car',
                            'brand': search.brand if search.brand else 'Unknown',
                            'model': search.model if search.model else 'Unknown',
                            'kilometers': 0,
                            'fuel_type': 'Unknown'
                        }
                    )

                    if created:
                        saved_count += 1


                        if not is_first_run and search.user.email:
                            subject = f"🚀 DealTracker: Нова обява за {search.title}"
                            message = f"""
                            Здравей, {search.user.username}!

                            Роботът току-що откри нова обява, която отговаря на твоето търсене "{search.title}":

                            🚗 Автомобил: {item['title']}
                            💰 Цена: {item['price']} лв/евро
                            📅 Година: {item['year']}

                            Виж я веднага тук: {item['link']}

                            Поздрави,
                            DealTracker Bot 🤖
                            """

                            send_mail(
                                subject=subject,
                                message=message,
                                from_email=settings.DEFAULT_FROM_EMAIL,
                                recipient_list=[search.user.email],
                                fail_silently=True
                            )
                except Exception as e:
                    print(f"Error saving: {e}")

            self.stdout.write(self.style.SUCCESS(f"   Saved {saved_count} new cars for '{search.title}'"))

            if is_first_run:
                search.is_initial_scan_done = True
                search.save()
                self.stdout.write(
                    self.style.SUCCESS(f"   [Muted] Initial scan completed. Future updates will trigger emails."))