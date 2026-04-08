from flask import Blueprint, session, redirect,flash, render_template, request, jsonify, url_for
from flask_jwt_extended import jwt_required, current_user, get_jwt_identity
from App.controllers import (
    get_customer_region,
    get_route_by_id,
    get_today_customer_request, 
    delete_today_pending_customer_order,  
    get_active_van_plate, 
    get_van_for_customer_route,
    get_customer_route_id, 
    add_customer_stop_to_route, 
    create_customer_request, 
    get_daily_inventory_item, 
    get_customers_storepage_inventory,
    get_customer_request_total
)

import json

customer_views = Blueprint('customer_views', __name__, template_folder='../templates')

# ── Page Routes ───────────────────────────────────────────────────────────────

@customer_views.route('/customer/home', methods=['GET'])
@jwt_required()
def customer_homepage():
    if current_user.role != 'customer':
        return redirect(url_for('index_views.index'))
    customer_id = get_jwt_identity()
    stop = get_today_customer_request(customer_id)

    if stop:
        order_total = get_customer_request_total(customer_id, stop)
    else:
        order_total = 0
    return render_template('customer/homepage.html', stop=stop, order_total = order_total)

@customer_views.route('/customer/schedule', methods=['GET'])
@jwt_required()
def customer_schedule():
    if current_user.role != 'customer':
        return redirect(url_for('index_views.index'))

    todays_route_id, route_stops = get_customer_route_id(get_jwt_identity())
    
    if todays_route_id is None:
        return redirect(url_for('customer_views.customer_homepage', 
                                message='The Bread Van is not scheduled to operate in your area at the moment'))
    
    customer_route = get_route_by_id(todays_route_id)
    route_start_time = customer_route.start_time

    customer_region = get_customer_region(get_jwt_identity())    

    return render_template('customer/schedule.html', route_start_time=route_start_time, route_stops=route_stops, customer_region=customer_region.name)

@customer_views.route('/customer/authorize-store', methods=['POST'])
def authorize_store():
    # Receive the validation result from the frontend
    data = request.get_json()
    
    if data.get('authorized'):
        session['store_access'] = True
        return jsonify({'redirect': url_for('customer_views.customer_store')})
    
    return jsonify({'error': 'Not authorized'}), 403

@customer_views.route('/customer/store', methods=['GET'])
@jwt_required()
def customer_store():
    if current_user.role != 'customer':
        return redirect(url_for('index_views.index'))
    
    if not session.pop('store_access', False):  # consume the flag immediately
        return redirect(url_for('customer_views.customer_homepage', 
                                message='Access Denied'))
    
    stop = get_today_customer_request(get_jwt_identity())

    if stop and (stop['status_id'] == 3 or stop['status_id'] == 4):
        return redirect(url_for('customer_views.customer_homepage', message="You have already made an order for today.The store is now unavailable until tomorrow."))

    store_items = get_customers_storepage_inventory(get_jwt_identity())
    
    #The store should never be empty if route is assigned
    #to the customers region
    if store_items is None:
        store_items = []

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
             return redirect(url_for('customer_views.customer_store', message="Your cart is empty, please add items to it first"))

        session['order'] = order
        return redirect(url_for('customer_views.customer_checkout'))
    
    order = session.get('order', [])
    order_total = 0

    for item in order:
        order_total += item['price'] * item['quantity']

    van_plate = get_active_van_plate()

    return render_template('customer/checkout.html', order=order, order_total =order_total, van_plate = van_plate )

# ── API Routes ────────────────────────────────────────────────────────────────
@customer_views.route('/api/customer/route', methods=['GET'])
@jwt_required()
def get_customer_route():
    if current_user.role != 'customer':
        return jsonify(message='Unauthorized'), 403

    todays_route_id, route_stops = get_customer_route_id(get_jwt_identity())

    if not todays_route_id:
         return '', 400
    
    return jsonify({"route_id": todays_route_id, "stops": route_stops}), 200


@customer_views.route('/api/customer/item/<int:item_id>', methods=['GET'])
@jwt_required()
def get_store_item(item_id):
    if current_user.role != 'customer':
        return jsonify(message='Unauthorized'), 403

    store_item = get_daily_inventory_item(item_id)
    return jsonify(store_item), 200

@customer_views.route('/api/customer/update-session', methods =['POST'])
@jwt_required()
def update_customer_session():
    if current_user.role != 'customer':
        return jsonify(message='Unauthorized'), 403

    order = request.get_json().get("order")
    session['order'] = order
    return '', 200

