from App.database import db
from App.models import RouteArea


# ── Queries ────────────────────────────────────────────────────────────────────

def get_route_area_by_id(route_area_id):
    return db.session.get(RouteArea, route_area_id)


def get_areas_for_route(route_id):
    """Return all RouteArea records for a given route."""
    return db.session.scalars(
        db.select(RouteArea).filter_by(route_id=route_id)
    ).all()


def get_routes_for_region(region_id):
    """Return all RouteArea records that serve a given region."""
    return db.session.scalars(
        db.select(RouteArea).filter_by(region_id=region_id)
    ).all()


def route_serves_region(route_id, region_id):
    """Return True if the route already covers the given region."""
    return db.session.execute(
        db.select(RouteArea).filter_by(route_id=route_id, region_id=region_id)
    ).scalar_one_or_none() is not None


# ── Create / delete ────────────────────────────────────────────────────────────

def add_region_to_route(route_id, region_id):
    """
    Link a region to a route (idempotent).
    Returns the existing or newly created RouteArea record.
    """
    existing = db.session.execute(
        db.select(RouteArea).filter_by(route_id=route_id, region_id=region_id)
    ).scalar_one_or_none()

    if existing:
        return existing

    route_area = RouteArea(route_id=route_id, region_id=region_id)
    db.session.add(route_area)
    db.session.commit()
    return route_area


def remove_region_from_route(route_id, region_id):
    """
    Remove a region from a route's coverage.
    Returns True on success, False if the link did not exist.
    """
    route_area = db.session.execute(
        db.select(RouteArea).filter_by(route_id=route_id, region_id=region_id)
    ).scalar_one_or_none()

    if not route_area:
        return False

    db.session.delete(route_area)
    db.session.commit()
    return True


def remove_all_regions_from_route(route_id):
    """Remove every region link for a route. Useful before deleting a route."""
    areas = get_areas_for_route(route_id)
    for area in areas:
        db.session.delete(area)
    db.session.commit()
    return len(areas)