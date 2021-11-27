import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'csv_data_gen.settings')

app = Celery('csv_celery')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
