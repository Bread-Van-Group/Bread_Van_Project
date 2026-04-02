from App.database import db
from App.models import StopRequest
from datetime import datetime, time, timezone, timedelta
from App.controllers.van import reserve_inventory, get_active_van 
from App.controllers.customer import get_customer_by_id

UTC_MINUS_4 = timezone(timedelta(hours=-4))

def get_stop_request_by_id(stop_request_id):
    return db.session.get(StopRequest, stop_request_id)

#Status id 1 = pending
#Status id 2 = confirmed

def get_pending_stops_by_area_route(route_id):
    pending_stops  = db.session.execute(
        db.select(StopRequest)
        .filter(StopRequest.status_id == 1)
        .filter(StopRequest.route_id == route_id)
        .distinct()
    ).scalars().all()

    return [pending_stop.get_json() for pending_stop in pending_stops]

def get_active_stops_by_area_route(route_id):
    active_stops = db.session.execute(
        db.select(StopRequest)
        .filter(StopRequest.status_id == 2)
        .filter(StopRequest.route_id == route_id)
        .distinct()
    ).scalars().all()

    return [active_stop.get_json() for active_stop in active_stops]



def add_customer_stop_to_route(route_id, customer_id, address, lat, lng, status_id):
    if get_today_customer_request(customer_id):
        print("Customer already has an active stop request for today.")
        return None

    stop = StopRequest(
        route_id=route_id,
        customer_id=customer_id,
        address=address,
        lat=lat,
        lng=lng,
        status_id=status_id,
    )

    db.session.add(stop)
    db.session.commit()
    return stop.get_json()

def edit_customer_stop(id, lat, lng, address, status):
    stop = get_stop_request_by_id(id)

    if not stop:
        return False
    
    stop.lat = lat
    stop.lng = lng
    stop.address = address
    stop.status_id = status
    
    db.session.add(stop)
    db.session.commit()

    return True


def update_request_status(status_id, stop_id , fulfilled=False):
    """Update the status (and optionally fulfilled_time) of a customer request."""
    stop = get_stop_request_by_id(stop_id)
    if not stop:
        return None

    stop.status_id = status_id
    if fulfilled:
        stop.fulfilled_time = datetime.now(UTC_MINUS_4)

    if status_id == 3 or status_id == 4:
        van_id = get_active_van().van_id
        requests = stop.customer_requests

        for request in requests:
            reserve_inventory(van_id, request.item_id, -request.quantity)

    db.session.commit()
    return stop

def get_today_customer_request(customer_id):
    customer = get_customer_by_id(customer_id)
    if not customer:
        return None

    today_start = datetime.combine(datetime.today(), time.min) 
    today_end = datetime.combine(datetime.today(), time.max)
    
    try:
        stop = db.session.execute(
            db.select(StopRequest)
            .filter(StopRequest.customer_id == customer_id)
            .filter(StopRequest.created_at.between(today_start, today_end))
        ).scalar_one_or_none()

        if stop:
            return stop.get_json()
        else:
            return None
    except:
        return None

def get_customer_request_total(customer_id, stop):
    requests = stop['customer_requests']

    return sum(
        order['quantity'] * order['item']['price']
        for order in requests
    )

def delete_today_pending_customer_order(customer_id):
    customer = get_customer_by_id(customer_id)
    if not customer:
        return False
    
    today_start = datetime.combine(datetime.today(), time.min) 
    today_end = datetime.combine(datetime.today(), time.max)
    

    stop = db.session.execute(
        db.select(StopRequest)
        .filter(StopRequest.customer_id == customer_id)
        .filter(StopRequest.created_at.between(today_start, today_end))
    ).scalar_one_or_none()

    van_id = get_active_van().van_id
    requests = stop.customer_requests
    
    for request in requests:
            reserve_inventory(van_id, request.item_id, -request.quantity)
    
    
    db.session.delete(stop)
    db.session.commit()
    return True