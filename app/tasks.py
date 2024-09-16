from app import celery
from datetime import datetime, timedelta
from app.models import *
from flask import current_app

@celery.task
def check_and_notify_before_expiry():
    with app.app_context():
        FoodInventory.check_and_notify_expiring_items()

@celery.task
def check_and_notify_after_expiry():
    with app.app_context():
        FoodInventory.check_and_notify_expiring_items(threshold=0)


