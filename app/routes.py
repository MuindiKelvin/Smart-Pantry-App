from flask import Blueprint, render_template, flash, redirect, request, url_for,session
from app import app
from app.models import *

# main = Blueprint('main', __name__, template_folder='templates')

# @app.route('/')
# def index():
#     if session.get('logged_in'):
#         user_id = session['user_id']
#         food_categories = FoodCategory.query.all()
#         for category in food_categories:
#             category.food_items = FoodInventory.fetch_user_inventory_for_category(user_id, category.category_id)
#         return render_template('index.html', food_categories=food_categories)
#     return render_template('auth/login.html')

@app.route('/')
def index():
    if session.get('logged_in'):
        return redirect(url_for('foodinventory.dashboard'))
    return render_template('auth/login.html')