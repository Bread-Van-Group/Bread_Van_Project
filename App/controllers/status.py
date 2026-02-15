from App.database import db
from App.models import Status


def get_status_by_id(status_id):
    return db.session.get(Status, status_id)


def get_status_by_name(status_name):
    return db.session.execute(
        db.select(Status).filter_by(status_name=status_name)
    ).scalar_one_or_none()


def get_all_statuses():
    return db.session.scalars(db.select(Status)).all()


def create_status(status_name, description=None):
    existing = get_status_by_name(status_name)
    if existing:
        return existing  # Idempotent – don't duplicate named statuses
    status = Status(status_name=status_name, description=description)
    db.session.add(status)
    db.session.commit()
    return status