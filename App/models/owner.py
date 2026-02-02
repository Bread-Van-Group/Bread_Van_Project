from App.database import db
from .user import User

class Owner(User):
    __tablename__ = "owner"
    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "owner"
    }
    
    def __init__(self, name, email, password, address):
        super().__init__(name=name, email=email, password=password, address=address, role="owner")
    