function changeContent(page) {
  const mainContent = document.querySelector("#main-content");

  const map = document.querySelector("#map");

  const orderSection = document.querySelector("#order-section");

  const mapBtn = document.querySelector("#map-button");
  const orderBtn = document.querySelector("#order-button");

  const myOrderStatus = document.querySelector("#my-order-status");

  if (String(page) === "map") {
    map.style.zIndex = 1;
    map.style.opacity = 1;

    orderBtn.classList.add("content-navbar-btn-inactive");
    mapBtn.classList.remove("content-navbar-btn-inactive");

    myOrderStatus.classList.add("my-order-status-inactive");

    orderSection.style.zIndex = -1;
    orderSection.style.opacity = 0;
  } else {
    mapBtn.classList.add("content-navbar-btn-inactive");
    orderBtn.classList.remove("content-navbar-btn-inactive");

    myOrderStatus.classList.remove("my-order-status-inactive");

    orderSection.style.zIndex = 1;
    orderSection.style.opacity = 1;

    map.style.zIndex = -1;
    map.style.opacity = 0;
  }
}

//If on Homepage This Code is Mounted
//Update the ETA field every second with current
//ETA calculated at location_retriever.js from
//the customer's location and the van's location
//Also states whether bread van is nearby on homepage
setInterval(() => {
  if (vanArrivalTime == null) return;

  const map = document.querySelector("#map");

  if (isClose() && map.style.zIndex == 1) {
    const activeDriverText = document.querySelector("#active-driver-text");
    activeDriverText.style.opacity = 1;
    activeDriverText.style.zIndex = 99;
  } else {
    const activeDriverText = document.querySelector("#active-driver-text");
    activeDriverText.style.opacity = 0;
    activeDriverText.style.zIndex = -99;
  }

  const eta = document.querySelector("#order-eta");

  eta.innerHTML = vanArrivalTime;
}, 1000);
