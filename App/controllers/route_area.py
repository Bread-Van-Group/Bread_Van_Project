from App.database import db
from App.models import RouteArea


# ── Queries ────────────────────────────────────────────────────────────────────

def get_route_area_by_id(route_area_id):
    return db.session.get(RouteArea, route_area_id)


def get_area_for_route(route_id):
    """Return all RouteArea records for a given route."""
    return db.session.execute(
        db.select(RouteArea).filter_by(route_id=route_id)
    ).scalar_one_or_none()


def get_route_for_region(region_id):
    """Return all RouteArea records that serve a given region."""
    return db.session.execute(
        db.select(RouteArea).filter_by(region_id=region_id)
    ).scalar_one_or_none()


def route_serves_region(route_id, region_id):
    """Return True if the route already covers the given region."""
    return db.session.execute(
        db.select(RouteArea).filter_by(route_id=route_id, region_id=region_id)
    ).scalar_one_or_none() is not None
