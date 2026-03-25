from App.database import db
from App.models import RouteHistory


# ── Queries ────────────────────────────────────────────────────────────────────

def get_history_by_id(history_id):
    return db.session.get(RouteHistory, history_id)


def get_history_for_route(route_id):
    """Return all drive sessions for a route, most recent first."""
    return db.session.scalars(
        db.select(RouteHistory)
        .filter_by(route_id=route_id)
        .order_by(RouteHistory.started_at.desc())
    ).all()


def get_history_for_driver(driver_id):
    """Return all drive sessions for a driver, most recent first."""
    return db.session.scalars(
        db.select(RouteHistory)
        .filter_by(driver_id=driver_id)
        .order_by(RouteHistory.started_at.desc())
    ).all()


def get_history_for_van(van_id):
    """Return all drive sessions for a van, most recent first."""
    return db.session.scalars(
        db.select(RouteHistory)
        .filter_by(van_id=van_id)
        .order_by(RouteHistory.started_at.desc())
    ).all()


def get_active_session(van_id):
    """Return the current in-progress drive session for a van, or None."""
    return db.session.execute(
        db.select(RouteHistory)
        .filter_by(van_id=van_id, status='in_progress')
    ).scalar_one_or_none()


# ── Create / update ────────────────────────────────────────────────────────────

def start_route_session(route_id, van_id, driver_id):
    """
    Begin a new drive session.
    Raises a ValueError if the van already has an in-progress session.
    Returns the new RouteHistory record.
    """
    if get_active_session(van_id):
        raise ValueError(f"Van {van_id} already has an active drive session.")

    session = RouteHistory(route_id=route_id, van_id=van_id, driver_id=driver_id)
    db.session.add(session)
    db.session.commit()
    return session


def complete_route_session(history_id):
    """
    Mark a drive session as completed.
    Returns the updated RouteHistory, or None if not found.
    """
    session = get_history_by_id(history_id)
    if not session:
        return None
    session.complete()
    db.session.commit()
    return session


def complete_active_session_for_van(van_id):
    """
    Convenience helper: find and complete the active session for a van.
    Returns the completed RouteHistory, or None if no active session exists.
    """
    session = get_active_session(van_id)
    if not session:
        return None
    session.complete()
    db.session.commit()
    return session