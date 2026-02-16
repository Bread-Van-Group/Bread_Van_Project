from App.database import db
from datetime import datetime, timedelta, timezone

UTC_MINUS_4 = timezone(timedelta(hours=-4))


class Van(db.Model):
    __tablename__ = "vans"

    van_id           = db.Column(db.Integer, primary_key=True)
    license_plate    = db.Column(db.String(20),  nullable=False, unique=True)
    current_route_id = db.Column(db.Integer, db.ForeignKey("routes.route_id"),   nullable=True)
    status           = db.Column(db.String(20),  nullable=True)
    owner_id         = db.Column(db.Integer, db.ForeignKey("owners.owner_id"),   nullable=False)
    created_at       = db.Column(db.DateTime(timezone=True), nullable=True,
                                 default=lambda: datetime.now(UTC_MINUS_4))

    # Relationships
    daily_inventories  = db.relationship("DailyInventory",  backref="van", lazy=True)
    customer_requests  = db.relationship("CustomerRequest", backref="van", lazy=True)
    transactions       = db.relationship("Transaction",     backref="van", lazy=True)

    def __init__(self, license_plate, owner_id, current_route_id=None, status="inactive"):
        self.license_plate    = license_plate
        self.owner_id         = owner_id
        self.current_route_id = current_route_id
        self.status           = status

    def get_json(self):
        return {
            "van_id":           self.van_id,
            "license_plate":    self.license_plate,
            "current_route_id": self.current_route_id,
            "status":           self.status,
            "owner_id":         self.owner_id,
            "created_at":       self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Van {self.van_id} | {self.license_plate}>"