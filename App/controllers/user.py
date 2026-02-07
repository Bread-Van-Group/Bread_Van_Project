from App.models import User
from App.models.driver import Driver
from App.models.customer import Customer
from App.models.owner import Owner
from App.database import db

def create_user(name, email, password, address, role="customer"):  # Added address parameter
    """Create a new user with the specified role"""
    existing_user = get_user_by_username(name)
    if existing_user:
        return None
    
    newuser = User(name=name, email=email, password=password, address=address, role=role)
    db.session.add(newuser)
    db.session.commit()
    return newuser

def create_driver(name, email, password, address):  # Removed default None
    """Create a driver user with address"""
    existing_user = get_user_by_username(name)
    if existing_user:
        return None
    
    new_driver = Driver(name=name, email=email, password=password, address=address)
    db.session.add(new_driver)
    db.session.commit()
    return new_driver

def create_customer(name, email, password, address):  
    """Create a customer user"""
    existing_user = get_user_by_username(name)
    if existing_user:
        return None
    
    new_customer = Customer(name=name, email=email, password=password, address=address)
    db.session.add(new_customer)
    db.session.commit()
    return new_customer

def create_owner(name, email, password, address):  
    """Create an owner user"""
    existing_user = get_user_by_username(name)
    if existing_user:
        return None
    
    new_owner = Owner(name=name, email=email, password=password, address=address)
    db.session.add(new_owner)
    db.session.commit()
    return new_owner

def get_user_by_username(name):
    """Get user by username"""
    result = db.session.execute(db.select(User).filter_by(name=name))
    return result.scalar_one_or_none()

def get_user(id):
    """Get user by ID"""
    return db.session.get(User, id)

def get_all_users():
    """Get all users"""
    return db.session.scalars(db.select(User)).all()

def get_all_users_json():
    """Get all users as JSON"""
    users = get_all_users()
    if not users:
        return []
    users = [user.get_json() for user in users]
    return users

def update_user(id, name):
    """Update user's name"""
    user = get_user(id)
    if user:
        user.name = name
        db.session.commit()
        return user
    return None