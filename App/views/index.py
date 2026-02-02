from flask import Blueprint, redirect, render_template, request, send_from_directory, jsonify, url_for
from flask_jwt_extended import jwt_required, current_user, verify_jwt_in_request
from App.controllers import create_user, initialize

index_views = Blueprint('index_views', __name__, template_folder='../templates')

@index_views.route('/', methods=['GET'])
def index():
    # Check if user is already logged in
    try:
        verify_jwt_in_request()
        # User is authenticated, redirect based on role
        if current_user.role == 'driver':
            return redirect(url_for('index_views.driver_homepage'))
        elif current_user.role == 'owner':
            return redirect(url_for('index_views.owner_homepage'))
        elif current_user.role == 'customer':
            return redirect(url_for('index_views.customer_homepage'))
    except:
        # User not authenticated, show login page
        pass
    
    return render_template('login.html')

@index_views.route('/driver/home', methods=['GET'])
@jwt_required()
def driver_homepage():
    if current_user.role != 'driver':
        return redirect(url_for('index_views.index'))
    return render_template('driver/homepage.html')

@index_views.route('/owner/home', methods=['GET'])
@jwt_required()
def owner_homepage():
    if current_user.role != 'owner':
        return redirect(url_for('index_views.index'))
    return render_template('owner/homepage.html')

@index_views.route('/customer/home', methods=['GET'])
@jwt_required()
def customer_homepage():
    if current_user.role != 'customer':
        return redirect(url_for('index_views.index'))
    return render_template('customer/homepage.html')

@index_views.route('/init', methods=['GET'])
def init():
    initialize()
    return jsonify(message='db initialized!')

@index_views.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status':'healthy'})