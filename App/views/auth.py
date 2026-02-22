from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_jwt_extended import (
    jwt_required, current_user, unset_jwt_cookies,
    set_access_cookies, decode_token
)
from App.database import db
from App.models import User
from App.controllers import login
import os
from werkzeug.utils import secure_filename

auth_views = Blueprint('auth_views', __name__, template_folder='../templates')


# ── Page / Action Routes ──────────────────────────────────────────────────────

@auth_views.route('/identify', methods=['GET'])
@jwt_required()
def identify_page():
    return render_template(
        'message.html',
        title="Identify",
        message=f"You are logged in as {current_user.user_id} - {current_user.email}"
    )


@auth_views.route('/login', methods=['POST'])
def login_action():
    data = request.form
    # Login now uses email instead of username
    token = login(data['email'], data['password'])

    if not token:
        flash('Bad email or password given', 'error')
        return redirect(url_for('index_views.index'))

    decoded_token = decode_token(token)
    user_id = int(decoded_token['sub'])
    user = db.session.get(User, user_id)

    flash('Login Successful', 'success')

    if user.role == 'driver':
        response = redirect(url_for('driver_views.driver_homepage'))
    elif user.role == 'owner':
        response = redirect(url_for('index_views.owner_homepage'))
    elif user.role == 'customer':
        response = redirect(url_for('customer_views.customer_homepage'))
    else:
        response = redirect(url_for('index_views.index'))

    set_access_cookies(response, token)
    return response


@auth_views.route('/logout', methods=['GET'])
def logout():
    """Logout the user by clearing JWT cookies"""
    response = redirect(url_for('index_views.index'))
    unset_jwt_cookies(response)
    flash('You have been logged out successfully.', 'success')
    return response


@auth_views.route('/signup', methods=['GET'])
def signup_page():
    """Display the signup page"""
    return render_template('signup.html')


@auth_views.route('/signup', methods=['POST'])
def signup_action():
    """Handle signup form submission"""
    data = request.form
    
    # Validate required fields
    required_fields = ['first_name', 'last_name', 'email', 'username', 'password', 'verify_password']
    for field in required_fields:
        if not data.get(field):
            flash(f'{field.replace("_", " ").title()} is required', 'error')
            return redirect(url_for('auth_views.signup_page'))
    
    # Check if passwords match
    if data['password'] != data['verify_password']:
        flash('Passwords do not match', 'error')
        return redirect(url_for('auth_views.signup_page'))
    
    # Check if email already exists
    existing_user = User.query.filter_by(email=data['email']).first()
    if existing_user:
        flash('Email already registered', 'error')
        return redirect(url_for('auth_views.signup_page'))
    
    # Check if username already exists
    if data.get('username'):
        existing_username = User.query.filter_by(username=data['username']).first()
        if existing_username:
            flash('Username already taken', 'error')
            return redirect(url_for('auth_views.signup_page'))
    
    # Handle profile picture upload (optional)
    profile_picture = None
    if 'profile_picture' in request.files:
        file = request.files['profile_picture']
        if file and file.filename != '':
            filename = secure_filename(file.filename)
            # Create uploads directory if it doesn't exist
            upload_folder = os.path.join('App', 'static', 'uploads', 'profiles')
            os.makedirs(upload_folder, exist_ok=True)
            
            # Save file with unique name
            ext = os.path.splitext(filename)[1]
            unique_filename = f"{data['email'].replace('@', '_').replace('.', '_')}{ext}"
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)
            profile_picture = f"/static/uploads/profiles/{unique_filename}"
    
    # Create new user
    try:
        new_user = User(
            email=data['email'],
            password=data['password'],  # Will be hashed by set_password()
            role='customer',  # All signups are customers
            username=data.get('username'),
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            age=int(data['age']) if data.get('age') else None,
            address=data.get('address'),
            profile_picture=profile_picture
        )
        
        db.session.add(new_user)
        db.session.commit()
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('index_views.index'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error creating account: {str(e)}', 'error')
        return redirect(url_for('auth_views.signup_page'))


# ── API Routes ────────────────────────────────────────────────────────────────

@auth_views.route('/api/login', methods=['POST'])
def user_login_api():
    data = request.json
    token = login(data['email'], data['password'])
    if not token:
        return jsonify(message='Bad email or password given'), 401
    response = jsonify(access_token=token)
    set_access_cookies(response, token)
    return response


@auth_views.route('/api/identify', methods=['GET'])
@jwt_required()
def identify_user():
    return jsonify({
        'message': f"email: {current_user.email}, id: {current_user.user_id}, role: {current_user.role}"
    })