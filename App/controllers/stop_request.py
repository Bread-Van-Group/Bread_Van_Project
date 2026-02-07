from App.database import db
from App.models import StopRequest

def get_stop_request_by_id(stop_request_id):
    return db.session.get(StopRequest, stop_request_id)

def get_all_stop_requests():
    return db.session.scalars(db.select(StopRequest)).all()

def get_all_active_stop_requests():
    result = db.session.execute(db.select(StopRequest).filter_by(status='active'))
    return result.scalars().all()

def get_all_pending_stop_requests():
    result = db.session.execute(db.select(StopRequest).filter_by(status='pending'))
    return result.scalars().all()

def cancel_stop_request(stop_request_id, driver_id=None):
    stop_request = db.session.get(StopRequest, stop_request_id)
    stop_request.driver_id = driver_id
    stop_request.status = 'cancelled'

    db.session.add(stop_request)
    db.session.commit()