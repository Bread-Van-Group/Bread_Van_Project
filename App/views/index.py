from flask import Blueprint, redirect, render_template, request, jsonify, url_for
from flask_jwt_extended import jwt_required, current_user, verify_jwt_in_request
from App.controllers import initialize
from App.controllers.transaction import get_report_data
from App.database import db

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

@index_views.route('/customer/cart', methods=['GET'])
@jwt_required()
def customer_cart():
    if current_user.role != 'customer':
        return redirect(url_for('index_views.index'))
    return render_template('customer/cart.html')


@index_views.route('/owner/inventory', methods=['GET'])
@jwt_required()
def owner_inventory():
    if current_user.role != 'owner':
        return redirect(url_for('index_views.index'))
    return render_template('owner/set_inventory.html')

@index_views.route('/api/owner/vans', methods=['GET'])
@jwt_required()
def get_owner_vans():
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403
    from App.controllers.owner import get_owner_vans
    vans = get_owner_vans(current_user.owner_id)
    return jsonify([v.get_json() for v in vans])


@index_views.route('/api/owner/vans/<int:van_id>/inventory', methods=['GET'])
@jwt_required()
def get_van_inventory(van_id):
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    from App.controllers.van import get_van_daily_inventory
    from datetime import date

    date_str = request.args.get('date')
    target_date = date.fromisoformat(date_str) if date_str else date.today()

    inventory = get_van_daily_inventory(van_id, target_date)
    return jsonify([inv.get_json() for inv in inventory])


@index_views.route('/api/owner/vans/<int:van_id>/inventory', methods=['POST'])
@jwt_required()
def set_van_inventory(van_id):
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    from App.controllers.van import set_van_inventory as set_inventory
    from datetime import date

    data = request.json
    date_str = data.get('date')
    target_date = date.fromisoformat(date_str) if date_str else date.today()

    for item in data.get('items', []):
        set_inventory(van_id, item['item_id'], item['quantity'], target_date)

    return jsonify(message='Inventory updated successfully')


@index_views.route('/api/inventory/items', methods=['GET'])
@jwt_required()
def get_all_items():
    from App.controllers.inventory_item import get_all_items
    items = get_all_items()
    return jsonify([item.get_json() for item in items])


@index_views.route('/api/inventory/items/prices', methods=['PUT'])
@jwt_required()
def update_item_prices():
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    from App.controllers.inventory_item import update_item_price

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
    #Delete an inventory item/product
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    from App.models import InventoryItem

    item = InventoryItem.query.get(item_id)
    if not item:
        return jsonify(message='Item not found'), 404

    db.session.delete(item)
    db.session.commit()

    return jsonify(message='Product deleted')


@index_views.route('/api/inventory/items', methods=['POST'])
@jwt_required()
def create_inventory_item():
    #Create a new inventory item
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    from App.controllers.inventory_item import create_item

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
    #Update an existing inventory item
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    from App.models import InventoryItem

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


# Controller function in App/controllers/inventory_item.py:

def create_item(name, price, category='', description=''):
    #Create a new inventory item
    from App.models import InventoryItem
    from App.database import db

    item = InventoryItem(name=name, price=price, category=category, description=description)
    db.session.add(item)
    db.session.commit()
    return item

@index_views.route('/api/owner/dashboard/summary', methods=['GET'])
@jwt_required()
def owner_dashboard_summary():
    #Get today's summary stats for owner dashboard
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    from App.models import Transaction, TransactionItem, InventoryItem
    from datetime import date, datetime, timedelta, timezone
    from sqlalchemy import func

    UTC_MINUS_4 = timezone(timedelta(hours=-4))
    today_start = datetime.now(UTC_MINUS_4).replace(hour=0, minute=0, second=0, microsecond=0)
    today_end = datetime.now(UTC_MINUS_4).replace(hour=23, minute=59, second=59, microsecond=999999)

    # Get today's transactions
    today_txs = Transaction.query.filter(
        Transaction.transaction_time >= today_start,
        Transaction.transaction_time <= today_end
    ).all()

    total_transactions = len(today_txs)
    total_revenue = sum(float(tx.total_amount) for tx in today_txs)

    # Find best-selling item today
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
    #Get all routes for the owner
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    from App.controllers.owner import get_owner_routes
    routes = get_owner_routes(current_user.owner_id)

    return jsonify([{
        'route_id': r.route_id,
        'name': r.name,
        'start_time': r.start_time.strftime('%H:%M') if r.start_time else '',
        'end_time': r.end_time.strftime('%H:%M') if r.end_time else '',
        'day_of_week': r.day_of_week
    } for r in routes])


@index_views.route('/api/owner/inventory/low-stock', methods=['GET'])
@jwt_required()
def get_low_stock_items():
    #Get items with low stock for today
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    from App.models import DailyInventory, InventoryItem, Van
    from datetime import date

    # Get owner's van
    van = Van.query.filter_by(owner_id=current_user.owner_id).first()
    if not van:
        return jsonify([])

    # Get today's inventory with stock < 20
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
def get_route_stops(route_id):
    #Get all stops for a route
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    from App.controllers.route import get_route_stops
    stops = get_route_stops(route_id)

    return jsonify([{
        'stop_id': s.stop_id,
        'address': s.address,
        'lat': float(s.lat),
        'lng': float(s.lng),
        'stop_order': s.stop_order,
        'estimated_arrival_time': s.estimated_arrival_time.strftime('%H:%M') if s.estimated_arrival_time else ''
    } for s in stops])

@index_views.route('/api/owner/routes/<int:route_id>/stops', methods=['POST'])
@jwt_required()
def create_route_stop(route_id):
    """Add a stop to a route"""
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    from App.models import Route, RouteStop
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
        address=data.get('address', ''),
        lat=data['lat'],
        lng=data['lng'],
        stop_order=data.get('stop_order', 0),
        estimated_arrival_time=estimated_arrival
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

    from App.models import Route, RouteStop

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
    #Create a new route
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    from App.controllers.route import create_route
    from datetime import time

    data = request.json

    # Parse time strings
    start_time = time.fromisoformat(data['start_time'])
    end_time = time.fromisoformat(data['end_time'])

    route = create_route(
        name=data['name'],
        start_time=start_time,
        end_time=end_time,
        day_of_week=data['day_of_week'],
        owner_id=current_user.owner_id,
        description=data.get('description', '')
    )

    return jsonify(message='Route created', route_id=route.route_id)


@index_views.route('/api/owner/routes/<int:route_id>', methods=['PUT'])
@jwt_required()
def update_route(route_id):
    """Update an existing route"""
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    from App.models import Route
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

    db.session.commit()

    return jsonify(message='Route updated')


@index_views.route('/api/owner/routes/<int:route_id>', methods=['DELETE'])
@jwt_required()
def delete_route(route_id):
    """Delete a route and all its stops"""
    if current_user.role != 'owner':
        return jsonify(message='Unauthorized'), 403

    from App.controllers.route import get_route_by_id, delete_route as controller_delete_route

    route = get_route_by_id(route_id)
    if not route or route.owner_id != current_user.owner_id:
        return jsonify(message='Route not found'), 404

    success = controller_delete_route(route_id)
    if not success:
        return jsonify(message='Failed to delete route'), 500

    return jsonify(message='Route deleted'), 200