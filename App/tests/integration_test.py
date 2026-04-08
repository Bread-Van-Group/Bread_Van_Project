"""
Integration Tests
=================
Tests for multi-step flows where several controllers and models work together.
Each test verifies that a real user-facing scenario works end to end.
"""

import pytest
from datetime import date, time
from flask import Flask
from flask_jwt_extended import JWTManager


# ─────────────────────────────────────────────────────────────────────────────
# FIXTURE — full app with JWT configured
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def app():
    """Create a Flask app with JWT and an in-memory SQLite DB for integration tests."""
    from App.database import db as _db

    test_app = Flask(__name__)
    test_app.config["TESTING"] = True
    test_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    test_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    test_app.config["JWT_SECRET_KEY"] = "integration-test-secret"

    _db.init_app(test_app)
    JWTManager(test_app)

    with test_app.app_context():
        _db.create_all()
        yield test_app
        _db.drop_all()


@pytest.fixture(scope="function")
def db(app):
    """Clean database state for each integration test."""
    from App.database import db as _db
    with app.app_context():
        yield _db
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


# ─────────────────────────────────────────────────────────────────────────────
# FLOW 1 — USER REGISTRATION + LOGIN
# ─────────────────────────────────────────────────────────────────────────────

class TestAuthFlow:
    """
    Integration tests for the full registration → login flow.
    Verifies that a user can be created and then authenticated.
    """

    def test_register_customer_then_login_succeeds(self, db):
        """
        A newly registered customer should be able to log in
        and receive a JWT token.
        """
        from App.controllers.user import create_customer
        from App.controllers.auth import login

        customer = create_customer("newuser@test.com", "securepass", "New User")
        assert customer is not None, "Registration failed — customer was not created"

        token = login("newuser@test.com", "securepass")
        assert token is not None, "Login failed — no token returned for valid credentials"

    def test_login_with_wrong_password_returns_none(self, db):
        """
        Login should fail and return None when the wrong password is given,
        even if the email exists.
        """
        from App.controllers.user import create_customer
        from App.controllers.auth import login

        create_customer("wrongpass@test.com", "correctpass", "Test User")
        token = login("wrongpass@test.com", "wrongpass")
        assert token is None, "Login should have failed but returned a token"

    def test_login_with_nonexistent_email_returns_none(self, db):
        """Login should return None when the email does not exist in the database."""
        from App.controllers.auth import login

        token = login("ghost@test.com", "somepass")
        assert token is None

    def test_register_driver_then_login_succeeds(self, db):
        """A driver account should also be able to register and log in successfully."""
        from App.controllers.user import create_owner, create_driver
        from App.controllers.auth import login

        owner  = create_owner("driverowner@test.com", "pass")
        driver = create_driver("newdriver@test.com", "driverpass", "Test Driver",
                               owner_id=owner.owner_id)
        assert driver is not None

        token = login("newdriver@test.com", "driverpass")
        assert token is not None, "Driver login failed — no token returned"

    def test_duplicate_registration_is_rejected(self, db):
        """
        Registering a second account with the same email should fail.
        This prevents duplicate accounts in the system.
        """
        from App.controllers.user import create_customer

        first  = create_customer("same@test.com", "pass1", "First")
        second = create_customer("same@test.com", "pass2", "Second")

        assert first  is not None, "First registration should succeed"
        assert second is None,     "Second registration with same email should be rejected"


# ─────────────────────────────────────────────────────────────────────────────
# FLOW 2 — CUSTOMER PLACES AN ORDER
# ─────────────────────────────────────────────────────────────────────────────

