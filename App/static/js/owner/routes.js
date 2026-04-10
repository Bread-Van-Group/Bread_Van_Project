let map;
let routes = [];
let selectedRoute = null;
let routePolylines = [];
let stops = [];
let stopMarkers = [];
let activeRoutingControl = null;
let isSelectingLocation = false;
let isEditing = false;
let allDrivers = [];
let allRegions = [];

// ── Drivers ──────────────────────────────────────────────────────

async function loadDrivers() {
  try {
    const res = await fetch("/api/owner/drivers");
    allDrivers = await res.json();
    populateDriverSelect();
  } catch (err) {
    console.error("Failed to load drivers:", err);
  }
}

function populateDriverSelect(selectedDriverId = null) {
  const menu = document.getElementById("driver-select-menu");
  const label = document.getElementById("driver-select-label");
  const hidden = document.getElementById("route-driver");
  if (!menu) return;

  menu.innerHTML =
    `<li data-value="">-- No driver assigned --</li>` +
    allDrivers
      .map(
        (d) =>
          `<li data-value="${d.driver_id}">${d.name}${d.assigned_van_plate ? " (" + d.assigned_van_plate + ")" : ""}</li>`,
      )
      .join("");

  const selectedDriver = selectedDriverId
    ? allDrivers.find((d) => d.driver_id == selectedDriverId)
    : null;

  label.textContent = selectedDriver
    ? selectedDriver.name +
      (selectedDriver.assigned_van_plate
        ? " (" + selectedDriver.assigned_van_plate + ")"
        : "")
    : "-- No driver assigned --";
  hidden.value = selectedDriverId || "";

  menu.querySelectorAll("li").forEach((li) => {
    li.classList.toggle(
      "selected",
      li.dataset.value == (selectedDriverId || ""),
    );
    li.addEventListener("click", () => {
      menu
        .querySelectorAll("li")
        .forEach((x) => x.classList.remove("selected"));
      li.classList.add("selected");
      label.textContent = li.textContent;
      hidden.value = li.dataset.value;
      document.getElementById("driver-select").classList.remove("open");
      document
        .getElementById("driver-select-trigger")
        .setAttribute("aria-expanded", false);
    });
  });
}

function initDriverDropdown() {
  const wrapper = document.getElementById("driver-select");
  const trigger = document.getElementById("driver-select-trigger");

  trigger.addEventListener("click", (e) => {
    e.stopPropagation();
    const open = wrapper.classList.toggle("open");
    trigger.setAttribute("aria-expanded", open);
  });

  document.addEventListener("click", (e) => {
    if (!wrapper.contains(e.target)) {
      wrapper.classList.remove("open");
      trigger.setAttribute("aria-expanded", false);
    }
  });
}

function setDriverDropdownValue(driverId) {
  const driver = allDrivers.find((d) => d.driver_id == driverId);
  const label = document.getElementById("driver-select-label");
  const hidden = document.getElementById("route-driver");
  const menu = document.getElementById("driver-select-menu");
  if (!label || !hidden) return;

  label.textContent = driver
    ? driver.name +
      (driver.assigned_van_plate ? " (" + driver.assigned_van_plate + ")" : "")
    : "-- No driver assigned --";
  hidden.value = driverId || "";

  if (menu) {
    menu.querySelectorAll("li").forEach((li) => {
      li.classList.toggle("selected", li.dataset.value == (driverId || ""));
    });
  }
}

// ── Regions ──────────────────────────────────────────────────────

async function loadRegions() {
  try {
    const res = await fetch("/api/owner/regions");
    allRegions = await res.json();
    populateRegionSelect();
  } catch (err) {
    console.error("Failed to load regions:", err);
  }
}

function populateRegionSelect(selectedRegionId = null) {
  const menu = document.getElementById("region-select-menu");
  const label = document.getElementById("region-select-label");
  const hidden = document.getElementById("route-region");
  if (!menu) return;

  menu.innerHTML =
    `<li data-value="">-- No area assigned --</li>` +
    allRegions
      .map((r) => `<li data-value="${r.region_id}">${r.name}</li>`)
      .join("");

  const selected = selectedRegionId
    ? allRegions.find((r) => r.region_id == selectedRegionId)
    : null;

  label.textContent = selected ? selected.name : "-- No area assigned --";
  hidden.value = selectedRegionId || "";

  menu.querySelectorAll("li").forEach((li) => {
    li.classList.toggle(
      "selected",
      li.dataset.value == (selectedRegionId || ""),
    );
    li.addEventListener("click", () => {
      menu
        .querySelectorAll("li")
        .forEach((x) => x.classList.remove("selected"));
      li.classList.add("selected");
      label.textContent = li.textContent;
      hidden.value = li.dataset.value;
      document.getElementById("region-select").classList.remove("open");
      document
        .getElementById("region-select-trigger")
        .setAttribute("aria-expanded", false);
    });
  });
}

