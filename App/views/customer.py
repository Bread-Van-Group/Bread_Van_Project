from flask import Blueprint, redirect, render_template, request, jsonify, url_for
from flask_jwt_extended import jwt_required, current_user, verify_jwt_in_request
from App.controllers import initialize
from App.controllers.transaction import get_report_data


customer_views = Blueprint('cusomter_views', __name__, template_folder='../templates')

@customer_views.route('/customer/home', methods=['GET'])
@jwt_required()
def customer_homepage():
    if current_user.role != 'customer':
        return redirect(url_for('index_views.index'))
    return render_template('customer/homepage.html')

@customer_views.route('/customer/stock', methods=['GET'])
@jwt_required()
def customer_stock():
    if current_user.role != 'customer':
        return redirect(url_for('index_views.index'))
    return render_template('customer/stock.html')

@customer_views.route('/customer/schedule', methods=['GET'])
@jwt_required()
def customer_schedule():
    if current_user.role != 'customer':
        return redirect(url_for('index_views.index'))
    return render_template('customer/schedule.html')

@customer_views.route('/customer/profile', methods=['GET'])
@jwt_required()
def customer_profile():
    if current_user.role != 'customer':
        return redirect(url_for('index_views.index'))
    return render_template('customer/profile.html')

@customer_views.route('/customer/preorder', methods=['GET'])
@jwt_required()
def customer_preorder():
    if current_user.role != 'customer':
        return redirect(url_for('index_views.index'))
    return render_template('customer/preorder.html')

@customer_views.route('/customer/cart', methods=['GET'])
@jwt_required()
def customer_cart():
    if current_user.role != 'customer':
        return redirect(url_for('index_views.index'))
    return render_template('customer/cart.html')
