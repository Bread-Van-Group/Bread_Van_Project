from App.database import db
from App.models import Driver, DriverRoute, Route, RouteArea, Region


def get_driver_by_id(driver_id):
    return db.session.get(Driver, driver_id)


def get_all_drivers():
    return db.session.scalars(db.select(Driver)).all()


def get_assigned_driver_route(driver_id):
    #Return Route Assigned to Driver
    assigned_route = db.session.execute(
        db.select(DriverRoute).filter_by(driver_id=driver_id)
    ).scalar_one_or_none()

    return db.session.get(Route, assigned_route.route_id)

def get_assigned_driver_region(driver_id):
    driver_route = get_assigned_driver_route(driver_id)

    assigned_region = db.session.execute(
        db.select(RouteArea).filter_by(route_id = driver_route.route_id)
    ).scalar_one_or_none()

    return db.session.get(Region, assigned_region.region_id)

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

def update_driver_info(driver_id, name=None, address=None, phone=None, owner_id=None):
    """
    Partially update a driver's profile fields.
    Only non-None arguments are applied.
    Returns the updated Driver, or None if not found.
    """
    driver = get_driver_by_id(driver_id)
    if not driver:
        return None
    if name is not None: driver.name = name
    if address is not None: driver.address = address
    if phone is not None: driver.phone = phone
    if owner_id is not None: driver.owner_id = owner_id
    db.session.commit()
    return driver