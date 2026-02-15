from flask_jwt_extended import (
    create_access_token,
    jwt_required,
    JWTManager,
    get_jwt_identity,
    verify_jwt_in_request,
)

from App.models import User
from App.database import db


def login(email, password):
    """Authenticate a user by email and password, return a JWT on success."""
    result = db.session.execute(db.select(User).filter_by(email=email))
    user = result.scalar_one_or_none()
    if user and user.check_password(password):
        return create_access_token(identity=str(user.user_id))
    return None


def setup_jwt(app):
    jwt = JWTManager(app)

    @jwt.user_identity_loader
    def user_identity_lookup(identity):
        user_id = getattr(identity, "user_id", identity)
        return str(user_id) if user_id is not None else None

    @jwt.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        try:
            user_id = int(identity)
        except (TypeError, ValueError):
            return None
        return db.session.get(User, user_id)

    return jwt


def add_auth_context(app):
    """Inject is_authenticated and current_user into all Jinja2 templates."""

    @app.context_processor
    def inject_user():
        try:
            verify_jwt_in_request()
            identity = get_jwt_identity()
            user_id = int(identity) if identity is not None else None
            current_user = db.session.get(User, user_id) if user_id is not None else None
            is_authenticated = current_user is not None
        except Exception:
            is_authenticated = False
            current_user = None
        return dict(is_authenticated=is_authenticated, current_user=current_user)