from flask import Blueprint, redirect, render_template, request, jsonify, url_for
from flask_jwt_extended import  jwt_required, current_user, verify_jwt_in_request
from App.controllers import (
    initialize,
    assign_route_to_area,
    get_region_by_route_id,
    get_van_by_driver,
    assign_van_to_route,
    get_report_data,
    get_van_daily_inventory,
    set_van_inventory as set_inventory,
    get_route_daily_inventory,
    set_route_inventory as set_inv,
    get_route_stops,
    assign_driver_to_route,
    unassign_driver_from_route,
    get_all_items,
    update_item_price,
    create_item,
    get_user_by_email,
)
from App.models import Van, Driver, Region, RouteArea, Route, Transaction, TransactionItem, InventoryItem, DailyInventory
from App.database import db
from App.models.driver_route import DriverRoute
from sqlalchemy import func
from datetime import date, datetime, timedelta, timezone

UTC_MINUS_4 = timezone(timedelta(hours=-4))

index_views = Blueprint('index_views', __name__, template_folder='../templates')


# ----------REMOVE THIS IN PRODUCTION--------------
@index_views.route('/init', methods=['GET'])
def init():
    initialize()
    return jsonify(message='db initialized!')


# ----------REMOVE THIS IN PRODUCTION--------------

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
    return render_template('owner/live_tracking.html')


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


@index_views.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})


@index_views.route('/owner/inventory', methods=['GET'])
@jwt_required()
def owner_inventory():
    if current_user.role != 'owner':
        return redirect(url_for('index_views.index'))
    return render_template('owner/set_inventory.html')


@index_views.route('/api/owner/vans/<int:van_id>/inventory', methods=['GET'])
@jwt_required()
def get_van_inventory(van_id):
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    date_str = request.args.get('date')
    target_date = date.fromisoformat(date_str) if date_str else date.today()

    inventory = get_van_daily_inventory(van_id, target_date)
    return jsonify([inv.get_json() for inv in inventory])


@index_views.route('/api/owner/vans/<int:van_id>/inventory', methods=['POST'])
@jwt_required()
def set_van_inventory(van_id):
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    data = request.json
    date_str = data.get('date')
    target_date = date.fromisoformat(date_str) if date_str else date.today()

    for item in data.get('items', []):
        set_inventory(van_id, item['item_id'], item['quantity'], target_date)

    return jsonify(message='Inventory updated successfully')


@index_views.route('/api/inventory/items', methods=['GET'])
@jwt_required()
def get_all_items_route():
    items = get_all_items()
    return jsonify([item.get_json() for item in items])


@index_views.route('/api/inventory/items/prices', methods=['PUT'])
@jwt_required()
def update_item_prices():
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    data = request.json
    updated = []

    for item in data.get('items', []):
        result = update_item_price(item['item_id'], item['price'])
        if result:
            updated.append(item['item_id'])

    return jsonify(message=f'Updated {len(updated)} prices', updated=updated)


@index_views.route('/api/inventory/items/<int:item_id>', methods=['DELETE'])
@jwt_required()
def delete_inventory_item(item_id):
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    item = InventoryItem.query.get(item_id)
    if not item:
        return jsonify(message='Item not found'), 404

    db.session.delete(item)
    db.session.commit()

    return jsonify(message='Product deleted')


@index_views.route('/api/inventory/items', methods=['POST'])
@jwt_required()
def create_inventory_item():
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    data = request.json
    item = create_item(
        name=data['name'],
        price=data['price'],
        category=data.get('category', ''),
        description=data.get('description', '')
    )

    return jsonify(message='Product created', item_id=item.item_id)


@index_views.route('/api/inventory/items/<int:item_id>', methods=['PUT'])
@jwt_required()
def update_inventory_item(item_id):
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    item = InventoryItem.query.get(item_id)
    if not item:
        return jsonify(message='Item not found'), 404

    data = request.json
    item.name = data['name']
    item.price = data['price']
    item.category = data.get('category', '')
    item.description = data.get('description', '')

    db.session.commit()

    return jsonify(message='Product updated')


