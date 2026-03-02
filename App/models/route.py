from App.database import db
from datetime import datetime, timedelta, timezone

UTC_MINUS_4 = timezone(timedelta(hours=-4))


class Route(db.Model):
    __tablename__ = "routes"

    route_id    = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text,        nullable=True)
    start_time  = db.Column(db.Time,        nullable=False)
    end_time    = db.Column(db.Time,        nullable=False)
    day_of_week = db.Column(db.String(10),  nullable=False)
    owner_id    = db.Column(db.Integer, db.ForeignKey("owners.owner_id"), nullable=False)
    created_at  = db.Column(db.DateTime(timezone=True), nullable=True,
                            default=lambda: datetime.now(UTC_MINUS_4))

    # Relationships
    stops = db.relationship("RouteStop", backref="route", lazy=True, cascade="all, delete-orphan", passive_deletes=True)
    driver_routes = db.relationship("DriverRoute",  backref="route", lazy=True)

    def __init__(self, name, start_time, end_time, day_of_week, owner_id, description=None):
        self.name        = name
        self.start_time  = start_time
        self.end_time    = end_time
        self.day_of_week = day_of_week
        self.owner_id    = owner_id
        self.description = description

    def get_json(self):
        return {
            "route_id":    self.route_id,
            "name":        self.name,
            "description": self.description,
            "start_time":  str(self.start_time),
            "end_time":    str(self.end_time),
            "day_of_week": self.day_of_week,
            "owner_id":    self.owner_id,
            "created_at":  self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<Route {self.route_id} | {self.name}>"