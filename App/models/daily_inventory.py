from App.database import db
from datetime import datetime, timedelta, timezone

UTC_MINUS_4 = timezone(timedelta(hours=-4))


class DailyInventory(db.Model):
    __tablename__ = "daily_inventory"

    inventory_id       = db.Column(db.Integer, primary_key=True)
    van_id             = db.Column(db.Integer, db.ForeignKey("vans.van_id"),              nullable=False)
    date               = db.Column(db.Date,    nullable=False)
    item_id            = db.Column(db.Integer, db.ForeignKey("inventory_items.item_id"),  nullable=False)
    quantity_in_stock  = db.Column(db.Integer, nullable=False, default=0)
    quantity_reserved  = db.Column(db.Integer, nullable=False, default=0)
    quantity_available = db.Column(db.Integer, nullable=False, default=0)
    updated_at         = db.Column(db.DateTime(timezone=True), nullable=True,
                                   default=lambda: datetime.now(UTC_MINUS_4),
                                   onupdate=lambda: datetime.now(UTC_MINUS_4))

    def __init__(self, van_id, date, item_id, quantity_in_stock=0,
                 quantity_reserved=0, quantity_available=0):
        self.van_id             = van_id
        self.date               = date
        self.item_id            = item_id
        self.quantity_in_stock  = quantity_in_stock
        self.quantity_reserved  = quantity_reserved
        self.quantity_available = quantity_available

    def get_json(self):
        return {
            "inventory_id":       self.inventory_id,
            "van_id":             self.van_id,
            "date":               self.date.isoformat() if self.date else None,
            "item_id":            self.item_id,
            "quantity_in_stock":  self.quantity_in_stock,
            "quantity_reserved":  self.quantity_reserved,
            "quantity_available": self.quantity_available,
            "updated_at":         self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f"<DailyInventory {self.inventory_id} | Van {self.van_id} | Item {self.item_id}>"