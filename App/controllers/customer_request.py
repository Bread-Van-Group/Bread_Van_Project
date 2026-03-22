from App.database import db
from App.models import  CustomerRequest
from App.controllers.van import reserve_inventory, get_active_van 

def get_request_by_id(request_id):
    return db.session.execute(
        db.select(CustomerRequest)
        .filter_by(request_id=request_id)
    ).scalar_one_or_none()

def get_requests_by_stop_id(stop_id):
    return db.session.scalars(
        db.select(CustomerRequest)
        .filter_by(stop_id=stop_id)
    ).all()

def create_customer_request(customer_id, van_id, stop_id, item_id, quantity):
    """
    Place a new customer request for an item at a given route stop.

    Args:
        customer_id: ID of the requesting customer.
        van_id:      ID of the van serving the stop.
        stop_id:     ID of the route_stop where the customer will be.
        item_id:     ID of the inventory item being requested.
        quantity:    Number of units requested.

    Returns:
        The newly created CustomerRequest instance.
    """

    new_request = CustomerRequest(
        customer_id=customer_id,
        van_id=van_id,
        stop_id=stop_id,
        item_id=item_id,
        quantity=quantity,
    )

    van_id = get_active_van().van_id

    try:
        reserve_inventory(van_id, item_id, new_request.quantity)
    except Exception as e:
        db.session.rollback()
        print(f"Unexpected error: {e}")
        return None

    db.session.add(new_request)
    db.session.commit()
    return new_request

    