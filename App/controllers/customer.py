from App.database import db
from App.models import Customer

def get_customer_by_id(customer_id):
    return db.session.get(Customer, customer_id)


def get_all_customers():
    return db.session.scalars(db.select(Customer)).all()

def get_customers_by_region(region_id):
    """Return all customers in a given region."""
    return db.session.scalars(
        db.select(Customer).filter_by(region_id=region_id)
    ).all()


def update_customer_info(customer_id, name=None, address=None, phone=None, region_id=None):
    """
    Partially update a customer's profile fields.
    Only non-None arguments are applied.
    Returns the updated Customer, or None if not found.
    """
    customer = get_customer_by_id(customer_id)
    if not customer:
        return None
    if name      is not None: customer.name      = name
    if address   is not None: customer.address   = address
    if phone     is not None: customer.phone     = phone
    if region_id is not None: customer.region_id = region_id
    db.session.commit()
    return customer