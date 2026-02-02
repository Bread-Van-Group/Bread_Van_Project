from App.models import User
from App.database import db

def create_user(name, email, role, password):
    newuser = User(name=name, email=email, role=role, password=password)
    db.session.add(newuser)
    db.session.commit()
    return newuser

def get_user_by_name(username):
    result = db.session.execute(db.select(User).filter_by(name=username))
    return result.scalar_one_or_none()

def get_user(id):
    return db.session.get(User, id)

def get_all_users():
    return db.session.scalars(db.select(User)).all()

def get_all_users_json():
    users = get_all_users()
    if not users:
        return []
    users = [user.get_json() for user in users]
    return users

def update_user(id, username):
    user = get_user(id)
    if user:
        user.username = username
        # user is already in the session; no need to re-add
        db.session.commit()
        return True
    return None
