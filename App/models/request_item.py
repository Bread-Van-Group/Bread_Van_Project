from App.database import db
from datetime import datetime, timedelta, timezone

UTC_MINUS_4 = timezone(timedelta(hours=-4))


class RequestItem(db.Model):
    __tablename__ = "request_item"

    request_id     = db.Column(db.Integer, primary_key=True)
    stop_id        = db.Column(db.Integer, db.ForeignKey("stop_request.stop_request_id", ondelete="CASCADE"),   nullable=False)
    item_id        = db.Column(db.Integer, db.ForeignKey("inventory_items.item_id"), nullable=False)
    quantity       = db.Column(db.Integer, nullable=False)
    
    def __init__(self, stop_id, item_id, quantity):
        self.stop_id      = stop_id
        self.item_id      = item_id
        self.quantity     = quantity

    def get_json(self):
        return {
            "request_id":     self.request_id,
            "stop_id":        self.stop_id,
            "item_id":        self.item_id,
            "quantity":       self.quantity,
            "item" :          self.item.get_json()           
        }

    def __repr__(self):
        return f"<RequestItem {self.request_id} | Item {self.item}>"