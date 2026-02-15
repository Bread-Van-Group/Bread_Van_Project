from App.database import db
from App.models import Transaction, TransactionItem
from .inventory_item import increment_pairing
from itertools import combinations


def get_transaction_by_id(transaction_id):
    return db.session.get(Transaction, transaction_id)


def get_all_transactions():
    return db.session.scalars(db.select(Transaction)).all()


def get_customer_transactions(customer_id):
    return db.session.scalars(
        db.select(Transaction).filter_by(customer_id=customer_id)
    ).all()


def create_transaction(customer_id, van_id, total_amount,
                       items, stop_id=None, payment_method=None):
    """
    Create a transaction and its line items, then update product pairings.

    Args:
        customer_id:    ID of the purchasing customer.
        van_id:         ID of the serving van.
        total_amount:   Decimal total for the transaction.
        items:          List of dicts: [{'item_id': int, 'quantity': int}, ...]
        stop_id:        Optional route_stop ID where the sale occurred.
        payment_method: Optional string (e.g. 'cash', 'card').

    Returns:
        The committed Transaction instance.
    """
    transaction = Transaction(
        customer_id=customer_id,
        van_id=van_id,
        total_amount=total_amount,
        stop_id=stop_id,
        payment_method=payment_method,
    )
    db.session.add(transaction)
    db.session.flush()  # Obtain transaction.transaction_id before committing

    for item_data in items:
        tx_item = TransactionItem(
            transaction_id=transaction.transaction_id,
            item_id=item_data["item_id"],
            quantity=item_data["quantity"],
        )
        db.session.add(tx_item)

    db.session.commit()

    # Update product pairings for every pair of distinct items in this transaction
    item_ids = [i["item_id"] for i in items]
    for id1, id2 in combinations(set(item_ids), 2):
        increment_pairing(id1, id2)

    return transaction