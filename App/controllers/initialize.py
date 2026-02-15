from App.database import db
from .user import create_driver, create_customer, create_owner
from .status import create_status
from .inventory_item import create_item
from .route import create_route, add_stop_to_route
from .van import create_van, assign_van_to_route, set_van_inventory
from .driver import assign_driver_to_route
from datetime import time, date


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
    print(f"✓ Owner created  : {owner.email}")

    driver = create_driver(
        email="driver@test.com",
        password="password",
        name="John Driver",
        address="123 Main Street, Port of Spain",
        phone="868-100-0001",
    )
    print(f"✓ Driver created : {driver.email}")

    customer = create_customer(
        email="customer@test.com",
        password="password",
        name="Bob Customer",
        address="789 Pine Road, Port of Spain",
        phone="868-200-0001",
    )
    print(f"✓ Customer created: {customer.email}")

    # ── Inventory Items ───────────────────────────────────────────────────────
    hops  = create_item("Hops Bread",    price=3.50,  category="bread",
                        description="Classic hops rolls, baked fresh daily")
    salt  = create_item("Salt Bread",    price=3.00,  category="bread",
                        description="Soft salted rolls")
    whole = create_item("Whole Wheat",   price=4.00,  category="bread",
                        description="Whole wheat loaf")
    bara  = create_item("Bara",          price=1.50,  category="fried",
                        description="Fried bara for doubles")
    channa = create_item("Channa",       price=5.00,  category="filling",
                         description="Curried channa filling")

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

    print(f"✓ Route created  : {route.name} with {2} stops")

    # ── Van ───────────────────────────────────────────────────────────────────
    van = create_van(
        license_plate="PBK 1234",
        owner_id=owner.owner_id,
        status="active",
    )
    assign_van_to_route(van.van_id, route.route_id)

    # Seed today's inventory on the van
    today = date.today()
    set_van_inventory(van.van_id, hops.item_id,  quantity_in_stock=50, target_date=today)
    set_van_inventory(van.van_id, salt.item_id,  quantity_in_stock=40, target_date=today)
    set_van_inventory(van.van_id, whole.item_id, quantity_in_stock=20, target_date=today)
    set_van_inventory(van.van_id, bara.item_id,  quantity_in_stock=80, target_date=today)
    set_van_inventory(van.van_id, channa.item_id,quantity_in_stock=30, target_date=today)

    print(f"✓ Van created    : {van.license_plate}")

    # ── Driver Assignment ─────────────────────────────────────────────────────
    assign_driver_to_route(driver.driver_id, route.route_id)
    print(f"✓ Driver assigned to route")

    print("\n✅ Database initialised successfully.")