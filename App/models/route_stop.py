from App.database import db
from datetime import datetime, timedelta, timezone

UTC_MINUS_4 = timezone(timedelta(hours=-4))

"""
    Depending on whether the customer or owner id is null
    determines whether the stop is customer made or owner
    made. BOTH CAN NOT BE NULL

    Status ids may be null for owner stops along with ETA
"""

class RouteStop(db.Model):
    __tablename__ = "route_stops"

    stop_id                = db.Column(db.Integer, primary_key=True)
    route_id               = db.Column(db.Integer, db.ForeignKey("routes.route_id"),    nullable=False)
    owner_id               = db.Column(db.Integer, db.ForeignKey("owners.owner_id"),    nullable=True)
    customer_id            = db.Column(db.Integer, db.ForeignKey("customers.customer_id"), nullable=True)
    address                = db.Column(db.String(255), nullable=False)
    lat                    = db.Column(db.Float,       nullable=False)
    lng                    = db.Column(db.Float,       nullable=False)
    stop_order             = db.Column(db.Integer,     nullable=False)
    status_id              = db.Column(db.Integer, db.ForeignKey("statuses.status_id"),    nullable=True)
    estimated_arrival_time = db.Column(db.Time,        nullable=True)
    created_at             = db.Column(db.DateTime(timezone=True), nullable=True,
                                       default=lambda: datetime.now(UTC_MINUS_4))
    fulfilled_time         = db.Column(db.DateTime(timezone=True), nullable=True)

    # Relationships
    customer_requests = db.relationship("CustomerRequest", backref="stop", lazy=True, cascade="all, delete-orphan")
    transactions      = db.relationship("Transaction",     backref="stop", lazy=True)
    status = db.relationship("Status", backref="stop", lazy=True)


    def __init__(self, route_id, customer_id, owner_id, address, lat, lng, stop_order, status_id, fulfilled_time, estimated_arrival_time=None):
        self.route_id               = route_id
        self.owner_id               = owner_id
        self.customer_id            = customer_id
        self.address                = address
        self.lat                    = lat
        self.lng                    = lng
        self.stop_order             = stop_order
        self.status_id              = status_id
        self.estimated_arrival_time = estimated_arrival_time

    def get_json(self):
        return {
            "stop_id":                self.stop_id,
            "owner_id":               self.owner_id,
            "customer_id":            self.customer_id,
            "route_id":               self.route_id,
            "address":                self.address,
            "lat":                    self.lat,
            "lng":                    self.lng,
            "stop_order":             self.stop_order,
            "status_id":              self.status_id,
            "estimated_arrival_time": str(self.estimated_arrival_time) if self.estimated_arrival_time else None,
            "created_at":             self.created_at.isoformat() if self.created_at else None,
            "customer_requests":       [customer_request.get_json() for customer_request in self.customer_requests]
        }

    def __repr__(self):
        return f"<RouteStop {self.stop_id} | Route {self.route_id} | Order {self.stop_order}>"