@index_views.route('/api/owner/dashboard/summary', methods=['GET'])
@jwt_required()
def owner_dashboard_summary():
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    today_start = datetime.now(UTC_MINUS_4).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = datetime.now(UTC_MINUS_4).replace(hour=23, minute=59, second=59, microsecond=999999)

    today_txs = Transaction.query.filter(
        Transaction.transaction_time >= today_start,
        Transaction.transaction_time <= today_end
    ).all()

    total_transactions = len(today_txs)
    total_revenue = sum(float(tx.total_amount) for tx in today_txs)

    best_selling = db.session.query(
        InventoryItem.name,
        func.sum(TransactionItem.quantity).label('total_qty')
    ).join(
        TransactionItem, TransactionItem.item_id == InventoryItem.item_id
    ).join(
        Transaction, Transaction.transaction_id == TransactionItem.transaction_id
    ).filter(
        Transaction.transaction_time >= today_start,
        Transaction.transaction_time <= today_end
    ).group_by(
        InventoryItem.name
    ).order_by(
        func.sum(TransactionItem.quantity).desc()
    ).first()

    return jsonify({
        'total_transactions': total_transactions,
        'total_revenue': total_revenue,
        'best_selling_item': best_selling[0] if best_selling else None
    })


@index_views.route('/api/owner/routes', methods=['GET'])
@jwt_required()
def get_owner_routes():
    """Get all routes for this owner with enhanced data"""
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    from App.models import RouteStop

    routes = Route.query.filter_by(owner_id=current_user.owner_id).all()

    routes_data = []
    for route in routes:
        route_json = route.get_json()

        stops_count = RouteStop.query.filter_by(route_id=route.route_id).count()
        route_json['stops_count'] = stops_count

        driver_routes = DriverRoute.query.filter_by(route_id=route.route_id).all()
        assigned_drivers = []
        for dr in driver_routes:
            driver = Driver.query.get(dr.driver_id)
            if driver:
                assigned_drivers.append({
                    'driver_id': driver.driver_id,
                    'name': driver.name
                })
        route_json['assigned_drivers'] = assigned_drivers

        routes_data.append(route_json)

    return jsonify(routes_data)


@index_views.route('/api/owner/inventory/low-stock', methods=['GET'])
@jwt_required()
def get_low_stock_items():
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    van = Van.query.filter_by(owner_id=current_user.owner_id).first()
    if not van:
        return jsonify([])

    today = date.today()
    low_stock = db.session.query(
        DailyInventory, InventoryItem
    ).join(
        InventoryItem, InventoryItem.item_id == DailyInventory.item_id
    ).filter(
        DailyInventory.van_id == van.van_id,
        DailyInventory.date == today,
        DailyInventory.quantity_available < 20
    ).all()

    return jsonify([{
        'item_name': item.name,
        'quantity': inv.quantity_available
    } for inv, item in low_stock])


@index_views.route('/owner/routes', methods=['GET'])
@jwt_required()
def owner_routes():
    if current_user.role != 'owner':
        return redirect(url_for('index_views.index'))
    return render_template('owner/routes.html')


@index_views.route('/api/owner/routes/<int:route_id>/stops', methods=['GET'])
@jwt_required()
def get_route_stops_route(route_id):
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    stops = get_route_stops(route_id)

    return jsonify([{
        'stop_id': s.stop_id,
        'address': s.address,
        'lat': float(s.lat),
        'lng': float(s.lng),
        'stop_order': s.stop_order,
    } for s in stops])


