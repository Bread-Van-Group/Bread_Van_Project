from App.database import db
from App.models import Owner, Van, Route, Driver


def get_owner_by_id(owner_id):
    return db.session.get(Owner, owner_id)


def get_all_owners():
    return db.session.scalars(db.select(Owner)).all()


def get_owner_vans(owner_id):
    """Return all vans belonging to an owner."""
    return db.session.scalars(
        db.select(Van).filter_by(owner_id=owner_id)
    ).all()


def get_owner_routes(owner_id):
    """Return all routes created by an owner."""
    return db.session.scalars(
        db.select(Route).filter_by(owner_id=owner_id)
    ).all()


def get_owner_drivers(owner_id):
    """Return all drivers employed by an owner."""
    return db.session.scalars(
        db.select(Driver).filter_by(owner_id=owner_id)
    ).all()


#  Driver/ Owner linkage
def assign_driver_to_owner(driver_id, owner_id):
    """
    Link an existing driver to an owner.
    Returns the updated Driver, or None if either record is not found.
    """
    driver = db.session.get(Driver, driver_id)
    owner  = db.session.get(Owner, owner_id)
    if not driver or not owner:
        return None
    driver.owner_id = owner_id
    db.session.commit()
    return driver


def unassign_driver_from_owner(driver_id):
    """
    Remove the owner link from a driver.
    Returns the updated Driver, or None if not found.
    """
    driver = db.session.get(Driver, driver_id)
    if not driver:
        return None
    driver.owner_id = None
    db.session.commit()
    return driver