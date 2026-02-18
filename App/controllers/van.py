from App.database import db
from App.models import Van, DailyInventory
from datetime import date


def get_van_by_id(van_id):
    return db.session.get(Van, van_id)

def get_active_van():
    return db.session.execute(
        db.select(Van)
        .filter_by(status="active")
    ).scalar_one_or_none()


def get_all_vans():
    return db.session.scalars(db.select(Van)).all()


def create_van(license_plate, owner_id, current_route_id=None, status="inactive"):
    van = Van(license_plate=license_plate, owner_id=owner_id,
              current_route_id=current_route_id, status=status)
    db.session.add(van)
    db.session.commit()
    return van


def update_van_status(van_id, status):
    van = get_van_by_id(van_id)
    if not van:
        return None
    van.status = status
    db.session.commit()
    return van


def assign_van_to_route(van_id, route_id):
    van = get_van_by_id(van_id)
    if not van:
        return None
    van.current_route_id = route_id
    db.session.commit()
    return van


# Daily Inventory

def get_van_daily_inventory(van_id, target_date=None):
    """Return today's inventory records for a van (or a specified date)."""
    target_date = target_date or date.today()
    return db.session.scalars(
        db.select(DailyInventory).filter_by(van_id=van_id, date=target_date)
    ).all()


def set_van_inventory(van_id, item_id, quantity_in_stock, target_date=None):
    """
    Upsert a DailyInventory record for a van + item + date.
    quantity_available is set to match quantity_in_stock on creation
    (reserved starts at 0).
    """
    target_date = target_date or date.today()
    record = db.session.execute(
        db.select(DailyInventory).filter_by(
            van_id=van_id, item_id=item_id, date=target_date
        )
    ).scalar_one_or_none()

    if record:
        record.quantity_in_stock  = quantity_in_stock
        record.quantity_available = quantity_in_stock - record.quantity_reserved
    else:
        record = DailyInventory(
            van_id=van_id,
            date=target_date,
            item_id=item_id,
            quantity_in_stock=quantity_in_stock,
            quantity_reserved=0,
            quantity_available=quantity_in_stock,
        )
        db.session.add(record)

    db.session.commit()
    return record


def reserve_inventory(van_id, item_id, quantity, target_date=None):
    """
    Reserve `quantity` units for a customer request.
    Returns the updated DailyInventory or None if insufficient stock.
    """
    target_date = target_date or date.today()
    record = db.session.execute(
        db.select(DailyInventory).filter_by(
            van_id=van_id, item_id=item_id, date=target_date
        )
    ).scalar_one_or_none()

    if not record or record.quantity_available < quantity:
        return None

    record.quantity_reserved  += quantity
    record.quantity_available -= quantity
    db.session.commit()
    return record