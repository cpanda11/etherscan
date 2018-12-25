from __future__ import absolute_import

import os

from celery import Celery
from celery.schedules import crontab

from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'etherscan.settings')

# app = Celery('etherscan', broker='amqp://localhost')
app = Celery('etherscan', broker='redis://127.0.0.1')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)
app.conf.update(
    CELERY_BROKER_URL='redis://127.0.0.1',
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],
    CELERY_RESULT_SERIALIZER='json',
    CELERYBEAT_SCHEDULE={
        'scrap_ledu': {
            'task': 'product.tasks.scrap_ledu',
            'schedule': crontab(hour='*', minute='*/61'),
            'args': ()
        },
        'scrap_coinmarketcap': {
            'task': 'coinmarketcap.tasks.scrap_coinmarketcap',
            'schedule': crontab(hour='*', minute='*/1'),
            'args': ()
        },
    }
)
# celery -A etherscan worker -l info --concurrency 5
# celery -A etherscan beat -l info
