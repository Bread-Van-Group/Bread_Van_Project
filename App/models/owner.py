from App.database import db
from .user import User

class Owner(User):
    __tablename__ = "owners"

    owner_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), primary_key=True)

    # Relationships
    vans   = db.relationship("Van",   backref="owner",  lazy=True)
    routes = db.relationship("Route", backref="owner",  lazy=True)

    __mapper_args__ = {
        "polymorphic_identity": "owner",
    }

    def __init__(self, email, password):
        super().__init__(email=email, password=password, role="owner")

    def get_json(self):
        base = super().get_json()
        base.update({
            "owner_id": self.owner_id,
        })
        return base

    def __repr__(self):
        return f"<Owner {self.owner_id}>"