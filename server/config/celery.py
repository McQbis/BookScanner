import os
from celery import Celery
from kombu import Queue

CELERY_TASK_QUEUES = (
    Queue('gpu'),
    Queue('cpu'),
)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

app = Celery('project')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()