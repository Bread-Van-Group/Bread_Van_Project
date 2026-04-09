import os

SQLALCHEMY_DATABASE_URI = os.environ.get(
    "SQLALCHEMY_DATABASE_URI",  
    "sqlite:///temp-database.db"  
)
SECRET_KEY="secret key"