import os
from celery import Celery

# Задаваме пътя до настройките на Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'UniversalDealTracker.settings')

app = Celery('UniversalDealTracker')

# Зареждаме настройките от settings.py, които започват с "CELERY_"
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматично намира задачите (tasks) във всичките ни app-ове
app.autodiscover_tasks()