from django.core.management.base import BaseCommand
from listings.scrapers.job_scraper import DevBgScraper
from listings.models import JobListing, Search


class Command(BaseCommand):
    help = 'Scrapes jobs from Dev.bg based on Search entries'

    def handle(self, *args, **kwargs):
        # Търсим само търсения за РАБОТА ('job')
        searches = Search.objects.filter(category='job')

        if not searches.exists():
            self.stdout.write(self.style.WARNING("Няма записани търсения за работа! Добави в Админа."))
            return

        for search in searches:
            self.stdout.write(f"--> Processing Jobs: {search.title}")

            scraper = DevBgScraper(search.url)
            items = scraper.run()

            if not items:
                continue

            saved_count = 0
            for item in items:
                try:
                    obj, created = JobListing.objects.update_or_create(
                        url=item['link'],
                        defaults={
                            'title': item['title'],
                            'category': 'job',
                            # Специфичните полета за JobListing:
                            'company_name': item['company'],
                            'location': item['location'],
                            'is_remote': item['remote'],
                            'salary_min': item['salary']
                        }
                    )
                    if created:
                        saved_count += 1
                except Exception as e:
                    print(f"Error saving job: {e}")

            self.stdout.write(self.style.SUCCESS(f"   Saved {saved_count} new jobs."))