@index_views.route('/api/owner/routes/<int:route_id>/stops', methods=['POST'])
@jwt_required()
def create_route_stop(route_id):
    """Add a stop to a route"""
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    from App.models import RouteStop
    from datetime import time

    route = Route.query.get(route_id)
    if not route or route.owner_id != current_user.owner_id:
        return jsonify(message='Route not found'), 404

    data = request.json

    estimated_arrival = None
    if data.get('estimated_arrival_time'):
        try:
            estimated_arrival = time.fromisoformat(data['estimated_arrival_time'])
        except (ValueError, TypeError):
            estimated_arrival = None

    stop = RouteStop(
        route_id=route_id,
        owner_id=current_user.owner_id,
        customer_id=None,
        address=data.get('address', ''),
        lat=data['lat'],
        lng=data['lng'],
        stop_order=data.get('stop_order', 0),
        status_id=None,
        fulfilled_time=None,
        estimated_arrival_time=estimated_arrival,
    )

    db.session.add(stop)
    db.session.commit()

    return jsonify(message='Stop created', stop_id=stop.stop_id), 201


@index_views.route('/api/owner/routes/<int:route_id>/stops/<int:stop_id>', methods=['DELETE'])
@jwt_required()
def delete_route_stop(route_id, stop_id):
    """Delete a stop from a route"""
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    from App.models import RouteStop

    route = Route.query.get(route_id)
    if not route or route.owner_id != current_user.owner_id:
        return jsonify(message='Route not found'), 404

    stop = RouteStop.query.filter_by(stop_id=stop_id, route_id=route_id).first()
    if not stop:
        return jsonify(message='Stop not found'), 404

    db.session.delete(stop)
    db.session.commit()

    return jsonify(message='Stop deleted'), 200


@index_views.route('/api/owner/routes', methods=['POST'])
@jwt_required()
def create_route():
    """Create a new route with stops"""
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    from App.models import RouteStop
    from datetime import time

    data = request.json

    start_time = time.fromisoformat(data['start_time'])
    end_time = time.fromisoformat(data['end_time'])

    route = Route(
        name=data['name'],
        start_time=start_time,
        end_time=end_time,
        day_of_week=data['day_of_week'],
        owner_id=current_user.owner_id,
        description=data.get('description', '')
    )
    db.session.add(route)
    db.session.flush()

    route_assginment = assign_route_to_area(route.route_id, data.get('region_id')) if data.get('region_id') else None

    for stop_data in data.get('stops', []):
        stop = RouteStop(
            route_id=route.route_id,
            owner_id=current_user.owner_id,
            address=stop_data.get('address', ''),
            lat=stop_data['lat'],
            lng=stop_data['lng'],
            stop_order=stop_data['order'],
        )
        db.session.add(stop)

    db.session.commit()
    return jsonify(message='Route created', route_id=route.route_id)


@index_views.route('/api/owner/routes/<int:route_id>', methods=['PUT'])
@jwt_required()
def update_route(route_id):
    """Update an existing route and its stops"""
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    from App.models import RouteStop
    from datetime import time

    route = Route.query.get(route_id)
    if not route or route.owner_id != current_user.owner_id:
        return jsonify(message='Route not found'), 404

    data = request.json

    route.name = data['name']
    route.start_time = time.fromisoformat(data['start_time'])
    route.end_time = time.fromisoformat(data['end_time'])
    route.day_of_week = data['day_of_week']
    route.description = data.get('description', '')
    route.region_id = data.get('region_id')

    route_assginment = assign_route_to_area(route_id, route.region_id) if route.region_id else None

    RouteStop.query.filter_by(route_id=route_id).delete()

    for stop_data in data.get('stops', []):
        stop = RouteStop(
            route_id=route.route_id,
            owner_id=current_user.owner_id,
            address=stop_data.get('address', ''),
            lat=stop_data['lat'],
            lng=stop_data['lng'],
            stop_order=stop_data['order'],
        )
        db.session.add(stop)

    db.session.commit()
    return jsonify(message='Route updated')


