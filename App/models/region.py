from App.database import db
from datetime import datetime, timedelta, timezone

UTC_MINUS_4 = timezone(timedelta(hours=-4))


class Region(db.Model):
    """Geographic regions (Chaguanas, San Fernando, Port of Spain, etc.)"""
    __tablename__ = "regions"

    region_id   = db.Column(db.Integer, primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)

    # Relationships
    customers   = db.relationship("Customer", backref="region", lazy=True)
    route_areas = db.relationship("RouteArea", backref="region", lazy=True, cascade="all, delete-orphan")

    def __init__(self, name, description=None):
        self.name        = name
        self.description = description

    def get_json(self):
        return {
            "region_id":      self.region_id,
            "name":           self.name,
            "description":    self.description,
            "customer_count": len(self.customers) if self.customers else 0,
        }

    def __repr__(self):
        return f"<Region {self.region_id} | {self.name}>"