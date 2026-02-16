from App.database import db
from App.models import Transaction, TransactionItem, InventoryItem, ProductPairing
from .inventory_item import increment_pairing
from itertools import combinations
from datetime import datetime, timedelta, timezone
from sqlalchemy import func

UTC_MINUS_4 = timezone(timedelta(hours=-4))


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
    transaction = Transaction(
        customer_id=customer_id,
        van_id=van_id,
        total_amount=total_amount,
        stop_id=stop_id,
        payment_method=payment_method,
    )
    db.session.add(transaction)
    db.session.flush()

    for item_data in items:
        tx_item = TransactionItem(
            transaction_id=transaction.transaction_id,
            item_id=item_data["item_id"],
            quantity=item_data["quantity"],
        )
        db.session.add(tx_item)

    db.session.commit()

    item_ids = [i["item_id"] for i in items]
    for id1, id2 in combinations(set(item_ids), 2):
        increment_pairing(id1, id2)

    return transaction


# Report Data 

def get_report_data(period='week'):
    """
    Return all data needed for the owner report page.

    Args:
        period: 'week' (7 days), 'month' (30 days), or 'year' (365 days)

    Returns a dict with:
        - daily_labels:     list of date strings for the x-axis
        - avg_order_values: average transaction total per day
        - traffic:          number of transactions per day
        - top_selling:      top 5 items by units sold
        - frequently_bought_together: top 5 product pairings
    """
    days = {'week': 7, 'month': 30, 'year': 365}.get(period, 7)
    now = datetime.now(UTC_MINUS_4)
    start_date = now - timedelta(days=days)

    # Fetch all transactions in the period
    transactions = db.session.scalars(
        db.select(Transaction).where(Transaction.transaction_time >= start_date)
    ).all()

    # Build per-day buckets
    date_format = '%b %d' if days <= 30 else '%b %Y'
    buckets = {}
    for i in range(days):
        day = (now - timedelta(days=days - 1 - i)).strftime(date_format)
        buckets[day] = {'total': 0.0, 'count': 0}

    for tx in transactions:
        tx_time = tx.transaction_time
        if tx_time.tzinfo is None:
            tx_time = tx_time.replace(tzinfo=UTC_MINUS_4)
        label = tx_time.strftime(date_format)
        if label in buckets:
            buckets[label]['total'] += float(tx.total_amount)
            buckets[label]['count'] += 1

    daily_labels     = list(buckets.keys())
    avg_order_values = [
        round(v['total'] / v['count'], 2) if v['count'] > 0 else 0
        for v in buckets.values()
    ]
    traffic = [v['count'] for v in buckets.values()]

    # Top 5 selling items by quantity
    top_selling_rows = db.session.execute(
        db.select(
            InventoryItem.name,
            func.sum(TransactionItem.quantity).label('total_qty')
        )
        .join(TransactionItem, TransactionItem.item_id == InventoryItem.item_id)
        .join(Transaction, Transaction.transaction_id == TransactionItem.transaction_id)
        .where(Transaction.transaction_time >= start_date)
        .group_by(InventoryItem.item_id)
        .order_by(func.sum(TransactionItem.quantity).desc())
        .limit(5)
    ).all()

    top_selling = [
        {'rank': i + 1, 'name': row.name, 'quantity': int(row.total_qty)}
        for i, row in enumerate(top_selling_rows)
    ]

    # Top 5 frequently bought together pairings
    pairing_rows = db.session.execute(
        db.select(
            InventoryItem.name.label('item1_name'),
            ProductPairing.item2_id,
            ProductPairing.count
        )
        .join(InventoryItem, InventoryItem.item_id == ProductPairing.item1_id)
        .order_by(ProductPairing.count.desc())
        .limit(5)
    ).all()

    frequently_bought = []
    for row in pairing_rows:
        item2 = db.session.get(InventoryItem, row.item2_id)
        frequently_bought.append({
            'item1': row.item1_name,
            'item2': item2.name if item2 else 'Unknown',
            'count': row.count,
        })

    return {
        'daily_labels':               daily_labels,
        'avg_order_values':           avg_order_values,
        'traffic':                    traffic,
        'top_selling':                top_selling,
        'frequently_bought_together': frequently_bought,
    }