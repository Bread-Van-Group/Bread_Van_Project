from flask import Blueprint, session, redirect, render_template, request, jsonify, url_for, flash
from flask_jwt_extended import jwt_required, current_user, verify_jwt_in_request, get_jwt_identity
from jwt import ExpiredSignatureError
from App.controllers import (
    get_assigned_driver_route,
    assign_driver_to_route,
    unassign_driver_from_route,
    get_daily_inventory_item_by_id,
    get_pending_stops_by_area_route,
    get_active_stops_by_area_route,
    get_daily_inventory,
    update_request_status,
    get_van_by_driver,
    create_transaction,
    create_map_stop,
    update_stock,
    get_van_daily_inventory,
)
from App.controllers.route import get_route_stops

from datetime import date

driver_views = Blueprint('driver_views', __name__, template_folder='../templates')


# ── Page Routes ───────────────────────────────────────────────────────────────

@driver_views.route('/driver/home', methods=['GET'])
@jwt_required() 
def driver_homepage():
    if current_user.role != 'driver':
        return redirect(url_for('index_views.index'))

    driver_id = int(get_jwt_identity())
    return render_template('driver/homepage.html')


@driver_views.route('/driver/inventory', methods=['GET'])
@jwt_required() 
def driver_inventory_page():
    if current_user.role != 'driver':
        return redirect(url_for('index_views.index'))

    driver_id = int(get_jwt_identity())
    van_id = get_van_by_driver(driver_id).van_id

    today = date.today()

    daily_inventory = get_van_daily_inventory(van_id, today)

    return render_template('driver/inventory.html', daily_inventory = daily_inventory)

@driver_views.route('/driver/requests', methods=['GET'])
@jwt_required() 
def driver_requests_page():
    if current_user.role != 'driver':
        return redirect(url_for('index_views.index'))

    route_id = get_assigned_driver_route(get_jwt_identity()).route_id
    pending_stops = get_pending_stops_by_area_route(route_id)

    print(route_id)

    return render_template('driver/requests_page.html', pending_stops=pending_stops)

@driver_views.route('/driver/requests/accept/<int:stop_id>', methods=['GET'])
@jwt_required() 
def driver_accept_request(stop_id):
    if current_user.role != 'driver':
        return redirect(url_for('index_views.index'))
    
    route_id = get_assigned_driver_route(get_jwt_identity()).route_id
    pending_stops = get_pending_stops_by_area_route(route_id)

    if not update_request_status(2, stop_id):
        flash('Error Could not accept request.', 'error')
        return render_template('driver/requests_page.html', pending_stops=pending_stops)

    pending_stops = get_pending_stops_by_area_route(route_id)
    return render_template('driver/requests_page.html', pending_stops=pending_stops)

@driver_views.route('/driver/requests/deny/<int:stop_id>', methods=['GET'])
@jwt_required() 
def driver_deny_request(stop_id):
    if current_user.role != 'driver':
        return redirect(url_for('index_views.index'))
    
    route_id = get_assigned_driver_route(get_jwt_identity()).route_id
    pending_stops = get_pending_stops_by_area_route(route_id)

    if not update_request_status(4, stop_id, False):
        flash('Error Could not deny request.', 'error')
        return render_template('driver/requests_page.html', pending_stops=pending_stops)

    pending_stops = get_pending_stops_by_area_route(route_id)
    return render_template('driver/requests_page.html', pending_stops=pending_stops)

@driver_views.route('/driver/transaction', methods=['GET'])
@jwt_required() 
def driver_transaction_page():
    if current_user.role != 'driver':
        return redirect(url_for('index_views.index'))

    today = date.today()

    daily_inventory = get_daily_inventory(today)

    transaction_items = session.get('transaction_items', [])

    return render_template('driver/transactions.html', transaction_items = transaction_items, daily_inventory=daily_inventory)


# ── API Routes ────────────────────────────────────────────────────────────────
@driver_views.route('/api/driver/plate', methods=['GET'])
@jwt_required()
def get_driver_plate():
    if current_user.role != 'driver':
        return jsonify(message='Unauthorized'), 403
    
    van_plate = get_van_by_driver(get_jwt_identity()).license_plate
    return jsonify({"plate":van_plate}), 200

@driver_views.route('/api/driver/route', methods=['GET'])
@jwt_required()
def get_assigned_route():
    if current_user.role != 'driver':
        return jsonify(message='Unauthorized'), 403

    route = get_assigned_driver_route(get_jwt_identity())
    return jsonify([stop.get_json() for stop in route.stops])


@driver_views.route('/api/driver/routes/<int:route_id>/assign', methods=['POST'])
@jwt_required()
def assign_route(route_id):
    """Assign the current driver to a route."""
    if current_user.role != 'driver':
        return jsonify(message='Unauthorized'), 403

    result = assign_driver_to_route(current_user.driver_id, route_id)
    if not result:
        return jsonify(message='Already assigned to this route'), 400
    return jsonify(result.get_json()), 201


