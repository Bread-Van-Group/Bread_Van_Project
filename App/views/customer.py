from flask import Blueprint, redirect, render_template, request, jsonify, url_for
from flask_jwt_extended import jwt_required, current_user, verify_jwt_in_request, get_jwt_identity
from App.controllers import (initialize, get_daily_inventory_item, get_daily_inventory, get_customer_requests, get_customer_request_total)
from App.controllers.transaction import get_report_data

from datetime import date

customer_views = Blueprint('customer_views', __name__, template_folder='../templates')

# ── Page Routes ───────────────────────────────────────────────────────────────

@customer_views.route('/customer/home', methods=['GET'])
@jwt_required()
def customer_homepage():
    if current_user.role != 'customer':
        return redirect(url_for('index_views.index'))
    customer_id = get_jwt_identity()
    orders = get_customer_requests(customer_id)
    order_total = get_customer_request_total(customer_id)
    return render_template('customer/homepage.html', orders=orders, order_total = order_total)

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

@customer_views.route('/customer/store', methods=['GET'])
@jwt_required()
def customer_store():
    if current_user.role != 'customer':
        return redirect(url_for('index_views.index'))
    
    today = date.today()

    store_items = get_daily_inventory(today)
    
    return render_template('customer/store.html', store_items=store_items)

@customer_views.route('/customer/cart', methods=['GET'])
@jwt_required()
def customer_cart():
    if current_user.role != 'customer':
        return redirect(url_for('index_views.index'))
    return render_template('customer/cart.html')

# ── API Routes ────────────────────────────────────────────────────────────────

@customer_views.route('/api/customer/item/<int:item_id>', methods=['GET'])
@jwt_required()
def get_store_item(item_id):
    store_item = get_daily_inventory_item(item_id)
    return jsonify(store_item), 200