class TestCustomerOrderFlow:
    """
    Integration tests for the full order flow:
    customer created → inventory stocked → stop request added →
    request item placed → inventory levels updated.
    """

    def _setup_order_environment(self, db):
        """
        Helper: build the minimum required environment for placing an order.
        Creates owner, customer, van, item, route, stop request, and daily inventory.
        Returns all created objects for use in tests.
        """
        from App.controllers.user import create_owner, create_customer
        from App.controllers.van import create_van
        from App.controllers.inventory_item import create_item
        from App.controllers.route import create_route
        from App.controllers.stop_request import add_customer_stop_to_route
        from App.models import DailyInventory

        owner    = create_owner("orderowner@test.com", "pass")
        customer = create_customer("ordercust@test.com", "pass", "Order Customer")
        van      = create_van("ORD 0001", owner.owner_id, status="active")
        item     = create_item("Hops Bread", price=3.50, category="bread")
        route    = create_route("Test Route", time(6, 0), time(10, 0), "Monday", owner.owner_id)

        stop_json = add_customer_stop_to_route(
            route_id    = route.route_id,
            customer_id = customer.customer_id,
            address     = "123 Test Street",
            lat         = 10.65,
            lng         = -61.52,
            status_id   = 1,
        )

        inventory = DailyInventory(
            van_id             = van.van_id,
            date               = date.today(),
            item_id            = item.item_id,
            quantity_in_stock  = 20,
            quantity_reserved  = 0,
            quantity_available = 20,
        )
        db.session.add(inventory)
        db.session.commit()

        return owner, customer, van, item, route, stop_json, inventory

    def test_placing_order_reduces_available_inventory(self, db):
        """
        When a customer places a request for 3 units,
        the available inventory on the van should decrease by 3.
        """
        from App.controllers.request_item import create_customer_request
        from App.models import DailyInventory

        owner, customer, van, item, route, stop_json, inventory = self._setup_order_environment(db)

        create_customer_request(
            van_id   = van.van_id,
            stop_id  = stop_json["stop_id"],
            item_id  = item.item_id,
            quantity = 3,
        )

        updated = db.session.get(DailyInventory, inventory.inventory_id)
        assert updated.quantity_available == 17, \
            f"Expected 17 available, got {updated.quantity_available}"
        assert updated.quantity_reserved == 3, \
            f"Expected 3 reserved, got {updated.quantity_reserved}"

    def test_placing_order_creates_customer_request_record(self, db):
        """
        A RequestItem record should exist in the database
        after an order is successfully placed.
        """
        from App.controllers.request_item import create_customer_request

        owner, customer, van, item, route, stop_json, inventory = self._setup_order_environment(db)

        request = create_customer_request(
            van_id   = van.van_id,
            stop_id  = stop_json["stop_id"],
            item_id  = item.item_id,
            quantity = 2,
        )

        assert request is not None
        assert request.stop_id  == stop_json["stop_id"]
        assert request.item_id  == item.item_id
        assert request.quantity == 2

    def test_order_exceeding_stock_fails_gracefully(self, db):
        """
        Attempting to order more than the available stock should fail
        and return None rather than crashing or corrupting inventory.
        """
        from App.controllers.request_item import create_customer_request
        from App.models import DailyInventory

        owner, customer, van, item, route, stop_json, inventory = self._setup_order_environment(db)

        result = create_customer_request(
            van_id   = van.van_id,
            stop_id  = stop_json["stop_id"],
            item_id  = item.item_id,
            quantity = 999,
        )

        assert result is None, "Order above stock limit should have returned None"

        unchanged = db.session.get(DailyInventory, inventory.inventory_id)
        assert unchanged.quantity_available == 20, \
            "Inventory should not change after a failed order"

    def test_full_order_flow_end_to_end(self, db):
        """
        Full end-to-end flow:
        register customer → stock van → place stop request → place item request
        → verify inventory updated.
        """
        from App.controllers.user import create_owner, create_customer
        from App.controllers.auth import login
        from App.controllers.van import create_van
        from App.controllers.inventory_item import create_item
        from App.controllers.route import create_route
        from App.controllers.stop_request import add_customer_stop_to_route
        from App.controllers.request_item import create_customer_request
        from App.models import DailyInventory

        # Step 1 — Register and login
        owner    = create_owner("e2eowner@test.com", "pass")
        customer = create_customer("e2ecust@test.com", "custpass", "E2E Customer")
        token    = login("e2ecust@test.com", "custpass")
        assert token is not None, "Customer should be able to log in"

        # Step 2 — Set up van and stock
        van  = create_van("E2E 0001", owner.owner_id, status="active")
        item = create_item("Salt Bread", price=3.00, category="bread")

        inventory = DailyInventory(
            van_id=van.van_id, date=date.today(), item_id=item.item_id,
            quantity_in_stock=15, quantity_reserved=0, quantity_available=15,
        )
        db.session.add(inventory)
        db.session.commit()

        # Step 3 — Create route and stop request
        route     = create_route("E2E Route", time(7, 0), time(11, 0), "Tuesday", owner.owner_id)
        stop_json = add_customer_stop_to_route(
            route_id=route.route_id, customer_id=customer.customer_id,
            address="456 E2E Avenue", lat=10.70, lng=-61.50, status_id=1,
        )
        assert stop_json is not None, "Stop request should have been created"

        # Step 4 — Place item request
        request = create_customer_request(
            van_id=van.van_id, stop_id=stop_json["stop_id"],
            item_id=item.item_id, quantity=5,
        )
        assert request is not None, "Request item should have been created"

        # Step 5 — Verify inventory reflects the order
        updated = db.session.get(DailyInventory, inventory.inventory_id)
        assert updated.quantity_available == 10
        assert updated.quantity_reserved  == 5

