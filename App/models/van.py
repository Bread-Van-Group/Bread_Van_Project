from App.database import db
from datetime import datetime, timedelta, timezone

UTC_MINUS_4 = timezone(timedelta(hours=-4))


class Van(db.Model):
    __tablename__ = "vans"

    van_id = db.Column(db.Integer, primary_key=True)
    license_plate = db.Column(db.String(20), nullable=False, unique=True)
    current_route_id = db.Column(db.Integer, db.ForeignKey("routes.route_id",ondelete="SET NULL"), nullable=True)
    status = db.Column(db.String(20), nullable=True)
    owner_id = db.Column(db.Integer, db.ForeignKey("owners.owner_id"), nullable=False)

    # NEW
    current_driver_id = db.Column(db.Integer, db.ForeignKey("drivers.driver_id",ondelete="SET NULL"), nullable=True)
    current_lat = db.Column(db.Float, nullable=True)
    current_lng = db.Column(db.Float, nullable=True)
    last_location_update = db.Column(db.DateTime(timezone=True), nullable=True)

    created_at = db.Column(db.DateTime(timezone=True), nullable=True,
                           default=lambda: datetime.now(UTC_MINUS_4))

    # Relationships
    daily_inventories = db.relationship("DailyInventory", backref="van", lazy=True)
    transactions = db.relationship("Transaction", backref="van", lazy=True)
    current_driver = db.relationship("Driver", foreign_keys=[current_driver_id], backref="assigned_van", lazy=True)

    def __init__(self, license_plate, owner_id, current_route_id=None, status="inactive"):
        self.license_plate = license_plate
        self.owner_id = owner_id
        self.current_route_id = current_route_id
        self.status = status

    def update_location(self, lat, lng):
        """Update van's GPS location (called by driver via WebSocket/API)"""
        self.current_lat = lat
        self.current_lng = lng
        self.last_location_update = datetime.now(UTC_MINUS_4)

    def assign_driver(self, driver_id):
        """Assign a driver to this van"""
        self.current_driver_id = driver_id

    def unassign_driver(self):
        """Remove driver assignment"""
        self.current_driver_id = None

    def get_json(self):
        return {
            "van_id": self.van_id,
            "license_plate": self.license_plate,
            "current_route_id": self.current_route_id,
            "status": self.status,
            "owner_id": self.owner_id,
            "current_driver_id": self.current_driver_id,
            "current_driver_name": self.current_driver.name if self.current_driver else None,
            "current_lat": self.current_lat,
            "current_lng": self.current_lng,
            "last_location_update": self.last_location_update.isoformat() if self.last_location_update else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Van {self.van_id} | {self.license_plate}>"