from App.database import db
from .user import User


class Driver(User):
    __tablename__ = "drivers"

    driver_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(255), nullable=True)
    phone = db.Column(db.String(20), nullable=True)

    # NEW: Link to owner (which owner employs this driver)
    owner_id = db.Column(db.Integer, db.ForeignKey("owners.owner_id"), nullable=True)

    # Relationships
    driver_routes = db.relationship("DriverRoute", backref="driver", lazy=True)
    # 'assigned_van' relationship created by Van model's backref

    __mapper_args__ = {
        "polymorphic_identity": "driver",
    }

    def __init__(self, email, password, name, owner_id=None, address=None, phone=None):
        super().__init__(email=email, password=password, role="driver")
        self.name = name
        self.owner_id = owner_id
        self.address = address
        self.phone = phone

    def get_json(self):
        base = super().get_json()
        assigned_van = getattr(self, 'assigned_van', None)
        # assigned_van is a list backref when lazy=True — grab first item if populated
        if isinstance(assigned_van, list):
            assigned_van = assigned_van[0] if assigned_van else None
        base.update({
            "driver_id":          self.driver_id,
            "name":               self.name,
            "address":            self.address,
            "phone":              self.phone,
            "owner_id":           self.owner_id,
            "assigned_van_id":    assigned_van.van_id        if assigned_van else None,
            "assigned_van_plate": assigned_van.license_plate if assigned_van else None,
        })
        return base

    def __repr__(self):
        return f"<Driver {self.driver_id} | {self.name}>"