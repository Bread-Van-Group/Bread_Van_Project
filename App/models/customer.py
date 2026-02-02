from App.database import db
from .user import User

class Customer(User):
    __tablename__ = "customer"
    id = db.Column(db.Integer, db.ForeignKey("users.id"), primary_key=True)
    address = db.Column(db.String(256), nullable=False)

    __mapper_args__ = {
        "polymorphic_identity": "customer"
    }
    
    def __init__(self, name, email, password, address):
        super().__init__(name, email, password, role="customer")
        self.address = address
    