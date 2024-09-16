from flask import Blueprint, render_template, request, redirect, url_for, Response, flash, session, abort, jsonify
from app.models import *

your_shared_food = Blueprint('yourSharedFood', __name__, template_folder='templates')

@your_shared_food.route('/')
def index():
    if session.get('logged_in'):
        user_id = session['user_id']
        user_claims = SharedFoodClaims.get_user_claims(user_id)
        shared_items = SharedFood.get_user_shared_items(user_id)
        shared_items_list = [
            {'share_id': item[0], 'title': item[1], 'description': item[2], 'quantity': item[3], 'food_name': item[4], 'expiration_date': item[5], 'status' : item[6]}
            for item in shared_items
        ]
        return render_template('your-shared-food.html', shared_items=shared_items_list, user_claims=user_claims)
    return render_template('auth/login.html')

@your_shared_food.route('/dashboard')
def dashboard():
    pass

@your_shared_food.route('/share-food', methods=['GET', 'POST'])
def share_food():
    if request.method == 'POST':
        food_id = request.form.get('food_id')
        post_title = request.form.get('post_title')
        description = request.form.get('description')
        status = 'Shared' 
        quantity_to_share = int(request.form.get('quantity'))
        available_quantity = int(request.form.get('available_quantity'))
        # quantity_being_shared = SharedFood.get_total_quantity_being_shared(food_id)
        expiry_date = FoodInventory.query.filter(FoodInventory.food_id == food_id).first().expiration_date

        # check if food has expired
        if expiry_date and expiry_date < date.today():
            flash('You cannot share an expired food item')
            return redirect(url_for('foodinventory.dashboard'))

        if quantity_to_share > available_quantity:
            flash('You have already shared all the available quantity for this food item')
            return redirect(url_for('foodinventory.dashboard'))
        
        available_quantity = available_quantity - quantity_to_share
        FoodInventory.query.filter(FoodInventory.food_id == food_id).update({'quantity': available_quantity})

        new_shared_food = SharedFood.create_new(
            food_id=food_id,
            status=status,
            title=post_title,
            description=description,
            quantity=quantity_to_share
        )
        return redirect(url_for('foodinventory.dashboard'))

@your_shared_food.route("/unshare-food", methods=['GET', 'POST'])
def unshare_food():
    if request.method == 'POST':
        share_id = request.form.get('share_id')
        shared_item = SharedFood.query.filter(SharedFood.share_id == share_id).first()
        food_id = shared_item.food_id
        quantity_to_unshare = shared_item.quantity
        available_quantity = FoodInventory.query.filter(FoodInventory.food_id == food_id).first().quantity
        available_quantity = available_quantity + quantity_to_unshare
        FoodInventory.query.filter(FoodInventory.food_id == food_id).update({'quantity': available_quantity})
        SharedFoodClaims.query.filter(SharedFoodClaims.share_id == share_id).delete()
        SharedFood.query.filter(SharedFood.share_id == share_id).delete()
        db.session.commit()
        return redirect(url_for('yourSharedFood.index'))

@your_shared_food.route("/get-shared-item/<id>", methods=['GET', 'POST'])
def get_shared_item(id):
    shared_item = SharedFood.query.filter(SharedFood.share_id == id).first()
    shared_item_dict = {
        'share_id': shared_item.share_id,
        'title': shared_item.title,
        'description': shared_item.description,
        'quantity': shared_item.quantity
    }
    return jsonify(shared_item_dict)


@your_shared_food.route("/edit-share/<int:share_id>", methods=['GET', 'POST'])
def edit_share(share_id):
    if request.method == 'POST':
        post_title = request.form.get('post_title')
        description = request.form.get('description')
        quantity_to_share_now = int(request.form.get('quantity'))

        shared_item = SharedFood.query.filter(SharedFood.share_id == share_id).first()
        quantity_currently_shared = shared_item.quantity
        food_id = shared_item.food_id
        available_quantity = FoodInventory.query.filter(FoodInventory.food_id == food_id).first().quantity
        
        quantity_to_share_now = quantity_to_share_now if quantity_to_share_now <= available_quantity + quantity_currently_shared else available_quantity + quantity_currently_shared
        available_quantity = available_quantity + quantity_currently_shared - quantity_to_share_now
        FoodInventory.query.filter(FoodInventory.food_id == food_id).update({'quantity': available_quantity})
        SharedFood.query.filter(SharedFood.share_id == share_id).update({'title': post_title, 'description': description, 'quantity': quantity_to_share_now})
        db.session.commit()
        return redirect(url_for('yourSharedFood.index'))
    return redirect(url_for('yourSharedFood.index'))


@your_shared_food.route("/get-claims/<int:share_id>", methods=['GET', 'POST'])
def get_claims(share_id):
    logged_in_user_id = session.get('user_id')
    shared_food = db.session.query(FoodInventory.user_id).join(SharedFood, FoodInventory.food_id == SharedFood.food_id).filter(SharedFood.share_id == share_id).first()
    if not shared_food:
        abort(404, description="Shared food item not found.")
    sharer_user_id = shared_food.user_id
    if logged_in_user_id != sharer_user_id:
        abort(403, description="Access denied.")
    claim_details = SharedFoodClaims.get_claim_details_by_share_id(share_id)
    return jsonify(claim_details)


@your_shared_food.route("/approve-claim/<claim_id>", methods=['GET', 'POST'])
def approve_claim(claim_id):
    logged_in_user_id = session.get('user_id')
    claim = SharedFoodClaims.query.get(claim_id)
    # share_id =
    if not claim:
        abort(404, description="Claim record not found.")
    sharer_user_id = FoodInventory.query.filter(FoodInventory.food_id == SharedFood.query.filter(SharedFood.share_id == claim.share_id).first().food_id).first().user_id
    if logged_in_user_id != sharer_user_id:
        abort(403, description="Access denied.")
    SharedFoodClaims.query.filter(SharedFoodClaims.claim_id == claim_id).update({'claimfoodstatus': 1})
    SharedFood.query.filter(SharedFood.share_id == claim.share_id).update({'status': 'Claimed'})
    db.session.commit()
    return redirect(url_for('yourSharedFood.index'))


@your_shared_food.route('/unclaim-food', methods=['POST'])
def unclaim_food():
    if not session.get('logged_in'):
        flash('You need to be logged in to unclaim food', 'warning')
        return redirect(url_for('yourSharedFood.index'))
    claim_id = request.form.get('claim_id')
    # Fetch the claim record from the database
    claim = SharedFoodClaims.query.get(claim_id)
    if not claim:
        flash('Claim record not found', 'warning')
        return redirect(url_for('yourSharedFood.index'))
    # Check if the current user is the one who made the claim
    if claim.claimer_user_id != session.get('user_id'):
        flash('You are not authorized to unclaim this food item', 'danger')
        return redirect(url_for('yourSharedFood.index'))
    # Delete the claim record
    db.session.delete(claim)
    db.session.commit()
    flash('You have successfully unclaimed the food item', 'success')
    return redirect(url_for('yourSharedFood.index'))