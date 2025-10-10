# celery_setup.py (для будущего использования)
"""
Инструкция по настройке Celery:

1. Раскомментировать в settings.py:
   - CELERY_BROKER_URL
   - CELERY_RESULT_BACKEND
   - CELERY_BEAT_SCHEDULE

2. Запустить Redis:
   redis-server --port 6380

3. Запустить Celery worker:
   celery -A mailing_system worker --loglevel=info --pool=solo

4. Запустить Celery beat:
   celery -A mailing_system beat --loglevel=info
"""
