from django.core.management.base import BaseCommand
from listings.scrapers.job_scraper import DevBgScraper, JobsBgScraper
from listings.models import JobListing, Search
from django.core.mail import send_mail
from django.conf import settings


class Command(BaseCommand):
    help = 'Scrapes jobs from Dev.bg based on Search entries'

    def handle(self, *args, **kwargs):

        searches = Search.objects.filter(category='job')

        if not searches.exists():
            self.stdout.write(self.style.WARNING("Няма записани търсения за работа! Добави в Админа."))
            return

        for search in searches:
            self.stdout.write(f"--> Processing Jobs: {search.title}")

            if 'dev.bg' in search.url:
                scraper = DevBgScraper(search.url)
            else:
                self.stdout.write(self.style.ERROR(f"   [Грешка] Неподдържан сайт в линка: {search.url}"))
                continue
            items = scraper.run()

            if not items:
                self.stdout.write(self.style.WARNING(f"   No items found for {search.title}"))
                continue

            saved_count = 0


            is_first_run = not search.is_initial_scan_done

            for item in items:
                try:
                    obj, created = JobListing.objects.update_or_create(
                        url=item['link'],
                        defaults={
                            'title': item['title'],
                            'category': 'job',
                            'company_name': item['company'],
                            'location': item['location'],
                            'is_remote': item['remote'],
                            'salary_min': item['salary']
                        }
                    )

                    if created:
                        saved_count += 1


                        if not is_first_run and search.user.email:
                            subject = f"💼 DealTracker: Нова IT позиция за {search.title}"


                            remote_text = " (Remote)" if item['remote'] else ""

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
                except Exception as e:
                    print(f"Error saving job: {e}")

            self.stdout.write(self.style.SUCCESS(f"   Saved {saved_count} new jobs."))


            if is_first_run:
                search.is_initial_scan_done = True
                search.save()
                self.stdout.write(
                    self.style.SUCCESS(f"   [Muted] Initial scan completed. Future updates will trigger emails."))