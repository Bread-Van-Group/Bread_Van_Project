//Needed to wait for time
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

function populateSideContent(marker) {
  const sideContentBody = document.getElementById("side-content-body");

  //Do this check if not on homepage
  if (sideContentBody == null) return;

  let preOrderHtml;

  if (marker.customer_requests.length == 0) {
    preOrderHtml = `<p>No Order Attached<p>`;
  } else {
    preOrderHtml = marker.customer_requests
      .map((customer_request) => {
        return `
      <div class="pre-order-item">
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

  //Do this check incase you are not on the homepage
  if (sideContent == null) return;

  sideContent.style.width = "30%";
  sideContent.style.opacity = "1";
  sideContent.style.padding = "4px 24px";
  sideContent.style.marginRight = "24px";
}

async function hideSideContent() {
  const sideContent = document.getElementById("side-content");

  //Deselect marker
  if (currentlySelectedMarker) {
    currentlySelectedMarker.setIcon(markerIcon);
    currentlySelectedMarker = null;
  }
  requestShowing = false;

  sideContent.style.width = "0%";
  sideContent.style.opacity = "0";
  sideContent.style.padding = "0px";
  sideContent.style.marginRight = "0px";

  await sleep(500);

  map.flyTo(breadVanDummyMarker.getLatLng(), 17);
  map.closePopup();
}

//All execution of other code afterwards
(async () => {
  await initMap();
  map.flyTo(breadVanDummyMarker.getLatLng(), 17);

  const waypoints = [
    breadVanDummyMarker.getLatLng(),
    ...markers.map((marker) => L.latLng(marker.lat, marker.lng)),
  ];

  buildRoute(waypoints);
})();

// //This code is for testing, remove later
// map.on("click", function (e) {
//   const lat = e.latlng.lat;
//   const lng = e.latlng.lng;

//   console.log("User clicked at:", lat, lng);
// });

// map.on("click", function (e) {
//   // Create a new marker where the user clicks
//   const newMarker = L.marker(e.latlng, {
//     icon: markerIcon,
//   }).addTo(map);

//   // Add it to your markers array
//   markers.push({ lat: e.latlng.lat, lng: e.latlng.lng });

//   // Rebuild the route including the new marker
//   const waypoints = [
//     breadVanDummyMarker.getLatLng(),
//     ...markers.map((marker) => L.latLng(marker.lat, marker.lng)),
//   ];

//   buildRoute(waypoints);
// });
