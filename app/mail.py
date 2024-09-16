from flask import render_template, url_for, session
from flask_mail import Message
from app import *
from app.models import *

def send_reset_email(user):
    token = user.get_reset_token()
    msg = Message()
    msg.subject = "SmartPantry Password Reset Request"
    msg.sender = EMAIL_CONF['mailusername']
    msg.recipients = [user.email]
    msg.body = f"Hi\n\nWe have received a request to reset your Smart Pantry password. To do this, please click on the link below:\n\n{url_for('auth.reset_password', token=token, _external=True)}\nThis link is valid for the next 1 hours.\nIf you did not intend to reset your password, please ignore this email and your password will not change.\n\nThanks\n\nThe SmartPantry team"
    mail.send(msg)


def send_expiry_reminder():
    pass
