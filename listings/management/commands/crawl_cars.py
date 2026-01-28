from django.core.management.base import BaseCommand
from listings.scrapers.car_scraper import MobileBgScraper
from listings.models import CarListing, Search


class Command(BaseCommand):
    help = 'Scrapes cars based on saved Searches in database'

    def handle(self, *args, **kwargs):

        searches = Search.objects.filter(category='car')

        if not searches.exists():
            self.stdout.write(self.style.WARNING("No searches found in database! Go to Admin and add one."))
            return

        self.stdout.write(f"Found {searches.count()} active searches. Starting job...")

        # 2. Въртим цикъл през всяко търсене
        for search in searches:
            self.stdout.write(f"--> Processing: {search.title}")

            scraper = MobileBgScraper(search.url)
            items = scraper.run()

            if not items:
                self.stdout.write(self.style.WARNING(f"   No items found for {search.title}"))
                continue

            saved_count = 0
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
                except Exception as e:
                    print(f"Error saving: {e}")

            self.stdout.write(self.style.SUCCESS(f"   Saved {saved_count} new cars for '{search.title}'"))