from App.database import db
from App.models import InventoryItem, ProductPairing


def get_item_by_id(item_id):
    return db.session.get(InventoryItem, item_id)


def get_all_items():
    return db.session.scalars(db.select(InventoryItem)).all()


def get_items_by_category(category):
    return db.session.scalars(
        db.select(InventoryItem).filter_by(category=category)
    ).all()


def create_item(name, price, description=None, category=None):
    item = InventoryItem(name=name, price=price,
                         description=description, category=category)
    db.session.add(item)
    db.session.commit()
    return item


def update_item(item_id, **kwargs):
    """Update any combination of name, price, description, category."""
    item = get_item_by_id(item_id)
    if not item:
        return None
    for field, value in kwargs.items():
        if hasattr(item, field):
            setattr(item, field, value)
    db.session.commit()
    return item


def delete_item(item_id):
    item = get_item_by_id(item_id)
    if not item:
        return False
    db.session.delete(item)
    db.session.commit()
    return True


# Product Pairings 

def get_product_pairings(item_id):
    """Return all pairing records that involve a given item."""
    return db.session.scalars(
        db.select(ProductPairing).where(
            (ProductPairing.item1_id == item_id) |
            (ProductPairing.item2_id == item_id)
        )
    ).all()


def increment_pairing(item1_id, item2_id):
    """
    Increment the co-purchase count for two items.
    The pair is stored with the lower ID first for consistency.
    """
    lo, hi = min(item1_id, item2_id), max(item1_id, item2_id)
    pairing = db.session.execute(
        db.select(ProductPairing).filter_by(item1_id=lo, item2_id=hi)
    ).scalar_one_or_none()

    if pairing:
        pairing.count += 1
    else:
        pairing = ProductPairing(item1_id=lo, item2_id=hi, count=1)
        db.session.add(pairing)

    db.session.commit()
    return pairing