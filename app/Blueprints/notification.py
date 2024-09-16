from flask import Blueprint, render_template, request, redirect, url_for, Response, flash, session, g
from app.models import *

notification = Blueprint('notification', __name__, template_folder='templates')

@notification.before_app_request
def get_unread_count():
    if session.get('logged_in'):
        user_id = session['user_id'] 
        unread_count = Notification.query.filter_by(user_id=user_id, status='Unread').count()
        g.unread_count = unread_count

@notification.route('/notifications')
def index():
    if session.get('logged_in'):
        user_id = session['user_id']  # Assuming you have a user_id stored in the session
        notifications = Notification.get_notifications_for_user(user_id)
        return render_template('notification.html', notifications=notifications)
    return render_template('auth/login.html')

@notification.route('/mark_as_read/<int:notification_id>')
def mark_as_read(notification_id):
    # Update the notification status to 'Read' for the given notification_id
    notification = Notification.query.get(notification_id)
    if notification:
        notification.status = 'Read'
        db.session.commit()
        flash('Notification marked as read', 'success')
    return redirect(url_for('notification.index'))

@notification.route('/delete_notification/<int:notification_id>')
def delete_notification(notification_id):
    # Delete the notification for the given notification_id
    notification = Notification.query.get(notification_id)
    if notification:
        db.session.delete(notification)
        db.session.commit()
        flash('Notification deleted', 'success')
    return redirect(url_for('notification.index'))