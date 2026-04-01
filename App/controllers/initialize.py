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
from App.models import Transaction,RouteHistory
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
    region_diego = create_region("Diego Martin", "Northwest residential borough")
    region_san_juan = create_region("San Juan-Laventille", "East Port of Spain urban corridor")
    region_tunapuna = create_region("Tunapuna-Piarco", "East-West Corridor and airport region")
    region_arima = create_region("Arima", "Northeast borough and market town")
    region_sangre = create_region("Sangre Grande", "Large rural northeast county")
    region_couva = create_region("Couva-Tabaquite-Talparo", "Central Trinidad industrial and rural belt")
    region_rio = create_region("Rio Claro-Mayaro", "Southeast coast and fishing villages")
    region_penal = create_region("Penal-Debe", "South-central agricultural region")
    region_prince = create_region("Prince Town", "South-central sugarcane and farming area")
    region_fortin = create_region("Point Fortin", "Southwest oil and gas borough")
    region_siparia = create_region("Siparia", "Southwest rural and petroleum region")

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

    customer4 = create_customer(
        email="customer4@test.com",
        password="password",
        name="David Customer",
        address="45 Coffee Street, San Fernando",
        phone="868-300-0003",
        region_id=region_sf.region_id,
    )

    customer5 = create_customer(
        email="customer5@test.com",
        password="password",
        name="Eve Customer",
        address="45 Coffee Street, San Fernando",
        phone="868-300-0003",
        region_id=region_sf.region_id,
    )

    customer6 = create_customer(
        email="customer6@test.com",
        password="password",
        name="Frank Customer",
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
    cake = create_item("Cake Slice", 5.00 , category="sweets", description="Sweet, tender baked dessert")
    cookie = create_item("Chocolate Chip Cookie", 2.50, category="sweets", description="Drop cookie that contains pieces of chocolate" )
    items = [hops, salt, whole, bara, channa,cake,cookie]
    print("✓ Inventory items created")

    # ── Routes ────────────────────────────────────────────────────────────────
    # Three routes covering different areas and days so the report shows
    # meaningful variation across routes.

    route_east = create_route(
        name="Morning East Route",
        start_time=time(6, 0), end_time=time(10, 0),
        day_of_week="Monday",
        owner_id=owner.owner_id,
        description="East Trinidad morning bread delivery",
    )
    route_central = create_route(
        name="Central Chaguanas Run",
        start_time=time(6, 30), end_time=time(11, 0),
        day_of_week="Wednesday",
        owner_id=owner.owner_id,
        description="Chaguanas and environs mid-morning run",
    )
    route_south = create_route(
        name="South San Fernando Circuit",
        start_time=time(5, 30), end_time=time(9, 30),
        day_of_week="Friday",
        owner_id=owner.owner_id,
        description="San Fernando early morning delivery circuit",
    )

    # ── Stops ─────────────────────────────────────────────────────────────────
    # East route stops
    add_stop_to_route(
        route_id=route_east.route_id, owner_id=owner.owner_id,
        address="Bakery depot, St. Augustine",
        lat=10.640908716845667, lng=-61.39593945274354, stop_order=1,
    )
    stop_e1 = add_customer_stop_to_route(
        route_id=route_east.route_id, customer_id=customer2.customer_id,
        address="123 Main Street, St. Augustine",
        lat=10.640808716845667, lng=-61.39583945274354,
        status_id=confirmed.status_id,
    )
    stop_e2 = add_customer_stop_to_route(
        route_id=route_east.route_id, customer_id=customer3.customer_id,
        address="456 Oak Avenue, Toco",
        lat=10.64294795513197, lng=-61.395367383956916,
        status_id=confirmed.status_id,
    )

    # Central route stops
    add_stop_to_route(
        route_id=route_central.route_id, owner_id=owner.owner_id,
        address="Bakery depot, Chaguanas",
        lat=10.5167, lng=-61.4114, stop_order=1,
    )
    stop_c1 = add_customer_stop_to_route(
        route_id=route_central.route_id, customer_id=customer.customer_id,
        address="Centre Pointe Mall area, Chaguanas",
        lat=10.5190, lng=-61.4080,
        status_id=confirmed.status_id,
    )
    stop_c2 = add_customer_stop_to_route(
        route_id=route_central.route_id, customer_id=customer6.customer_id,
        address="Endeavour Road, Chaguanas",
        lat=10.5145, lng=-61.4050,
        status_id=confirmed.status_id,
    )

    # South route stops
    add_stop_to_route(
        route_id=route_south.route_id, owner_id=owner.owner_id,
        address="Bakery depot, San Fernando",
        lat=10.2796, lng=-61.4589, stop_order=1,
    )
    stop_s1 = add_customer_stop_to_route(
        route_id=route_south.route_id, customer_id=customer4.customer_id,
        address="Coffee Street, San Fernando",
        lat=10.2810, lng=-61.4600,
         status_id=confirmed.status_id,
    )
    stop_s2 = add_customer_stop_to_route(
        route_id=route_south.route_id, customer_id=customer5.customer_id,
        address="High Street, San Fernando",
        lat=10.2775, lng=-61.4570,
        status_id=confirmed.status_id,
    )

    print(f"✓ Routes created  : {route_east.name}, {route_central.name}, {route_south.name}")

    # ── Vans ─────────────────────────────────────────────────────────────────
    # Each active van is assigned to a distinct route so the revenue-per-route
    # calculation in get_report_data() has three separate buckets to work with.
    from App.controllers.van import get_van_by_id

    van1 = create_van(license_plate="PBK 1234", owner_id=owner.owner_id, status="active")
    assign_van_to_route(van1.van_id, route_east.route_id)
    van1_obj = get_van_by_id(van1.van_id)
    van1_obj.assign_driver(driver1.driver_id)
    van1_obj.update_location(10.6409, -61.3953)  # Chaguanas Centre
    db.session.commit()

    van2 = create_van(license_plate="TCH 5678", owner_id=owner.owner_id, status="active")
    assign_van_to_route(van2.van_id, route_central.route_id)
    van2_obj = get_van_by_id(van2.van_id)
    van2_obj.assign_driver(driver2.driver_id)
    van2_obj.update_location(10.5190, -61.4080)  # Chaguanas
    db.session.commit()

    van3 = create_van(license_plate="PDM 9012", owner_id=owner.owner_id, status="active")
    assign_van_to_route(van3.van_id, route_south.route_id)
    van3_obj = get_van_by_id(van3.van_id)
    van3_obj.assign_driver(driver3.driver_id)
    van3_obj.update_location(10.2796, -61.4589)  # San Fernando
    db.session.commit()

    van4 = create_van(license_plate="POS 3456", owner_id=owner.owner_id, status="inactive")

    print(f"✓ Vans created    : {van1.license_plate}, {van2.license_plate}, {van3.license_plate}, {van4.license_plate}")
    print(f"  • Van 1 → {route_east.name}    (Driver: {driver1.name})")
    print(f"  • Van 2 → {route_central.name} (Driver: {driver2.name})")
    print(f"  • Van 3 → {route_south.name}   (Driver: {driver3.name})")
    print(f"  • Van 4 → Inactive (no driver)")

    # ── Route Inventory (today, per route van) ────────────────────────────────
    today = date.today()
    tomorrow = today + timedelta(days=1)

    # Van 1 — East route
    set_van_inventory(van1.van_id, hops.item_id, quantity=50, date=today)
    set_van_inventory(van1.van_id, salt.item_id, quantity=40, date=today)
    set_van_inventory(van1.van_id, whole.item_id, quantity=20, date=today)
    set_van_inventory(van1.van_id, bara.item_id, quantity=80, date=today)
    set_van_inventory(van1.van_id, channa.item_id, quantity=30, date=today)

    # Van 2 — Central route
    set_van_inventory(van2.van_id, hops.item_id, quantity=60, date=today)
    set_van_inventory(van2.van_id, salt.item_id, quantity=50, date=today)
    set_van_inventory(van2.van_id, cake.item_id, quantity=40, date=today)
    set_van_inventory(van2.van_id, cookie.item_id, quantity=35, date=today)
    set_van_inventory(van2.van_id, bara.item_id, quantity=70, date=today)

    # Van 3 — South route
    set_van_inventory(van3.van_id, hops.item_id, quantity=45, date=today)
    set_van_inventory(van3.van_id, channa.item_id, quantity=40, date=today)
    set_van_inventory(van3.van_id, whole.item_id, quantity=25, date=today)
    set_van_inventory(van3.van_id, cake.item_id, quantity=30, date=today)
    set_van_inventory(van3.van_id, cookie.item_id, quantity=25, date=today)

    print("✓ Route inventory set for today (all three vans)")

    # ── Customer Requests ─────────────────────────────────────────────────────
    create_customer_request(van1.van_id, stop_id=stop_e1['stop_id'], item_id=hops.item_id, quantity=2)
    create_customer_request(van1.van_id, stop_id=stop_e1['stop_id'], item_id=bara.item_id, quantity=1)
    create_customer_request(van2.van_id, stop_id=stop_c1['stop_id'], item_id=hops.item_id, quantity=1)
    create_customer_request(van2.van_id, stop_id=stop_c1['stop_id'], item_id=cake.item_id, quantity=2)
    create_customer_request(van3.van_id, stop_id=stop_s1['stop_id'], item_id=channa.item_id, quantity=1)
    create_customer_request(van3.van_id, stop_id=stop_s1['stop_id'], item_id=whole.item_id, quantity=1)
    print("✓ Customer requests created")

    # ── Driver → Route assignments ────────────────────────────────────────────
    assign_driver_to_route(driver1.driver_id, route_east.route_id)
    assign_driver_to_route(driver2.driver_id, route_central.route_id)
    assign_driver_to_route(driver3.driver_id, route_south.route_id)
    print("✓ Drivers assigned to routes")

    # ── Dummy Transactions (last 30 days) ─────────────────────────────────────
    # ─ Dummy Transactions (last 30 days) AI-generated realistic sales patterns for report testing
    # Each van/route gets its own item mix and volume so the Most Profitable
    # Routes table shows clear differentiation.

    # Route East  (van1) — high volume, bread-focused
    # Route Central (van2) — medium volume, pastry mix
    # Route South  (van3) — lower volume, filling-heavy

    route_configs = [
        {
            'van_id': van1.van_id,
            'stops': [stop_e1, stop_e2],
            'items': [(hops, 0.35), (bara, 0.30), (salt, 0.20), (channa, 0.10), (whole, 0.05)],
            'weekday_orders': (8, 15),
            'weekend_orders': (3, 7),
        },
        {
            'van_id': van2.van_id,
            'stops': [stop_c1, stop_c2],
            'items': [(hops, 0.25), (cake, 0.30), (cookie, 0.25), (bara, 0.15), (salt, 0.05)],
            'weekday_orders': (5, 10),
            'weekend_orders': (2, 5),
        },
        {
            'van_id': van3.van_id,
            'stops': [ stop_s1, stop_s2],
            'items': [(channa, 0.35), (whole, 0.25), (hops, 0.20), (cake, 0.15), (cookie, 0.05)],
            'weekday_orders': (4, 8),
            'weekend_orders': (1, 3),
        },
    ]

    tx_count = 0

    for days_ago in range(30, 0, -1):
        tx_date = datetime.now(UTC_MINUS_4) - timedelta(days=days_ago)
        is_weekend = tx_date.weekday() >= 5

        for cfg in route_configs:
            lo, hi = cfg['weekend_orders'] if is_weekend else cfg['weekday_orders']
            daily_orders = random.randint(lo, hi)

            for _ in range(daily_orders):
                chosen = random.sample(cfg['items'], k=random.randint(1, 3))
                order_items = []
                total = 0.0

                for item, _ in chosen:
                    qty = random.randint(1, 4)
                    order_items.append({'item_id': item.item_id, 'quantity': qty})
                    total += round(float(item.price) * qty, 2)

                stop = random.choice(cfg['stops'])
                tx = create_transaction(
                    customer_id=customer.customer_id,
                    van_id=cfg['van_id'],
                    total_amount=round(total, 2),
                    items=order_items,
                    stop_id=stop['stop_id'],
                    payment_method=random.choice(['cash', 'card']),
                )

                tx.transaction_time = tx_date.replace(
                    hour=random.randint(6, 10),
                    minute=random.randint(0, 59),
                    second=0,
                )
                db.session.add(tx)
                tx_count += 1

    db.session.commit()
    print(f"✓ Dummy transactions: {tx_count} seeded over last 30 days (3 routes)")

    # ── Dummy Route History (last 30 days) ────────────────────────────────────
    # Weekday sessions only. Each van/driver/route pair runs once per weekday.
    # 90 % complete successfully; 10 % left in_progress (forgot to end session).
    # Route East runs slightly longer on average than the others.

    van_route_driver = [
        (van1.van_id, route_east.route_id, driver1.driver_id, 120, 240),  # 2–4 hrs
        (van2.van_id, route_central.route_id, driver2.driver_id, 100, 200),  # 1.7–3.3 hrs
        (van3.van_id, route_south.route_id, driver3.driver_id, 90, 180),  # 1.5–3 hrs
    ]

    history_count = 0

    for days_ago in range(30, 0, -1):
        session_date = datetime.now(UTC_MINUS_4) - timedelta(days=days_ago)
        if session_date.weekday() >= 5:  # skip weekends
            continue

        for van_id, route_id, driver_id, min_dur, max_dur in van_route_driver:
            h = RouteHistory(route_id=route_id, van_id=van_id, driver_id=driver_id)

            h.started_at = session_date.replace(
                hour=6, minute=random.randint(0, 20), second=0, microsecond=0,
            )

            if random.random() < 0.90:
                h.ended_at = h.started_at + timedelta(minutes=random.randint(min_dur, max_dur))
                h.status = 'completed'
            else:
                h.ended_at = None
                h.status = 'in_progress'

            db.session.add(h)
            history_count += 1

    db.session.commit()
    print(f"✓ Route history   : {history_count} sessions seeded over last 30 days (weekdays only)")

    print("✓ Database initialised successfully!")

