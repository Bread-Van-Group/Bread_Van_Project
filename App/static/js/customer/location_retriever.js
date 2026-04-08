//Global Variables
let vanArrivalTime = null;

//Getting User's Current Location
let customerMarker = null;

navigator.geolocation.watchPosition(success, error, {
  enableHighAccuracy: true,
  maximumAge: 1000,
  timeout: 10000,
});

function success(position) {
  const lat = position.coords.latitude;
  const lon = position.coords.longitude;

  if (!customerMarker) {
    customerMarker = L.marker([lat, lon], {
      icon: customerMarkerIcon,
      iconSize: [40, 40],
      className: "marker-icon",
    }).addTo(map);

    markers.addLayer(customerMarker);
  } else {
    customerMarker.setLatLng([lat, lon]);
  }
}

function error(err) {
  if (err.code === 1) {
    alert("Error: Please allow geolocation access");
  } else {
    alert("Error: Position is unavailable!");
  }
}

//Getting the driver's live location
const socket = io();
var breadVanMarker = null;
let lastUpdate = 0;
const MIN_UPDATE_INTERVAL = 3000;

socket.on("driver_update", function (data) {
  const now = Date.now();

  if (now - lastUpdate < MIN_UPDATE_INTERVAL) {
    return;
  }
  lastUpdate = now;

  // Can't calculate ETA without customer location
  if (!customerMarker) return;

  vanLatLng = L.latLng(data.lat, data.lng);
  vanArrivalTime = calculateETAToCustomer(customerMarker, vanLatLng);

  if (breadVanIsClose()) {
    if (breadVanMarker == null) {
      breadVanMarker = L.marker([data.lat, data.lng], {
        icon: L.divIcon({
          html: vanSVG,
          iconSize: [40, 40],
          className: "van-icon",
        }),
      }).addTo(map);
      markers.addLayer(breadVanMarker);
    } else {
      breadVanMarker.setLatLng([data.lat, data.lng]);
    }
  } else {
    if (breadVanMarker !== null) {
      breadVanMarker.remove();
      breadVanMarker = null;
    }
  }
});

function calculateETAToCustomer(destination, vanLatLng) {
  const vanDistanceMetres = vanLatLng.distanceTo(destination.getLatLng());
  const vanDistanceKm = vanDistanceMetres / 1000;

  const totalSeconds = Math.floor((vanDistanceKm / VAN_SPEED) * 3600);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;

  const arrivalTime =
    String(hours).padStart(2, "0") +
    ":" +
    String(minutes).padStart(2, "0") +
    ":" +
    String(seconds).padStart(2, "0");

  return arrivalTime;
}

function breadVanIsClose() {
  if (vanArrivalTime == null) return false;

  const [hours, minutes, seconds] = vanArrivalTime.split(":").map(Number);
  const totalSeconds = hours * 3600 + minutes * 60 + seconds;
  return totalSeconds <= STORE_OPENING_ETA * 60;
}
