from App.database import db
from App.models import Driver, StopRequest

def create_driver(name, email, password):
    new_driver = Driver(name=name, email=email, password=password)
    db.session.add(new_driver)
    db.session.commit()
    return new_driver

def get_driver_by_id(driver_id):
    return db.session.get(Driver, driver_id)

def get_all_drivers():
    return db.session.scalars(db.select(Driver)).all()

def accept_stop_request(driver_id, stop_request_id):
    stop_request = db.session.get(StopRequest, stop_request_id)
    stop_request.driver_id = driver_id
    stop_request.status = 'accepted'

    db.session.add(stop_request)
    db.session.commit()