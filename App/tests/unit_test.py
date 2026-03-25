"""
Unit Tests
==========
Tests for individual model methods and controller functions in isolation.
Each test uses a fresh in-memory SQLite database (see conftest.py).
"""

import pytest
from datetime import date


# ─────────────────────────────────────────────────────────────────────────────
# USER MODEL
# ─────────────────────────────────────────────────────────────────────────────

class TestUserModel:
    """Tests for the User model's password hashing and JSON output."""

    def test_password_is_hashed_on_creation(self, db):
        """Password stored should not equal the plaintext password."""
        from App.models import User
        user = User(email="test@example.com", password="secret123")
        assert user.password != "secret123"

    def test_check_password_returns_true_for_correct_password(self, db):
        """check_password should return True when the correct password is given."""
        from App.models import User
        user = User(email="test@example.com", password="secret123")
        assert user.check_password("secret123") is True

    def test_check_password_returns_false_for_wrong_password(self, db):
        """check_password should return False for an incorrect password."""
        from App.models import User
        user = User(email="test@example.com", password="secret123")
        assert user.check_password("wrongpassword") is False

    def test_set_password_updates_hash(self, db):
        """set_password should replace the old hash so the new password works."""
        from App.models import User
        user = User(email="test@example.com", password="original")
        user.set_password("newpassword")
        assert user.check_password("newpassword") is True
        assert user.check_password("original") is False

    def test_get_json_contains_expected_keys(self, db):
        """get_json should return a dict with the correct structure."""
        from App.models import User
        user = User(email="test@example.com", password="secret123")
        result = user.get_json()
        assert "email" in result
        assert "role" in result
        assert result["email"] == "test@example.com"
        assert result["role"] == "customer"

    def test_repr_contains_role(self, db):
        """__repr__ should include the role string."""
        from App.models import User
        user = User(email="test@example.com", password="secret123", role="driver")
        assert "driver" in repr(user)


# ─────────────────────────────────────────────────────────────────────────────
# VAN MODEL
# ─────────────────────────────────────────────────────────────────────────────

class TestVanModel:
    """Tests for Van model helper methods (no DB commit needed)."""

    def test_update_location_sets_lat_lng(self, db):
        """update_location should update current_lat and current_lng."""
        from App.models import Van
        van = Van(license_plate="TST 0001", owner_id=1)
        van.update_location(10.65, -61.52)
        assert van.current_lat == 10.65
        assert van.current_lng == -61.52

    def test_update_location_sets_timestamp(self, db):
        """update_location should set last_location_update to a non-None value."""
        from App.models import Van
        van = Van(license_plate="TST 0002", owner_id=1)
        van.update_location(10.65, -61.52)
        assert van.last_location_update is not None

    def test_assign_driver_sets_driver_id(self, db):
        """assign_driver should set current_driver_id."""
        from App.models import Van
        van = Van(license_plate="TST 0003", owner_id=1)
        van.assign_driver(42)
        assert van.current_driver_id == 42

    def test_unassign_driver_clears_driver_id(self, db):
        """unassign_driver should set current_driver_id back to None."""
        from App.models import Van
        van = Van(license_plate="TST 0004", owner_id=1)
        van.assign_driver(42)
        van.unassign_driver()
        assert van.current_driver_id is None


# ─────────────────────────────────────────────────────────────────────────────
# ROUTE HISTORY MODEL
# ─────────────────────────────────────────────────────────────────────────────

class TestRouteHistoryModel:
    """Tests for RouteHistory.complete()."""

    def test_complete_sets_status_to_completed(self, db):
        """complete() should change the status to 'completed'."""
        from App.models import RouteHistory
        session = RouteHistory(route_id=1, van_id=1, driver_id=1)
        assert session.status == "in_progress"
        session.complete()
        assert session.status == "completed"

    def test_complete_sets_ended_at(self, db):
        """complete() should populate ended_at with a datetime."""
        from App.models import RouteHistory
        session = RouteHistory(route_id=1, van_id=1, driver_id=1)
        assert session.ended_at is None
        session.complete()
        assert session.ended_at is not None


