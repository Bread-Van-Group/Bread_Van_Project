// ============================================
// OWNER LIVE TRACKING - FIXED VERSION
// ============================================

const socket = io();

var vanSVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640">
  <path d="M96 128C60.7 128 32 156.7 32 192L32 400C32 435.3 60.7 464 96 464L96.4 464C100.4 508.9 138.1 544 184 544C229.9 544 267.6 508.9 271.6 464L376.3 464C380.3 508.9 418 544 463.9 544C510 544 547.8 508.6 551.6 463.5C583.3 459.7 607.9 432.7 607.9 400L607.9 298.7C607.9 284.9 603.4 271.4 595.1 260.3L515.1 153.6C503.1 137.5 484.1 128 464 128L96 128zM536 288L416 288L416 192L464 192L536 288zM96 288L96 192L192 192L192 288L96 288zM256 288L256 192L352 192L352 288L256 288zM424 456C424 433.9 441.9 416 464 416C486.1 416 504 433.9 504 456C504 478.1 486.1 496 464 496C441.9 496 424 478.1 424 456zM184 416C206.1 416 224 433.9 224 456C224 478.1 206.1 496 184 496C161.9 496 144 478.1 144 456C144 433.9 161.9 416 184 416z"/>
</svg>`;

let vanMarkers = {};
let hasInitialized = false;

function createVanIcon(isActive) {
  return L.divIcon({
    html: vanSVG,
    iconSize: [40, 40],
    className: isActive ? 'van-icon' : 'van-icon van-icon-inactive',
    popupAnchor: [0, -20]
  });
}

// Map initialization
var map = L.map("tracking-map", {
  center: [10.64179, -61.400861],
  zoom: 14,
  maxZoom: 18,
  scrollWheelZoom: true,
});

L.tileLayer("https://tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 18,
  attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
}).addTo(map);

// ── Fetch helpers ────────────────────────────────────────────────

async function fetchVans() {
  try {
    const res = await fetch("/api/owner/vans/tracking");
    if (!res.ok) {
      console.error("Failed to fetch vans:", res.status);
      return [];
    }
    const data = await res.json();
    console.log("Fetched vans:", data);
    return data;
  } catch (e) {
    console.error("Error fetching vans:", e);
    return [];
  }
}

async function fetchTodayRoutes() {
  try {
    const res = await fetch("/api/owner/routes");
    if (!res.ok) {
      console.error("Failed to fetch routes:", res.status);
      return [];
    }
    const allRoutes = await res.json();
    console.log("Fetched all routes:", allRoutes);

    // Filter for today's day of week
    const today = new Date().toLocaleDateString('en-US', { weekday: 'long' });
    const todayRoutes = allRoutes.filter(r => r.day_of_week === today);
    console.log(`Today is ${today}, found ${todayRoutes.length} routes`);

    return todayRoutes;
  } catch (e) {
    console.error("Error fetching routes:", e);
    return [];
  }
}

// ── Update UI ────────────────────────────────────────────────────

async function updateAll() {
  console.log("Updating all data...");
  const [vans, todayRoutes] = await Promise.all([fetchVans(), fetchTodayRoutes()]);

  updateStats(vans, todayRoutes);
  updateMapMarkers(vans);
  updateVanStatusList(vans);
  updateTodayRoutesList(todayRoutes);
}

function updateStats(vans, todayRoutes) {
  console.log("Updating stats...", { vans: vans.length, routes: todayRoutes.length });

  // Active vans = status active
  const activeVansCount = vans.filter(v => v.status === 'active').length;
  document.getElementById('active-vans').textContent = activeVansCount;

  // Routes today
  document.getElementById('active-routes').textContent = todayRoutes.length;

  // Active drivers = vans with a driver assigned
  const activeDriversCount = vans.filter(v => v.current_driver_id).length;
  document.getElementById('active-drivers').textContent = activeDriversCount;

  // Total items - placeholder for now
  document.getElementById('total-inventory').textContent = '—';
}

function updateMapMarkers(vans) {
  console.log("Updating map markers...");
  const vansWithGPS = vans.filter(v => v.current_lat && v.current_lng);
  console.log(`${vansWithGPS.length} vans have GPS data`);

  vansWithGPS.forEach(van => {
    const isActive = van.status === 'active';
    const icon = createVanIcon(isActive);
    const latlng = [van.current_lat, van.current_lng];

    const popupContent = `
      <div style="font-family:'Caveat Brush',cursive; min-width:160px;">
        <div style="font-size:1.2rem;font-weight:bold;color:#e07b39;margin-bottom:6px;">
          ${van.license_plate}
        </div>
        <div style="font-family:'Shadows Into Light Two',cursive;font-size:0.95rem;color:#2a1a0e;">
          <div>👤 ${van.current_driver_name || 'No driver'}</div>
          <div>📡 ${van.status || 'unknown'}</div>
          <div style="color:#7a5a3e;font-size:0.85rem;margin-top:4px;">
            Updated: ${van.last_location_update
              ? new Date(van.last_location_update).toLocaleTimeString()
              : 'Never'}
          </div>
        </div>
      </div>`;

    if (vanMarkers[van.van_id]) {
      // Update existing marker
      vanMarkers[van.van_id].setLatLng(latlng);
      vanMarkers[van.van_id].setIcon(icon);
      vanMarkers[van.van_id].getPopup().setContent(popupContent);
    } else {
      // Create new marker
      const marker = L.marker(latlng, { icon }).addTo(map);
      marker.bindPopup(popupContent);
      vanMarkers[van.van_id] = marker;
      console.log(`Created marker for van ${van.van_id} at`, latlng);
    }
  });

  // Remove markers for vans that lost GPS
  Object.keys(vanMarkers).forEach(id => {
    if (!vansWithGPS.find(v => v.van_id == id)) {
      map.removeLayer(vanMarkers[id]);
      delete vanMarkers[id];
      console.log(`Removed marker for van ${id}`);
    }
  });

  // Fit map to markers if any exist and first load
  if (vansWithGPS.length > 0 && Object.keys(vanMarkers).length > 0) {
    if (!hasInitialized) {
      const group = L.featureGroup(Object.values(vanMarkers));
      map.fitBounds(group.getBounds().pad(0.3));
      hasInitialized = true;
      console.log("Fitted map to markers");
    }
  } else {
    console.log("No vans with GPS to show on map");
  }
}

function updateVanStatusList(vans) {
  const el = document.getElementById('van-status-list');
  if (!el) return;

  if (vans.length === 0) {
    el.innerHTML = '<div class="empty-state">No vans found</div>';
    return;
  }

  el.innerHTML = vans.map(van => `
    <div class="van-status-item ${van.status === 'active' ? 'active' : ''}">
      <div>
        <div class="van-plate">${van.license_plate}</div>
        <div class="van-driver">${van.current_driver_name || 'No driver assigned'}</div>
      </div>
      <div class="van-status-badge ${van.status || 'inactive'}">${van.status || 'inactive'}</div>
    </div>
  `).join('');
}

function updateTodayRoutesList(routes) {
  const el = document.getElementById('today-routes-list');
  if (!el) return;

  if (routes.length === 0) {
    const today = new Date().toLocaleDateString('en-US', { weekday: 'long' });
    el.innerHTML = `<div class="empty-state">No routes scheduled for ${today}</div>`;
    return;
  }

  el.innerHTML = routes.map(r => {
    // Get assigned drivers from driver_routes if available
    const driverNames = r.assigned_drivers ? r.assigned_drivers.map(d => d.name).join(', ') : 'No driver assigned';
    const stopsCount = r.stops_count || r.stops?.length || 0;

    return `
      <div class="van-status-item">
        <div>
          <div class="van-plate">${r.name}</div>
          <div class="van-driver">
            ⏰ ${r.start_time} – ${r.end_time}
            ${driverNames ? ' · 👤 ' + driverNames : ''}
          </div>
        </div>
        <div class="van-status-badge active">${stopsCount} stops</div>
      </div>
    `;
  }).join('');
}

// ── Refresh ──────────────────────────────────────────────────────

async function refreshTracking() {
  console.log("Manual refresh triggered");
  await updateAll();
  const btn = document.getElementById('refresh-btn');
  const orig = btn.innerHTML;
  btn.innerHTML = '<span class="icon">✓</span> Updated';
  setTimeout(() => { btn.innerHTML = orig; }, 2000);
}

// ── Auto-refresh ─────────────────────────────────────────────────

let autoRefreshInterval = null;

document.getElementById('auto-refresh-toggle')?.addEventListener('change', e => {
  if (e.target.checked) {
    console.log("Auto-refresh enabled");
    autoRefreshInterval = setInterval(updateAll, 30000);
  } else {
    console.log("Auto-refresh disabled");
    clearInterval(autoRefreshInterval);
    autoRefreshInterval = null;
  }
});

// ── Init ─────────────────────────────────────────────────────────

(async () => {
  console.log("Initializing live tracking...");
  await updateAll();
  autoRefreshInterval = setInterval(updateAll, 30000);
  console.log("Live tracking initialized, auto-refresh every 30s");
})();

// WebSocket live updates
socket.on('van_location_update', data => {
  console.log("WebSocket: van location update", data);
  if (vanMarkers[data.van_id]) {
    vanMarkers[data.van_id].setLatLng([data.lat, data.lng]);
  }
});