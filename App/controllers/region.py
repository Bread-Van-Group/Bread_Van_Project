from App.database import db
from App.models import Region


# ── Queries ────────────────────────────────────────────────────────────────────

def get_region_by_id(region_id):
    return db.session.get(Region, region_id)


def get_region_by_name(name):
    return db.session.execute(
        db.select(Region).filter_by(name=name)
    ).scalar_one_or_none()

# ── Create / update / delete ───────────────────────────────────────────────────

def create_region(name, description=None):
    """
    Create a new geographic region.
    Returns None (idempotent) if a region with the same name already exists.
    """
    if get_region_by_name(name):
        return None
    region = Region(name=name, description=description)
    db.session.add(region)
    db.session.commit()
    return region


def update_region(region_id, name=None, description=None):
    """
    Partially update a region's fields.
    Returns the updated Region, or None if not found.
    """
    region = get_region_by_id(region_id)
    if not region:
        return None
    if name        is not None: region.name        = name
    if description is not None: region.description = description
    db.session.commit()
    return region


def delete_region(region_id):
    """
    Delete a region.
    Cascade rules on the model will remove related RouteArea records.
    Returns True on success, False if not found.
    """
    region = get_region_by_id(region_id)
    if not region:
        return False
    db.session.delete(region)
    db.session.commit()
    return True