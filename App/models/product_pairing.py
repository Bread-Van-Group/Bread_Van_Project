from App.database import db
from datetime import datetime, timedelta, timezone

UTC_MINUS_4 = timezone(timedelta(hours=-4))


class ProductPairing(db.Model):
    __tablename__ = "product_pairings"

    pairing_id   = db.Column(db.Integer, primary_key=True)
    item1_id     = db.Column(db.Integer, db.ForeignKey("inventory_items.item_id"), nullable=False)
    item2_id     = db.Column(db.Integer, db.ForeignKey("inventory_items.item_id"), nullable=False)
    count        = db.Column(db.Integer, nullable=False, default=0)
    last_updated = db.Column(db.DateTime(timezone=True), nullable=True,
                             default=lambda: datetime.now(UTC_MINUS_4),
                             onupdate=lambda: datetime.now(UTC_MINUS_4))

    # Relationships
    item1 = db.relationship("InventoryItem", foreign_keys=[item1_id], lazy=True)
    item2 = db.relationship("InventoryItem", foreign_keys=[item2_id], lazy=True)

    def __init__(self, item1_id, item2_id, count=0):
        self.item1_id = item1_id
        self.item2_id = item2_id
        self.count    = count

    def get_json(self):
        return {
            "pairing_id":   self.pairing_id,
            "item1_id":     self.item1_id,
            "item2_id":     self.item2_id,
            "count":        self.count,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None,
        }

    def __repr__(self):
        return f"<ProductPairing {self.pairing_id} | {self.item1_id} <-> {self.item2_id}>"