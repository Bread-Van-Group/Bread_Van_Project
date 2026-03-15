let map;
let routes = [];
let selectedRoute = null;
let routePolylines = [];
let stops = []; // Array of {lat, lng, order} objects
let stopMarkers = []; // Array of marker objects
let activeRoutingControl = null;
let isSelectingLocation = false;
let isEditing = false;

// Icons
let numberIcons = {}; // Cache for numbered markers
function createNumberedIcon(number) {
  if (!numberIcons[number]) {
    // Create custom icon with number

    const html = `<div class="numbered-marker-inner">${number}</div>`;
    numberIcons[number] = L.divIcon({
      html: html,
      className: 'numbered-marker',
      iconSize: [32, 32],
      iconAnchor: [16, 32],
      popupAnchor: [0, -32]
    });
  }
  return numberIcons[number];
}

// Routing
function buildRoutingPath() {
  clearRoutingPath();
  if (stops.length < 2) return;

  const waypoints = stops.map(s => L.latLng(s.lat, s.lng));
  activeRoutingControl = L.Routing.control({
    waypoints: waypoints,
    show: false,
    addWaypoints: false,
    draggableWaypoints: false,
    fitSelectedRoutes: true,
    createMarker: () => null, // We create our own markers
    lineOptions: {
      styles: [{ className: 'route-path-line' }]
    }
  }).addTo(map);
}

function clearRoutingPath() {
  if (activeRoutingControl) {
    map.removeControl(activeRoutingControl);
    activeRoutingControl = null;
  }
}

function clearMap() {
  clearRoutingPath();
  routePolylines.forEach(l => map.removeLayer(l));
  routePolylines = [];
  stopMarkers.forEach(m => map.removeLayer(m));
  stopMarkers = [];
  map.eachLayer(layer => {
    if (layer instanceof L.Marker) map.removeLayer(layer);
  });
}

// Map init
function initMap() {
  map = L.map('map').setView([10.6409, -61.3953], 13);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors',
    maxZoom: 19
  }).addTo(map);
  map.on('click', handleMapClick);
}

// Custom dropdown
function initDayDropdown() {
  const wrapper = document.getElementById('day-select');
  const trigger = document.getElementById('day-select-trigger');
  const menu = document.getElementById('day-select-menu');
  const label = document.getElementById('day-select-label');
  const hidden = document.getElementById('route-day');

  trigger.addEventListener('click', e => {
    e.stopPropagation();
    const open = wrapper.classList.toggle('open');
    trigger.setAttribute('aria-expanded', open);
  });

  menu.querySelectorAll('li').forEach(li => {
    li.addEventListener('click', () => {
      menu.querySelectorAll('li').forEach(x => x.classList.remove('selected'));
      li.classList.add('selected');
      label.textContent = li.dataset.value;
      hidden.value = li.dataset.value;
      wrapper.classList.remove('open');
      trigger.setAttribute('aria-expanded', false);
    });
  });

  document.addEventListener('click', e => {
    if (!wrapper.contains(e.target)) {
      wrapper.classList.remove('open');
      trigger.setAttribute('aria-expanded', false);
    }
  });
}

function setDropdownValue(value) {
  const menu = document.getElementById('day-select-menu');
  const label = document.getElementById('day-select-label');
  const hidden = document.getElementById('route-day');
  menu.querySelectorAll('li').forEach(li => {
    li.classList.toggle('selected', li.dataset.value === value);
  });
  label.textContent = value;
  hidden.value = value;
}

// Map hint
function updateMapHint() {
  const hint = document.getElementById('map-selection-hint');
  if (!isSelectingLocation) {
    hint.style.display = 'none';
    return;
  }
  hint.style.display = 'block';
  hint.textContent = `📍 Click map to add Stop `;
  hint.style.borderColor = '#0077be';
  hint.style.background = 'rgba(0,119,190,0.12)';
  hint.style.color = '#014361';
}

