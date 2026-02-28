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
    requests = customer.requests
    return [request.get_json() for request in requests]

def get_customer_request_total(customer_id):
    customer = get_customer_by_id(customer_id)
    if not customer:
        return None
    requests = customer.requests
    return sum(
        order.quantity * order.item.price
        for order in requests
    )


