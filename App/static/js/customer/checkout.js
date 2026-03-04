const customerMarkerSVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path fill="rgb(0, 124, 232)" d="M128 252.6C128 148.4 214 64 320 64C426 64 512 148.4 512 252.6C512 371.9 391.8 514.9 341.6 569.4C329.8 582.2 310.1 582.2 298.3 569.4C248.1 514.9 127.9 371.9 127.9 252.6zM320 320C355.3 320 384 291.3 384 256C384 220.7 355.3 192 320 192C284.7 192 256 220.7 256 256C256 291.3 284.7 320 320 320z"/></svg>`;

const customerMarkerIcon = L.divIcon({
  html: customerMarkerSVG,
  iconSize: [30, 30],
  className: "marker-icon ",
});

//This gets the customer location
// navigator.geolocation.watchPosition(success, error, {
//   enableHighAccuracy: true,
//   maximumAge: 1000,
//   timeout: 10000,
// });

//Dummy Customer Location
var dummyCustomerMarker = L.marker([10.6405359397094, -61.39297485351563], {
  icon: customerMarkerIcon,
}).addTo(map);

//Dummy Driver Location
breadVanMarker = L.marker([10.642156853165652, -61.39825880527497], {
  icon: L.divIcon({
    html: vanSVG,
    iconSize: [30, 30],
    className: "van-icon",
  }),
}).addTo(map);

const waypoints = [breadVanMarker.getLatLng(), dummyCustomerMarker.getLatLng()];
buildRoute(waypoints);

//Do this to fly to center of driver and customer
const m1 = breadVanMarker.getLatLng();
const m2 = dummyCustomerMarker.getLatLng();

const avgLat = (m1.lat + m2.lat) / 2;
const avgLng = (m1.lng + m2.lng) / 2;

map.flyTo([avgLat, avgLng], 15);
