from App.database import db
from .user import User

class Driver(User):
    __tablename__ = "driver"
    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)

    __mapper_args__ = {
        "polymorphic_identity": "driver"
    }
    
    def __init__(self, name, email, password, address):
        super().__init__(name, email, password, role="driver")
        self.address = address
    