from App.database import db

class StopRequest(db.Model):
    __tablename__ = "stop_request"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable= True)
    address = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    orders = db.relationship('Order', backref='stop_request', lazy=True)

    def __init__(self, customer_id, driver_id, address, status='pending'):
        self.customer_id = customer_id
        self.driver_id = driver_id
        self.address = address
        self.status = status