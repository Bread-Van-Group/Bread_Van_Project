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
