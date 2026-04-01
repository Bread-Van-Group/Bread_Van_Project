from App.database import db
from App.models import MapStop


def create_map_stop(address,lat,lng):
    new_stop = MapStop(
        address=address,
        lat=lat,
        lng=lng,
    )

    db.session.add(new_stop)
    db.session.commit()
    return new_stop
