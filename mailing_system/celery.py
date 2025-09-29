import os
from celery import Celery

# Установите модуль настроек Django по умолчанию
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mailing_system.settings')

app = Celery('mailing')

# Используйте строку настроек из Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматическое обнаружение задач из всех приложений Django
app.autodiscover_tasks()

@app.task(bind=True, ignore_result=True)
def debug_task(self):
    print(f'Request: {self.request!r}')
