import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'doctor_appointment.settings')

app = Celery('doctor_appointment')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
