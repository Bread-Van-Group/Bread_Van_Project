from App.database import db
from App.models import Customer, StopRequest, Order

def create_customer(name, email, password, address):
    new_customer = Customer(name=name, email=email, password=password, address=address)
    db.session.add(new_customer)
    db.session.commit()
    return new_customer

def get_customer_by_id(customer_id):
    return db.session.get(Customer, customer_id)

def get_all_customers():
    return db.session.scalars(db.select(Customer)).all()

def get_customer_stop_requests(customer_id):
    customer = get_customer_by_id(customer_id)
    if not customer:
        return f"Customer with id {customer_id} not found."
    
    return customer.stop_requests

def create_stop_request(customer_id, address, lat, lng, orders=None):
    new_stop_request = StopRequest(customer_id=customer_id, driver_id=None, address=address,lat=lat, lng=lng)
    db.session.add(new_stop_request)
    db.session.commit()

    if orders:
        for order_data in orders:
            new_order = Order(
                stop_request_id=new_stop_request.id,
                item_name=order_data['item_name'],
                quantity=order_data['quantity']
            )
            db.session.add(new_order)
        db.session.commit()

    return new_stop_request
