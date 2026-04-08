"""
System Tests
============
Tests the full application stack end-to-end by hitting real HTTP endpoints
via Flask's test client. Verifies that routes, controllers, models, and the
database all work together correctly as a complete system.
"""

import pytest
from datetime import date, time, datetime


# ─────────────────────────────────────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def app():
    """Full application with all blueprints and an in-memory test database."""
    from App.main import create_app
    from App.database import db as _db

    test_app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
        "JWT_SECRET_KEY": "system-test-secret",
        "JWT_COOKIE_SECURE": False,
        "WTF_CSRF_ENABLED": False,
    })

    with test_app.app_context():
        _db.create_all()
        yield test_app
        _db.drop_all()


@pytest.fixture(scope="function")
def db(app):
    """Clean database for each test."""
    from App.database import db as _db
    with app.app_context():
        yield _db
        _db.session.rollback()
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()


@pytest.fixture(scope="function")
def client(app):
    """Flask test client."""
    return app.test_client()


def get_token(client, email, password):
    """Helper: log in via the API and return the JWT token string."""
    resp = client.post("/api/login", json={"email": email, "password": password})
    assert resp.status_code == 200, f"Login failed for {email}: {resp.get_data(as_text=True)}"
    data = resp.get_json()
    return data.get("access_token") or data.get("token")


def auth_headers(token):
    """Helper: build Authorization header dict from a token."""
    return {"Authorization": f"Bearer {token}"}


# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM TEST 1 — AUTHENTICATION ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

class TestAuthSystem:
    """
    System tests for the authentication API.
    Hits /api/login and /api/identify through the full HTTP stack.
    """

    def test_api_login_returns_token_for_valid_credentials(self, client, db):
        """POST /api/login with valid credentials should return a JWT token."""
        from App.controllers.user import create_customer
        create_customer("sysauth@test.com", "password", "Sys Auth User")

        resp = client.post("/api/login", json={
            "email": "sysauth@test.com",
            "password": "password",
        })

        assert resp.status_code == 200
        token = resp.get_json().get("access_token")
        assert token is not None, "Response should contain an access_token"

    def test_api_login_rejects_wrong_password(self, client, db):
        """POST /api/login with wrong password should return 401."""
        from App.controllers.user import create_customer
        create_customer("wrongpass@test.com", "correctpass", "Wrong Pass User")

        resp = client.post("/api/login", json={
            "email": "wrongpass@test.com",
            "password": "wrongpass",
        })

        assert resp.status_code == 401

    def test_api_login_rejects_unknown_email(self, client, db):
        """POST /api/login with an email that doesn't exist should return 401."""
        resp = client.post("/api/login", json={
            "email": "nobody@test.com",
            "password": "password",
        })

        assert resp.status_code == 401

    def test_identify_returns_user_info_when_authenticated(self, client, db):
        """GET /api/identify with a valid token should return the user's email in the message."""
        from App.controllers.user import create_customer
        create_customer("identify@test.com", "password", "Identify User")

        token = get_token(client, "identify@test.com", "password")
        resp  = client.get("/api/identify", headers=auth_headers(token))

        assert resp.status_code == 200
        data = resp.get_json()
        assert "identify@test.com" in data["message"]

    def test_identify_redirects_unauthenticated_request(self, client, db):
        """GET /api/identify without a token should redirect to login (302)."""
        resp = client.get("/api/identify")
        # App redirects unauthenticated requests rather than returning 401
        assert resp.status_code in (302, 401)


# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM TEST 2 — CUSTOMER API ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

