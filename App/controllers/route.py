from App.database import db
from App.models import Route, RouteStop


def get_route_by_id(route_id):
    return db.session.get(Route, route_id)


def get_all_routes():
    return db.session.scalars(db.select(Route)).all()


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