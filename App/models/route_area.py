from App.database import db


class RouteArea(db.Model):
    """Bridge table: Routes ↔ Regions (which regions does each route serve)"""
    __tablename__ = "route_areas"

    route_area_id = db.Column(db.Integer, primary_key=True)
    route_id      = db.Column(db.Integer, db.ForeignKey("routes.route_id", ondelete="CASCADE"), nullable=False)
    region_id     = db.Column(db.Integer, db.ForeignKey("regions.region_id", ondelete="CASCADE"), nullable=False)

    # Unique constraint - a route can only serve each region once
    __table_args__ = (db.UniqueConstraint('route_id', 'region_id', name='uq_route_region'),)

    def __init__(self, route_id, region_id):
        self.route_id  = route_id
        self.region_id = region_id

    def get_json(self):
        return {
            "route_area_id": self.route_area_id,
            "route_id":      self.route_id,
            "region_id":     self.region_id,
            "region_name":   self.region.name if self.region else None,
        }

    def __repr__(self):
        return f"<RouteArea {self.route_area_id} | Route {self.route_id} → Region {self.region_id}>"