# ─────────────────────────────────────────────────────────────────────────────
# FLOW 3 — VAN GPS TRACKING
# ─────────────────────────────────────────────────────────────────────────────

class TestVanTrackingFlow:
    """
    Integration tests for van GPS location updates.
    Verifies that location data is persisted correctly and driver
    assignment works alongside location tracking.
    """

    def test_update_location_stores_lat_lng(self, db):
        """
        Calling update_location on a van should persist the
        coordinates to the database.
        """
        from App.controllers.user import create_owner
        from App.controllers.van import create_van, get_van_by_id

        owner = create_owner("gpsowner@test.com", "pass")
        van   = create_van("GPS 0001", owner.owner_id, status="active")

        van.update_location(10.6420, -61.4005)
        db.session.commit()

        refreshed = get_van_by_id(van.van_id)
        assert refreshed.current_lat == 10.6420, "Latitude was not saved"
        assert refreshed.current_lng == -61.4005, "Longitude was not saved"

    def test_update_location_sets_timestamp(self, db):
        """
        update_location should also record the time of the update
        so the owner dashboard can show a 'last seen' value.
        """
        from App.controllers.user import create_owner
        from App.controllers.van import create_van, get_van_by_id

        owner = create_owner("tsowner@test.com", "pass")
        van   = create_van("GPS 0002", owner.owner_id, status="active")

        assert van.last_location_update is None, \
            "Timestamp should be null before any location update"

        van.update_location(10.6409, -61.3959)
        db.session.commit()

        refreshed = get_van_by_id(van.van_id)
        assert refreshed.last_location_update is not None, \
            "Timestamp should be set after location update"

    def test_assign_driver_then_update_location(self, db):
        """
        A van with an assigned driver should still accept location
        updates without losing the driver assignment.
        """
        from App.controllers.user import create_owner, create_driver
        from App.controllers.van import create_van, get_van_by_id

        owner  = create_owner("assignowner@test.com", "pass")
        driver = create_driver("assigndriver@test.com", "pass", "Test Driver",
                               owner_id=owner.owner_id)
        van    = create_van("GPS 0003", owner.owner_id, status="active")

        van.assign_driver(driver.driver_id)
        van.update_location(10.6445, -61.3842)
        db.session.commit()

        refreshed = get_van_by_id(van.van_id)
        assert refreshed.current_driver_id == driver.driver_id, \
            "Driver assignment should not be cleared by a location update"
        assert refreshed.current_lat == 10.6445
        assert refreshed.current_lng == -61.3842

    def test_location_update_overwrites_previous(self, db):
        """
        A second location update should replace the first,
        not accumulate or fail.
        """
        from App.controllers.user import create_owner
        from App.controllers.van import create_van, get_van_by_id

        owner = create_owner("overwriteowner@test.com", "pass")
        van   = create_van("GPS 0004", owner.owner_id, status="active")

        van.update_location(10.6420, -61.4005)
        db.session.commit()

        van.update_location(10.6409, -61.3959)
        db.session.commit()

        refreshed = get_van_by_id(van.van_id)
        assert refreshed.current_lat == 10.6409, "Location should reflect the latest update"
        assert refreshed.current_lng == -61.3959


# ─────────────────────────────────────────────────────────────────────────────
# FLOW 4 — DRIVER MAKES A SALE (TRANSACTION)
# ─────────────────────────────────────────────────────────────────────────────

