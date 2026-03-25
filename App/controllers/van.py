from App.database import db
from App.models import Van, DailyInventory
from datetime import date


def get_van_by_id(van_id):
    return db.session.get(Van, van_id)

def get_van_by_driver(driver_id):
    return db.session.execute(
        db.select(Van)
        .filter_by(current_driver_id=driver_id)
    ).scalar_one_or_none()

def get_active_van():
    from App.models import Van
    return db.session.execute(
        db.select(Van).filter_by(status='active')
    ).scalars().first()  # ✅ Returns first active van

def get_active_van_plate():
    van = db.session.execute(
        db.select(Van)
        .filter_by(status="active")
    ).scalars().first()

    return van.license_plate

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

def get_daily_inventory_item_by_id(inventory_id):
    return db.session.get(DailyInventory, inventory_id)

def get_van_daily_inventory(van_id, target_date=None):
    """Return today's inventory records for a van (or a specified date)."""
    target_date = target_date or date.today()
    return db.session.scalars(
        db.select(DailyInventory).filter_by(van_id=van_id, date=target_date)
    ).all()


# Replace the set_van_inventory function in App/controllers/van.py with this:

def set_van_inventory(van_id, item_id, quantity, date):
    """Set or delete daily inventory for a van"""
    from App.models import DailyInventory
    from App.database import db

    # Find existing inventory record
    existing = DailyInventory.query.filter_by(
        van_id=van_id,
        item_id=item_id,
        date=date
    ).first()

    if quantity == 0:
        # DELETE the record completely when quantity is 0
        if existing:
            db.session.delete(existing)
            db.session.commit()
            print(f"Deleted inventory: van_id={van_id}, item_id={item_id}, date={date}")
    else:
        # CREATE or UPDATE the record
        if existing:
            # Update existing record
            existing.quantity_available = quantity
            existing.quantity_in_stock = quantity
            print(f"Updated inventory: van_id={van_id}, item_id={item_id}, quantity={quantity}")
        else:
            # Create new record
            new_inventory = DailyInventory(
                van_id=van_id,
                item_id=item_id,
                date=date,
                quantity_available=quantity,
                quantity_in_stock=quantity
            )
            db.session.add(new_inventory)
            print(f"Created inventory: van_id={van_id}, item_id={item_id}, quantity={quantity}")

        db.session.commit()

    return True
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

    try:
        record.quantity_reserved  += quantity
        record.quantity_available -= quantity
    except:
        db.session.rollback()
        return None
    
    db.session.commit()
    return record

def update_stock(van_id, item_id, quantity,target_date =None):
    target_date = target_date or date.today()
    
    record = db.session.execute(
        db.select(DailyInventory).filter_by(
            van_id=van_id, item_id=item_id, date=target_date
        )
    ).scalar_one_or_none()

    if not record:
        return None
    
    try:
        record.quantity_in_stock -= quantity
        record.quantity_available -= quantity
    except:
        db.session.rollback()
        return None
    
    db.session.commit()
    return record