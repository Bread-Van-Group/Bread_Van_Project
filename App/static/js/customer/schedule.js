const now = new Date();
const options = {
  weekday: "short",
  day: "numeric",
  month: "short",
  year: "numeric",
};
document.getElementById("today-date").textContent = now.toLocaleDateString(
  "en-GB",
  options,
);

//Helper function to add string times
function addTimes(time1, time2) {
  const toSeconds = (t) => {
    const [h, m, s] = t.split(":").map(Number);
    return h * 3600 + m * 60 + s;
  };

  const totalSeconds = toSeconds(time1) + toSeconds(time2);

  const h = Math.floor(totalSeconds / 3600);
  const m = Math.floor((totalSeconds % 3600) / 60);
  const s = totalSeconds % 60;

  return [h, m, s].map((v) => String(v).padStart(2, "0")).join(":");
}

//Populate the stop list with the route stop details
document.addEventListener("DOMContentLoaded", async function () {
  const stopItems = document.querySelectorAll(".stop-item");
  let startLat = null;
  let startLng = null;
  let newStartTime = null;

  for (const item of stopItems) {
    const lat = item.getAttribute("data-lat");
    const lng = item.getAttribute("data-lng");
    const order = item.getAttribute("data-order");
    const startTime = item.getAttribute("data-startTime");

    const addressData = await reverseGeocode(lat, lng); // ← actually awaits now
    let address =
      addressData?.display_name?.replace(", Trinidad and Tobago", "") ??
      "Unknown";
    address = address.split(",").slice(0, -2).join(",");

    let eta = null;
    let distance = null;
    if (order == 0) {
      eta = startTime;
      newStartTime = startTime;
      startLat = lat;
      startLng = lng;
      distance = 0;
    } else {
      const destination = { getLatLng: () => L.latLng(lat, lng) };
      const startLoc = L.latLng(startLat, startLng);
      eta = calculateETAToCustomer(destination, startLoc);
      eta = addTimes(newStartTime, eta);
      newStartTime = eta;
      const distanceMetres = startLoc.distanceTo(destination.getLatLng());
      distance = distanceMetres / 1000;
    }

    item.querySelector(".stop-area").innerHTML = address;
    item.querySelector(".stop-time").innerHTML = eta + " p.m";
    item.querySelector(".stop-distance").innerHTML = distance.toFixed(2) + "km";

    await delay(1100);
  }
});
