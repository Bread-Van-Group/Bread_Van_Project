from App.database import db
from App.models import  CustomerRequest
from App.controllers.van import reserve_inventory, get_active_van 

def get_request_by_id(request_id):
    return db.session.execute(
        db.select(CustomerRequest)
        .filter_by(request_id=request_id)
    ).scalar_one_or_none()

def create_customer_request(customer_id, van_id, stop_id, item_id, quantity,status_id):
    """
    Place a new customer request for an item at a given route stop.

    Args:
        customer_id: ID of the requesting customer.
        van_id:      ID of the van serving the stop.
        stop_id:     ID of the route_stop where the customer will be.
        item_id:     ID of the inventory item being requested.
        quantity:    Number of units requested.
        status_id:   Initial status (1:"pending", 2:"confirmed", 3:"fufilled", 4:"cancelled").

    Returns:
        The newly created CustomerRequest instance.
    """

    new_request = CustomerRequest(
        customer_id=customer_id,
        van_id=van_id,
        stop_id=stop_id,
        item_id=item_id,
        quantity=quantity,
        status_id=status_id,
    )
    db.session.add(new_request)
    db.session.commit()
    return new_request


def update_request_status(request_id, status_id, fulfilled=False):
    """Update the status (and optionally fulfilled_time) of a customer request."""
    from datetime import datetime, timedelta, timezone
    UTC_MINUS_4 = timezone(timedelta(hours=-4))

    request = db.session.get(CustomerRequest, request_id)
    if not request:
        return None

    request.status_id = status_id
    if fulfilled:
        request.fulfilled_time = datetime.now(UTC_MINUS_4)

    db.session.commit()
    return request

def set_request_confirmed(request_id):
    update_request_status(request_id, 2, False)

    request = get_request_by_id(request_id)
    inventory_item_id = request.item.item_id
    van_id = get_active_van().van_id

    try:
        reserve_inventory(van_id, inventory_item_id, request.quantity)
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Unexpected error: {e}")
        return False
