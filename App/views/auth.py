from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_jwt_extended import (
    jwt_required, current_user, unset_jwt_cookies,
    set_access_cookies, decode_token
)
from App.database import db
from App.models import User
from App.controllers import login

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
        response = redirect(url_for('index_views.customer_homepage'))
    else:
        response = redirect(url_for('index_views.index'))

    set_access_cookies(response, token)
    return response


@auth_views.route('/logout', methods=['GET'])
def logout_action():
    response = redirect(url_for('index_views.index'))
    flash("Logged Out!", 'info')
    unset_jwt_cookies(response)
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


@auth_views.route('/api/logout', methods=['GET'])
def logout_api():
    response = jsonify(message="Logged Out!")
    unset_jwt_cookies(response)
    return response
