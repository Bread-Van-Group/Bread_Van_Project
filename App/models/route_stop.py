from App.database import db
from .map_stop import MapStop
from datetime import datetime, timedelta, timezone

UTC_MINUS_4 = timezone(timedelta(hours=-4))

class RouteStop(MapStop):
    __tablename__ = "route_stops"

    stop_id                = db.Column(db.Integer, db.ForeignKey("map_stops.stop_id"),  primary_key=True)
    route_id               = db.Column(db.Integer, db.ForeignKey("routes.route_id"),    nullable=False)
    owner_id               = db.Column(db.Integer, db.ForeignKey("owners.owner_id"),    nullable=False)
    stop_order             = db.Column(db.Integer,     nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "route_stop",
    }
    
    def __init__(self, route_id, owner_id, address, lat, lng, stop_order):
        self.route_id               = route_id
        self.owner_id               = owner_id
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