@index_views.route('/api/owner/routes/<int:route_id>', methods=['DELETE'])
@jwt_required()
def delete_route(route_id):
    """Delete a route"""
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    route = Route.query.get(route_id)
    route_area = RouteArea.query.filter_by(route_id=route_id).first()
    route_assignment = DriverRoute.query.filter_by(route_id=route_id).first()
    if not route or route.owner_id != current_user.owner_id:
        return jsonify(message='Route not found'), 404

    db.session.delete(route_area) if route_area else None
    db.session.delete(route_assignment) if route_assignment else None
    db.session.delete(route)
    db.session.commit()

    return jsonify(message='Route deleted')


@index_views.route('/api/owner/routes/<int:route_id>/assign-driver', methods=['POST'])
@jwt_required()
def assign_driver_to_route_api(route_id):
    """Assign a driver to a route via the DriverRoute bridge table"""
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    route = Route.query.get(route_id)
    if not route or route.owner_id != current_user.owner_id:
        return jsonify(message='Route not found'), 404

    data = request.json
    driver_id = data.get('driver_id')
    if not driver_id:
        return jsonify(message='driver_id is required'), 400

    result = assign_driver_to_route(driver_id, route_id)
    driver_van = get_van_by_driver(driver_id)
    van_assignment = assign_van_to_route(driver_van.van_id, route_id) if driver_van else None
    return jsonify(message='Driver assigned to route'), 200


@index_views.route('/api/owner/routes/<int:route_id>/assign-driver', methods=['DELETE'])
@jwt_required()
def unassign_driver_from_route_api(route_id):
    """Remove a driver from a route"""
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    data = request.json or {}
    driver_id = data.get('driver_id')
    if not driver_id:
        return jsonify(message='driver_id is required'), 400

    success = unassign_driver_from_route(driver_id, route_id)
    if not success:
        return jsonify(message='Assignment not found'), 404
    return jsonify(message='Driver unassigned from route'), 200


@index_views.route('/owner/fleet', methods=['GET'])
@jwt_required()
def owner_fleet():
    """Fleet Management page"""
    if current_user.role != 'owner':
        return redirect(url_for('index_views.index'))
    return render_template('owner/fleet_management.html')


@index_views.route('/api/owner/drivers', methods=['GET'])
@jwt_required()
def get_owner_drivers():
    """Get all drivers for this owner"""
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    drivers = Driver.query.filter_by(owner_id=current_user.owner_id).all()
    return jsonify([d.get_json() for d in drivers])


@index_views.route('/api/owner/drivers', methods=['POST'])
@jwt_required()
def create_driver():
    """Create a new driver"""
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    data = request.json

    if get_user_by_email(data.get('email', '')):
        return jsonify(message='A user with that email already exists'), 409

    try:
        driver = Driver(
            email=data['email'],
            password=data['password'],
            name=data['name'],
            owner_id=current_user.owner_id,
            phone=data.get('phone'),
            address=data.get('address')
        )
        db.session.add(driver)
        db.session.commit()
        db.session.refresh(driver)
    except Exception as e:
        db.session.rollback()
        return jsonify(message=f'Database error: {str(e)}'), 500

    return jsonify(driver.get_json()), 201


@index_views.route('/api/owner/vans', methods=['GET'])
@jwt_required()
def get_owner_vans():
    """Get all vans for this owner"""
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    vans = Van.query.filter_by(owner_id=current_user.owner_id).all()
    return jsonify([v.get_json() for v in vans])


@index_views.route('/api/owner/vans', methods=['POST'])
@jwt_required()
def create_van():
    """Create a new van"""
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    data = request.json

    van = Van(
        license_plate=data['license_plate'],
        owner_id=current_user.owner_id,
        status='inactive'
    )
    db.session.add(van)
    db.session.commit()

    return jsonify(van.get_json()), 201


