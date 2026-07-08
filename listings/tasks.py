from celery import shared_task
from django.core.management import call_command
import logging
from django.core.mail import send_mail

logger = logging.getLogger(__name__)

@shared_task
def auto_crawl_cars():
    logger.info("Starting automated car scrape...")
    call_command('crawl_cars')
    return "Car scrape completed."

@shared_task
def auto_crawl_jobs():
    logger.info("Starting automated job scrape...")
    call_command('crawl_jobs')
    return "Job scrape completed."


@shared_task
def send_deal_email_task(subject, message, from_email, recipient_list):
    """
    Асинхронна Celery задача за изпращане на имейли.
    """
    try:
        send_mail(
            subject=subject,
            message=message,
            from_email=from_email,
            recipient_list=recipient_list,
            fail_silently=False
        )
        logger.info(f"Успешно изпратен мейл до {recipient_list}")
    except Exception as e:
        logger.error(f"Грешка при изпращане на мейл до {recipient_list}: {e}")