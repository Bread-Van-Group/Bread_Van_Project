from App.database import db
from datetime import datetime, timedelta, timezone

UTC_MINUS_4 = timezone(timedelta(hours=-4))


class Transaction(db.Model):
    __tablename__ = "transactions"

    transaction_id   = db.Column(db.Integer, primary_key=True)
    customer_id      = db.Column(db.Integer, db.ForeignKey("customers.customer_id"), nullable=False)
    van_id           = db.Column(db.Integer, db.ForeignKey("vans.van_id"),           nullable=False)
    stop_id          = db.Column(db.Integer, db.ForeignKey("route_stops.stop_id"),   nullable=True)
    transaction_time = db.Column(db.DateTime(timezone=True), nullable=True,
                                 default=lambda: datetime.now(UTC_MINUS_4))
    total_amount     = db.Column(db.Numeric(10, 2), nullable=False)
    payment_method   = db.Column(db.String(50),     nullable=True)

    # Relationships
    items = db.relationship("TransactionItem", backref="transaction", lazy=True)

    def __init__(self, customer_id, van_id, total_amount, stop_id=None, payment_method=None):
        self.customer_id    = customer_id
        self.van_id         = van_id
        self.stop_id        = stop_id
        self.total_amount   = total_amount
        self.payment_method = payment_method

    def get_json(self):
        return {
            "transaction_id":   self.transaction_id,
            "customer_id":      self.customer_id,
            "van_id":           self.van_id,
            "stop_id":          self.stop_id,
            "transaction_time": self.transaction_time.isoformat() if self.transaction_time else None,
            "total_amount":     float(self.total_amount),
            "payment_method":   self.payment_method,
            "items":            [item.get_json() for item in self.items],
        }

    def __repr__(self):
        return f"<Transaction {self.transaction_id} | Customer {self.customer_id}>"


class TransactionItem(db.Model):
    __tablename__ = "transaction_items"

    transaction_item_id = db.Column(db.Integer, primary_key=True)
    transaction_id      = db.Column(db.Integer, db.ForeignKey("transactions.transaction_id"), nullable=False)
    item_id             = db.Column(db.Integer, db.ForeignKey("inventory_items.item_id"),     nullable=False)
    quantity            = db.Column(db.Integer, nullable=False)

    def __init__(self, transaction_id, item_id, quantity):
        self.transaction_id = transaction_id
        self.item_id        = item_id
        self.quantity       = quantity

    def get_json(self):
        return {
            "transaction_item_id": self.transaction_item_id,
            "transaction_id":      self.transaction_id,
            "item_id":             self.item_id,
            "quantity":            self.quantity,
        }

    def __repr__(self):
        return f"<TransactionItem {self.transaction_item_id} | Tx {self.transaction_id}>"