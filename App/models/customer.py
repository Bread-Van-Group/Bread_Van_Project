from App.database import db
from .user import User

class Customer(User):
    __tablename__ = "customers"

    customer_id = db.Column(db.Integer, db.ForeignKey("users.user_id"), primary_key=True)
    name        = db.Column(db.String(100), nullable=False)
    address     = db.Column(db.String(255), nullable=True)
    phone       = db.Column(db.String(20),  nullable=True)
    area        = db.Column(db.String(100), nullable=True) 

  
    requests     = db.relationship("CustomerRequest", backref="customer", lazy=True)
    transactions = db.relationship("Transaction",     backref="customer", lazy=True)

    __mapper_args__ = {
        "polymorphic_identity": "customer",
    }

    def __init__(self, email, password, name, address=None, phone=None, area=None):
        super().__init__(email=email, password=password, role="customer")
        self.name    = name
        self.address = address
        self.phone   = phone
        self.area    = area 

    def get_json(self):
        base = super().get_json()
        base.update({
            "customer_id": self.customer_id,
            "name":        self.name,
            "address":     self.address,
            "phone":       self.phone,
            "area":        self.area, 
        })
        return base

    def __repr__(self):
        return f"<Customer {self.customer_id} | {self.name}>"