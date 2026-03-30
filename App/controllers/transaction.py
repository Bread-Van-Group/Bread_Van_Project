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


# ── Report Data ───────────────────────────────────────────────────

def get_report_data(period='week'):
    """
    Return all data needed for the owner report page.

    Args:
        period: 'week' (7 days), 'month' (30 days), or 'year' (365 days)

    Returns a dict with:
        - daily_labels:               list of date strings for the x-axis
        - avg_order_values:           average transaction total per day
        - traffic:                    number of transactions per day
        - top_selling:                top 5 items by units sold
        - frequently_bought_together: top 5 product pairings
        - most_profitable_routes:     top 5 routes by total transaction revenue
        - revenue_per_route:          total period revenue / number of routes with sales
        - most_active_routes:         top 5 routes by number of history sessions
        - driver_activity:            top 5 drivers by number of sessions
    """
    from App.models import RouteHistory, Route, Driver, Van

    days       = {'week': 7, 'month': 30, 'year': 365}.get(period, 7)
    now        = datetime.now(UTC_MINUS_4)
    start_date = now - timedelta(days=days)

    # ── Transactions ──────────────────────────────────────────────

    transactions = db.session.scalars(
        db.select(Transaction).where(Transaction.transaction_time >= start_date)
    ).all()

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

    # Top 5 selling items
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

    # Top 5 frequently bought together
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

    # ── Route Revenue ─────────────────────────────────────────────
    # Join path: Transaction.van_id → Van.current_route_id → Route
    # Revenue for each transaction is attributed to the route the van
    # is currently assigned to.

    route_revenue = {}  # route_id -> {'name': str, 'total': float}

    for tx in transactions:
        van = db.session.get(Van, tx.van_id)
        if not van or not van.current_route_id:
            continue
        route_id = van.current_route_id
        if route_id not in route_revenue:
            route = db.session.get(Route, route_id)
            route_revenue[route_id] = {
                'name':  route.name if route else f'Route {route_id}',
                'total': 0.0,
            }
        route_revenue[route_id]['total'] += float(tx.total_amount)

    most_profitable_routes = [
        {
            'rank':       i + 1,
            'route_name': v['name'],
            'revenue':    round(v['total'], 2),
        }
        for i, (_, v) in enumerate(
            sorted(route_revenue.items(), key=lambda x: x[1]['total'], reverse=True)[:5]
        )
    ]

    total_revenue     = sum(v['total'] for v in route_revenue.values())
    n_routes          = len(route_revenue)
    revenue_per_route = round(total_revenue / n_routes, 2) if n_routes > 0 else 0.0

    # ── Route History ─────────────────────────────────────────────

    history_in_period = db.session.scalars(
        db.select(RouteHistory).where(RouteHistory.started_at >= start_date)
    ).all()

    route_counts = {}
    for h in history_in_period:
        route_counts[h.route_id] = route_counts.get(h.route_id, 0) + 1

    most_active_routes = []
    for route_id, count in sorted(route_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        route = db.session.get(Route, route_id)
        most_active_routes.append({
            'route_name': route.name if route else f'Route {route_id}',
            'runs':       count,
        })

    driver_counts = {}
    for h in history_in_period:
        driver_counts[h.driver_id] = driver_counts.get(h.driver_id, 0) + 1

    driver_activity = []
    for driver_id, count in sorted(driver_counts.items(), key=lambda x: x[1], reverse=True)[:5]:
        driver = db.session.get(Driver, driver_id)
        driver_activity.append({
            'driver_name': driver.name if driver else f'Driver {driver_id}',
            'sessions':    count,
        })

    return {
        'daily_labels':               daily_labels,
        'avg_order_values':           avg_order_values,
        'traffic':                    traffic,
        'top_selling':                top_selling,
        'frequently_bought_together': frequently_bought,
        'most_profitable_routes':     most_profitable_routes,
        'revenue_per_route':          revenue_per_route,
        'most_active_routes':         most_active_routes,
        'driver_activity':            driver_activity,
    }