class TestCustomerAPISystem:
    """
    System tests for the customer-facing API.
    Verifies that the full request pipeline works: auth → route → controller → DB.
    """

    def _seed(self, db):
        """Seed the minimum data needed for customer API tests."""
        from App.controllers.user import create_owner, create_customer
        from App.controllers.van import create_van
        from App.controllers.route import create_route, assign_route_to_area
        from App.controllers.region import create_region

        today    = datetime.now().strftime("%A")
        region   = create_region("Test Region", "A test region")
        owner    = create_owner("custsysowner@test.com", "pass")
        customer = create_customer(
            "custsys@test.com", "password", "Sys Customer",
            region_id=region.region_id,
        )
        van   = create_van("SYS 0001", owner.owner_id, status="active")
        route = create_route("Sys Route", time(6, 0), time(10, 0),
                             today, owner.owner_id)

        # Link route to region so get_customer_route_id can find it
        assign_route_to_area(route_id=route.route_id, region_id=region.region_id)

        return owner, customer, van, route, region

    def test_unauthenticated_customer_route_redirects(self, client, db):
        """GET /api/customer/route without auth should redirect to login."""
        resp = client.get("/api/customer/route")
        assert resp.status_code in (302, 401)

    def test_authenticated_customer_can_access_route_endpoint(self, client, db):
        """GET /api/customer/route with a valid customer token should return 200."""
        self._seed(db)
        token = get_token(client, "custsys@test.com", "password")
        resp  = client.get("/api/customer/route", headers=auth_headers(token))
        assert resp.status_code == 200

    def test_get_order_returns_none_when_no_order_placed(self, client, db):
        """GET /api/customer/get-order should return null when no order exists today."""
        self._seed(db)
        token = get_token(client, "custsys@test.com", "password")
        resp  = client.get("/api/customer/get-order", headers=auth_headers(token))

        assert resp.status_code == 200
        data = resp.get_json()
        assert data is None or data.get("order") is None

    def test_make_stop_request_creates_order(self, client, db):
        """POST /api/customer/make-stop-request should create a stop and return 200."""
        owner, customer, van, route, region = self._seed(db)

        from App.controllers.driver import assign_driver_to_route
        from App.controllers.user import create_driver
        from App.controllers.van import assign_van_to_route

        driver = create_driver("sysdriver@test.com", "pass", "Sys Driver",
                               owner_id=owner.owner_id)
        assign_van_to_route(van.van_id, route.route_id)
        assign_driver_to_route(driver.driver_id, route.route_id)
        van.assign_driver(driver.driver_id)
        db.session.commit()

        token = get_token(client, "custsys@test.com", "password")
        resp  = client.post("/api/customer/make-stop-request",
                            json={"lat": 10.6420, "lng": -61.4005,
                                  "address": "123 Test Street"},
                            headers=auth_headers(token))

        assert resp.status_code == 200


# ─────────────────────────────────────────────────────────────────────────────
# SYSTEM TEST 3 — DRIVER API ENDPOINTS
# ─────────────────────────────────────────────────────────────────────────────

class TestDriverAPISystem:
    """
    System tests for the driver-facing API.
    Verifies driver authentication and route/stop data retrieval.
    """

    def _seed(self, db):
        from App.controllers.user import create_owner, create_driver
        from App.controllers.van import create_van, assign_van_to_route
        from App.controllers.route import create_route
        from App.controllers.driver import assign_driver_to_route

        today  = datetime.now().strftime("%A")
        owner  = create_owner("drvsysowner@test.com", "pass")
        driver = create_driver("drvsys@test.com", "password", "Sys Driver",
                               owner_id=owner.owner_id)
        van    = create_van("DRV 0001", owner.owner_id, status="active")
        route  = create_route("Driver Sys Route", time(6, 0), time(10, 0),
                              today, owner.owner_id)

        assign_van_to_route(van.van_id, route.route_id)
        assign_driver_to_route(driver.driver_id, route.route_id)
        van.assign_driver(driver.driver_id)
        db.session.commit()

        return owner, driver, van, route

    def test_unauthenticated_driver_plate_redirects(self, client, db):
        """GET /api/driver/plate without auth should redirect to login."""
        resp = client.get("/api/driver/plate")
        assert resp.status_code in (302, 401)

    def test_driver_can_get_their_van_plate(self, client, db):
        """GET /api/driver/plate should return the van plate assigned to the driver."""
        owner, driver, van, route = self._seed(db)
        token = get_token(client, "drvsys@test.com", "password")
        resp  = client.get("/api/driver/plate", headers=auth_headers(token))

        assert resp.status_code == 200
        assert resp.get_json()["plate"] == "DRV 0001"

    def test_driver_can_get_their_route(self, client, db):
        """GET /api/driver/route should return the route assigned to the driver."""
        owner, driver, van, route = self._seed(db)
        token = get_token(client, "drvsys@test.com", "password")
        resp  = client.get("/api/driver/route", headers=auth_headers(token))

        assert resp.status_code == 200

    def test_driver_active_stops_returns_list(self, client, db):
        """GET /api/driver/active-stops should return a list (empty or populated)."""
        owner, driver, van, route = self._seed(db)
        token = get_token(client, "drvsys@test.com", "password")
        resp  = client.get("/api/driver/active-stops", headers=auth_headers(token))

        assert resp.status_code == 200
        assert isinstance(resp.get_json(), list)
