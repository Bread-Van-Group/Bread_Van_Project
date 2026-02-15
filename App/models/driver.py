from App.database import db
from .user import User

class Driver(User):
    __tablename__ = "drivers"

    driver_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), primary_key=True)
    name      = db.Column(db.String(100), nullable=False)
    address   = db.Column(db.String(255), nullable=True)
    phone     = db.Column(db.String(20),  nullable=True)


    driver_routes    = db.relationship("DriverRoute", backref="driver", lazy=True)

    __mapper_args__ = {
        "polymorphic_identity": "driver",
    }

    def __init__(self, email, password, name, address=None, phone=None):
        super().__init__(email=email, password=password, role="driver")
        self.name    = name
        self.address = address
        self.phone   = phone

    def get_json(self):
        base = super().get_json()
        base.update({
            "driver_id": self.driver_id,
            "name":      self.name,
            "address":   self.address,
            "phone":     self.phone,
        })
        return base

    def __repr__(self):
        return f"<Driver {self.driver_id} | {self.name}>"