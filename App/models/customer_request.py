from App.database import db
from datetime import datetime, timedelta, timezone

UTC_MINUS_4 = timezone(timedelta(hours=-4))


class CustomerRequest(db.Model):
    __tablename__ = "customer_requests"

    request_id     = db.Column(db.Integer, primary_key=True)
    customer_id    = db.Column(db.Integer, db.ForeignKey("customers.customer_id"), nullable=False)
    van_id         = db.Column(db.Integer, db.ForeignKey("vans.van_id"),           nullable=False)
    stop_id        = db.Column(db.Integer, db.ForeignKey("route_stops.stop_id", ondelete="CASCADE"),   nullable=False)
    item_id        = db.Column(db.Integer, db.ForeignKey("inventory_items.item_id"), nullable=False)
    quantity       = db.Column(db.Integer, nullable=False)
    
    def __init__(self, customer_id, van_id, stop_id, item_id, quantity):
        self.customer_id  = customer_id
        self.van_id       = van_id
        self.stop_id      = stop_id
        self.item_id      = item_id
        self.quantity     = quantity

    def get_json(self):
        return {
            "request_id":     self.request_id,
            "customer_id":    self.customer_id,
            "van_id":         self.van_id,
            "stop_id":        self.stop_id,
            "item_id":        self.item_id,
            "quantity":       self.quantity,
            "item" :          self.item.get_json()           
        }

    def __repr__(self):
        return f"<CustomerRequest {self.request_id} | Customer {self.customer_id}>"