function initRegionDropdown() {
  const wrapper = document.getElementById("region-select");
  const trigger = document.getElementById("region-select-trigger");

  trigger.addEventListener("click", (e) => {
    e.stopPropagation();
    const open = wrapper.classList.toggle("open");
    trigger.setAttribute("aria-expanded", open);
  });

  document.addEventListener("click", (e) => {
    if (!wrapper.contains(e.target)) {
      wrapper.classList.remove("open");
      trigger.setAttribute("aria-expanded", false);
    }
  });
}

function setRegionDropdownValue(regionId) {
  const region = allRegions.find((r) => r.region_id == regionId);
  const label = document.getElementById("region-select-label");
  const hidden = document.getElementById("route-region");
  const menu = document.getElementById("region-select-menu");
  if (!label || !hidden) return;

  label.textContent = region ? region.name : "-- No area assigned --";
  hidden.value = regionId || "";

  if (menu) {
    menu.querySelectorAll("li").forEach((li) => {
      li.classList.toggle("selected", li.dataset.value == (regionId || ""));
    });
  }
}

// ── Icons ─────────────────────────────────────────────────────────

let numberIcons = {};
function createNumberedIcon(number) {
  if (!numberIcons[number]) {
    numberIcons[number] = L.divIcon({
      html: `<div class="numbered-marker-inner">${number}</div>`,
      className: "numbered-marker",
      iconSize: [32, 32],
      iconAnchor: [16, 32],
      popupAnchor: [0, -32],
    });
  }
  return numberIcons[number];
}

// ── Routing ───────────────────────────────────────────────────────

function buildRoute(waypoints, routingControl) {
  if (routingControl) {
    routingControl.setWaypoints(waypoints);
  } else {
    routingControl = L.Routing.control({
      waypoints: waypoints,
      router: L.Routing.osrmv1({
        serviceUrl: "https://bread-van-osrm-server.onrender.com/route/v1",
      }),
      show: false,
      addWaypoints: false,
      draggableWaypoints: false,
      fitSelectedRoutes: true,
      createMarker: () => null,
      lineOptions: {
        styles: [{ className: "route-path-line" }],
      },
    }).addTo(map);

    routingControl.on("routesfound", function (e) {
      const container = routingControl.getContainer();
      if (container) container.style.display = "none";
    });
  }

  return routingControl;
}

function clearRoutingPath() {
  if (activeRoutingControl) {
    map.removeControl(activeRoutingControl);
    activeRoutingControl = null;
  }
}

function clearMap() {
  clearRoutingPath();
  routePolylines.forEach((l) => map.removeLayer(l));
  routePolylines = [];
  stopMarkers.forEach((m) => map.removeLayer(m));
  stopMarkers = [];
  map.eachLayer((layer) => {
    if (layer instanceof L.Marker) map.removeLayer(layer);
  });
}

// ── Map init ──────────────────────────────────────────────────────

function initMap() {
  map = L.map("map").setView([10.6409, -61.3953], 13);
  L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
    attribution: "© OpenStreetMap contributors",
    maxZoom: 19,
  }).addTo(map);
  map.on("click", handleMapClick);
}

// ── Day dropdown ──────────────────────────────────────────────────

function initDayDropdown() {
  const wrapper = document.getElementById("day-select");
  const trigger = document.getElementById("day-select-trigger");
  const menu = document.getElementById("day-select-menu");
  const label = document.getElementById("day-select-label");
  const hidden = document.getElementById("route-day");

  trigger.addEventListener("click", (e) => {
    e.stopPropagation();
    const open = wrapper.classList.toggle("open");
    trigger.setAttribute("aria-expanded", open);
  });

  menu.querySelectorAll("li").forEach((li) => {
    li.addEventListener("click", () => {
      menu
        .querySelectorAll("li")
        .forEach((x) => x.classList.remove("selected"));
      li.classList.add("selected");
      label.textContent = li.dataset.value;
      hidden.value = li.dataset.value;
      wrapper.classList.remove("open");
      trigger.setAttribute("aria-expanded", false);
    });
  });

  document.addEventListener("click", (e) => {
    if (!wrapper.contains(e.target)) {
      wrapper.classList.remove("open");
      trigger.setAttribute("aria-expanded", false);
    }
  });
}

