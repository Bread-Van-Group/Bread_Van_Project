from flask import Blueprint, render_template, jsonify, request, flash, redirect, url_for
from flask_jwt_extended import jwt_required, current_user as jwt_current_user
from .index import index_views
from App.controllers import (
    get_all_users,
    get_all_users_json,
    create_customer,
    create_driver,
    create_owner,
)

user_views = Blueprint('user_views', __name__, template_folder='../templates')


# ── Page Routes ───────────────────────────────────────────────────────────────

@user_views.route('/users', methods=['GET'])
@jwt_required()
def get_user_page():
    if jwt_current_user.role != 'owner':
        return redirect(url_for('index_views.index'))
    users = get_all_users()
    return render_template('users.html', users=users)


# ── API Routes ────────────────────────────────────────────────────────────────

@user_views.route('/api/users', methods=['GET'])
@jwt_required()
def get_users_action():
    if jwt_current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403
    return jsonify(get_all_users_json())


@user_views.route('/api/users/customer', methods=['POST'])
def create_customer_endpoint():
    data = request.json
    user = create_customer(
        email=data['email'],
        password=data['password'],
        name=data['name'],
        address=data.get('address'),
        phone=data.get('phone'),
    )
    if not user:
        return jsonify(message='A user with that email already exists'), 400
    return jsonify(user.get_json()), 201


@user_views.route('/api/users/driver', methods=['POST'])
@jwt_required()
def create_driver_endpoint():
    if jwt_current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403
    data = request.json
    user = create_driver(
        email=data['email'],
        password=data['password'],
        name=data['name'],
        address=data.get('address'),
        phone=data.get('phone'),
    )
    if not user:
        return jsonify(message='A user with that email already exists'), 400
    return jsonify(user.get_json()), 201


@user_views.route('/api/users/owner', methods=['POST'])
def create_owner_endpoint():
    data = request.json
    user = create_owner(
        email=data['email'],
        password=data['password'],
    )
    if not user:
        return jsonify(message='A user with that email already exists'), 400
    return jsonify(user.get_json()), 201
