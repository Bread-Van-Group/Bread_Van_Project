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

function changeContent(page) {
  const mainContent = document.querySelector("#main-content");
  const map = document.querySelector("#map");
  const orderSection = document.querySelector("#order-section");

  if (String(page) === "map") {
    map.style.zIndex = 1;
    map.style.opacity = 1;

    orderSection.style.zIndex = -1;
    orderSection.style.opacity = 0;
  } else {
    orderSection.style.zIndex = 1;
    orderSection.style.opacity = 1;

    map.style.zIndex = -1;
    map.style.opacity = 0;
  }
}
