from App.database import db
from datetime import datetime, timedelta, timezone

UTC_MINUS_4 = timezone(timedelta(hours=-4))

class Order(db.Model):
    __tablename__ = "order"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    inventory_item_id = db.Column(db.Integer, db.ForeignKey('inventory_item.id'), nullable=False)
    stop_request_id = db.Column(db.Integer, db.ForeignKey('stop_request.id'), nullable= False)
    quantity = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=True)
    date = db.Column(db.DateTime(timezone=True), nullable = False, default=lambda: datetime.now(UTC_MINUS_4))

    def __init__(self, inventory_item_id, stop_request_id, quantity, description=None):
        self.inventory_item_id = inventory_item_id
        self.stop_request_id = stop_request_id
        self.quantity = quantity
        self.description = description