// Render stop markers
function renderStops() {
  // Clear existing markers
  stopMarkers.forEach(m => map.removeLayer(m));
  stopMarkers = [];

  // Create numbered markers for each stop
  stops.forEach((stop, index) => {
    const marker = L.marker([stop.lat, stop.lng], {
      icon: createNumberedIcon(index + 1)
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

  // Update routing
  buildRoutingPath();

  // Update stops list display
  updateStopsList();
}

function updateStopsList() {
  const container = document.getElementById('stops-list-container');
  if (stops.length === 0) {
    container.innerHTML = '<div class="loc-text">No stops added yet. Click the map to add stops.</div>';
    return;
  }

  let html = '';
  stops.forEach((stop, index) => {
    html += `
      <div class="location-row">
        <span class="loc-dot" style="background: #0077be;">${index + 1}</span>
        <div class="loc-text set">Stop #${index + 1}: (${stop.lat.toFixed(4)}, ${stop.lng.toFixed(4)})</div>
        <button class="loc-reset-btn" onclick="removeStop(${index})">Remove</button>
      </div>
    `;
  });
  container.innerHTML = html;
}

// Map click - add stop
function handleMapClick(e) {
  if (!isSelectingLocation) return;
  const { lat, lng } = e.latlng;

  // Add stop to array
  stops.push({ lat, lng, order: stops.length });

  // Render all stops
  renderStops();
  updateMapHint();
}

function removeStop(index) {
  stops.splice(index, 1);
  // Reorder remaining stops
  stops.forEach((stop, idx) => {
    stop.order = idx;
  });
  renderStops();

  // Close any open popups
  map.closePopup();
}

function clearAllStops() {
  stops = [];
  renderStops();
}

function stopSelecting() {
  isSelectingLocation = false;
  document.getElementById('map').classList.remove('map-clickable');
  updateMapHint();
}

function startSelecting() {
  isSelectingLocation = true;
  document.getElementById('map').classList.add('map-clickable');
  updateMapHint();
}

// Load routes
async function loadRoutes() {
  try {
    const res = await fetch('/api/owner/routes');
    routes = await res.json();
    renderRoutesList();
  } catch (err) {
    console.error('Failed to load routes:', err);
    document.getElementById('routes-list').innerHTML =
      '<div style="text-align:center;padding:40px;color:#94a3b8;">Failed to load routes</div>';
  }
}

function renderRoutesList() {
  const list = document.getElementById('routes-list');
  if (routes.length === 0) {
    list.innerHTML = '<div style="text-align:center;padding:40px;color:#94a3b8;">No routes yet</div>';
    return;
  }

  list.innerHTML = routes.map(route => `
    <div class="route-card ${selectedRoute && selectedRoute.route_id === route.route_id ? 'active' : ''}"
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
      <span class="route-card-day">${route.day_of_week}</span>
    </div>
  `).join('');
}

// Select route - display on map
async function selectRoute(routeId) {
  selectedRoute = routes.find(r => r.route_id === routeId);
  renderRoutesList();
  clearMap();

  try {
    const res = await fetch(`/api/owner/routes/${routeId}/stops`);
    const stopsData = await res.json();

    if (stopsData.length === 0) {
      alert('This route has no stops yet');
      return;
    }

    // Display stops
    stopsData.forEach((stop, idx) => {
      const marker = L.marker([stop.lat, stop.lng], {
        icon: createNumberedIcon(idx + 1)
      }).addTo(map);
      marker.bindPopup(`<strong>Stop #${idx + 1}</strong><br>${stop.address || ''}`);
      stopMarkers.push(marker);
    });

    // Build route
    const waypoints = stopsData.map(s => L.latLng(s.lat, s.lng));
    if (waypoints.length > 1) {
      activeRoutingControl = L.Routing.control({
        waypoints: waypoints,
        show: false,
        addWaypoints: false,
        draggableWaypoints: false,
        fitSelectedRoutes: true,
        createMarker: () => null,
        lineOptions: {
          styles: [{ className: 'route-path-line' }]
        }
      }).addTo(map);
    } else {
      map.setView([stopsData[0].lat, stopsData[0].lng], 14);
    }
  } catch (err) {
    console.error('Failed to load stops:', err);
  }
}

function viewAllRoutes() {
  selectedRoute = null;
  renderRoutesList();
  clearMap();
  map.setView([10.6409, -61.3953], 13);
}

// Show/hide editor
function showRouteEditor(editing = false) {
  document.getElementById('panel-list-view').style.display = 'none';
  document.getElementById('panel-editor-view').style.display = 'flex';

  isEditing = editing;
  clearAllStops();

  if (editing && selectedRoute) {
    document.getElementById('editor-title').textContent = 'Edit Route';
    document.getElementById('route-name').value = selectedRoute.name;
    setDropdownValue(selectedRoute.day_of_week);
    document.getElementById('route-start-time').value = selectedRoute.start_time;
    document.getElementById('route-end-time').value = selectedRoute.end_time;
    document.getElementById('route-description').value = selectedRoute.description || '';

    // Load existing stops
    loadRouteStopsForEdit(selectedRoute.route_id);
  } else {
    document.getElementById('editor-title').textContent = 'New Route';
    document.getElementById('route-name').value = '';
    setDropdownValue('Monday');
    document.getElementById('route-start-time').value = '06:00';
    document.getElementById('route-end-time').value = '10:00';
    document.getElementById('route-description').value = '';
  }

  startSelecting();
}

async function loadRouteStopsForEdit(routeId) {
  try {
    const res = await fetch(`/api/owner/routes/${routeId}/stops`);
    const stopsData = await res.json();
    stops = stopsData.map((s, idx) => ({
      lat: s.lat,
      lng: s.lng,
      order: idx
    }));
    renderStops();
  } catch (err) {
    console.error('Failed to load stops:', err);
  }
}

function hideRouteEditor() {
  document.getElementById('panel-list-view').style.display = 'flex';
  document.getElementById('panel-editor-view').style.display = 'none';
  stopSelecting();
  clearAllStops();
  clearMap();
  if (selectedRoute) selectRoute(selectedRoute.route_id);
}

function editRoute(routeId) {
  selectedRoute = routes.find(r => r.route_id === routeId);
  showRouteEditor(true);
}

async function deleteRoute(routeId) {
  const route = routes.find(r => r.route_id === routeId);
  if (!confirm(`Delete route "${route.name}"?`)) return;

  try {
    const res = await fetch(`/api/owner/routes/${routeId}`, { method: 'DELETE' });
    if (res.ok) {
      alert('✅ Route deleted');
      await loadRoutes();
      clearMap();
      selectedRoute = null;
    }
  } catch (err) {
    console.error('Failed to delete:', err);
    alert('❌ Failed to delete route');
  }
}

// Save route
async function saveRoute() {
  const name = document.getElementById('route-name').value.trim();
  const day = document.getElementById('route-day').value;
  const startTime = document.getElementById('route-start-time').value;
  const endTime = document.getElementById('route-end-time').value;
  const description = document.getElementById('route-description').value.trim();

  if (!name) {
    alert('Please enter a route name');
    return;
  }

  if (stops.length < 2) {
    alert('Please add at least 2 stops to the route');
    return;
  }

  const routeData = {
    name,
    day_of_week: day,
    start_time: startTime,
    end_time: endTime,
    description,
    stops: stops.map((stop, index) => ({
      lat: stop.lat,
      lng: stop.lng,
      order: index,
      address: '' // You can add address lookup here if needed
    }))
  };

  try {
    const url = isEditing && selectedRoute
      ? `/api/owner/routes/${selectedRoute.route_id}`
      : '/api/owner/routes';

    const res = await fetch(url, {
      method: isEditing && selectedRoute ? 'PUT' : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(routeData)
    });

    if (res.ok) {
      alert('✅ Route saved successfully!');
      hideRouteEditor();
      await loadRoutes();
    } else {
      throw new Error('Save failed');
    }
  } catch (err) {
    console.error('Failed to save route:', err);
    alert('❌ Failed to save route');
  }
}

// Initialize
document.addEventListener('DOMContentLoaded', async () => {
  initMap();
  initDayDropdown();
  await loadRoutes();

  document.getElementById('add-route-btn').addEventListener('click', () => {
    selectedRoute = null;
    showRouteEditor(false);
  });

  document.getElementById('edit-route-btn').addEventListener('click', () => {
    if (selectedRoute) showRouteEditor(true);
  });

  document.getElementById('view-routes-btn').addEventListener('click', viewAllRoutes);
  document.getElementById('save-route-btn').addEventListener('click', saveRoute);
});