@driver_views.route('/api/driver/routes/<int:route_id>/unassign', methods=['DELETE'])
@jwt_required()
def unassign_route(route_id):
    """Remove the current driver from a route."""
    if current_user.role != 'driver':
        return jsonify(message='Unauthorized'), 403

    success = unassign_driver_from_route(current_user.driver_id, route_id)
    if not success:
        return jsonify(message='Assignment not found'), 404
    return jsonify(message='Unassigned successfully')

@driver_views.route('/api/driver/active-stops', methods=['GET'])
@jwt_required()
def get_active_requests():
    if current_user.role != 'driver':
        return jsonify(message='Unauthorized'), 403

    # Get pending requests
    route_id = get_assigned_driver_route(get_jwt_identity()).route_id
    active_stops = get_active_stops_by_area_route(route_id)

    return active_stops

@driver_views.route('/api/driver/pending-stops', methods=['GET'])
@jwt_required()
def get_pending_requests():
    if current_user.role != 'driver':
        return jsonify(message='Unauthorized'), 403

    # Get pending requests
    route_id = get_assigned_driver_route(get_jwt_identity()).route_id
    pending_stops = get_pending_stops_by_area_route(route_id)

    return pending_stops

@driver_views.route('/api/driver/update-stop', methods=['POST'])
@jwt_required()
def complete_stop():
    if current_user.role != 'driver':
        return jsonify(message='Unauthorized'), 403
    
    stop_id = request.get_json().get('stop_id')
    status = request.get_json().get('status')

    if not update_request_status(status, stop_id):
        return '', 500
    else:
        return '', 200


@driver_views.route('/api/driver/make-transaction', methods=['POST'])
@jwt_required()
def make_transaction():
    if current_user.role != 'driver':
        return jsonify(message='Unauthorized'), 403
    
    transaction_list = []
    total = 0.0

    address = request.get_json().get('address')
    lat = request.get_json().get('lat')
    lng = request.get_json().get('lng')

    #The below field is only present when driver completes 
    #existing stop request with order attached
    order_items = request.get_json().get('order_items')

    if order_items:
        for item in order_items:
            transaction_list.append(
                {'item_id': item['item']['item_id'], 
                'quantity': item['quantity']
                })
            total += float(item['quantity'] * item['item']['price'])
    else:
        for item in session['transaction_items']:
            transaction_list.append(
                {'item_id': item['transaction_item']['item_id'], 
                'quantity': item['quantity']
                })
            total += float(item['total'])
    
    try:
        current_stop = create_map_stop(
            address= address,
            lat=lat,
            lng=lng,
        )

        transaction = create_transaction(
            customer_id=None,
            van_id=get_van_by_driver(get_jwt_identity()).van_id,
            total_amount= round(total,2),
            items=transaction_list,
            stop_id= current_stop.stop_id,
            payment_method='cash',
        )

        for item in transaction_list:
            update_stock(
                van_id=get_van_by_driver(get_jwt_identity()).van_id,
                item_id = item['item_id'],
                quantity= item['quantity']
            )

        session.pop('transaction_items', None)
        return '', 200
    except Exception as e:
        print(e)
        return '', 500

@driver_views.route('/api/driver/update-session', methods=['POST'])
@jwt_required()
def update_driver_session():
    if current_user.role != 'driver':
        return jsonify(message='Unauthorized'), 403
    
    inventory_id = request.get_json().get('inventory_id')
    transaction_item = get_daily_inventory_item_by_id(inventory_id).get_json()
    quantity = request.get_json().get('quantity')

    transaction_item = {'transaction_item' : transaction_item, 'quantity':quantity, 'total':transaction_item['item']['price']}
    #Initialize session items if not already initialized
    session.setdefault('transaction_items', [])

    for item in session['transaction_items']:   
        if item['transaction_item']['inventory_id'] == inventory_id:
            return '', 400
    
    session['transaction_items'] += [transaction_item]
    session.modified = True
    return '', 200
    
@driver_views.route('/api/driver/update-session-item', methods=['POST'])
@jwt_required()
def update_driver_session_item():
    if current_user.role != 'driver':
        return jsonify(message='Unauthorized'), 403
    
    inventory_id = request.get_json().get('inventory_id')
    quantity = request.get_json().get('quantity')
    total = request.get_json().get('total')

    for item in session['transaction_items']:
        if item['transaction_item']['inventory_id'] == inventory_id:
            item['quantity'] = quantity
            item['total'] = total

            session.modified = True
            return '', 200
    
    return '', 400   

@driver_views.route('/api/driver/delete-session-item', methods=['POST'])
@jwt_required()
def delete_driver_session_item():
    if current_user.role != 'driver':
        return jsonify(message='Unauthorized'), 403
    
    inventory_id = request.get_json().get('inventory_id')
    transaction_item = get_daily_inventory_item_by_id(inventory_id).get_json()
    
    for item in session['transaction_items']:   
        if item['transaction_item']['inventory_id'] == inventory_id:
            session['transaction_items'].remove(item)
            session.modified = True

            return '', 200
    
    return '', 400

@driver_views.route('/api/driver/clear-session', methods=['POST'])
@jwt_required()
def clear_driver_session():
    if current_user.role != 'driver':
        return jsonify(message='Unauthorized'), 403
    
    session.pop('transaction_items', None)
    return '', 200

