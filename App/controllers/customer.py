from App.database import db
from datetime import date
from App.models import Customer, CustomerRequest
from App.controllers.route import get_stop_by_id


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

def get_today_customer_requests(customer_id):
    customer = get_customer_by_id(customer_id)
    if not customer:
        return None
    
    requests = []
    for request in customer.requests:
        request_day = request.request_time.date()
        if request_day == date.today() and (request.status_id == 1 or request.status_id== 2):
            requests.append(request)

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

def delete_today_pending_customer_order(customer_id):
    customer = get_customer_by_id(customer_id)
    stops = []
    if not customer:
        return False

    for request in customer.requests:
        request_day = request.request_time.date()
        if (request.status_id == 1 or request.status_id == 2) and request_day == date.today():
            stops.append(get_stop_by_id(request.stop_id))
            db.session.delete(request)
    
    for stop in stops:
        db.session.delete(stop)
    db.session.commit()
    return True