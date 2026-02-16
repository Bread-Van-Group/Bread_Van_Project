from App.database import db


class DriverRoute(db.Model):
    __tablename__ = "driver_routes"

    driver_route_id = db.Column(db.Integer, primary_key=True)
    route_id        = db.Column(db.Integer, db.ForeignKey("routes.route_id"),   nullable=False)
    driver_id       = db.Column(db.Integer, db.ForeignKey("drivers.driver_id"), nullable=False)

    def __init__(self, route_id, driver_id):
        self.route_id  = route_id
        self.driver_id = driver_id

    def get_json(self):
        return {
            "driver_route_id": self.driver_route_id,
            "route_id":        self.route_id,
            "driver_id":       self.driver_id,
        }

    def __repr__(self):
        return f"<DriverRoute {self.driver_route_id} | Driver {self.driver_id} -> Route {self.route_id}>"