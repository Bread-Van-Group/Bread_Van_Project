from App.database import db
from .user import create_driver, create_customer, create_owner
from .request_item import create_customer_request
from .status import create_status
from .inventory_item import create_item
from .route import create_route, add_stop_to_route
from .stop_request import add_customer_stop_to_route
from .van import create_van, assign_van_to_route, set_van_inventory
from .driver import assign_driver_to_route
from .transaction import create_transaction
from .region import *
from App.models import Transaction
from datetime import time, date, datetime, timedelta, timezone
import random

UTC_MINUS_4 = timezone(timedelta(hours=-4))


def initialize():
    """Drop and recreate all tables, then seed with sample data."""
    db.drop_all()
    db.create_all()

    # ── Statuses ──────────────────────────────────────────────────────────────
    pending = create_status("pending", "Request submitted, awaiting confirmation")
    confirmed = create_status("confirmed", "Request confirmed by driver")
    fulfilled = create_status("fulfilled", "Order delivered to customer")
    cancelled = create_status("cancelled", "Request cancelled")

    print("✓ Statuses created")

    # ── Regions ───────────────────────────────────────────────────────────────
    region_pos = create_region("Port of Spain", "Capital city and surrounding area")
    region_chag = create_region("Chaguanas", "Central Trinidad commercial hub")
    region_sf = create_region("San Fernando", "South Trinidad industrial city")

    print("✓ Regions created")

    # ── Users ─────────────────────────────────────────────────────────────────
    owner = create_owner(
        email="owner@test.com",
        password="password",
    )
    print(f"✓ Owner created   : {owner.email}")

    # Create multiple drivers for testing
    driver1 = create_driver(
        email="driver@test.com",
        password="password",
        name="John Driver",
        owner_id=owner.owner_id,
        address="123 Main Street, Port of Spain",
        phone="868-100-0001",
    )

    driver2 = create_driver(
        email="driver2@test.com",
        password="password",
        name="Maria Rodriguez",
        owner_id=owner.owner_id,
        address="45 High Street, Chaguanas",
        phone="868-100-0002",
    )

    driver3 = create_driver(
        email="driver3@test.com",
        password="password",
        name="David Singh",
        owner_id=owner.owner_id,
        address="78 Coffee Street, San Fernando",
        phone="868-100-0003",
    )

    print(f"✓ Drivers created : {driver1.email}, {driver2.email}, {driver3.email}")

    customer = create_customer(
        email="customer@test.com",
        password="password",
        name="Bob Customer",
        address="789 Pine Road, Port of Spain",
        phone="868-100-0001",
        region_id=region_pos.region_id,
    )

    customer2 = create_customer(
        email="customer2@test.com",
        password="password",
        name="Alice Customer",
        address="12 High Street, Chaguanas",
        phone="868-200-0002",
        region_id=region_chag.region_id,
    )
    customer3 = create_customer(
        email="customer3@test.com",
        password="password",
        name="Charlie Customer",
        address="45 Coffee Street, San Fernando",
        phone="868-300-0003",
        region_id=region_sf.region_id,
    )

    print(f"✓ Customers created")

    # ── Inventory Items ───────────────────────────────────────────────────────
    hops = create_item("Hops Bread", price=3.50, category="bread", description="Classic hops rolls, baked fresh daily")
    salt = create_item("Salt Bread", price=3.00, category="bread", description="Soft salted rolls")
    whole = create_item("Whole Wheat", price=4.00, category="bread", description="Whole wheat loaf")
    bara = create_item("Bara", price=1.50, category="fried", description="Fried bara for doubles")
    channa = create_item("Channa", price=5.00, category="filling", description="Curried channa filling")

    items = [hops, salt, whole, bara, channa]
    print("✓ Inventory items created")

    # ── Route ─────────────────────────────────────────────────────────────────
    route = create_route(
        name="Morning East Route",
        start_time=time(6, 0),
        end_time=time(10, 0),
        day_of_week=datetime.now().strftime("%A"),
        owner_id=owner.owner_id,
        description="East Trinidad morning bread delivery",
    )

    owner_stop1 = add_stop_to_route(
        route_id=  route.route_id,
        address= "Somewhere in St Augustine",
        lat=10.640908716845667,
        lng=-61.39593945274354,
        stop_order=1
    )

    stop1 = add_customer_stop_to_route(
        route_id=route.route_id,
        customer_id=customer2.customer_id,
        address="123 Main Street, St. Augustine",
        lat=10.640808716845667,
        lng=-61.39583945274354,
        stop_order=1,
        status_id=2,
    )

    stop2 = add_customer_stop_to_route(
        route_id=route.route_id,
        customer_id=customer3.customer_id,
        address="456 Oak Avenue, Toco",
        lat=10.64294795513197,
        lng=-61.395367383956916,
        stop_order=2,
        status_id=2,
    )

    print(f"✓ Route created   : {route.name} with 2 stops")

    # ── Vans with GPS Locations ───────────────────────────────────────────────
    # Van 1 - Active with driver, in Chaguanas Centre
    van1 = create_van(
        license_plate="PBK 1234",
        owner_id=owner.owner_id,
        status="active",
    )
    assign_van_to_route(van1.van_id, route.route_id)

    # Assign driver and set GPS location
    from App.controllers.van import get_van_by_id
    van1_obj = get_van_by_id(van1.van_id)
    van1_obj.assign_driver(driver1.driver_id)
    van1_obj.update_location(10.6409, -61.3953)  # Chaguanas Centre
    db.session.commit()

    # Van 2 - Active with driver, in Endeavour area
    van2 = create_van(
        license_plate="TCH 5678",
        owner_id=owner.owner_id,
        status="active",
    )
    van2_obj = get_van_by_id(van2.van_id)
    van2_obj.assign_driver(driver2.driver_id)
    van2_obj.update_location(10.6455, -61.4021)  # Endeavour
    db.session.commit()

    # Van 3 - Active with driver, in Edinburgh area
    van3 = create_van(
        license_plate="PDM 9012",
        owner_id=owner.owner_id,
        status="active",
    )
    van3_obj = get_van_by_id(van3.van_id)
    van3_obj.assign_driver(driver3.driver_id)
    van3_obj.update_location(10.6378, -61.4105)  # Edinburgh
    db.session.commit()

    # Van 4 - Inactive, no driver, no GPS (for testing)
    van4 = create_van(
        license_plate="POS 3456",
        owner_id=owner.owner_id,
        status="inactive",
    )

    print(f"✓ Vans created    : {van1.license_plate}, {van2.license_plate}, {van3.license_plate}, {van4.license_plate}")
    print(f"  • Van 1: Active @ Chaguanas Centre (Driver: {driver1.name})")
    print(f"  • Van 2: Active @ Endeavour (Driver: {driver2.name})")
    print(f"  • Van 3: Active @ Edinburgh (Driver: {driver3.name})")
    print(f"  • Van 4: Inactive (No driver)")

    # Set inventory for today and tomorrow (Van 1 only for simplicity)
    today = date.today()
    tomorrow = today + timedelta(days=1)

    # Today's inventory
    set_van_inventory(van1.van_id, hops.item_id, quantity=50, date=today)
    set_van_inventory(van1.van_id, salt.item_id, quantity=40, date=today)
    set_van_inventory(van1.van_id, whole.item_id, quantity=20, date=today)
    set_van_inventory(van1.van_id, bara.item_id, quantity=80, date=today)
    set_van_inventory(van1.van_id, channa.item_id, quantity=30, date=today)

    # Tomorrow's inventory
    set_van_inventory(van1.van_id, hops.item_id, quantity=60, date=tomorrow)
    set_van_inventory(van1.van_id, salt.item_id, quantity=45, date=tomorrow)
    set_van_inventory(van1.van_id, whole.item_id, quantity=25, date=tomorrow)
    set_van_inventory(van1.van_id, bara.item_id, quantity=90, date=tomorrow)
    set_van_inventory(van1.van_id, channa.item_id, quantity=35, date=tomorrow)

    # ── Customer Requests ─────────────────────────────────────────────────────
    request1 = create_customer_request(
        stop_id=stop1['stop_id'],
        item_id=hops.item_id,
        quantity=1,
    )

    request2 = create_customer_request(
        stop_id=stop1['stop_id'],
        item_id=bara.item_id,
        quantity=1,
    )

    print(f"✓ Requests created for stop orders")

    # ── Driver Assignment ─────────────────────────────────────────────────────
    assign_driver_to_route(driver1.driver_id, route.route_id)
    print(f"✓ Driver assigned to route")

    # ─ Dummy Transactions (last 30 days) AI-generated realistic sales patterns for report testing
    # Realistic daily sales patterns — heavier on hops/bara, lighter on whole wheat
    item_weights = [
        (hops, 0.35),  # 35% chance of being in an order
        (bara, 0.30),  # 30%
        (salt, 0.20),  # 20%
        (channa, 0.10),  # 10%
        (whole, 0.05),  # 5%
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
                van_id=van1.van_id,
                total_amount=round(total, 2),
                items=order_items,
                stop_id=stop['stop_id'],
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


    print("✓ Database initialised successfully!")

