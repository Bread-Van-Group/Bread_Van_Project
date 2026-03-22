from App.database import db
from datetime import date
from App.models import Customer, RouteStop
from App.controllers.route import get_stop_by_id
from datetime import datetime, time
from App.controllers.van import reserve_inventory, get_active_van 
from App.controllers.customer_request import get_requests_by_stop_id



def get_customer_by_id(customer_id):
    return db.session.get(Customer, customer_id)


def get_all_customers():
    return db.session.scalars(db.select(Customer)).all()

def get_today_customer_request(customer_id):
    customer = get_customer_by_id(customer_id)
    if not customer:
        return None

    today_start = datetime.combine(datetime.today(), time.min) 
    today_end = datetime.combine(datetime.today(), time.max)
    
    stop = db.session.execute(
        db.select(RouteStop)
        .filter(RouteStop.customer_id == customer_id)
        .filter(RouteStop.created_at.between(today_start, today_end))
    ).scalar_one_or_none()

    if stop:
        return stop.get_json()
    
    return None

def get_customer_request_total(customer_id, stop_id):
    customer = get_customer_by_id(customer_id)
    if not customer:
        return None
    stop = get_stop_by_id(stop_id)

    return sum(
        order.quantity * order.item.price
        for order in stop.customer_requests
    )

def delete_today_pending_customer_order(customer_id):
    customer = get_customer_by_id(customer_id)
    if not customer:
        return False
    
    today_start = datetime.combine(datetime.today(), time.min) 
    today_end = datetime.combine(datetime.today(), time.max)
    

    stop = db.session.execute(
        db.select(RouteStop)
        .filter(RouteStop.customer_id == customer_id)
        .filter(RouteStop.created_at.between(today_start, today_end))
    ).scalar_one_or_none()

    van_id = get_active_van().van_id
    requests = get_requests_by_stop_id(stop.stop_id)
    
    for request in requests:
            reserve_inventory(van_id, request.item_id, -request.quantity)
    
    
    db.session.delete(stop)
    db.session.commit()
    return True