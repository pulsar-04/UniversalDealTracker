import logging
from django.core.management.base import BaseCommand
from listings.scrapers.job_scraper import DevBgScraper
from listings.models import JobListing, Search
from django.core.mail import send_mail
from django.conf import settings


logger = logging.getLogger('scrapers')

class Command(BaseCommand):
    help = 'Scrapes jobs from Dev.bg based on Search entries'

    def handle(self, *args, **kwargs):
        searches = Search.objects.filter(category='job')

        if not searches.exists():
            logger.warning("Няма записани търсения за работа! Добави в Админа.")
            return

        logger.info(f"Found {searches.count()} active job searches. Starting job...")

        for search in searches:
            logger.info(f"--> Processing Jobs: {search.title}")

            if 'dev.bg' in search.url:
                scraper = DevBgScraper(search.url)
            else:
                logger.error(f"   [Грешка] Неподдържан сайт в линка: {search.url}")
                continue

            items = scraper.run()

            if not items:
                logger.warning(f"   No items found for {search.title}")
                continue

            saved_count = 0
            is_first_run = not search.is_initial_scan_done

            for item in items:
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
                            search=search
                        )
                        saved_count += 1

                        if not is_first_run and search.user.email and hasattr(search.user, 'profile') and search.user.profile.receive_emails:
                            remote_text = " (Remote)" if item['remote'] else ""
                            subject = f"💼 DealTracker: Нова IT позиция за {search.title}"
                            message = f"""
                            Здравей, {search.user.username}!

                            Роботът току-що откри нова позиция, която отговаря на твоето търсене "{search.title}":

                            🏢 Компания: {item['company']}
                            📌 Позиция: {item['title']}
                            📍 Локация: {item['location']}{remote_text}

                            Виж обявата веднага тук: {item['link']}

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
                    else:
                        job.title = item['title']
                        job.company_name = item['company']
                        job.location = item['location']
                        job.is_remote = item['remote']
                        job.search = search
                        job.save()

                except Exception as e:
                    logger.error(f"Error saving job: {e}", exc_info=True)

            logger.info(f"   Saved {saved_count} new jobs for '{search.title}'")

            if is_first_run:
                search.is_initial_scan_done = True
                search.save()
                logger.info(f"   [Muted] Initial scan completed. Future updates will trigger emails.")