class TestTransactionFlow:
    """
    Integration tests for the transaction/sale flow.
    Verifies that sales are recorded correctly and inventory
    is reduced when a driver completes a delivery.
    """

    def _setup(self, db):
        """Minimal environment: owner, customer, van, item, stocked inventory."""
        from App.controllers.user import create_owner, create_customer
        from App.controllers.van import create_van
        from App.controllers.inventory_item import create_item
        from App.models import DailyInventory

        owner    = create_owner("txowner@test.com", "pass")
        customer = create_customer("txcust@test.com", "pass", "TX Customer")
        van      = create_van("TX 0001", owner.owner_id, status="active")
        item     = create_item("Hops Bread", price=3.50, category="bread")

        inventory = DailyInventory(
            van_id=van.van_id, date=date.today(), item_id=item.item_id,
            quantity_in_stock=30, quantity_reserved=0, quantity_available=30,
        )
        db.session.add(inventory)
        db.session.commit()

        return owner, customer, van, item, inventory

    def test_transaction_is_saved_to_database(self, db):
        """
        Creating a transaction should produce a Transaction record
        with the correct customer, van, and total amount.
        """
        from App.controllers.transaction import create_transaction, get_transaction_by_id

        owner, customer, van, item, inventory = self._setup(db)

        tx = create_transaction(
            customer_id=customer.customer_id,
            van_id=van.van_id,
            total_amount=7.00,
            items=[{"item_id": item.item_id, "quantity": 2}],
            payment_method="cash",
        )

        assert tx is not None
        fetched = get_transaction_by_id(tx.transaction_id)
        assert fetched.customer_id   == customer.customer_id
        assert fetched.van_id        == van.van_id
        assert float(fetched.total_amount) == 7.00
        assert fetched.payment_method == "cash"

    def test_transaction_creates_line_items(self, db):
        """
        Each item in the sale should produce a TransactionItem record
        linked to the transaction.
        """
        from App.controllers.transaction import create_transaction
        from App.models import TransactionItem

        owner, customer, van, item, inventory = self._setup(db)

        tx = create_transaction(
            customer_id=customer.customer_id,
            van_id=van.van_id,
            total_amount=10.50,
            items=[{"item_id": item.item_id, "quantity": 3}],
        )

        line_items = db.session.scalars(
            db.select(TransactionItem).filter_by(transaction_id=tx.transaction_id)
        ).all()

        assert len(line_items) == 1
        assert line_items[0].item_id  == item.item_id
        assert line_items[0].quantity == 3

    def test_transaction_reduces_van_inventory(self, db):
        """
        After a sale is made, the van's available inventory for that item
        should decrease by the quantity sold.
        """
        from App.controllers.transaction import create_transaction
        from App.controllers.van import reserve_inventory
        from App.models import DailyInventory

        owner, customer, van, item, inventory = self._setup(db)

        qty_sold = 4
        reserve_inventory(van.van_id, item.item_id, qty_sold, is_complete=True)

        updated = db.session.get(DailyInventory, inventory.inventory_id)
        assert updated.quantity_available == 26, \
            f"Expected 26 available after selling 4, got {updated.quantity_available}"
        assert updated.quantity_in_stock == 26, \
            f"Expected stock of 26, got {updated.quantity_in_stock}"

    def test_multiple_transactions_accumulate_correctly(self, db):
        """
        Two separate sales should each reduce inventory independently,
        and both transaction records should exist in the database.
        """
        from App.controllers.transaction import create_transaction, get_customer_transactions
        from App.controllers.van import reserve_inventory
        from App.models import DailyInventory

        owner, customer, van, item, inventory = self._setup(db)

        create_transaction(
            customer_id=customer.customer_id, van_id=van.van_id,
            total_amount=3.50, items=[{"item_id": item.item_id, "quantity": 1}],
        )
        reserve_inventory(van.van_id, item.item_id, 1, is_complete=True)

        create_transaction(
            customer_id=customer.customer_id, van_id=van.van_id,
            total_amount=7.00, items=[{"item_id": item.item_id, "quantity": 2}],
        )
        reserve_inventory(van.van_id, item.item_id, 2, is_complete=True)

        transactions = get_customer_transactions(customer.customer_id)
        assert len(transactions) == 2, "Both transactions should be recorded"

        updated = db.session.get(DailyInventory, inventory.inventory_id)
        assert updated.quantity_in_stock == 27, \
            f"Expected 27 remaining after selling 3 total, got {updated.quantity_in_stock}"