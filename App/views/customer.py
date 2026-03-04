from flask import Blueprint, session, redirect,flash, render_template, request, jsonify, url_for
from flask_jwt_extended import jwt_required, current_user, verify_jwt_in_request, get_jwt_identity
from App.controllers import (initialize, get_todays_route, add_stop_to_route, get_active_van, create_customer_request, get_daily_inventory_item, get_daily_inventory, get_customer_requests, get_customer_request_total)
from App.controllers.transaction import get_report_data

from datetime import date, time
import json

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
    customer_order = session.get('order', [])

    return render_template('customer/store.html', store_items=store_items, customer_order= customer_order)

@customer_views.route('/customer/checkout', methods=['GET', 'POST'])
@jwt_required()
def customer_checkout():
    if current_user.role != 'customer':
        return redirect(url_for('index_views.index'))

    if request.method == 'POST':
        order = json.loads(request.form.get('order'))

        if len(order) == 0:
             return redirect(url_for('customer_views.customer_store', error="Your cart is empty, please add items to it first"))

        session['order'] = order
        return redirect(url_for('customer_views.customer_checkout'))
    
    order = session.get('order', [])
    order_total = 0

    for item in order:
        order_total += item['price'] * item['quantity']

    return render_template('customer/checkout.html', order=order, order_total =order_total )

# ── API Routes ────────────────────────────────────────────────────────────────

@customer_views.route('/api/customer/item/<int:item_id>', methods=['GET'])
@jwt_required()
def get_store_item(item_id):
    store_item = get_daily_inventory_item(item_id)
    return jsonify(store_item), 200

@customer_views.route('/api/customer/update-session', methods =['POST'])
@jwt_required()
def update_customer_session():
    order = request.get_json().get("order")
    session['order'] = order
    return '', 200

@customer_views.route('/api/customer/make-order', methods=['POST'])
@jwt_required()
def customer_make_request():
    data = request.get_json()
    
    lat = data.get('lat')
    lng = data.get('lng')
    order = session.get('order', [])

    new_stop = add_stop_to_route(
        route_id=get_todays_route().route_id,
        address="Placeholder",
        lat=lat,
        lng=lng,
        stop_order=0,
        estimated_arrival_time=time(7, 15),
    )

    for item in order:
        new_request = create_customer_request(
            customer_id=get_jwt_identity(),
            van_id=get_active_van().van_id,
            stop_id=new_stop.stop_id,
            item_id=item['inventory_id'],
            quantity=item['quantity'],
            status_id=1
        )

    session.pop('order', None) 
    return '', 200