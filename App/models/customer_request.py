from App.database import db
from datetime import datetime, timedelta, timezone

UTC_MINUS_4 = timezone(timedelta(hours=-4))


class CustomerRequest(db.Model):
    __tablename__ = "customer_requests"

    request_id     = db.Column(db.Integer, primary_key=True)
    customer_id    = db.Column(db.Integer, db.ForeignKey("customers.customer_id"), nullable=False)
    van_id         = db.Column(db.Integer, db.ForeignKey("vans.van_id"),           nullable=False)
    stop_id        = db.Column(db.Integer, db.ForeignKey("route_stops.stop_id"),   nullable=False)
    item_id        = db.Column(db.Integer, db.ForeignKey("inventory_items.item_id"), nullable=False)
    quantity       = db.Column(db.Integer, nullable=False)
    status_id      = db.Column(db.Integer, db.ForeignKey("statuses.status_id"),    nullable=False)
    request_time   = db.Column(db.DateTime(timezone=True), nullable=True,
                               default=lambda: datetime.now(UTC_MINUS_4))
    fulfilled_time = db.Column(db.DateTime(timezone=True), nullable=True)

    # Relationship to Status
    status = db.relationship("Status", backref="customer_requests", lazy=True)

    def __init__(self, customer_id, van_id, stop_id, item_id, quantity, status_id):
        self.customer_id  = customer_id
        self.van_id       = van_id
        self.stop_id      = stop_id
        self.item_id      = item_id
        self.quantity     = quantity
        self.status_id    = status_id

    def get_json(self):
        return {
            "request_id":     self.request_id,
            "customer_id":    self.customer_id,
            "van_id":         self.van_id,
            "stop_id":        self.stop_id,
            "item_id":        self.item_id,
            "quantity":       self.quantity,
            "status_id":      self.status_id,
            "request_time":   self.request_time.isoformat()   if self.request_time   else None,
            "fulfilled_time": self.fulfilled_time.isoformat() if self.fulfilled_time else None, 
            "item" :          self.item.get_json()           
        }

    def __repr__(self):
        return f"<CustomerRequest {self.request_id} | Customer {self.customer_id}>"