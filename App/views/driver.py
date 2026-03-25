from flask import Blueprint, session, redirect, render_template, request, jsonify, url_for, flash
from flask_jwt_extended import jwt_required, current_user, verify_jwt_in_request, get_jwt_identity
from jwt import ExpiredSignatureError
from App.controllers import (
    get_driver_routes,
    assign_driver_to_route,
    unassign_driver_from_route,
    get_daily_inventory_item_by_id,
    get_pending_stops,
    get_active_stops,
    get_daily_inventory,
    get_stop_by_id,
    update_request_status,
    add_stop_to_end_of_route,
    get_todays_route,
    get_van_by_driver
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

    today = date.today()

    daily_inventory = get_daily_inventory(today)

    return render_template('driver/inventory.html', daily_inventory = daily_inventory)

@driver_views.route('/driver/requests', methods=['GET'])
@jwt_required() 
def driver_requests_page():
    if current_user.role != 'driver':
        return redirect(url_for('index_views.index'))

    pending_stops = get_pending_stops()

    return render_template('driver/requests_page.html', pending_stops=pending_stops)

@driver_views.route('/driver/requests/accept/<int:stop_id>', methods=['GET'])
@jwt_required() 
def driver_accept_request(stop_id):
    if current_user.role != 'driver':
        return redirect(url_for('index_views.index'))
    
    pending_stops = get_pending_stops()

    if not update_request_status(2, stop_id):
        flash('Error Could not accept request.', 'error')
        return render_template('driver/requests_page.html', pending_stops=pending_stops)

    if not add_stop_to_end_of_route(get_todays_route().route_id, stop_id):
        flash('Error Could not accept request.', 'error')
        return render_template('driver/requests_page.html', pending_stops=pending_stops)

    pending_stops = get_pending_stops()
    return render_template('driver/requests_page.html', pending_stops=pending_stops)

@driver_views.route('/driver/requests/deny/<int:stop_id>', methods=['GET'])
@jwt_required() 
def driver_deny_request(stop_id):
    if current_user.role != 'driver':
        return redirect(url_for('index_views.index'))

    pending_stops = get_pending_stops()

    stop = get_stop_by_id(stop_id)


    if not update_request_status(4, stop_id, False):
        flash('Error Could not deny request.', 'error')
        return render_template('driver/requests_page.html', pending_stops=pending_stops)

    pending_stops = get_pending_stops()
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

@driver_views.route('/api/driver/routes', methods=['GET'])
@jwt_required()
def get_my_routes():
    """Return all routes assigned to the currently logged-in driver."""
    if current_user.role != 'driver':
        return jsonify(message='Unauthorized'), 403

    driver_routes = get_driver_routes(current_user.driver_id)
    return jsonify([dr.get_json() for dr in driver_routes])


@driver_views.route('/api/driver/routes/<int:route_id>/stops', methods=['GET'])
@jwt_required()
def get_stops_for_route(route_id):
    """Return the ordered stops for a given route."""
    if current_user.role != 'driver':
        return jsonify(message='Unauthorized'), 403

    stops = get_route_stops(route_id)
    return jsonify([stop.get_json() for stop in stops])


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
    stops = get_active_stops()

    return stops

@driver_views.route('/api/driver/pending-stops', methods=['GET'])
@jwt_required()
def get_pending_requests():
    if current_user.role != 'driver':
        return jsonify(message='Unauthorized'), 403

    # Get pending requests
    stops = get_pending_stops()

    return stops

@driver_views.route('/api/driver/update-session', methods=['POST'])
@jwt_required()
def update_driver_session():
    if current_user.role != 'driver':
        return jsonify(message='Unauthorized'), 403
    
    inventory_id = request.get_json().get('inventory_id')
    transaction_item = get_daily_inventory_item_by_id(inventory_id).get_json()
    
    #Initialize session items if not already initialized
    session.setdefault('transaction_items', [])

    if transaction_item not in session['transaction_items']:
        session['transaction_items'] += [transaction_item]
        session.modified = True
        return '', 200
    else:
        return '', 400
    
@driver_views.route('/api/driver/clear-session', methods=['POST'])
@jwt_required()
def clear_driver_session():
    if current_user.role != 'driver':
        return jsonify(message='Unauthorized'), 403
    
    session.pop('transaction_items', None)
    return '', 200
