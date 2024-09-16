import os
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from app.models import *

food_inventory = Blueprint('foodinventory', __name__, template_folder='templates')

@food_inventory.route('/add-food-item', methods=['GET', 'POST'])
def add_food_item():
    if request.method == 'POST':
        user_id = session['user_id']
        category_id = request.form.get('category_id')
        food_name = request.form.get('food_name')
        expiration_date = request.form.get('expiration_date')
        quantity = request.form.get('quantity')
        memo = request.form.get('memo')
        # Using the model's classmethod to create and save the new food item
        new_food_item = FoodInventory.create_new(
            user_id=user_id,
            category_id=category_id,
            food_name=food_name,
            expiration_date=expiration_date,
            quantity=quantity,
            memo=memo
        )
        # Using the model's classmethod to save the image
        file = request.files.get('food_image')
        image_url = request.form.get('food_image_url')
        if file:
            FoodImage.save_image(food_id=new_food_item.food_id, file=file, upload_folder=app.config['UPLOAD_FOLDER'])
        elif image_url:
            FoodImage.save_image(food_id=new_food_item.food_id, image_url=image_url, upload_folder=app.config['UPLOAD_FOLDER'])
        flash('Food item added successfully')
        return redirect(url_for('index'))
    categories = FoodCategory.query.all()
    return render_template('index.html', categories=categories)

@food_inventory.route('/dashboard')
def dashboard():
    if session.get('logged_in'):
        user_id = session['user_id']
        # Fetch food categories
        food_categories = FoodCategory.query.filter((FoodCategory.user_id == user_id) | (FoodCategory.user_id == None)).all()
        # Fetch food items for each category
        for category in food_categories:
            category.food_items = FoodInventory.fetch_user_inventory_for_category(user_id, category.category_id)
        # Fetch inventory analytics
        inventory_analytics = FoodInventory.fetch_inventory_analytics(user_id)
        print(inventory_analytics)
        return render_template('index.html', food_categories=food_categories, inventory_analytics=inventory_analytics)
    return redirect(url_for('index'))

@food_inventory.route('/add-category', methods=['GET', 'POST'])
def add_category():
    if request.method == 'POST':
        category_name = request.form.get('category_name').strip()
        user_id = session.get('user_id') 
        if user_id is None:
            flash('You need to be logged in to add a category.')
            return redirect(url_for('auth.index')) 
        new_category = FoodCategory(category_name=category_name, user_id=user_id)
        db.session.add(new_category)
        db.session.commit()
        flash('Category added successfully')
        return redirect(url_for('index'))
    return redirect(url_for('index'))

@food_inventory.route('/delete-category' , methods=['GET', 'POST'])
def delete_category():
    category_id = int(request.form.get('category_id'))
    category = FoodCategory.query.get(category_id)
    if category:
        db.session.delete(category)
        db.session.commit()
    flash('Category deleted successfully')
    return redirect(url_for('index'))

@food_inventory.route('/delete-food-item', methods=['GET', 'POST'])
def delete_food_item():
    food_id = request.form.get('food_id')
    food_id = int(food_id)
    success = FoodInventory.delete_with_images(food_id)
    if success:
        flash('Food item and images have been deleted.', 'success')
    else:
        flash('Food item could not be found.', 'error')
    return redirect(url_for('index'))

@food_inventory.route('/get-food-item/<id>', methods=['GET'])
def get_food_item(id):
    food_item = FoodInventory.query.get_or_404(id)
    return jsonify({
        'food_name': food_item.food_name,
        'expiration_date': food_item.expiration_date.strftime('%Y-%m-%d'),
        'category_id': food_item.category_id,
        'quantity': food_item.quantity,
        'memo': food_item.memo,
    })

@food_inventory.route('/edit-food-item/<int:id>', methods=['GET', 'POST'])
def edit_food_item(id):
    food_item = FoodInventory.query.get_or_404(id)
    food_item.food_name = request.form.get('food_name')
    food_item.quantity = request.form.get('quantity')
    food_item.expiration_date = request.form.get('expiration_date')
    food_item.memo = request.form.get('memo')

    file = request.files.get('food_image')
    if file and FoodImage.allowed_file(file.filename):
        existing_image = FoodImage.query.filter_by(food_id=id).first()
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], 'food_images', filename)
        file.save(file_path)

        relative_image_path = os.path.join('img','food_images', filename)
        print(file_path)

        if existing_image:
            existing_image.image_path = relative_image_path
        else:
            new_image = FoodImage(food_id=id, image_path=relative_image_path)
            db.session.add(new_image)
    
    db.session.commit()
    return redirect(url_for('index'))

@food_inventory.route("/mark-as-consumed", methods=['POST'])
def mark_as_consumed():
    food_id = request.form.get('food_id')
    if food_id:
        food_item = FoodInventory.query.get(food_id)
        if food_item:
            food_item.mark_as_consumed()
            flash('Food item marked as consumed.', 'success')
        else:
            flash('Food item not found.', 'error')
    else:
        flash('No food ID provided.', 'error')
    return redirect(url_for('index'))

@food_inventory.route("/mark-as-expired", methods=['POST'])
def mark_as_expired():
    food_id = request.form.get('food_id')
    if food_id:
        food_item = FoodInventory.query.get(food_id)
        if food_item:
            food_item.mark_as_expired()
            flash('Food item marked as expired.', 'success')
        else:
            flash('Food item not found.', 'error')
    else:
        flash('No food ID provided.', 'error')
    return redirect(url_for('index'))
