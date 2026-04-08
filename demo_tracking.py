"""
Bread Van Demo - Vehicle Tracking Simulation Script
====================================================
Fetches a real road-following route from OSRM then streams GPS coordinates
via WebSocket so the customer and owner dashboards update live.

Usage:
    python demo_tracking.py [options]

Options:
    --url       Server URL          (default: http://localhost:8080)
    --plate     Van license plate   (default: PBK 1234)
    --interval  Seconds per update  (default: 1.5)
    --loops     Times to repeat     (default: 1)
"""

import argparse
import time
import requests
import socketio

# ---------------------------------------------------------------------------
# Key delivery stops — OSRM will route between these along actual roads.
# Curepe → UWI Main Gate → St. Augustine depot → residential loop → back
# ---------------------------------------------------------------------------
ROUTE_WAYPOINTS = [
    (10.6409, -61.3959),  # Bakery Depot - Start
    (10.6421, -61.4005),  # UWI Main Gate
    (10.6405, -61.4012),  # UWI campus - stop 1
    (10.6390, -61.4002),  # UWI campus - stop 2
    (10.6421, -61.4005),  # Back out through Main Gate
    (10.6435, -61.3968),  # St. Augustine residential
    (10.6409, -61.3959),  # Bakery Depot - End
]



def fetch_osrm_route(waypoints):
    """Fetch actual road-following coordinates from the OSRM public API."""
    coords = ";".join(f"{lng},{lat}" for lat, lng in waypoints)
    url = f"http://router.project-osrm.org/route/v1/driving/{coords}"

    print("  Fetching road route from OSRM...")
    try:
        resp = requests.get(
            url,
            params={"overview": "full", "geometries": "geojson"},
            timeout=15,
        )
        data = resp.json()

        if data.get("code") != "Ok":
            raise Exception(f"OSRM returned: {data.get('code')}")

        # GeoJSON coordinates are [lng, lat] — swap to (lat, lng)
        raw = data["routes"][0]["geometry"]["coordinates"]
        route = [(round(lat, 6), round(lng, 6)) for lng, lat in raw]
        print(f"  Got {len(route)} road-following coordinates")
        return route

    except Exception as e:
        print(f"  [!] OSRM fetch failed: {e}")
        print("  [!] Falling back to direct waypoints (no road snapping)")
        return [(lat, lng) for lat, lng in waypoints]

import math

def densify_route(route, max_gap_metres=10):
    """Add interpolated points so no two consecutive coords are more than max_gap_metres apart."""
    def haversine(p1, p2):
        R = 6371000
        lat1, lng1 = math.radians(p1[0]), math.radians(p1[1])
        lat2, lng2 = math.radians(p2[0]), math.radians(p2[1])
        dlat, dlng = lat2 - lat1, lng2 - lng1
        a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlng/2)**2
        return R * 2 * math.asin(math.sqrt(a))

    dense = []
    for i in range(len(route) - 1):
        p1, p2 = route[i], route[i+1]
        dense.append(p1)
        dist = haversine(p1, p2)
        steps = int(dist // max_gap_metres)
        for s in range(1, steps):
            t = s / (steps)
            dense.append((
                round(p1[0] + (p2[0] - p1[0]) * t, 6),
                round(p1[1] + (p2[1] - p1[1]) * t, 6),
            ))
    dense.append(route[-1])
    return dense

def run_demo(url, plate, interval, loops):
    route = densify_route(fetch_osrm_route(ROUTE_WAYPOINTS), max_gap_metres=10)
    total_points = len(route)

    print(f"\n  Van plate : {plate}")
    print(f"  Server    : {url}")
    print(f"  Interval  : {interval}s per update")
    print(f"  Loops     : {loops}")
    print(f"  Route pts : {total_points} road-following coordinates\n")

    sio = socketio.Client(logger=False, engineio_logger=False)

    @sio.event
    def connect():
        print(f"[+] Connected to {url}")

    @sio.event
    def connect_error(data):
        print(f"[!] Connection failed: {data}")

    @sio.event
    def disconnect():
        print("[+] Disconnected")

    try:
        sio.connect(url, transports=["websocket", "polling"])
    except Exception as e:
        print(f"[!] Could not connect: {e}")
        print("    Is the server running? Check --url matches your Flask app.")
        return

    try:
        for loop_num in range(1, loops + 1):
            print(f"--- Loop {loop_num}/{loops} ---")
            for i, (lat, lng) in enumerate(route):
                sio.emit("driver_location", {"lat": lat, "lng": lng, "plate": plate})
                print(f"  [{i+1:>4}/{total_points}]  lat={lat:.6f}, lng={lng:.6f}")
                time.sleep(interval)
            print(f"--- Loop {loop_num} complete ---\n")

    except KeyboardInterrupt:
        print("\n[!] Demo stopped by user.")
    finally:
        sio.disconnect()


def main():
    parser = argparse.ArgumentParser(
        description="Bread Van demo: streams GPS coordinates via WebSocket."
    )
    parser.add_argument("--url", default="http://localhost:8080",
                        help="Server URL (default: http://localhost:8080)")
    parser.add_argument("--plate", default="PBK 1234",
                        help="Van license plate (default: PBK 1234)")
    parser.add_argument("--interval", type=float, default=1.5,
                        help="Seconds between updates (default: 1.5)")
    parser.add_argument("--loops", type=int, default=1,
                        help="Times to repeat the route (default: 1)")
    args = parser.parse_args()

    run_demo(url=args.url, plate=args.plate,
             interval=args.interval, loops=args.loops)


if __name__ == "__main__":
    main()
