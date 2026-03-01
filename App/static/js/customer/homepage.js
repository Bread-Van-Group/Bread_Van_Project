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
