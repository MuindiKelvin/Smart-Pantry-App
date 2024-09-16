from celery.schedules import crontab
from datetime import datetime, timedelta

schedule_time = datetime.utcnow() + timedelta(seconds=8)


CELERY_BROKER_URL = 'amqp://localhost'
CELERY_RESULT_BACKEND = 'rpc://'
CELERYBEAT_SCHEDULE = {
    'check-expiring-items-before-expire': {
        'task': 'app.tasks.check_and_notify_before_expiry',
        'schedule': crontab(minute=schedule_time.minute),
    },
    'check-expiring-items-expiry-date': {
        'task': 'app.tasks.check_and_notify_after_expiry',
        'schedule': crontab(minute=schedule_time.minute),
    },
}

