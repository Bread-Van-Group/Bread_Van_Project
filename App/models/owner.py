from App.database import db
from .user import User

class Owner(User):
    __tablename__ = "owners"

    owner_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), primary_key=True)

    # Relationships
    vans    = db.relationship("Van",    backref="owner", lazy=True)
    routes  = db.relationship("Route",  backref="owner", lazy=True)
    drivers = db.relationship("Driver", backref="owner", lazy=True, foreign_keys= "Driver.owner_id")  # NEW

    __mapper_args__ = {
        "polymorphic_identity": "owner",
    }

    def __init__(self, email, password):
        super().__init__(email=email, password=password, role="owner")

    def get_json(self):
        base = super().get_json()
        base.update({
            "owner_id":      self.owner_id,
            "vans_count":    len(self.vans) if self.vans else 0,
            "routes_count":  len(self.routes) if self.routes else 0,
            "drivers_count": len(self.drivers) if self.drivers else 0,
        })
        return base

    def __repr__(self):
        return f"<Owner {self.owner_id}>"