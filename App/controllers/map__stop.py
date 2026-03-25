from App.database import db
from App.models import MapStop


def create_map_stop(address,lat,lng,stop_order=0):
    new_stop = MapStop(
        address=address,
        lat=lat,
        lng=lng,
        stop_order=stop_order,
    )

    db.session.add(new_stop)
    db.session.commit()
    return new_stop
