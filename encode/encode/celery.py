
import os

from celery import Celery
from django.conf import settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'encode.settings')

app = Celery('encode')

app.config_from_object('django.conf:settings', namespace='CELERY')

from django.apps import apps


app.config_from_object(settings)
app.autodiscover_tasks(lambda: [n.name for n in apps.get_app_configs()])

app.conf.timezone = 'Europe/Moscow'
