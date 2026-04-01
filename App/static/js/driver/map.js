//This io() function is loaded from socket.io min.js
const socket = io();

var vanSVG = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M96 128C60.7 128 32 156.7 32 192L32 400C32 435.3 60.7 464 96 464L96.4 464C100.4 508.9 138.1 544 184 544C229.9 544 267.6 508.9 271.6 464L376.3 464C380.3 508.9 418 544 463.9 544C510 544 547.8 508.6 551.6 463.5C583.3 459.7 607.9 432.7 607.9 400L607.9 298.7C607.9 284.9 603.4 271.4 595.1 260.3L515.1 153.6C503.1 137.5 484.1 128 464 128L96 128zM536 288L416 288L416 192L464 192L536 288zM96 288L96 192L192 192L192 288L96 288zM256 288L256 192L352 192L352 288L256 288zM424 456C424 433.9 441.9 416 464 416C486.1 416 504 433.9 504 456C504 478.1 486.1 496 464 496C441.9 496 424 478.1 424 456zM184 416C206.1 416 224 433.9 224 456C224 478.1 206.1 496 184 496C161.9 496 144 478.1 144 456C144 433.9 161.9 416 184 416z"/></svg>
    `;

const markerSVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path fill="rgb(232, 152, 0)" d="M128 252.6C128 148.4 214 64 320 64C426 64 512 148.4 512 252.6C512 371.9 391.8 514.9 341.6 569.4C329.8 582.2 310.1 582.2 298.3 569.4C248.1 514.9 127.9 371.9 127.9 252.6zM320 320C355.3 320 384 291.3 384 256C384 220.7 355.3 192 320 192C284.7 192 256 220.7 256 256C256 291.3 284.7 320 320 320z"/></svg>`;
const selectedMarkerSVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path fill="rgb(0, 124, 232)" d="M128 252.6C128 148.4 214 64 320 64C426 64 512 148.4 512 252.6C512 371.9 391.8 514.9 341.6 569.4C329.8 582.2 310.1 582.2 298.3 569.4C248.1 514.9 127.9 371.9 127.9 252.6zM320 320C355.3 320 384 291.3 384 256C384 220.7 355.3 192 320 192C284.7 192 256 220.7 256 256C256 291.3 284.7 320 320 320z"/></svg>`;
const newMarkerSVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path fill="rgb(161, 3, 3)" d="M128 252.6C128 148.4 214 64 320 64C426 64 512 148.4 512 252.6C512 371.9 391.8 514.9 341.6 569.4C329.8 582.2 310.1 582.2 298.3 569.4C248.1 514.9 127.9 371.9 127.9 252.6zM320 320C355.3 320 384 291.3 384 256C384 220.7 355.3 192 320 192C284.7 192 256 220.7 256 256C256 291.3 284.7 320 320 320z"/></svg>`;

var requestShowing = false;
let currentlySelectedMarker = null;

var markers = [];
var leafletMarkers = {};

const newMarkerIcon = L.divIcon({
  html: newMarkerSVG,
  iconSize: [40, 40],
  className: "pending-icon",
});

const markerIcon = L.divIcon({
  html: markerSVG,
  iconSize: [40, 40],
  className: "marker-icon",
});

const selectedMarkerIcon = L.divIcon({
  html: selectedMarkerSVG,
  iconSize: [50, 50],
  className: "marker-icon ",
});

//Map initialization
var map = L.map("map", {
  center: [10.433, -61.2282],
  zoom: 10,
  maxZoom: 18,
  scrollWheelZoom: true,
  wheelPxPerZoomLevel: 200,
});

//Tile Layer displayed on the map
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 18,
  attribution:
    '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
}).addTo(map);

//Handles Marker Clustering
let markerClusterLayer = L.markerClusterGroup({
  iconCreateFunction: function (cluster) {
    const count = cluster.getChildCount();
    return L.divIcon({
      html: `
        <div class="marker-cluster">
         ${markerSVG.repeat(count)}
        </div>
      `,
      className: "",
      iconSize: [40, 40],
    });
  },
});
map.addLayer(markerClusterLayer);

let driverLocation = null;

navigator.geolocation.watchPosition(success, error, {
  enableHighAccuracy: true,
  maximumAge: 1000,
  timeout: 10000,
});

async function success(position) {
  const lat = position.coords.latitude;
  const lon = position.coords.longitude;

  const plate_object = await getFromApi("/api/driver/plate");

  socket.emit("driver_location", {
    lat: position.coords.latitude,
    lng: position.coords.longitude,
    plate: plate_object.plate,
  });

  if (!driverLocation) {
    driverLocation = L.marker([lat, lon], {
      icon: L.divIcon({
        html: vanSVG,
        iconSize: [40, 40],
        className: "van-icon",
      }),
    }).addTo(map);
  } else {
    driverLocation.setLatLng([lat, lon]);
  }

  buildRoute();
}

function error(err) {
  if (err.code === 1) {
    alert("Error: Please allow geolocation access");
  } else {
    alert("Error: Position is unavailable!");
  }
}

async function getFromApi(url) {
  const res = await fetch(url);
  const json = await res.json();

  return json;
}

async function initMap() {
  markers = await getFromApi("/api/driver/active-stops");

  markers.forEach(function (marker) {
    let mapMarker = L.marker([marker.lat, marker.lng], {
      icon: markerIcon,
    }).addTo(map);

    leafletMarkers[marker.stop_id] = mapMarker;

    mapMarker.on("click", async function (e) {
      populateSideContent(marker);
      displayRequestDetails(e);

      if (currentlySelectedMarker) {
        const isExistingMarker = markers.find(
          (m) =>
            m.lat == currentlySelectedMarker._latlng.lat &&
            m.lng == currentlySelectedMarker._latlng.lng,
        );
        if (isExistingMarker != undefined)
          currentlySelectedMarker.setIcon(markerIcon);
        else {
          currentlySelectedMarker.setIcon(newMarkerIcon);
        }
      }

      // Set this marker as selected
      mapMarker.setIcon(selectedMarkerIcon);
      currentlySelectedMarker = mapMarker;

      if (!requestShowing) await sleep(550);
      requestShowing = true;

      map.flyTo([marker.lat, marker.lng], 17);
    });
  });
}

//Routing Code
let routingControl = null;

async function buildRoute() {
  //Get Route from API
  const route_stops = await getFromApi("/api/driver/route");
  let waypoints = [
    driverLocation.getLatLng(),
    ...route_stops.map((stop) => L.latLng(stop.lat, stop.lng)),
  ];

  if (routingControl) {
    routingControl.setWaypoints(waypoints);
  } else {
    routingControl = L.Routing.control({
      waypoints: waypoints,
      show: false,
      createMarker: function (i, wp, nWps) {
        return null;
      },
    }).addTo(map);
  }
}
