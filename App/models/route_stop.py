from App.database import db
from datetime import datetime, timedelta, timezone

UTC_MINUS_4 = timezone(timedelta(hours=-4))


class RouteStop(db.Model):
    __tablename__ = "route_stops"

    stop_id                = db.Column(db.Integer, primary_key=True)
    route_id               = db.Column(db.Integer, db.ForeignKey("routes.route_id"),    nullable=False)
    address                = db.Column(db.String(255), nullable=False)
    lat                    = db.Column(db.Float,       nullable=False)
    lng                    = db.Column(db.Float,       nullable=False)
    stop_order             = db.Column(db.Integer,     nullable=False)
    estimated_arrival_time = db.Column(db.Time,        nullable=True)
    created_at             = db.Column(db.DateTime(timezone=True), nullable=True,
                                       default=lambda: datetime.now(UTC_MINUS_4))

    # Relationships
    customer_requests = db.relationship("CustomerRequest", backref="stop", lazy=True)
    transactions      = db.relationship("Transaction",     backref="stop", lazy=True)

    def __init__(self, route_id, address, lat, lng, stop_order, estimated_arrival_time=None):
        self.route_id               = route_id
        self.address                = address
        self.lat                    = lat
        self.lng                    = lng
        self.stop_order             = stop_order
        self.estimated_arrival_time = estimated_arrival_time

    def get_json(self):
        return {
            "stop_id":                self.stop_id,
            "route_id":               self.route_id,
            "address":                self.address,
            "lat":                    self.lat,
            "lng":                    self.lng,
            "stop_order":             self.stop_order,
            "estimated_arrival_time": str(self.estimated_arrival_time) if self.estimated_arrival_time else None,
            "created_at":             self.created_at.isoformat() if self.created_at else None,
            "customer_requests":       [customer_request.get_json() for customer_request in self.customer_requests]
        }

    def __repr__(self):
        return f"<RouteStop {self.stop_id} | Route {self.route_id} | Order {self.stop_order}>"