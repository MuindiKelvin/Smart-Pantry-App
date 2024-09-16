from flask import Blueprint, render_template, request, redirect, url_for, Response, flash,session
from app.models import *

discover = Blueprint('discover', __name__, template_folder='templates')

@discover.route('/')
def index():
    if session.get('logged_in'):
        return redirect(url_for('discover.get_shared_food_by_zip'))
    return render_template('auth/login.html')

@discover.route('/shared-items', methods=['GET'])
def get_shared_food_by_zip():
    if session.get('logged_in'):
        user_id = session.get('user_id')
        user = User.query.get(user_id)
        zip_code = user.zip_code
        shared_food_items = SharedFood.find_shared_food_by_zip_and_status(user_id, zip_code)
        num_items = len(shared_food_items)
        # return jsonify(shared_food_items)
        return render_template('discover.html', shared_food_items=shared_food_items, num_items = num_items)

@discover.route('/claim-shared-food/<int:share_id>', methods=['GET'])
def claim_shared_food(share_id):
    if not session.get('logged_in'):
        flash('You need to be logged in to claim food', 'warning')
        return redirect(url_for('auth.index'))

    user_id = session.get('user_id')
    shared_food = SharedFood.query.get(share_id)
    if not shared_food or shared_food.status == 'Unavailable':
        flash('This food item is not available for claim', 'warning')
        return redirect(url_for('discover.index'))

    if SharedFoodClaims.create_new_claim(share_id, user_id):
        flash('You have successfully claimed the food item', 'success')
    else:
        flash('Failed to claim the food item', 'error')

    return redirect(url_for('discover.index'))
    
@discover.route('/unclaim-food', methods=['POST'])
def unclaim_food():
    if not session.get('logged_in'):
        flash('You need to be logged in to unclaim food', 'warning')
        return redirect(url_for('discover.index'))
    claim_id = request.form.get('claim_id')
    # Fetch the claim record from the database
    claim = SharedFoodClaims.query.get(claim_id)
    if not claim:
        flash('Claim record not found', 'warning')
        return redirect(url_for('discover.index'))
    # Check if the current user is the one who made the claim
    if claim.claimer_user_id != session.get('user_id'):
        flash('You are not authorized to unclaim this food item', 'danger')
        return redirect(url_for('discover.index'))
    # Delete the claim record
    db.session.delete(claim)
    db.session.commit()
    flash('You have successfully unclaimed the food item', 'success')
    return redirect(url_for('discover.index'))