function setDropdownValue(value) {
  const menu = document.getElementById("day-select-menu");
  const label = document.getElementById("day-select-label");
  const hidden = document.getElementById("route-day");
  menu.querySelectorAll("li").forEach((li) => {
    li.classList.toggle("selected", li.dataset.value === value);
  });
  label.textContent = value;
  hidden.value = value;
}

// ── Map hint ──────────────────────────────────────────────────────

function updateMapHint() {
  const hint = document.getElementById("map-selection-hint");
  if (!isSelectingLocation) {
    hint.style.display = "none";
    return;
  }
  hint.style.display = "block";
  hint.textContent = "📍 Click map to add Stop";
  hint.style.borderColor = "#0077be";
  hint.style.background = "rgba(0,119,190,0.12)";
  hint.style.color = "#014361";
}

// ── Stops ─────────────────────────────────────────────────────────

function renderStops() {
  stopMarkers.forEach((m) => map.removeLayer(m));
  stopMarkers = [];

  stops.forEach((stop, index) => {
    const marker = L.marker([stop.lat, stop.lng], {
      icon: createNumberedIcon(index + 1),
    }).addTo(map);

    marker.bindPopup(`
      <strong>Stop #${index + 1}</strong><br>
      <button onclick="removeStop(${index})" style="
        background: #ef4444;
        color: white;
        border: none;
        padding: 4px 12px;
        border-radius: 6px;
        cursor: pointer;
        margin-top: 8px;
      ">Remove Stop</button>
    `);

    stopMarkers.push(marker);
  });

  if (stops.length >= 2) {
    const waypoints = stops.map((s) => L.latLng(s.lat, s.lng));
    activeRoutingControl = buildRoute(waypoints, activeRoutingControl);
  } else {
    clearRoutingPath();
  }

  updateStopsList();
}

function updateStopsList() {
  const container = document.getElementById("stops-list-container");
  if (stops.length === 0) {
    container.innerHTML =
      '<div class="loc-text">No stops added yet. Click the map to add stops.</div>';
    return;
  }

  container.innerHTML = stops
    .map(
      (stop, index) => `
      <div class="location-row">
        <span class="loc-dot" style="background: #0077be;">${index + 1}</span>
        <div class="loc-text set">Stop #${index + 1}: (${stop.lat.toFixed(4)}, ${stop.lng.toFixed(4)})</div>
        <button class="loc-reset-btn" onclick="removeStop(${index})">Remove</button>
      </div>
    `,
    )
    .join("");
}

function handleMapClick(e) {
  if (!isSelectingLocation) return;
  const { lat, lng } = e.latlng;
  stops.push({ lat, lng, order: stops.length });
  renderStops();
  updateMapHint();
}

function removeStop(index) {
  stops.splice(index, 1);
  stops.forEach((stop, idx) => {
    stop.order = idx;
  });
  renderStops();
  map.closePopup();
}

function clearAllStops() {
  stops = [];
  clearRoutingPath();
  renderStops();
}

function stopSelecting() {
  isSelectingLocation = false;
  document.getElementById("map").classList.remove("map-clickable");
  updateMapHint();
}

function startSelecting() {
  isSelectingLocation = true;
  document.getElementById("map").classList.add("map-clickable");
  updateMapHint();
}

// ── Routes list ───────────────────────────────────────────────────

async function loadRoutes() {
  try {
    const res = await fetch("/api/owner/routes");
    routes = await res.json();
    renderRoutesList();
  } catch (err) {
    console.error("Failed to load routes:", err);
    document.getElementById("routes-list").innerHTML =
      '<div style="text-align:center;padding:40px;color:#94a3b8;">Failed to load routes</div>';
  }
}

