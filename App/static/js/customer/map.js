var vanSVG = `
    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.1.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path d="M96 128C60.7 128 32 156.7 32 192L32 400C32 435.3 60.7 464 96 464L96.4 464C100.4 508.9 138.1 544 184 544C229.9 544 267.6 508.9 271.6 464L376.3 464C380.3 508.9 418 544 463.9 544C510 544 547.8 508.6 551.6 463.5C583.3 459.7 607.9 432.7 607.9 400L607.9 298.7C607.9 284.9 603.4 271.4 595.1 260.3L515.1 153.6C503.1 137.5 484.1 128 464 128L96 128zM536 288L416 288L416 192L464 192L536 288zM96 288L96 192L192 192L192 288L96 288zM256 288L256 192L352 192L352 288L256 288zM424 456C424 433.9 441.9 416 464 416C486.1 416 504 433.9 504 456C504 478.1 486.1 496 464 496C441.9 496 424 478.1 424 456zM184 416C206.1 416 224 433.9 224 456C224 478.1 206.1 496 184 496C161.9 496 144 478.1 144 456C144 433.9 161.9 416 184 416z"/></svg>
    `;
const customerMarkerSVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path fill="rgb(179, 4, 0)" d="M376 88C376 57.1 350.9 32 320 32C289.1 32 264 57.1 264 88C264 118.9 289.1 144 320 144C350.9 144 376 118.9 376 88zM400 300.7L446.3 363.1C456.8 377.3 476.9 380.3 491.1 369.7C505.3 359.1 508.3 339.1 497.7 324.9L427.2 229.9C402 196 362.3 176 320 176C277.7 176 238 196 212.8 229.9L142.3 324.9C131.8 339.1 134.7 359.1 148.9 369.7C163.1 380.3 183.1 377.3 193.7 363.1L240 300.7L240 576C240 593.7 254.3 608 272 608C289.7 608 304 593.7 304 576L304 416C304 407.2 311.2 400 320 400C328.8 400 336 407.2 336 416L336 576C336 593.7 350.3 608 368 608C385.7 608 400 593.7 400 576L400 300.7z"/></svg>`;
const orderMarkerSVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path fill="rgb(170, 87, 7)" d="M256 144C256 108.7 284.7 80 320 80C355.3 80 384 108.7 384 144L384 192L256 192L256 144zM208 192L144 192C117.5 192 96 213.5 96 240L96 448C96 501 139 544 192 544L448 544C501 544 544 501 544 448L544 240C544 213.5 522.5 192 496 192L432 192L432 144C432 82.1 381.9 32 320 32C258.1 32 208 82.1 208 144L208 192zM232 240C245.3 240 256 250.7 256 264C256 277.3 245.3 288 232 288C218.7 288 208 277.3 208 264C208 250.7 218.7 240 232 240zM384 264C384 250.7 394.7 240 408 240C421.3 240 432 250.7 432 264C432 277.3 421.3 288 408 288C394.7 288 384 277.3 384 264z"/></svg>`;
const markerSVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640"><!--!Font Awesome Free v7.2.0 by @fontawesome - https://fontawesome.com License - https://fontawesome.com/license/free Copyright 2026 Fonticons, Inc.--><path fill="rgb(161, 3, 3)" d="M128 252.6C128 148.4 214 64 320 64C426 64 512 148.4 512 252.6C512 371.9 391.8 514.9 341.6 569.4C329.8 582.2 310.1 582.2 298.3 569.4C248.1 514.9 127.9 371.9 127.9 252.6zM320 320C355.3 320 384 291.3 384 256C384 220.7 355.3 192 320 192C284.7 192 256 220.7 256 256C256 291.3 284.7 320 320 320z"/></svg>`;
const customerMarkerIcon = L.divIcon({
  html: customerMarkerSVG,
  iconSize: [40, 40],
  className: "marker-icon",
});

const orderMarkerIcon = L.divIcon({
  html: orderMarkerSVG,
  iconSize: [40, 40],
  className: "marker-icon ",
});

//Map initialization
var map = L.map("map", {
  center: [10.64179, -61.400861],
  zoom: 15,
  maxZoom: 18,
  minZoom: 13,
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

//Handles Marker Clustering
let markers = L.markerClusterGroup({
  iconCreateFunction: function (cluster) {
    const count = cluster.getChildCount();
    return L.divIcon({
      html: `
        <div class="marker-cluster">
         ${markerSVG.repeat(count)}
        </div>
      `,
      className: "", // clear default class
      iconSize: [40, 40],
    });
  },
});
map.addLayer(markers);

let orderMarker = null;

//Routing Code
let routingControl = null;

function buildRoute(waypoints) {
  if (routingControl) {
    routingControl.setWaypoints(waypoints);
  } else {
    routingControl = L.Routing.control({
      waypoints: waypoints,
      show: false,
      collapsible: false,
      createMarker: function (i, wp, nWps) {
        return null;
      },
    }).addTo(map);

    routingControl.on("routesfound", function () {
      const container = routingControl.getContainer();
      if (container) container.style.display = "none";
    });
  }
}

function drawRouteOnMap() {}