# ─────────────────────────────────────────────────────────────────────────────
# USER CONTROLLER
# ─────────────────────────────────────────────────────────────────────────────

class TestUserController:
    """Tests for user creation functions."""

    def test_create_customer_returns_customer(self, db):
        """create_customer should return a Customer object on success."""
        from App.controllers.user import create_customer
        customer = create_customer("cust@test.com", "pass123", "Alice")
        assert customer is not None
        assert customer.name == "Alice"

    def test_create_customer_duplicate_email_returns_none(self, db):
        """create_customer should return None if the email already exists."""
        from App.controllers.user import create_customer
        create_customer("dup@test.com", "pass123", "First")
        result = create_customer("dup@test.com", "pass456", "Second")
        assert result is None

    def test_create_driver_returns_driver(self, db):
        """create_driver should return a Driver object on success."""
        from App.controllers.user import create_driver
        driver = create_driver("driver@test.com", "pass123", "John Driver")
        assert driver is not None
        assert driver.name == "John Driver"
        assert driver.role == "driver"

    def test_create_driver_duplicate_email_returns_none(self, db):
        """create_driver should return None if the email already exists."""
        from App.controllers.user import create_driver
        create_driver("driver2@test.com", "pass123", "First Driver")
        result = create_driver("driver2@test.com", "pass456", "Second Driver")
        assert result is None

    def test_create_owner_returns_owner(self, db):
        """create_owner should return an Owner object on success."""
        from App.controllers.user import create_owner
        owner = create_owner("owner@test.com", "pass123")
        assert owner is not None
        assert owner.role == "owner"

    def test_create_owner_duplicate_email_returns_none(self, db):
        """create_owner should return None if the email already exists."""
        from App.controllers.user import create_owner
        create_owner("owner2@test.com", "pass123")
        result = create_owner("owner2@test.com", "pass456")
        assert result is None


# ─────────────────────────────────────────────────────────────────────────────
# STATUS CONTROLLER
# ─────────────────────────────────────────────────────────────────────────────

class TestStatusController:
    """Tests for status creation (idempotent behaviour)."""

    def test_create_status_returns_status_object(self, db):
        """create_status should return a Status with the correct name."""
        from App.controllers.status import create_status
        status = create_status("pending", "Awaiting confirmation")
        assert status is not None
        assert status.status_name == "pending"

    def test_create_status_is_idempotent(self, db):
        """Calling create_status twice with the same name should return the existing record."""
        from App.controllers.status import create_status
        first  = create_status("confirmed", "Order confirmed")
        second = create_status("confirmed", "Order confirmed again")
        assert first.status_id == second.status_id


# ─────────────────────────────────────────────────────────────────────────────
# REGION CONTROLLER
# ─────────────────────────────────────────────────────────────────────────────

class TestRegionController:
    """Tests for region CRUD operations."""

    def test_create_region_returns_region(self, db):
        """create_region should return a Region with the correct name."""
        from App.controllers.region import create_region
        region = create_region("Port of Spain", "Capital city")
        assert region is not None
        assert region.name == "Port of Spain"

    def test_create_region_duplicate_name_returns_none(self, db):
        """create_region should return None if the region name already exists."""
        from App.controllers.region import create_region
        create_region("Chaguanas")
        result = create_region("Chaguanas")
        assert result is None

    def test_update_region_changes_name(self, db):
        """update_region should update the name field."""
        from App.controllers.region import create_region, update_region
        region = create_region("OldName")
        updated = update_region(region.region_id, name="NewName")
        assert updated.name == "NewName"

    def test_update_region_returns_none_for_missing_id(self, db):
        """update_region should return None when the region does not exist."""
        from App.controllers.region import update_region
        result = update_region(99999, name="Ghost")
        assert result is None

    def test_delete_region_returns_true(self, db):
        """delete_region should return True when the region is successfully deleted."""
        from App.controllers.region import create_region, delete_region
        region = create_region("ToDelete")
        result = delete_region(region.region_id)
        assert result is True

    def test_delete_region_returns_false_for_missing_id(self, db):
        """delete_region should return False when the region does not exist."""
        from App.controllers.region import delete_region
        result = delete_region(99999)
        assert result is False


