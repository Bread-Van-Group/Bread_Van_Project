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
    """Get daily inventory for a van on a specific date"""
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
    """Set daily inventory for a van"""
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
    """Bulk update item prices"""
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