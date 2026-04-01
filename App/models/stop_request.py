from App.database import db
from App.models.map_stop import MapStop
from datetime import datetime, timedelta, timezone

UTC_MINUS_4 = timezone(timedelta(hours=-4))

class StopRequest(MapStop):
    __tablename__ = "stop_request"

    stop_request_id        = db.Column(db.Integer, db.ForeignKey("map_stops.stop_id"), primary_key=True)
    route_id               = db.Column(db.Integer, db.ForeignKey("routes.route_id"),    nullable=False)
    customer_id            = db.Column(db.Integer, db.ForeignKey("customers.customer_id"), nullable=False)
    status_id              = db.Column(db.Integer, db.ForeignKey("statuses.status_id"),    nullable=False)
    fulfilled_time         = db.Column(db.DateTime(timezone=True), default=None, nullable=True)

    __mapper_args__ = {
        "polymorphic_identity": "stop_request",
    }

    # Relationships
    customer_requests = db.relationship("RequestItem", backref="stop", lazy=True, cascade="all, delete-orphan")
    status = db.relationship("Status", backref="stop", lazy=True)


    def __init__(self, route_id, customer_id, address, lat, lng, status_id):
        self.route_id               = route_id
        self.customer_id            = customer_id
        self.address                = address
        self.lat                    = lat
        self.lng                    = lng
        self.status_id              = status_id

    def get_json(self):
        return {
            "stop_id":                self.stop_id,
            "customer_id":            self.customer_id,
            "route_id":               self.route_id,
            "address":                self.address,
            "lat":                    self.lat,
            "lng":                    self.lng,
            "status_id":              self.status_id,
            "created_at":             self.created_at.isoformat() if self.created_at else None,
            "fulfilled_time":         self.fulfilled_time,
            "customer_requests":       [customer_request.get_json() for customer_request in self.customer_requests]
        }

    def __repr__(self):
        return f"<RouteStop {self.stop_id} | Route {self.route_id}>"