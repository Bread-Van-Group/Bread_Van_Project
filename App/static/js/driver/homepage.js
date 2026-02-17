//Needed to wait for time
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

//Map initialization

//Production Map Config
// var map = L.map("map", {
//   center: [10.234144, -61.43942],
//   zoom: 16,
//   maxBoundsViscosity: 1.0,
//   minZoom: 16,
//   maxZoom: 18,
//   zoomControl: false,
//   scrollWheelZoom: true,
//   wheelPxPerZoomLevel: 200,
//   maxBounds: [
//     [10.24166, -61.45022],
//     [10.2274, -61.42478],
//   ],
// });

//Testing Map config
var map = L.map("map", {
  center: [10.64179, -61.400861],
  maxBounds: [
    [10.63555, -61.38032],
    [10.64829, -61.41387],
  ],
  maxBoundsViscosity: 1.0,
  zoom: 17,
  minZoom: 17,
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

// **NOTE** The code below will be used to get the driver's live location
// let driverLocation = null;

// navigator.geolocation.watchPosition(success, error, {
//   enableHighAccuracy: true,
//   maximumAge: 1000,
//   timeout: 10000,
// });

// function success(position) {
//   const lat = position.coords.latitude;
//   const lon = position.coords.longitude;
//   const accuracy = position.coords.accuracy;

//   if (!driverLocation) {
//     driverLocation = L.marker([lat, lon]).addTo(map);
//   } else {
//     liveMarker.setLatLng([lat, lon]);
//   }
// }

// function error(err) {
//   if (err.code === 1) {
//     alert("Error: Please allow geolocation access");
//   } else {
//     alert("Error: Position is unavailable!");
//   }
// }

var vanSVG = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M96 128C60.7 128 32 156.7 32 192L32 400C32 435.3 60.7 464 96 464L96.4 464C100.4 508.9 138.1 544 184 544C229.9 544 267.6 508.9 271.6 464L376.3 464C380.3 508.9 418 544 463.9 544C510 544 547.8 508.6 551.6 463.5C583.3 459.7 607.9 432.7 607.9 400L607.9 298.7C607.9 284.9 603.4 271.4 595.1 260.3L515.1 153.6C503.1 137.5 484.1 128 464 128L96 128zM536 288L416 288L416 192L464 192L536 288zM96 288L96 192L192 192L192 288L96 288zM256 288L256 192L352 192L352 288L256 288zM424 456C424 433.9 441.9 416 464 416C486.1 416 504 433.9 504 456C504 478.1 486.1 496 464 496C441.9 496 424 478.1 424 456zM184 416C206.1 416 224 433.9 224 456C224 478.1 206.1 496 184 496C161.9 496 144 478.1 144 456C144 433.9 161.9 416 184 416z"/></svg>
    `;

var breadVanDummyMarker = L.marker([10.642156853165652, -61.39825880527497], {
  icon: L.divIcon({
    html: vanSVG,
    iconSize: [40, 40],
    className: "van-icon",
  }),
}).addTo(map);

var requestShowing = false;
//Markers initialized here
var markers = [];

async function getActiveMarkers() {
  const res = await fetch("/api/driver/active-stops");
  const json = await res.json();

  return json;
}

async function initMap() {
  markers = await getActiveMarkers();
  console.log(markers);
  markers.forEach(function (marker) {
    mapMarker = L.marker([marker.lat, marker.lng])
      .addTo(map)
      .bindPopup("Request ID: " + marker.id, {
        autoClose: true,
      });

    mapMarker.on("click", async function (e) {
      populateSideContent(marker);
      displayRequestDetails(e);

      if (!requestShowing) await sleep(550);
      requestShowing = true;

      map.flyTo([marker.lat, marker.lng], 17);
    });
  });
}

function populateSideContent(marker) {
  const sideContentBody = document.getElementById("side-content-body");

  let preOrderHtml;

  if (marker.customer_requests.length == 0) {
    preOrderHtml = `<p>No Order Attached<p>`;
  } else {
    preOrderHtml = marker.customer_requests
      .map((customer_request) => {
        return `
      <div class="pre-order-item">
        <div>
          <img src="${customer_request.item.image_url}" alt="${customer_request.item.name}" />
        </div>
        <div>${customer_request.item.name}</div>
        <div>${customer_request.quantity}</div>
      </div>
    `;
      })
      .join("");
  }

  const html = `
          <div class="address-details">
            <h3>Address:</h3>
            <p>${marker.address}</p>
          </div>
          <div id= "pre-order-container" class="pre-order-container">
            <h3>Pre-Order Items:</h3>
            <div class="pre-order-list">
              ${preOrderHtml}
            </div>
          </div>
          <div class="request-buttons-container">
            <button class="request-btn accept-btn">✕ CANCEL</button>
            <button class="request-btn decline-btn">✓ COMPLETE</button>
          </div>`;

  sideContentBody.innerHTML = html;
}

function displayRequestDetails(e) {
  const sideContent = document.getElementById("side-content");

  sideContent.style.width = "30%";
  sideContent.style.opacity = "1";
  sideContent.style.padding = "4px 24px";
  sideContent.style.marginRight = "24px";
}

async function hideSideContent() {
  const sideContent = document.getElementById("side-content");

  requestShowing = false;

  sideContent.style.width = "0%";
  sideContent.style.opacity = "0";
  sideContent.style.padding = "0px";
  sideContent.style.marginRight = "0px";

  await sleep(500);

  map.flyTo(breadVanDummyMarker.getLatLng(), 17);
  map.closePopup();
}

//Routing Code
let routingControl = null;

function buildRoute() {
  const waypoints = [
    breadVanDummyMarker.getLatLng(),
    ...markers.map((marker) => L.latLng(marker.lat, marker.lng)),
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

//All execution of other code afterwards
(async () => {
  await initMap();
  buildRoute();
})();

//This code is for testing, remove later
map.on("click", function (e) {
  const lat = e.latlng.lat;
  const lng = e.latlng.lng;

  console.log("User clicked at:", lat, lng);
});

map.on("click", function (e) {
  // Create a new marker where the user clicks
  const newMarker = L.marker(e.latlng).addTo(map);

  // Add it to your markers array
  markers.push({ lat: e.latlng.lat, lng: e.latlng.lng });

  // Rebuild the route including the new marker
  buildRoute();
});
