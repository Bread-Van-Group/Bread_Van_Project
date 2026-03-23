from App.database import db
from App.models import Route, RouteStop
from sqlalchemy import func
from datetime import datetime
from App.controllers.van import reserve_inventory, get_active_van 
from App.controllers.customer_request import get_requests_by_stop_id


def get_route_by_id(route_id):
    return db.session.get(Route, route_id)

def get_todays_route():
    day = datetime.now().strftime("%A") 
    return db.session.execute(
        db.select(Route).filter_by(
            day_of_week = day
        )
    ).scalar_one_or_none()

def get_stop_by_id(stop_id):
    return db.session.get(RouteStop, stop_id)

def get_all_routes():
    return db.session.scalars(db.select(Route)).all()

#Status id 1 = pending
#Status id 2 = confirmed

def get_pending_stops():
    pending_stops = active_stops = db.session.execute(
        db.select(RouteStop)
        .filter(RouteStop.status_id == 1)
        .distinct()
    ).scalars().all()

    return [pending_stop.get_json() for pending_stop in pending_stops]

def get_active_stops():
    active_stops = active_stops = db.session.execute(
        db.select(RouteStop)
        .filter(RouteStop.status_id == 2)
        .distinct()
    ).scalars().all()

    return [active_stop.get_json() for active_stop in active_stops]



def create_route(name, start_time, end_time, day_of_week, owner_id, description=None):
    route = Route(
        name=name,
        start_time=start_time,
        end_time=end_time,
        day_of_week=day_of_week,
        owner_id=owner_id,
        description=description,
    )
    db.session.add(route)
    db.session.commit()
    return route


def get_route_stops(route_id):
    """Return all stops for a route, ordered by stop_order."""
    return db.session.scalars(
        db.select(RouteStop)
        .filter_by(route_id=route_id)
        .order_by(RouteStop.stop_order)
    ).all()

def add_customer_stop_to_route(route_id, customer_id, address, lat, lng, stop_order, status_id):
    #The owner_id is null to denote this as a customer made stop
    
    stop = RouteStop(
        route_id=route_id,
        owner_id=None,
        customer_id=customer_id,
        address=address,
        lat=lat,
        lng=lng,
        stop_order=stop_order,
        status_id=status_id,
        estimated_arrival_time=None,
        fulfilled_time=None
    )

    db.session.add(stop)
    db.session.commit()
    return stop.get_json()

def edit_customer_stop(id, lat, lng, status):
    stop = get_stop_by_id(id)

    if not stop:
        return False
    
    stop.lat = lat
    stop.lng = lng
    stop.status_id = status
    
    db.session.add(stop)
    db.session.commit()

    return True

def update_request_status(status_id, stop_id , fulfilled=False):
    """Update the status (and optionally fulfilled_time) of a customer request."""
    from datetime import datetime, timedelta, timezone
    UTC_MINUS_4 = timezone(timedelta(hours=-4))

    request = get_stop_by_id(stop_id)
    if not request:
        return None

    request.status_id = status_id
    if fulfilled:
        request.fulfilled_time = datetime.now(UTC_MINUS_4)

    if status_id == 3 or status_id == 4:
        van_id = get_active_van().van_id
        requests = get_requests_by_stop_id(stop_id)

        for request in requests:
            reserve_inventory(van_id, request.item_id, -request.quantity)

    db.session.commit()
    return request


def add_stop_to_route(route_id, address, lat, lng, stop_order, estimated_arrival_time=None):
    stop = RouteStop(
        route_id=route_id,
        address=address,
        lat=lat,
        lng=lng,
        stop_order=stop_order,
        estimated_arrival_time=estimated_arrival_time,
    )
    db.session.add(stop)
    db.session.commit()
    return stop

def add_stop_to_end_of_route(route_id, stop_id):
    stop = get_stop_by_id(stop_id)

    if not stop:
        return False

    try:
        last_stop_order = db.session.execute(
            db.select(func.max(RouteStop.stop_order))
            .where(RouteStop.route_id == route_id)
        ).scalar()

        stop.stop_order = (last_stop_order or 0) + 1
        db.session.commit()
        return True
    except Exception as e:
        db.session.rollback()
        print(f"Unexpected error: {e}")
        return False

def remove_stop_from_route(stop_id):
    """Delete a route stop by ID. Returns True on success, False if not found."""
    stop = db.session.get(RouteStop, stop_id)
    if not stop:
        return False
    
    db.session.delete(stop)
    db.session.commit()
    return True


def delete_route(route_id):
    """Delete a route and cascade-remove its stops. Returns True on success."""
    route = get_route_by_id(route_id)
    if not route:
        return False
    db.session.delete(route)
    db.session.commit()
    return True