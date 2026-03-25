from App.database import db
from datetime import datetime, timedelta, timezone

UTC_MINUS_4 = timezone(timedelta(hours=-4))

class MapStop(db.Model):
    __tablename__ = "map_stops"

    stop_id                = db.Column(db.Integer, primary_key=True)
    address                = db.Column(db.String(255), nullable=False)
    lat                    = db.Column(db.Float,       nullable=False)
    lng                    = db.Column(db.Float,       nullable=False)
    stop_type              = db.Column(db.String(20),  nullable=False)
    stop_order             = db.Column(db.Integer,     nullable=False)
    created_at             = db.Column(db.DateTime(timezone=True), nullable=True,
                                       default=lambda: datetime.now(UTC_MINUS_4))
   
    __mapper_args__ = {
        "polymorphic_on": stop_type,
        "polymorphic_identity": "map_stop",
    }
   
    # Relationships
    transactions      = db.relationship("Transaction",     backref="map_stop", lazy=True)

    def __init__(self, route_id, owner_id, address, lat, lng, stop_order):
        self.address                = address
        self.lat                    = lat
        self.lng                    = lng
        self.stop_order             = stop_order

    def get_json(self):
        return {
            "stop_id":                self.stop_id,
            "owner_id":               self.owner_id,
            "route_id":               self.route_id,
            "address":                self.address,
            "lat":                    self.lat,
            "lng":                    self.lng,
            "stop_order":             self.stop_order,
            "created_at":             self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<RouteStop {self.stop_id} | Route {self.route_id} | Order {self.stop_order}>"