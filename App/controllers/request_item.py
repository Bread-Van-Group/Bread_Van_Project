from App.database import db
from App.models import  RequestItem
from App.controllers.van import reserve_inventory 

def get_request_by_id(request_id):
    return db.session.execute(
        db.select(RequestItem)
        .filter_by(request_id=request_id)
    ).scalar_one_or_none()

def get_requests_by_stop_id(stop_id):
    return db.session.scalars(
        db.select(RequestItem)
        .filter_by(stop_id=stop_id)
    ).all()

def create_customer_request(van_id, stop_id, item_id, quantity):
    new_request = RequestItem(
        stop_id=stop_id,
        item_id=item_id,
        quantity=quantity,
    )

    result = reserve_inventory(van_id, item_id, new_request.quantity)
    if result is None:
        return None

    db.session.add(new_request)
    db.session.commit()
    return new_request

    