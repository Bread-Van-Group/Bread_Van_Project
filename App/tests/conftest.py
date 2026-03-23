import pytest
from flask import Flask
from App.database import db as _db


@pytest.fixture(scope="session")
def app():
    """Create a Flask app configured for testing with an in-memory SQLite DB."""
    test_app = Flask(__name__)
    test_app.config["TESTING"] = True
    test_app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    test_app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    test_app.config["JWT_SECRET_KEY"] = "test-secret"

    _db.init_app(test_app)

    with test_app.app_context():
        _db.create_all()
        yield test_app
        _db.drop_all()


@pytest.fixture(scope="function")
def db(app):
    """Provide a clean database session for each test (rolls back after each test)."""
    with app.app_context():
        yield _db
        _db.session.rollback()
        # Clear all tables between tests
        for table in reversed(_db.metadata.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()