function renderRoutesList() {
  const list = document.getElementById("routes-list");
  if (routes.length === 0) {
    list.innerHTML =
      '<div style="text-align:center;padding:40px;color:#94a3b8;">No routes yet</div>';
    return;
  }

  list.innerHTML = routes
    .map((route) => {
      const driverNames =
        route.assigned_drivers && route.assigned_drivers.length > 0
          ? route.assigned_drivers.map((d) => d.name).join(", ")
          : "No driver assigned";

      return `
        <div class="route-card ${selectedRoute && selectedRoute.route_id === route.route_id ? "active" : ""}"
             onclick="selectRoute(${route.route_id})">
          <div class="route-card-header">
            <div class="route-card-name">${route.name}</div>
            <div class="route-card-actions">
              <button class="route-edit-btn" onclick="event.stopPropagation(); editRoute(${route.route_id})">✎</button>
              <button class="route-delete-btn" onclick="event.stopPropagation(); deleteRoute(${route.route_id})">🗙</button>
            </div>
          </div>
          <div class="route-card-detail">⏰ ${route.start_time} - ${route.end_time}</div>
          <div class="route-card-detail">📍 ${route.stops_count || 0} stops</div>
          <div class="route-card-detail">👤 ${driverNames}</div>
          <span class="route-card-day">${route.day_of_week}</span>
        </div>
      `;
    })
    .join("");
}

// ── Select / view route ───────────────────────────────────────────

async function selectRoute(routeId) {
  selectedRoute = routes.find((r) => r.route_id === routeId);
  renderRoutesList();
  clearMap();

  try {
    const res = await fetch(`/api/owner/routes/${routeId}/stops`);
    const stopsData = await res.json();

    if (stopsData.length === 0) {
      alert("This route has no stops yet");
      return;
    }

    stopsData.forEach((stop, idx) => {
      const marker = L.marker([stop.lat, stop.lng], {
        icon: createNumberedIcon(idx + 1),
      }).addTo(map);
      marker.bindPopup(
        `<strong>Stop #${idx + 1}</strong><br>${stop.address || ""}`,
      );
      stopMarkers.push(marker);
    });

    if (stopsData.length > 1) {
      const waypoints = stopsData.map((s) => L.latLng(s.lat, s.lng));
      activeRoutingControl = buildRoute(waypoints, null);
    } else {
      map.setView([stopsData[0].lat, stopsData[0].lng], 14);
    }
  } catch (err) {
    console.error("Failed to load stops:", err);
  }
}

function viewAllRoutes() {
  selectedRoute = null;
  renderRoutesList();
  clearMap();
  map.setView([10.6409, -61.3953], 13);
}

// ── Editor ────────────────────────────────────────────────────────

async function showRouteEditor(editing = false) {
  document.getElementById("panel-list-view").style.display = "none";
  document.getElementById("panel-editor-view").style.display = "flex";

  isEditing = editing;
  clearAllStops();
  populateDriverSelect();
  populateRegionSelect();

  if (editing && selectedRoute) {
    document.getElementById("editor-title").textContent = "Edit Route";
    document.getElementById("route-name").value = selectedRoute.name;
    setDropdownValue(selectedRoute.day_of_week);
    document.getElementById("route-start-time").value =
      selectedRoute.start_time;
    document.getElementById("route-end-time").value = selectedRoute.end_time;
    document.getElementById("route-description").value =
      selectedRoute.description || "";

    const firstDriver =
      selectedRoute.assigned_drivers &&
      selectedRoute.assigned_drivers.length > 0
        ? selectedRoute.assigned_drivers[0]
        : null;
    populateDriverSelect(firstDriver ? firstDriver.driver_id : null);
    setDriverDropdownValue(firstDriver ? firstDriver.driver_id : null);

    //Set the region dropdown to the route's assigned region, if any
    try {
      const regionRes = await fetch(
        `/api/owner/route-region/${selectedRoute.route_id}`,
      );
      if (regionRes.ok) {
        const region = await regionRes.json();
        setRegionDropdownValue(region.region_id);
      } else {
        setRegionDropdownValue(null);
      }
    } catch (err) {
      console.error("Failed to load route region:", err);
      setRegionDropdownValue(null);
    }

    loadRouteStopsForEdit(selectedRoute.route_id);
  } else {
    document.getElementById("editor-title").textContent = "New Route";
    document.getElementById("route-name").value = "";
    setDropdownValue("Monday");
    document.getElementById("route-start-time").value = "06:00";
    document.getElementById("route-end-time").value = "10:00";
    document.getElementById("route-description").value = "";
    populateDriverSelect(null);
    setDriverDropdownValue(null);
    setRegionDropdownValue(null);
  }

  startSelecting();
}

