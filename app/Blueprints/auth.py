from flask import Blueprint, render_template, request, redirect, url_for, Response, flash,session
from app.models import *
from werkzeug.security import generate_password_hash, check_password_hash
from app.mail import *

auth = Blueprint('auth', __name__, template_folder='templates/auth')

@auth.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':

        if request.form.get('form_type') == 'register':
            # Handle registration form submission
            fname = request.form.get('fname')
            lname = request.form.get('lname')
            address = request.form.get('address')
            city = request.form.get('city')
            state = request.form.get('state')
            zip_code = request.form.get('zip')
            email = request.form.get('email')
            username = request.form.get('username')
            password = request.form.get('password')

            hashed_password = generate_password_hash(password)
            

            # Check if user already exists
            user = User.query.filter(or_(User.email == email, User.username == username)).first()


            if user:
                if user.email == email and user.username == username:
                    message = 'Email address and username already exist!'
                elif user.email == email:
                    message = 'Email address already exists!'
                elif user.username == username:
                    message = 'Username already exists!'
                else:
                    message = "An error occured while processing your request. Please try again later."
                return render_template('auth/login.html', message = message, user=user)

            new_user = User(
                first_name=fname,
                last_name=lname,
                address=address,
                city=city,
                state=state,
                zip_code=zip_code,
                email=email,
                username=username,
                password=hashed_password
            )

            db.session.add(new_user)
            db.session.commit()

            flash('Registration successful')
            return redirect(url_for('auth.index'))
        
        elif request.form.get('form_type') == 'login':
            email = request.form.get('email')
            password = request.form.get('password')

            if email and password:
                user = User.query.filter_by(email=email).first()
                if user and check_password_hash(user.password, password):
                    session['logged_in'] = True
                    session['user_id'] = user.user_id
                    session['first_name'] = user.first_name
                    return redirect(url_for('index'))
                else:
                    return render_template('auth/login.html', message='Invalid email or password', session=session.get('logged_in'))
    return render_template('auth/login.html')


@auth.route('/logout')
def logout():
    session['logged_in'] = False
    session['user_id'] = None
    session['first_name'] = None
    return redirect(url_for('index'))


@auth.route("/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('forgot_password_email')
        user = User.query.filter_by(email=email).first()
        print(user)
        if user:
            send_reset_email(user)
            flash('An email has been sent with instructions to reset your password.')
            print("Success")
            return redirect(url_for('auth.index'))
        else:
            flash('Email address not found')
            print("Failed")
            return redirect(url_for('auth.forgot_password'))
    return render_template('auth/forgot-password.html')  


@auth.route("/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    user = User.verify_reset_token(token)
    if not user:
        flash('Invalid or expired token')
        print("No user")
        return redirect(url_for('auth.index'))
    if request.method == 'POST':
        password = request.form.get('new-password')
        hashed_password = generate_password_hash(password, method='sha256')
        user.password = hashed_password
        db.session.commit()
        flash('Your password has been updated! You are now able to log in')
        return redirect(url_for('auth.index'))
    return render_template('auth/reset-password.html', token=token) 

