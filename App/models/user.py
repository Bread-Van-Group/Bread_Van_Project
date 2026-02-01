from werkzeug.security import check_password_hash, generate_password_hash
from App.database import db

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name =  db.Column(db.String(20), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256), nullable=False)
    role= db.Column(db.String(256),nullable=False, default="user")  #Create role column to distinguish user types

    __mapper_args__ = {
        "polymorphic_on": role,
        "polymorphic_identity": "user"
    }

    def __init__(self, name, email,password,role):
        self.name = name
        self.role=role
        self.set_password(password)
        self.email= email

    def set_password(self, password):
        """Create hashed password."""
        self.password = generate_password_hash(password)
    
    def check_password(self, password):
        """Check hashed password."""
        return check_password_hash(self.password, password)
    