@index_views.route('/api/owner/vans/<int:van_id>/assign-driver', methods=['POST'])
@jwt_required()
def assign_driver_to_van(van_id):
    """Assign a driver to a van"""
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    data = request.json
    driver_id = data.get('driver_id')

    van = Van.query.get(van_id)
    if not van or van.owner_id != current_user.owner_id:
        return jsonify(message='Van not found'), 404

    driver = Driver.query.get(driver_id)
    if not driver or driver.owner_id != current_user.owner_id:
        return jsonify(message='Driver not found'), 404

    van.assign_driver(driver_id)
    van.status = 'active'
    db.session.commit()

    return jsonify(van.get_json())


@index_views.route('/api/owner/vans/<int:van_id>/unassign-driver', methods=['POST'])
@jwt_required()
def unassign_driver_from_van(van_id):
    """Unassign driver from a van"""
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    van = Van.query.get(van_id)
    if not van or van.owner_id != current_user.owner_id:
        return jsonify(message='Van not found'), 404

    van.unassign_driver()
    van.status = 'inactive'
    db.session.commit()

    return jsonify(van.get_json())


@index_views.route('/owner/tracking', methods=['GET'])
@jwt_required()
def owner_tracking():
    """Live Tracking page"""
    if current_user.role != 'owner':
        return redirect(url_for('index_views.index'))
    return render_template('owner/live_tracking.html')


@index_views.route('/api/owner/vans/tracking', methods=['GET'])
@jwt_required()
def get_vans_tracking():
    """Get all vans with their current GPS locations"""
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    vans = Van.query.filter_by(owner_id=current_user.owner_id).all()
    return jsonify([v.get_json() for v in vans])


@index_views.route('/api/owner/vans/<int:van_id>/location', methods=['POST'])
@jwt_required()
def update_van_location(van_id):
    """Update van's GPS location"""
    data = request.json

    van = Van.query.get(van_id)
    if not van:
        return jsonify(message='Van not found'), 404

    van.update_location(data['lat'], data['lng'])
    db.session.commit()

    return jsonify(van.get_json())


@index_views.route('/api/owner/routes/<int:route_id>/inventory', methods=['GET'])
@jwt_required()
def get_route_inventory(route_id):
    """Return inventory for a route. Accepts optional ?date=YYYY-MM-DD param."""
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    date_str = request.args.get('date')
    target_date = date.fromisoformat(date_str) if date_str else date.today()
    return jsonify(get_route_daily_inventory(route_id, target_date))


@index_views.route('/api/owner/routes/<int:route_id>/inventory', methods=['POST'])
@jwt_required()
def set_route_inventory(route_id):
    """Set inventory for a route on a given date."""
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    data = request.json or {}
    date_str = data.get('date')
    target_date = date.fromisoformat(date_str) if date_str else date.today()
    items = data.get('items', [])

    saved = set_inv(route_id, items, target_date)
    if not saved:
        return jsonify(
            message='No van is linked to this route. '
                    'In Fleet Management, assign a van to the driver on this route, then try again.'
        ), 422

    return jsonify(message='Route inventory updated successfully')


@index_views.route('/api/owner/regions', methods=['GET'])
@jwt_required()
def get_regions():
    """Get all regions"""
    regions = Region.query.all()
    return jsonify([r.get_json() for r in regions])


@index_views.route('/api/owner/regions', methods=['POST'])
@jwt_required()
def create_region():
    """Create a new region"""
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    data = request.json

    region = Region(
        name=data['name'],
        description=data.get('description')
    )
    db.session.add(region)
    db.session.commit()

    return jsonify(region.get_json()), 201


@index_views.route('/api/owner/route-region/<int:route_id>', methods=['GET'])
@jwt_required()
def get_route_region(route_id):
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    region = get_region_by_route_id(route_id)
    if not region:
        return jsonify(message='No region assigned to this route'), 404

    return jsonify(region.get_json())


@index_views.route('/api/owner/driver-van/<int:driver_id>', methods=['GET'])
@jwt_required()
def get_driver_van(driver_id):
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    van = get_van_by_driver(driver_id)

    if not van:
        return '', 404
    else:
        return jsonify(van.get_json()), 200