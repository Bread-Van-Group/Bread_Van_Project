from App.database import db
from datetime import datetime, timedelta, timezone

UTC_MINUS_4 = timezone(timedelta(hours=-4))


class RouteHistory(db.Model):
    """Tracks each drive session (route history)"""
    __tablename__ = "route_history"

    history_id = db.Column(db.Integer, primary_key=True)
    route_id   = db.Column(db.Integer, db.ForeignKey("routes.route_id"), nullable=False)
    van_id     = db.Column(db.Integer, db.ForeignKey("vans.van_id"), nullable=False)
    driver_id  = db.Column(db.Integer, db.ForeignKey("drivers.driver_id"), nullable=False)
    started_at = db.Column(db.DateTime(timezone=True), nullable=False,
                          default=lambda: datetime.now(UTC_MINUS_4))
    ended_at   = db.Column(db.DateTime(timezone=True), nullable=True)
    status     = db.Column(db.String(20), nullable=False, default='in_progress')

    def __init__(self, route_id, van_id, driver_id):
        self.route_id  = route_id
        self.van_id    = van_id
        self.driver_id = driver_id
        self.status    = 'in_progress'

    def complete(self):
        """Mark this drive session as completed"""
        self.ended_at = datetime.now(UTC_MINUS_4)
        self.status   = 'completed'

    def get_json(self):
        return {
            "history_id": self.history_id,
            "route_id":   self.route_id,
            "van_id":     self.van_id,
            "driver_id":  self.driver_id,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "ended_at":   self.ended_at.isoformat() if self.ended_at else None,
            "status":     self.status,
        }

    def __repr__(self):
        return f"<RouteHistory {self.history_id} | Route {self.route_id} | {self.status}>"