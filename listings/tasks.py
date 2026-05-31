from celery import shared_task
from django.core.management import call_command
import logging

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