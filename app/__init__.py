from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
from app.config import *
from flask_mail import Mail, Message
import os
from flask import jsonify
from celery import Celery


app = Flask(__name__)

#set secret key
app.config['SECRET_KEY'] = '12345'

#DB Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{DB_CONF["username"]}:{DB_CONF["password"]}@{DB_CONF["host"]}/{DB_CONF["dbname"]}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

#MAIL Configurations
app.config['MAIL_SERVER'] = EMAIL_CONF['mailserver']
app.config['MAIL_PORT'] = EMAIL_CONF['mailport']
app.config['MAIL_USERNAME'] = EMAIL_CONF['mailusername']
app.config['MAIL_PASSWORD'] = EMAIL_CONF['mailpassword']
app.config['MAIL_USE_TLS'] = EMAIL_CONF['mailuse_tls']
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)

#UPLOAD Configurations
app.config['UPLOAD_FOLDER'] = os.path.join('app', 'static', 'img')

# register blueprints
from app.Blueprints.auth import auth
from app.Blueprints.foodinventory import food_inventory
from app.Blueprints.yourSharedFood import your_shared_food
from app.Blueprints.discover import discover
from app.Blueprints.notification import notification
# from app.routes import main
# app.register_blueprint(main)
app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(food_inventory, url_prefix='/food-inventory')
app.register_blueprint(your_shared_food, url_prefix='/your-shared-food')
app.register_blueprint(discover, url_prefix='/discover')
app.register_blueprint(notification, url_prefix='/notification')


# celery configurations

def make_celery(app):
    app.config['CELERY_BROKER_URL'] = 'amqp://localhost'
    celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)

    class ContextTask(celery.Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)
            
    celery.Task = ContextTask
    celery.config_from_object('app.celery_config')
    # celery.config_from_object(__name__)
    celery.conf.timezone = 'UTC'
    return celery


celery = make_celery(app)


from app.tasks import check_and_notify_after_expiry, check_and_notify_before_expiry

from app import routes, models