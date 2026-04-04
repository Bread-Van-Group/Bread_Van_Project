function buildRoute(waypoints, routingControl) {
  if (routingControl) {
    routingControl.setWaypoints(waypoints);
  } else {
    routingControl = L.Routing.control({
      waypoints: waypoints,
      router: L.Routing.osrmv1({
        serviceUrl: "https://bread-van-osrm-server.onrender.com/route/v1",
      }),
      show: false,
      createMarker: function (i, wp, nWps) {
        return null;
      },
    }).addTo(map);

    routingControl.on("routesfound", function (e) {
      const container = routingControl.getContainer();
      if (container) container.style.display = "none";
      routeCoordinates = e.routes[0].coordinates;
    });
  }

  return routingControl;
}
