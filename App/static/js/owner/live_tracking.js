const socket = io();

let lastUpdate = 0;
const MIN_UPDATE_INTERVAL = 3000;

let vanPositions = {};
let vanMarkers = {};
let hasInitialized = false;

// ── WebSocket ────────────────────────────────────────────────────

socket.on("driver_update", function (data) {
  const now = Date.now();

  if (now - lastUpdate < MIN_UPDATE_INTERVAL) return;
  lastUpdate = now;

  vanPositions[data.plate] = { lat: data.lat, lng: data.lng };

  // FIX 1: update markers immediately on every socket event, not just on 30s refresh
  updateMapMarkers();
});

// ── Van SVG & Icon ───────────────────────────────────────────────

var vanSVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640">
  <path d="M96 128C60.7 128 32 156.7 32 192L32 400C32 435.3 60.7 464 96 464L96.4 464C100.4 508.9 138.1 544 184 544C229.9 544 267.6 508.9 271.6 464L376.3 464C380.3 508.9 418 544 463.9 544C510 544 547.8 508.6 551.6 463.5C583.3 459.7 607.9 432.7 607.9 400L607.9 298.7C607.9 284.9 603.4 271.4 595.1 260.3L515.1 153.6C503.1 137.5 484.1 128 464 128L96 128zM536 288L416 288L416 192L464 192L536 288zM96 288L96 192L192 192L192 288L96 288zM256 288L256 192L352 192L352 288L256 288zM424 456C424 433.9 441.9 416 464 416C486.1 416 504 433.9 504 456C504 478.1 486.1 496 464 496C441.9 496 424 478.1 424 456zM184 416C206.1 416 224 433.9 224 456C224 478.1 206.1 496 184 496C161.9 496 144 478.1 144 456C144 433.9 161.9 416 184 416z"/>
</svg>`;

function createVanIcon(isActive) {
  return L.divIcon({
    html: vanSVG,
    iconSize: [40, 40],
    className: isActive ? "van-icon" : "van-icon van-icon-inactive",
    popupAnchor: [0, -20],
  });
}

// ── Map init ─────────────────────────────────────────────────────

var map = L.map("tracking-map", {
  center: [10.64179, -61.400861],
  zoom: 14,
  maxZoom: 18,
  scrollWheelZoom: true,
});

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 18,
  attribution:
    '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
}).addTo(map);

// ── Fetch helpers ────────────────────────────────────────────────

async function fetchVans() {
  try {
    const res = await fetch("/api/owner/vans/tracking");
    if (!res.ok) return [];
    return await res.json();
  } catch (e) {
    console.error("Error fetching vans:", e);
    return [];
  }
}

async function fetchTodayRoutes() {
  try {
    const res = await fetch("/api/owner/routes");
    if (!res.ok) return [];
    const allRoutes = await res.json();
    const today = new Date().toLocaleDateString("en-US", { weekday: "long" });
    return allRoutes.filter((r) => r.day_of_week === today);
  } catch (e) {
    console.error("Error fetching routes:", e);
    return [];
  }
}

// ── Update UI ────────────────────────────────────────────────────

async function updateAll() {
  const [vans, todayRoutes] = await Promise.all([
    fetchVans(),
    fetchTodayRoutes(),
  ]);
  updateStats(vans, todayRoutes);
  updateMapMarkers();
  updateVanStatusList(vans);
  updateTodayRoutesList(todayRoutes);
}

function updateStats(vans, todayRoutes) {
  document.getElementById("active-vans").textContent = vans.filter(
    (v) => v.status === "active",
  ).length;
  document.getElementById("active-routes").textContent = todayRoutes.length;
  document.getElementById("active-drivers").textContent = vans.filter(
    (v) => v.current_driver_id,
  ).length;
  document.getElementById("total-inventory").textContent = "—";
}

function updateMapMarkers() {
  for (const [plate, position] of Object.entries(vanPositions)) {
    const latlng = [position.lat, position.lng];

    if (vanMarkers[plate] == null) {
      const marker = L.marker(latlng, { icon: createVanIcon(true) }).addTo(map);
      marker.bindPopup(`<b>${plate}</b>`);
      vanMarkers[plate] = marker;
    } else {
      vanMarkers[plate].setLatLng(latlng);
    }
  }

  // FIX 2: auto-zoom to fit all markers on first load
  if (!hasInitialized && Object.keys(vanMarkers).length > 0) {
    const group = L.featureGroup(Object.values(vanMarkers));
    map.fitBounds(group.getBounds().pad(0.3));
    hasInitialized = true;
  }
}

function updateVanStatusList(vans) {
  const el = document.getElementById("van-status-list");
  if (!el) return;

  if (vans.length === 0) {
    el.innerHTML = '<div class="empty-state">No vans found</div>';
    return;
  }

  el.innerHTML = vans
    .map(
      (van) => `
    <div class="van-status-item ${van.status === "active" ? "active" : ""}">
      <div>
        <div class="van-plate">${van.license_plate}</div>
        <div class="van-driver">${van.current_driver_name || "No driver assigned"}</div>
      </div>
      <div class="van-status-badge ${van.status || "inactive"}">${van.status || "inactive"}</div>
    </div>
  `,
    )
    .join("");
}

function updateTodayRoutesList(routes) {
  const el = document.getElementById("today-routes-list");
  if (!el) return;

  if (routes.length === 0) {
    const today = new Date().toLocaleDateString("en-US", { weekday: "long" });
    el.innerHTML = `<div class="empty-state">No routes scheduled for ${today}</div>`;
    return;
  }

  el.innerHTML = routes
    .map((r) => {
      const driverNames = r.assigned_drivers
        ? r.assigned_drivers.map((d) => d.name).join(", ")
        : "No driver assigned";
      const stopsCount = r.stops_count || r.stops?.length || 0;

      return `
      <div class="van-status-item">
        <div>
          <div class="van-plate">${r.name}</div>
          <div class="van-driver">
            ⏰ ${r.start_time} – ${r.end_time}
            ${driverNames ? " · 👤 " + driverNames : ""}
          </div>
        </div>
        <div class="van-status-badge active">${stopsCount} stops</div>
      </div>
    `;
    })
    .join("");
}

// ── Refresh ──────────────────────────────────────────────────────

async function refreshTracking() {
  await updateAll();
  const btn = document.getElementById("refresh-btn");
  const orig = btn.innerHTML;
  btn.innerHTML = '<span class="icon">✓</span> Updated';
  setTimeout(() => {
    btn.innerHTML = orig;
  }, 2000);
}

// ── Auto-refresh ─────────────────────────────────────────────────

let autoRefreshInterval = null;

document
  .getElementById("auto-refresh-toggle")
  ?.addEventListener("change", (e) => {
    if (e.target.checked) {
      autoRefreshInterval = setInterval(updateAll, 30000);
    } else {
      clearInterval(autoRefreshInterval);
      autoRefreshInterval = null;
    }
  });

// ── Init ─────────────────────────────────────────────────────────

(async () => {
  await updateAll();
  autoRefreshInterval = setInterval(updateAll, 30000);
})();