async function loadRouteStopsForEdit(routeId) {
  try {
    const res = await fetch(`/api/owner/routes/${routeId}/stops`);
    const stopsData = await res.json();
    stops = stopsData.map((s, idx) => ({ lat: s.lat, lng: s.lng, order: idx }));
    renderStops();
  } catch (err) {
    console.error("Failed to load stops:", err);
  }
}

function hideRouteEditor() {
  document.getElementById("panel-list-view").style.display = "flex";
  document.getElementById("panel-editor-view").style.display = "none";
  stopSelecting();
  clearAllStops();
  clearMap();
  if (selectedRoute) selectRoute(selectedRoute.route_id);
}

function editRoute(routeId) {
  selectedRoute = routes.find((r) => r.route_id === routeId);
  showRouteEditor(true);
}

async function deleteRoute(routeId) {
  const route = routes.find((r) => r.route_id === routeId);
  if (!confirm(`Delete route "${route.name}"?`)) return;

  try {
    const res = await fetch(`/api/owner/routes/${routeId}`, {
      method: "DELETE",
    });
    if (res.ok) {
      alert("✅ Route deleted");
      await loadRoutes();
      clearMap();
      selectedRoute = null;
    }
  } catch (err) {
    console.error("Failed to delete:", err);
    alert("❌ Failed to delete route");
  }
}

// ── Driver assignment ─────────────────────────────────────────────

async function syncDriverAssignment(routeId, newDriverId) {
  const route = routes.find((r) => r.route_id === routeId);
  const currentDrivers =
    route && route.assigned_drivers ? route.assigned_drivers : [];

  await Promise.all(
    currentDrivers.map((d) =>
      fetch(`/api/owner/routes/${routeId}/assign-driver`, {
        method: "DELETE",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ driver_id: d.driver_id }),
      }),
    ),
  );

  if (newDriverId) {
    await fetch(`/api/owner/routes/${routeId}/assign-driver`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ driver_id: parseInt(newDriverId) }),
    });
  }
}

// ── Save ──────────────────────────────────────────────────────────

async function saveRoute() {
  const name = document.getElementById("route-name").value.trim();
  const day = document.getElementById("route-day").value;
  const startTime = document.getElementById("route-start-time").value;
  const endTime = document.getElementById("route-end-time").value;
  const description = document.getElementById("route-description").value.trim();
  const driverId = document.getElementById("route-driver").value;
  const regionId = document.getElementById("route-region").value;

  if (!name) {
    alert("Please enter a route name");
    return;
  }

  if (String(regionId) == "") {
    alert("Please select a route area");
    return;
  }

  if (stops.length < 2) {
    alert("Please add at least 2 stops to the route");
    return;
  }

  console.log(regionId);

  const routeData = {
    name,
    day_of_week: day,
    start_time: startTime,
    end_time: endTime,
    description,
    region_id: regionId ? parseInt(regionId) : null,
    stops: stops.map((stop, index) => ({
      lat: stop.lat,
      lng: stop.lng,
      order: index,
      address: "",
    })),
  };

  try {
    const url =
      isEditing && selectedRoute
        ? `/api/owner/routes/${selectedRoute.route_id}`
        : "/api/owner/routes";
    const method = isEditing && selectedRoute ? "PUT" : "POST";

    const res = await fetch(url, {
      method,
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(routeData),
    });

    if (!res.ok) throw new Error("Save failed");

    const result = await res.json();
    const savedRouteId =
      result.route_id || (selectedRoute && selectedRoute.route_id);

    await syncDriverAssignment(savedRouteId, driverId || null);

    alert("✅ Route saved successfully!");
    hideRouteEditor();
    await loadRoutes();
  } catch (err) {
    console.error("Failed to save route:", err);
    alert("❌ Failed to save route");
  }
}

// ── Init ──────────────────────────────────────────────────────────

document.addEventListener("DOMContentLoaded", async () => {
  initMap();
  initDayDropdown();
  initDriverDropdown();
  initRegionDropdown();
  await loadRoutes();
  await loadDrivers();
  await loadRegions();

  document.getElementById("add-route-btn").addEventListener("click", () => {
    selectedRoute = null;
    showRouteEditor(false);
  });

  document.getElementById("edit-route-btn").addEventListener("click", () => {
    if (selectedRoute) showRouteEditor(true);
  });

  document
    .getElementById("view-routes-btn")
    .addEventListener("click", viewAllRoutes);
  document
    .getElementById("save-route-btn")
    .addEventListener("click", saveRoute);
});
