from flask import Blueprint, redirect, render_template, request, jsonify, url_for
from flask_jwt_extended import jwt_required, current_user
from App.controllers import (
    get_driver_by_id,
    get_driver_routes,
    assign_driver_to_route,
    unassign_driver_from_route,
)
from App.controllers.route import get_route_stops
from App.models import CustomerRequest, RouteStop, Customer, InventoryItem, Status
from App.database import db

driver_views = Blueprint('driver_views', __name__, template_folder='../templates')


# ── Page Routes ───────────────────────────────────────────────────────────────

@driver_views.route('/driver/home', methods=['GET'])
@jwt_required()
def driver_homepage():
    if current_user.role != 'driver':
        return redirect(url_for('index_views.index'))
    return render_template('driver/homepage.html')


# ── API Routes ────────────────────────────────────────────────────────────────

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


@driver_views.route('/api/driver/requests/<int:request_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_request(request_id):
    if current_user.role != 'driver':
        return jsonify(message='Unauthorized'), 403

    cancelled = db.session.execute(
        db.select(Status).filter_by(status_name='cancelled')
    ).scalar_one_or_none()
    if not cancelled:
        return jsonify(message='Status not found'), 500

    req = db.session.get(CustomerRequest, request_id)
    if not req:
        return jsonify(message='Request not found'), 404

    req.status_id = cancelled.status_id
    db.session.commit()
    return jsonify(message='Request cancelled')


@driver_views.route('/api/driver/requests/<int:request_id>/complete', methods=['POST'])
@jwt_required()
def complete_request(request_id):
    if current_user.role != 'driver':
        return jsonify(message='Unauthorized'), 403

    from datetime import datetime, timedelta, timezone
    UTC_MINUS_4 = timezone(timedelta(hours=-4))

    fulfilled = db.session.execute(
        db.select(Status).filter_by(status_name='fulfilled')
    ).scalar_one_or_none()
    if not fulfilled:
        return jsonify(message='Status not found'), 500

    req = db.session.get(CustomerRequest, request_id)
    if not req:
        return jsonify(message='Request not found'), 404

    req.status_id      = fulfilled.status_id
    req.fulfilled_time = datetime.now(UTC_MINUS_4)
    db.session.commit()
    return jsonify(message='Request completed')


@driver_views.route('/api/driver/active-requests', methods=['GET'])
@jwt_required()
def get_active_requests():
    """
    Return all pending customer requests as map markers.
    Each entry includes lat/lng (from the route stop), customer name,
    address, and the list of pre-ordered items — matching what the
    map JS expects.
    """
    if current_user.role != 'driver':
        return jsonify(message='Unauthorized'), 403

    # Get pending status id
    pending_status = db.session.execute(
        db.select(Status).filter_by(status_name='pending')
    ).scalar_one_or_none()

    if not pending_status:
        return jsonify([])

    requests = db.session.scalars(
        db.select(CustomerRequest).filter_by(status_id=pending_status.status_id)
    ).all()

    result = []
    for req in requests:
        stop     = db.session.get(RouteStop,     req.stop_id)
        customer = db.session.get(Customer,      req.customer_id)
        item     = db.session.get(InventoryItem, req.item_id)

        if not stop or not customer or not item:
            continue

        result.append({
            'id':            req.request_id,
            'lat':           stop.lat,
            'lng':           stop.lng,
            'address':       stop.address,
            'customer_name': customer.name,
            'status':        pending_status.status_name,
            'orders': [
                {
                    'name':      item.name,
                    'quantity':  req.quantity,
                    'image_url': '',        # add a real URL when available
                }
            ]
        })

    return jsonify(result)