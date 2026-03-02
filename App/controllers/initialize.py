from App.database import db
from .user import create_driver, create_customer, create_owner
from .customer_request import create_customer_request, set_request_confirmed
from .status import create_status
from .inventory_item import create_item
from .route import create_route, add_stop_to_route
from .van import create_van, assign_van_to_route, set_van_inventory
from .driver import assign_driver_to_route
from .transaction import create_transaction
from App.models import Transaction
from datetime import time, date, datetime, timedelta, timezone
import random

UTC_MINUS_4 = timezone(timedelta(hours=-4))


def initialize():
    """Drop and recreate all tables, then seed with sample data."""
    db.drop_all()
    db.create_all()

    # ── Statuses ──────────────────────────────────────────────────────────────
    pending   = create_status("pending",   "Request submitted, awaiting confirmation")
    confirmed = create_status("confirmed", "Request confirmed by driver")
    fulfilled = create_status("fulfilled", "Order delivered to customer")
    cancelled = create_status("cancelled", "Request cancelled")

    print("✓ Statuses created")

    # ── Users ─────────────────────────────────────────────────────────────────
    owner = create_owner(
        email="owner@test.com",
        password="password",
    )
    print(f"✓ Owner created   : {owner.email}")

    driver = create_driver(
        email="driver@test.com",
        password="password",
        name="John Driver",
        address="123 Main Street, Port of Spain",
        phone="868-100-0001",
    )
    print(f"✓ Driver created  : {driver.email}")

    customer = create_customer(
        email="customer@test.com",
        password="password",
        name="Bob Customer",
        address="789 Pine Road, Port of Spain",
        phone="868-200-0001",
        area="Port of Spain",
    )
    print(f"✓ Customer created: {customer.email}")

    # ── Inventory Items ───────────────────────────────────────────────────────
    hops   = create_item("Hops Bread",  price=3.50, category="bread",   description="Classic hops rolls, baked fresh daily")
    salt   = create_item("Salt Bread",  price=3.00, category="bread",   description="Soft salted rolls")
    whole  = create_item("Whole Wheat", price=4.00, category="bread",   description="Whole wheat loaf")
    bara   = create_item("Bara",        price=1.50, category="fried",   description="Fried bara for doubles")
    channa = create_item("Channa",      price=5.00, category="filling", description="Curried channa filling")

    items = [hops, salt, whole, bara, channa]
    print("✓ Inventory items created")

    # ── Route ─────────────────────────────────────────────────────────────────
    route = create_route(
        name="Morning East Route",
        start_time=time(6, 0),
        end_time=time(10, 0),
        day_of_week="Monday",
        owner_id=owner.owner_id,
        description="East Trinidad morning bread delivery",
    )

    stop1 = add_stop_to_route(
        route_id=route.route_id,
        address="123 Main Street, St. Augustine",
        lat=10.640808716845667,
        lng=-61.39583945274354,
        stop_order=1,
        estimated_arrival_time=time(6, 30),
    )

    stop2 = add_stop_to_route(
        route_id=route.route_id,
        address="456 Oak Avenue, Toco",
        lat=10.64294795513197,
        lng=-61.395367383956916,
        stop_order=2,
        estimated_arrival_time=time(7, 15),
    )

    stop3 = add_stop_to_route(
        route_id=route.route_id,
        address="That Street Dey",
        lat=10.639817798264305, 
        lng=-61.39347910881043,
        stop_order=0,
        estimated_arrival_time=time(7, 15),
    )

    stop4 = add_stop_to_route(
        route_id=route.route_id,
        address="The Other Street Dey",
        lat=10.64161027605682,
        lng=-61.39279246330262,
        stop_order=0,
        estimated_arrival_time=time(7, 15),
    )

    print(f"✓ Route created   : {route.name} with 4 stops")

    # ── Van ───────────────────────────────────────────────────────────────────
    van = create_van(
        license_plate="PBK 1234",
        owner_id=owner.owner_id,
        status="active",
    )
    assign_van_to_route(van.van_id, route.route_id)

    # Set inventory for today and tomorrow
    today = date.today()
    tomorrow = today + timedelta(days=1)

    # Today's inventory
    set_van_inventory(van.van_id, hops.item_id, quantity_in_stock=50, target_date=today)
    set_van_inventory(van.van_id, salt.item_id, quantity_in_stock=40, target_date=today)
    set_van_inventory(van.van_id, whole.item_id, quantity_in_stock=20, target_date=today)
    set_van_inventory(van.van_id, bara.item_id, quantity_in_stock=80, target_date=today)
    set_van_inventory(van.van_id, channa.item_id, quantity_in_stock=30, target_date=today)

    # Tomorrow's inventory
    set_van_inventory(van.van_id, hops.item_id, quantity_in_stock=60, target_date=tomorrow)
    set_van_inventory(van.van_id, salt.item_id, quantity_in_stock=45, target_date=tomorrow)
    set_van_inventory(van.van_id, whole.item_id, quantity_in_stock=25, target_date=tomorrow)
    set_van_inventory(van.van_id, bara.item_id, quantity_in_stock=90, target_date=tomorrow)
    set_van_inventory(van.van_id, channa.item_id, quantity_in_stock=35, target_date=tomorrow)

    print(f"✓ Van created     : {van.license_plate}")


    # ── Customer Requests ─────────────────────────────────────────────────────
    request1 = create_customer_request(
        customer_id=customer.customer_id,
        van_id=van.van_id,
        stop_id=stop1.stop_id,
        item_id= hops.item_id,
        quantity= 1,
        status_id=2
    )

    request2 = create_customer_request(
        customer_id=customer.customer_id,
        van_id=van.van_id,
        stop_id=stop1.stop_id,
        item_id= bara.item_id,
        quantity= 1,
        status_id=2
    )

    request3 = create_customer_request(
        customer_id=customer.customer_id,
        van_id=van.van_id,
        stop_id=stop2.stop_id,
        item_id= bara.item_id,
        quantity= 1,
        status_id=2
    )

    #Set the preset requests which are confirmed to adhere to db rules
    set_request_confirmed(request1.request_id)
    set_request_confirmed(request2.request_id)
    set_request_confirmed(request3.request_id)

    request4 = create_customer_request(
        customer_id=customer.customer_id,
        van_id=van.van_id,
        stop_id=stop3.stop_id,
        item_id= salt.item_id,
        quantity= 1,
        status_id=1
    )

    request5 = create_customer_request(
        customer_id=customer.customer_id,
        van_id=van.van_id,
        stop_id=stop4.stop_id,
        item_id= channa.item_id,
        quantity= 1,
        status_id=1
    )

    print(f"✓ Requests created for stop orders")
    # ── Driver Assignment ─────────────────────────────────────────────────────
    assign_driver_to_route(driver.driver_id, route.route_id)
    print(f"✓ Driver assigned to route")

    # ─ Dummy Transactions (last 30 days) AI-generated realistic sales patterns for report testing 
    # Realistic daily sales patterns — heavier on hops/bara, lighter on whole wheat
    item_weights = [
        (hops,   0.35),   # 35% chance of being in an order
        (bara,   0.30),   # 30%
        (salt,   0.20),   # 20%
        (channa, 0.10),   # 10%
        (whole,  0.05),   # 5%
    ]

    stops = [stop1, stop2]
    tx_count = 0

    for days_ago in range(30, 0, -1):
        # Vary sales volume — busier on weekdays, quieter on weekends
        tx_date = datetime.now(UTC_MINUS_4) - timedelta(days=days_ago)
        is_weekend = tx_date.weekday() >= 5
        daily_orders = random.randint(2, 5) if is_weekend else random.randint(6, 14)

        for _ in range(daily_orders):
            # Pick 1–3 random items for this transaction
            chosen = random.sample(item_weights, k=random.randint(1, 3))
            order_items = []
            total = 0.0

            for item, _ in chosen:
                qty = random.randint(1, 4)
                order_items.append({'item_id': item.item_id, 'quantity': qty})
                total += round(float(item.price) * qty, 2)

            stop = random.choice(stops)
            tx = create_transaction(
                customer_id=customer.customer_id,
                van_id=van.van_id,
                total_amount=round(total, 2),
                items=order_items,
                stop_id=stop.stop_id,
                payment_method=random.choice(['cash', 'card']),
            )

            # Backdate the transaction_time so the report charts show history
            tx.transaction_time = tx_date.replace(
                hour=random.randint(6, 10),
                minute=random.randint(0, 59),
                second=0,
            )
            db.session.add(tx)
            tx_count += 1

    db.session.commit()
    print(f"✓ Dummy transactions: {tx_count} transactions seeded over last 30 days")

    print("\n✓ Database initialised successfully.")