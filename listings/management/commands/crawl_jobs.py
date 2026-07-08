import logging
import types
from django.core.management.base import BaseCommand
from listings.scrapers.job_scraper import DevBgScraper
from listings.models import JobListing, Search
from listings.tasks import send_deal_email_task
from django.conf import settings

logger = logging.getLogger('scrapers')

class Command(BaseCommand):
    help = 'Scrapes jobs from Dev.bg based on Search entries'

    def handle(self, *args, **kwargs):
        searches = Search.objects.filter(category='job', is_paused=False)

        if not searches.exists():
            return

        for search in searches:
            if 'dev.bg' in search.url:
                scraper = DevBgScraper(search.url)
            else:
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
                        job = JobListing.objects.filter(url=item['link']).first()

                        if not job:
                            job = JobListing.objects.create(
                                url=item['link'],
                                title=item['title'],
                                category='job',
                                company_name=item['company'],
                                location=item['location'],
                                is_remote=item['remote'],
                                salary_min=item['salary'],
                                search=search,
                                image_url=item.get('image_url')
                            )
                            saved_count += 1

                            if not is_first_run and search.user.email and hasattr(search.user, 'profile') and search.user.profile.receive_emails:
                                subject = f"💼 DealTracker: Нова IT позиция за {search.title}"
                                message = f"Здравей!\n\nНова позиция:\n🏢 {item['company']}\n📌 {item['title']}\n\nЛинк: {item['link']}"
                                send_deal_email_task.delay(
                                    subject,
                                    message,
                                    settings.DEFAULT_FROM_EMAIL,
                                    [search.user.email]
                                )
                        else:
                            job.title = item['title']
                            job.company_name = item['company']
                            job.location = item['location']
                            job.is_remote = item['remote']
                            if item.get('image_url'):
                                job.image_url = item.get('image_url')
                            job.save()

                    except Exception as e:
                        logger.error(f"Error saving job: {e}")

            if is_first_run:
                search.is_initial_scan_done = True
                search.save()