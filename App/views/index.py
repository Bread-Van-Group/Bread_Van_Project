from flask import Blueprint, redirect, render_template, request, jsonify, url_for
from flask_jwt_extended import jwt_required, current_user, verify_jwt_in_request
from App.controllers import initialize
from App.controllers.transaction import get_report_data


index_views = Blueprint('index_views', __name__, template_folder='../templates')


@index_views.route('/', methods=['GET'])
def index():
    try:
        verify_jwt_in_request()
        if current_user.role == 'driver':
            return redirect(url_for('driver_views.driver_homepage'))
        elif current_user.role == 'owner':
            return redirect(url_for('index_views.owner_homepage'))
        elif current_user.role == 'customer':
            return redirect(url_for('index_views.customer_homepage'))
    except Exception:
        pass
    return render_template('login.html')


@index_views.route('/owner/home', methods=['GET'])
@jwt_required()
def owner_homepage():
    if current_user.role != 'owner':
        return redirect(url_for('index_views.index'))
    return render_template('owner/homepage.html')


@index_views.route('/owner/report', methods=['GET'])
@jwt_required()
def owner_report():
    if current_user.role != 'owner':
        return redirect(url_for('index_views.index'))
    return render_template('owner/report.html')

@index_views.route('/api/owner/report', methods=['GET'])
@jwt_required()
def owner_report_api():
    """Return report data as JSON. Query param: ?period=week|month|year"""
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403
    period = request.args.get('period', 'week')
    data = get_report_data(period)
    return jsonify(data)

@index_views.route('/init', methods=['GET'])
def init():
    initialize()
    return jsonify(message='db initialized!')


@index_views.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status':'healthy'})

@index_views.route('/customer/home', methods=['GET'])
@jwt_required()
def customer_homepage():
    if current_user.role != 'customer':
        return redirect(url_for('index_views.index'))
    return render_template('customer/homepage.html')

@index_views.route('/customer/stock', methods=['GET'])
@jwt_required()
def customer_stock():
    if current_user.role != 'customer':
        return redirect(url_for('index_views.index'))
    return render_template('customer/stock.html')

@index_views.route('/customer/schedule', methods=['GET'])
@jwt_required()
def customer_schedule():
    if current_user.role != 'customer':
        return redirect(url_for('index_views.index'))
    return render_template('customer/schedule.html')

@index_views.route('/customer/profile', methods=['GET'])
@jwt_required()
def customer_profile():
    if current_user.role != 'customer':
        return redirect(url_for('index_views.index'))
    return render_template('customer/profile.html')

@index_views.route('/customer/preorder', methods=['GET'])
@jwt_required()
def customer_preorder():
    if current_user.role != 'customer':
        return redirect(url_for('index_views.index'))
    return render_template('customer/preorder.html')