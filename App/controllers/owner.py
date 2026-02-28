from App.database import db
from App.models import Owner, Van, Route


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

def get_owner_routes(owner_id):
    """Get all routes belonging to an owner"""
    from App.models import Route
    return Route.query.filter_by(owner_id=owner_id).all()