from App.database import db
from App.models import Customer, CustomerRequest


def get_customer_by_id(customer_id):
    return db.session.get(Customer, customer_id)


def get_all_customers():
    return db.session.scalars(db.select(Customer)).all()


def get_customer_requests(customer_id):
    """Return all requests belonging to a customer."""
    customer = get_customer_by_id(customer_id)
    if not customer:
        return None
    return customer.requests


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