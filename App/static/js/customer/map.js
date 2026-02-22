var vanSVG = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M96 128C60.7 128 32 156.7 32 192L32 400C32 435.3 60.7 464 96 464L96.4 464C100.4 508.9 138.1 544 184 544C229.9 544 267.6 508.9 271.6 464L376.3 464C380.3 508.9 418 544 463.9 544C510 544 547.8 508.6 551.6 463.5C583.3 459.7 607.9 432.7 607.9 400L607.9 298.7C607.9 284.9 603.4 271.4 595.1 260.3L515.1 153.6C503.1 137.5 484.1 128 464 128L96 128zM536 288L416 288L416 192L464 192L536 288zM96 288L96 192L192 192L192 288L96 288zM256 288L256 192L352 192L352 288L256 288zM424 456C424 433.9 441.9 416 464 416C486.1 416 504 433.9 504 456C504 478.1 486.1 496 464 496C441.9 496 424 478.1 424 456zM184 416C206.1 416 224 433.9 224 456C224 478.1 206.1 496 184 496C161.9 496 144 478.1 144 456C144 433.9 161.9 416 184 416z"/></svg>
    `;

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
  zoom: 15,
  minZoom: 15,
  maxZoom: 18,
  scrollWheelZoom: true,
  zoomControl: false,
  wheelPxPerZoomLevel: 200,
});

//Tile Layer displayed on the map
L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 18,
  attribution:
    '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
}).addTo(map);

//Getting the driver's live location
const socket = io();
var breadVanMarker = null;

socket.on("driver_update", function (data) {
  if (breadVanMarker == null) {
    breadVanDummyMarker = L.marker([data.lat, data.lng], {
      icon: L.divIcon({
        html: vanSVG,
        iconSize: [40, 40],
        className: "van-icon",
      }),
    }).addTo(map);
  } else {
    breadVanMarker.setLatLng([data.lat, data.lng]);
  }
});
