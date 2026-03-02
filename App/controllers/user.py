from App.models import User, Driver, Customer, Owner
from App.database import db


# User queries

def get_user(user_id):
    return db.session.get(User, user_id)


def get_user_by_email(email):
    return db.session.execute(
        db.select(User).filter_by(email=email)
    ).scalar_one_or_none()


def get_all_users():
    return db.session.scalars(db.select(User)).all()


def get_all_users_json():
    return [u.get_json() for u in get_all_users()]


# create users

def create_driver(email, password, name, address=None, phone=None):
    if get_user_by_email(email):
        return None
    driver = Driver(email=email, password=password, name=name,
                    address=address, phone=phone)
    db.session.add(driver)
    db.session.commit()
    return driver


def create_customer(email, password, name, address=None, phone=None, area=None):
    if get_user_by_email(email):
        return None
    customer = Customer(email=email, password=password, name=name,
                        address=address, phone=phone, area=area)
    db.session.add(customer)
    db.session.commit()
    return customer


def create_owner(email, password):
    if get_user_by_email(email):
        return None
    owner = Owner(email=email, password=password)
    db.session.add(owner)
    db.session.commit()
    return owner


def update_user_email(user_id, new_email):
    user = get_user(user_id)
    if user:
        user.email = new_email
        db.session.commit()
        return user
    return None