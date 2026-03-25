const checkoutCustomerMarkerIcon = L.divIcon({
  html: customerMarkerSVG,
  iconSize: [30, 30],
  className: "marker-icon ",
});

//CHANGE THIS DEPENDING ON DESIRED VAN SPEED
const VAN_SPEED = 48.2803; //km an hour

//----------------------------TESTING CODE---------------------------
// //Dummy Driver Location
// breadVanMarker = L.marker([10.642156853165652, -61.39825880527497], {
//   icon: L.divIcon({
//     html: vanSVG,
//     iconSize: [30, 30],
//     className: "van-icon",
//   }),
// }).addTo(map);

// //Popup Code
// const vanDistanceMetres = breadVanMarker
//   .getLatLng()
//   .distanceTo(dummyCustomerMarker.getLatLng());
// const vanDistanceKm = (vanDistanceMetres / 1000).toFixed(2);

// const popupContent = `
//       <div class="popup-container">
//         <p class="popup-van-plate">Plate No. : <span>${van_plate}</span></p>
//         <p class="popup-van-dist">Distance : <span>${vanDistanceKm}km</span></p>
//       </div>
// `;

// if (breadVanMarker) {
//   breadVanMarker
//     .bindPopup(popupContent, {
//       autoClose: false,
//       closeOnClick: false,
//     })
//     .openPopup();
// }

// //Build the route between customer and driver
// const waypoints = [breadVanMarker.getLatLng(), dummyCustomerMarker.getLatLng()];
// buildRoute(waypoints);

// //Do this to fly to center of driver and customer
// const m1 = breadVanMarker.getLatLng();
// const m2 = dummyCustomerMarker.getLatLng();

// const avgLat = (m1.lat + m2.lat) / 2;
// const avgLng = (m1.lng + m2.lng) / 2;

// map.flyTo([avgLat, avgLng], 15);

//--------------------------PRODUCTION CODE BELOW---------------

var isCentered = false;
var popupOpened = false;
let detectDriverInterval = null;

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
    buildRoute(waypoints);

    centerMap();
    clearInterval(detectDriverInterval);
  }
}, 1000);

//Set Distance of Van and reset Route Periodically
setInterval(() => {
  if (breadVanMarker == null) return;

  //ETA Code
  const vanDistanceMetres = breadVanMarker
    .getLatLng()
    .distanceTo(customerMarker.getLatLng());
  const vanDistanceKm = vanDistanceMetres / 1000;

  const eta = document.querySelector("#order-eta");

  const seconds = Math.floor((vanDistanceKm / VAN_SPEED) * 3600);
  const minutes = Math.floor(seconds / 60);
  const hours = Math.floor(minutes / 60);

  const arrivalTime =
    String(hours).padStart(2, "0") +
    ":" +
    String(minutes).padStart(2, "0") +
    ":" +
    String(seconds).padStart(2, "0");

  eta.innerHTML = arrivalTime;

  //Build the route between customer and driver
  const waypoints = [breadVanMarker.getLatLng(), customerMarker.getLatLng()];
  buildRoute(waypoints);

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
