//CHANGE THIS DEPENDING ON DESIRED VAN SPEED
const VAN_SPEED = 48.2803; //km an hour

function changeContent(page) {
  const mainContent = document.querySelector("#main-content");

  const map = document.querySelector("#map");
  const mapText = document.querySelector("#map-text");

  const orderSection = document.querySelector("#order-section");

  const mapBtn = document.querySelector("#map-button");
  const orderBtn = document.querySelector("#order-button");

  const myOrderStatus = document.querySelector("#my-order-status");

  if (String(page) === "map") {
    if (breadVanMarker == null) {
      toggleMapInactive();

      map.style.zIndex = 1;
    } else {
      map.style.zIndex = 1;
      map.style.opacity = 1;
    }
    orderBtn.classList.add("content-navbar-btn-inactive");
    mapBtn.classList.remove("content-navbar-btn-inactive");

    myOrderStatus.classList.add("my-order-status-inactive");

    orderSection.style.zIndex = -1;
    orderSection.style.opacity = 0;
  } else {
    mapBtn.classList.add("content-navbar-btn-inactive");
    orderBtn.classList.remove("content-navbar-btn-inactive");

    myOrderStatus.classList.remove("my-order-status-inactive");

    mapText.style.opacity = 0;

    orderSection.style.zIndex = 1;
    orderSection.style.opacity = 1;

    map.style.zIndex = -1;
    map.style.opacity = 0;
  }
}

//Checks to see if Van is active every second
//Also updates ETA if it is
setInterval(() => {
  const orderSection = document.querySelector("#order-section");

  if (breadVanMarker == null && orderSection.style.opacity == 0) {
    toggleMapInactive();
  } else {
    toggleMapActive();

    if (breadVanMarker == null) return;

    if (orderMarker != null) destination = orderMarker;
    else destination = customerMarker;

    const eta = document.querySelector("#order-eta");

    const vanDistanceMetres = breadVanMarker
      .getLatLng()
      .distanceTo(destination.getLatLng());
    const vanDistanceKm = vanDistanceMetres / 1000;

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
  }
}, 1000);

function toggleMapActive() {
  const map = document.querySelector("#map");
  const mapText = document.querySelector("#map-text");
  map.style.opacity = 1;
  mapText.style.opacity = 0;
  mapText.style.zIndex = -2;
}

function toggleMapInactive() {
  const map = document.querySelector("#map");
  const mapText = document.querySelector("#map-text");
  map.style.opacity = 0.3;
  mapText.style.opacity = 1;
  mapText.style.zIndex = 2;
}