@customer_views.route('/api/customer/delete-order', methods=['POST'])
@jwt_required()
def delete_customer_orders():
    if current_user.role != 'customer':
        return jsonify(message='Unauthorized'), 403
    
    customer_id = get_jwt_identity()
    customer_request = get_today_customer_request(customer_id)

    if customer_request['status_id'] == 3 or customer_request['status_id'] == 4 :
        return '', 400

    isDeleted = delete_today_pending_customer_order(customer_id)

    if isDeleted:
        return '', 200
    else:
        return redirect(url_for('customer_views.customer_checkout', message="Could not delete order, please try again later")), 500


@customer_views.route('/api/customer/get-order', methods=['GET'])
@jwt_required()
def get_active_order():
    if current_user.role != 'customer':
        return jsonify(message='Unauthorized'), 403
    
    active_order = get_today_customer_request(get_jwt_identity())

    if active_order:
        return jsonify({"response":True})
    else:
        return jsonify({"response":False})

#REQUEST WITH AN ORDER ATTACHED
@customer_views.route('/api/customer/make-order', methods=['POST'])
@jwt_required()
def customer_make_request():
    if current_user.role != 'customer':
        return jsonify(message='Unauthorized'), 403

    data = request.get_json()
    
    lat = data.get('lat')
    lng = data.get('lng')
    address = data.get('address')

    stop = get_today_customer_request(get_jwt_identity())
    todays_route_id, route_stops = get_customer_route_id(get_jwt_identity())

    if not todays_route_id:
         return '', 400

    order = session.get('order', [])

    #Create stop if there isnt an existing one
    if not stop:
        stop = add_customer_stop_to_route(
            route_id=todays_route_id,
            customer_id=get_jwt_identity(),
            address=address,
            lat=lat,
            lng=lng,
            status_id=1
        )        
    
    for item in order:
        new_request = create_customer_request(
            van_id= get_van_for_customer_route(get_jwt_identity()).van_id,
            stop_id=stop['stop_id'],
            item_id=item['inventory_id'],
            quantity=item['quantity'],
        )

    session.pop('order', None) 
    return '', 200


#REQUEST WITHOUT AN ORDER
@customer_views.route('/api/customer/make-stop-request', methods=['POST'])
@jwt_required()
def customer_request_stop():
    if current_user.role != 'customer':
        return jsonify(message='Unauthorized'), 403

    data = request.get_json()
    lat = data.get('lat')
    lng = data.get('lng')
    address = data.get('address')

    stop = get_today_customer_request(get_jwt_identity())
    todays_route_id, route_stops = get_customer_route_id(get_jwt_identity())    

    if not todays_route_id:
         return '', 400

    if not stop:
        stop = add_customer_stop_to_route(
            route_id=todays_route_id,
            customer_id=get_jwt_identity(),
            address=address,
            lat=lat,
            lng=lng,
            status_id=1
        )

    return '', 200

@customer_views.route('/api/customer/clear-requests', methods=['POST'])
@jwt_required()
def customer_clear_request_items():
    if current_user.role != 'customer':
        return jsonify(message='Unauthorized'), 403
    
    customer_id = get_jwt_identity()
    stop = get_today_customer_request(customer_id)

    #Deletes the orders along with its associated stop request
    isDeleted = delete_today_pending_customer_order(customer_id)

    todays_route_id, route_stops = get_customer_route_id(get_jwt_identity())    

    if not todays_route_id:
         return '', 400


    #Remakes a new stop request from scratch for the customer
    stop = add_customer_stop_to_route(
            route_id=todays_route_id,
            customer_id=get_jwt_identity(),
            address=stop["address"],
            lat=stop['lat'],
            lng=stop['lng'],
            status_id=stop['status_id']
    )

    return '', 200

@customer_views.route('/api/customer/region', methods=['GET'])
@jwt_required()
def customer_get_region():
    if current_user.role != 'customer':
        return jsonify(message='Unauthorized'), 403
    
    customer_region = get_customer_region(get_jwt_identity()).name 

    if customer_region:
        return jsonify({"region":customer_region}), 200
    else:
        return '', 400
    
@customer_views.route('/api/customer/stop-request', methods=['GET'])
@jwt_required()
def customer_get_stop_request():
    if current_user.role != 'customer':
        return jsonify(message='Unauthorized'), 403
    
    customer_request = get_today_customer_request(get_jwt_identity())['stop_id'] 

    if customer_request:
        return jsonify({"stop_id":customer_request}), 200
    else:
        return '', 400   