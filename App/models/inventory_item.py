from App.database import db
from datetime import datetime, timedelta, timezone

UTC_MINUS_4 = timezone(timedelta(hours=-4))


class InventoryItem(db.Model):
    __tablename__ = "inventory_items"

    item_id     = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text,        nullable=True)
    price       = db.Column(db.Numeric(10, 2), nullable=False)
    category    = db.Column(db.String(50),  nullable=True)
    created_at  = db.Column(db.DateTime(timezone=True), nullable=True,
                            default=lambda: datetime.now(UTC_MINUS_4))

    # Relationships
    daily_inventories  = db.relationship("DailyInventory",  backref="item", lazy=True)
    transaction_items  = db.relationship("TransactionItem", backref="item", lazy=True)
    customer_requests  = db.relationship("CustomerRequest", backref="item", lazy=True)

    def __init__(self, name, price, description=None, category=None):
        self.name        = name
        self.price       = price
        self.description = description
        self.category    = category

    def get_json(self):
        return {
            "item_id":     self.item_id,
            "name":        self.name,
            "description": self.description,
            "price":       float(self.price),
            "category":    self.category,
            "created_at":  self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<InventoryItem {self.item_id} | {self.name}>"