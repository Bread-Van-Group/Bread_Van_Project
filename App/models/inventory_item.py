from App.database import db

class InventoryItem(db.Model):
    __tablename__ = "inventory_item"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    name = db.Column(db.String(100), nullable=False) 
    quantity = db.Column(db.Integer, nullable=False, default=0)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)

    def __init__(self, name, quantity, price, description):
        self.name = name
        self.quantity = quantity
        self.price = price
        self.description = description