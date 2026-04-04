var isCentered = false;
var popupOpened = false;
let detectDriverInterval = null;

let checkoutRoutingControl = null;

detectDriverInterval = setInterval(() => {
  if (breadVanMarker != null && customerMarker != null) {
    //Popup Code
    const vanDistanceMetres = breadVanMarker
      .getLatLng()
      .distanceTo(customerMarker.getLatLng());
    const vanDistanceKm = (vanDistanceMetres / 1000).toFixed(2);

    const popupContent = `
      <div class="popup-container">
        <p class="popup-van-plate">Plate No. : <span>${van_plate}</span></p>
        <p class="popup-van-dist">Distance : <span id="van-distance">${vanDistanceKm}km</span></p>
      </div>
    `;

    //Bind the popup once marker detected
    if (!popupOpened) {
      breadVanMarker
        .setIcon(
          L.divIcon({
            html: vanSVG,
            iconSize: [30, 30],
            className: "van-icon",
          }),
        )
        .bindPopup(popupContent, {
          autoClose: false,
          closeOnClick: false,
        })
        .openPopup();

      popupOpened = true;
    }

    //Build the route between customer and driver
    const waypoints = [breadVanMarker.getLatLng(), customerMarker.getLatLng()];
    checkoutRoutingControl = buildRoute(waypoints, checkoutRoutingControl);

    centerMap();
    clearInterval(detectDriverInterval);
  }
}, 1000);

//Set Distance of Van and reset Route Periodically
setInterval(() => {
  if (breadVanMarker == null) return;

  //ETA Code
  vanLatLng = L.latLng(data.lat, data.lng);
  arrivalTime = calculateETAToCustomer(customerMarker, vanLatLng);

  eta.innerHTML = arrivalTime;

  //Build the route between customer and driver
  const waypoints = [breadVanMarker.getLatLng(), customerMarker.getLatLng()];
  checkoutRoutingControl = buildRoute(waypoints, checkoutRoutingControl);

  document.querySelector("#van-distance").innerHTML = vanDistanceKm + "km";
}, 1000);

function centerMap() {
  if (isCentered) return;

  //Do this to fly to center of driver and customer
  const m1 = breadVanMarker.getLatLng();
  const m2 = customerMarker.getLatLng();

  const avgLat = (m1.lat + m2.lat) / 2;
  const avgLng = (m1.lng + m2.lng) / 2;

  map.flyTo([avgLat, avgLng], 15);

  isCentered = true;
}
