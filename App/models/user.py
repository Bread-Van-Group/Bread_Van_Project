from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db
from datetime import datetime, timedelta, timezone

UTC_MINUS_4 = timezone(timedelta(hours=-4))


class User(db.Model):
    __tablename__ = "users"

    user_id   = db.Column(db.Integer, primary_key=True)
    email     = db.Column(db.String(255), nullable=False, unique=True)
    password  = db.Column(db.String(255), nullable=False)
    role      = db.Column(db.String(20),  nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=True,
                           default=lambda: datetime.now(UTC_MINUS_4))

    __mapper_args__ = {
        "polymorphic_on": role,
        "polymorphic_identity": "user",
    }

    def __init__(self, email, password, role="customer"):
        self.email = email
        self.role  = role
        self.set_password(password)

    def set_password(self, password):
        """Hash and store the password."""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Verify a plaintext password against the stored hash."""
        return check_password_hash(self.password, password)

    def get_json(self):
        return {
            "user_id":    self.user_id,
            "email":      self.email,
            "role":       self.role,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f"<User {self.user_id} | {self.role}>"