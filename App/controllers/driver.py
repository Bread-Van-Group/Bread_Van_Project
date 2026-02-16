from App.database import db
from App.models import Driver, DriverRoute, Route


def get_driver_by_id(driver_id):
    return db.session.get(Driver, driver_id)


def get_all_drivers():
    return db.session.scalars(db.select(Driver)).all()


def get_driver_routes(driver_id):
    """Return all routes assigned to a driver."""
    return db.session.scalars(
        db.select(DriverRoute).filter_by(driver_id=driver_id)
    ).all()


def assign_driver_to_route(driver_id, route_id):
    """
    Assign a driver to a route.
    Returns the new DriverRoute record, or None if the assignment already exists.
    """
    existing = db.session.execute(
        db.select(DriverRoute).filter_by(driver_id=driver_id, route_id=route_id)
    ).scalar_one_or_none()

    if existing:
        return None

    driver_route = DriverRoute(route_id=route_id, driver_id=driver_id)
    db.session.add(driver_route)
    db.session.commit()
    return driver_route


def unassign_driver_from_route(driver_id, route_id):
    """Remove a driver-route assignment. Returns True on success, False if not found."""
    driver_route = db.session.execute(
        db.select(DriverRoute).filter_by(driver_id=driver_id, route_id=route_id)
    ).scalar_one_or_none()

    if not driver_route:
        return False

    db.session.delete(driver_route)
    db.session.commit()
    return True