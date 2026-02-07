from App.database import db
from App.models import Customer

class StopRequest(db.Model):
    __tablename__ = "stop_request"
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable= True)
    address = db.Column(db.String(200), nullable=False)
    lng = db.Column(db.Float, nullable=False)
    lat = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='pending')
    orders = db.relationship('Order', backref='stop_request', lazy=True)

    def __init__(self, customer_id, driver_id, address, lat, lng, status='pending'):
        self.customer_id = customer_id
        self.driver_id = driver_id
        self.address = address
        self.lat = lat
        self.lng = lng
        self.status = status

    def to_dict(self):
        return {
            'id': self.id,
            'customer_id': self.customer_id,
            'customer_name': db.session.get(Customer, self.customer_id).name,
            'driver_id': self.driver_id,
            'address': self.address,
            'lat': self.lat,
            'lng': self.lng,
            'status': self.status,
            'orders': [order.to_dict() for order in self.orders]
        }