# ─────────────────────────────────────────────────────────────────────────────
# VAN CONTROLLER — reserve_inventory
# ─────────────────────────────────────────────────────────────────────────────

class TestReserveInventory:
    """Tests for the reserve_inventory controller function."""

    def _setup_van_and_inventory(self, db):
        """Helper: create an owner, van, inventory item, and daily inventory record."""
        from App.controllers.user import create_owner
        from App.controllers.van import create_van
        from App.controllers.inventory_item import create_item
        from App.models import DailyInventory

        owner = create_owner("vanowner@test.com", "pass")
        van   = create_van("INV 0001", owner.owner_id)
        item  = create_item("Test Bread", price=3.50)

        record = DailyInventory(
            van_id=van.van_id,
            date=date.today(),
            item_id=item.item_id,
            quantity_in_stock=10,
            quantity_reserved=0,
            quantity_available=10,
        )
        db.session.add(record)
        db.session.commit()
        return van, item, record

    def test_reserve_inventory_reduces_available(self, db):
        """Reserving stock should decrease quantity_available by the requested amount."""
        from App.controllers.van import reserve_inventory
        van, item, record = self._setup_van_and_inventory(db)
        result = reserve_inventory(van.van_id, item.item_id, 3)
        assert result is not None
        assert result.quantity_available == 7
        assert result.quantity_reserved  == 3

    def test_reserve_inventory_insufficient_stock_returns_none(self, db):
        """reserve_inventory should return None when there is not enough stock."""
        from App.controllers.van import reserve_inventory
        van, item, record = self._setup_van_and_inventory(db)
        result = reserve_inventory(van.van_id, item.item_id, 999)
        assert result is None


# ─────────────────────────────────────────────────────────────────────────────
# ROUTE HISTORY CONTROLLER
# ─────────────────────────────────────────────────────────────────────────────

class TestRouteHistoryController:
    """Tests for start_route_session and complete_route_session."""

    def _setup(self, db):
        """Helper: create owner, driver, van, and route."""
        from App.controllers.user import create_owner, create_driver
        from App.controllers.van import create_van
        from App.controllers.route import create_route
        from datetime import time

        owner  = create_owner("rhowner@test.com", "pass")
        driver = create_driver("rhdriver@test.com", "pass", "Test Driver", owner_id=owner.owner_id)
        van    = create_van("RH 0001", owner.owner_id)
        route  = create_route("Test Route", time(6, 0), time(10, 0), "Monday", owner.owner_id)
        return van, driver, route

    def test_start_route_session_creates_session(self, db):
        """start_route_session should return a RouteHistory with status 'in_progress'."""
        from App.controllers.route_history import start_route_session
        van, driver, route = self._setup(db)
        session = start_route_session(route.route_id, van.van_id, driver.driver_id)
        assert session is not None
        assert session.status == "in_progress"

    def test_start_route_session_raises_if_already_active(self, db):
        """start_route_session should raise ValueError if the van already has an active session."""
        from App.controllers.route_history import start_route_session
        van, driver, route = self._setup(db)
        start_route_session(route.route_id, van.van_id, driver.driver_id)
        with pytest.raises(ValueError):
            start_route_session(route.route_id, van.van_id, driver.driver_id)

    def test_complete_route_session_sets_completed(self, db):
        """complete_route_session should mark the session as 'completed'."""
        from App.controllers.route_history import start_route_session, complete_route_session
        van, driver, route = self._setup(db)
        session   = start_route_session(route.route_id, van.van_id, driver.driver_id)
        completed = complete_route_session(session.history_id)
        assert completed.status   == "completed"
        assert completed.ended_at is not None

    def test_complete_route_session_returns_none_for_invalid_id(self, db):
        """complete_route_session should return None when history_id does not exist."""
        from App.controllers.route_history import complete_route_session
        result = complete_route_session(99999)
        assert result is None