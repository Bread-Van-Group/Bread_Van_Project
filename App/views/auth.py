from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_jwt_extended import (
    jwt_required, current_user, unset_jwt_cookies,
    set_access_cookies, decode_token
)
from App.database import db
from App.models import User
from App.controllers import login
from App.controllers.user import create_customer

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
    response = redirect(url_for('index_views.index'))
    unset_jwt_cookies(response)
    flash('You have been logged out successfully.', 'success')
    return response


@auth_views.route('/signup', methods=['GET'])
def signup_page():
    return render_template('signup.html')


@auth_views.route('/signup', methods=['POST'])
def signup_action():
    data = request.form

    # Validate required fields
    for field in ['first_name', 'last_name', 'email', 'password', 'verify_password']:
        if not data.get(field):
            flash(f'{field.replace("_", " ").title()} is required', 'error')
            return redirect(url_for('auth_views.signup_page'))

    if data['password'] != data['verify_password']:
        flash('Passwords do not match', 'error')
        return redirect(url_for('auth_views.signup_page'))

    # Combine first + last name into the single 'name' field Customer expects
    full_name = f"{data['first_name'].strip()} {data['last_name'].strip()}"

    # create_customer returns None if email already exists
    new_user = create_customer(
        email=data['email'],
        password=data['password'],
        name=full_name,
        address=data.get('address') or None,
        phone=data.get('phone') or None,
    )

    if not new_user:
        flash('An account with that email already exists', 'error')
        return redirect(url_for('auth_views.signup_page'))

    # Log the new user in immediately after signup
    token = login(data['email'], data['password'])
    flash('Account created successfully! Welcome aboard.', 'success')
    response = redirect(url_for('customer_views.customer_homepage'))
    set_access_cookies(response, token)
    return response


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