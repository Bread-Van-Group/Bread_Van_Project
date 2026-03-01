let map;
let routes               = [];
let selectedRoute        = null;
let routePolylines       = [];
let startMarker          = null;
let endMarker            = null;
let startLocation        = null;
let endLocation          = null;
let isSelectingLocation  = false;
let selectingFor         = null;
let activeRoutingControl = null;
let isEditing            = false;

//  Icons 
let greenIcon, redIcon;
function createIcons() {
  const shadow = 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png';
  const base   = 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img';
  const opts   = { iconSize:[25,41], iconAnchor:[12,41], popupAnchor:[1,-34], shadowSize:[41,41], shadowUrl:shadow };
  greenIcon = L.icon({ ...opts, iconUrl:`${base}/marker-icon-2x-green.png` });
  redIcon   = L.icon({ ...opts, iconUrl:`${base}/marker-icon-2x-red.png` });
}

//  Routing 
function buildRoutingPath(start, end) {
  clearRoutingPath();
  activeRoutingControl = L.Routing.control({
    waypoints: [L.latLng(start.lat, start.lng), L.latLng(end.lat, end.lng)],
    show: false, addWaypoints: false, draggableWaypoints: false,
    fitSelectedRoutes: true, createMarker: () => null,
    lineOptions: { styles: [{ color:'#0077be', weight:5, opacity:0.85 }] }
  }).addTo(map);
}
function clearRoutingPath() {
  if (activeRoutingControl) { map.removeControl(activeRoutingControl); activeRoutingControl = null; }
}
function clearMap() {
  clearRoutingPath();
  routePolylines.forEach(l => map.removeLayer(l)); routePolylines = [];
  map.eachLayer(layer => { if (layer instanceof L.Marker) map.removeLayer(layer); });
}

//  Map init 
function initMap() {
  map = L.map('map').setView([10.6409, -61.3953], 13);
  L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors', maxZoom: 19
  }).addTo(map);
  createIcons();
  map.on('click', handleMapClick);
}

//  Custom dropdown 
function initDayDropdown() {
  const wrapper  = document.getElementById('day-select');
  const trigger  = document.getElementById('day-select-trigger');
  const menu     = document.getElementById('day-select-menu');
  const label    = document.getElementById('day-select-label');
  const hidden   = document.getElementById('route-day');

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
      hidden.value      = li.dataset.value;
      wrapper.classList.remove('open');
      trigger.setAttribute('aria-expanded', false);
    });
  });

  // Close when clicking outside
  document.addEventListener('click', e => {
    if (!wrapper.contains(e.target)) {
      wrapper.classList.remove('open');
      trigger.setAttribute('aria-expanded', false);
    }
  });
}

function setDropdownValue(value) {
  const menu   = document.getElementById('day-select-menu');
  const label  = document.getElementById('day-select-label');
  const hidden = document.getElementById('route-day');
  menu.querySelectorAll('li').forEach(li => {
    li.classList.toggle('selected', li.dataset.value === value);
  });
  label.textContent = value;
  hidden.value      = value;
}

//  Map hint 
function updateMapHint() {
  const hint = document.getElementById('map-selection-hint');
  if (!isSelectingLocation) { hint.style.display = 'none'; return; }
  hint.style.display = 'block';
  if (selectingFor === 'start') {
    hint.textContent = '🟢 Click map to set Start Point';
    Object.assign(hint.style, { borderColor:'#22c55e', background:'rgba(34,197,94,0.12)', color:'#166534' });
  } else {
    hint.textContent = '🔴 Click map to set End Point';
    Object.assign(hint.style, { borderColor:'#ef4444', background:'rgba(239,68,68,0.12)', color:'#991b1b' });
  }
}

//  Map click 
function handleMapClick(e) {
  if (!isSelectingLocation) return;
  const { lat, lng } = e.latlng;

  if (selectingFor === 'start') {
    if (startMarker) map.removeLayer(startMarker);
    startMarker   = L.marker([lat, lng], { icon: greenIcon }).addTo(map).bindPopup('<strong>Start</strong>').openPopup();
    startLocation = { lat, lng };
    setLocDisplay('start', lat, lng);
    selectingFor  = endLocation ? null : 'end';
    if (!selectingFor) stopSelecting();

  } else if (selectingFor === 'end') {
    if (endMarker) map.removeLayer(endMarker);
    endMarker   = L.marker([lat, lng], { icon: redIcon }).addTo(map).bindPopup('<strong>End</strong>').openPopup();
    endLocation = { lat, lng };
    setLocDisplay('end', lat, lng);
    selectingFor = startLocation ? null : 'start';
    if (!selectingFor) stopSelecting();
  }

  if (startLocation && endLocation) buildRoutingPath(startLocation, endLocation);
  updateMapHint();
}

function stopSelecting() {
  isSelectingLocation = false;
  document.getElementById('map').classList.remove('map-clickable');
}

function setLocDisplay(which, lat, lng) {
  const textEl  = document.getElementById(`${which}-location`);
  const resetEl = document.getElementById(`${which}-reset-btn`);
  textEl.textContent = `(${lat.toFixed(4)}, ${lng.toFixed(4)})`;
  textEl.classList.add('set');
  resetEl.style.display = 'inline-block';
}

function clearLocDisplay(which) {
  const textEl  = document.getElementById(`${which}-location`);
  const resetEl = document.getElementById(`${which}-reset-btn`);
  textEl.textContent = 'Click map to set';
  textEl.classList.remove('set');
  resetEl.style.display = 'none';
}

function resetPoint(which) {
  if (which === 'start') {
    if (startMarker) { map.removeLayer(startMarker); startMarker = null; }
    startLocation = null;
    clearLocDisplay('start');
  } else {
    if (endMarker) { map.removeLayer(endMarker); endMarker = null; }
    endLocation = null;
    clearLocDisplay('end');
  }
  clearRoutingPath();
  isSelectingLocation = true;
  selectingFor = which;
  document.getElementById('map').classList.add('map-clickable');
  updateMapHint();
}

function setSelecting(which) {
  isSelectingLocation = true;
  selectingFor = which;
  document.getElementById('map').classList.add('map-clickable');
  updateMapHint();
}

//  Panel switching 
function showEditorPanel() {
  document.getElementById('panel-list-view').style.display   = 'none';
  document.getElementById('panel-editor-view').style.display = 'flex';
}
function showListPanel() {
  document.getElementById('panel-editor-view').style.display = 'none';
  document.getElementById('panel-list-view').style.display   = 'flex';
}

// Load & render routes
async function loadRoutes() {
  try {
    const res = await fetch('/api/owner/routes');
    routes = await res.json();
    renderRoutesList();
  } catch (err) {
    console.error('Failed to load routes:', err);
    document.getElementById('routes-list').innerHTML =
      '<div style="text-align:center;padding:40px;color:#e74c3c;">Failed to load routes</div>';
  }
}

function renderRoutesList() {
  const list = document.getElementById('routes-list');
  if (!routes.length) {
    list.innerHTML = '<div style="text-align:center;padding:40px;color:#94a3b8;">No routes yet. Click "+ Add Route" to create one.</div>';
    return;
  }
  list.innerHTML = routes.map(r => `
    <div class="route-card ${selectedRoute?.route_id === r.route_id ? 'active' : ''}"
         onclick="selectRoute(${r.route_id})">
      <div class="route-card-header">
        <div class="route-card-name">${r.name}</div>
        <div class="route-card-actions">
          <button class="route-edit-btn" onclick="event.stopPropagation(); openEditEditor(${r.route_id})" title="Edit">&#9998;</button>
          <button class="route-delete-btn" onclick="event.stopPropagation(); deleteRoute(${r.route_id}, '${r.name.replace(/'/g, "\\'")}')" title="Delete">&#128465;</button>
        </div>
      </div>
      <div class="route-card-detail">&#9200; ${r.start_time} – ${r.end_time}</div>
      <div class="route-card-detail">&#128205; ${r.stops_count ?? 0} stops</div>
      <span class="route-card-day">${r.day_of_week}</span>
    </div>
  `).join('');
}

// Select route and view on map
async function selectRoute(routeId) {
  selectedRoute = routes.find(r => r.route_id === routeId);
  renderRoutesList();
  clearMap();

  const editBtn = document.getElementById('edit-route-btn');
  if (editBtn) editBtn.style.display = 'inline-block';

  try {
    const res   = await fetch(`/api/owner/routes/${routeId}/stops`);
    const stops = await res.json();
    if (!stops?.length) { showNoStopsHint(); return; }

    stops.sort((a, b) => a.stop_order - b.stop_order);
    const first = stops[0], last = stops[stops.length - 1];

    L.marker([first.lat, first.lng], { icon: greenIcon }).addTo(map).bindPopup('<strong>Start</strong>');
    if (stops.length > 1) {
      L.marker([last.lat, last.lng], { icon: redIcon }).addTo(map).bindPopup('<strong>End</strong>');
      buildRoutingPath({ lat:first.lat, lng:first.lng }, { lat:last.lat, lng:last.lng });
    } else {
      map.setView([first.lat, first.lng], 14);
    }
  } catch (err) { console.error('Failed to load stops:', err); }
}

function showNoStopsHint() {
  const hint = document.getElementById('map-selection-hint');
  hint.textContent = 'No location data — click ✎ Edit Route to set start & end points.';
  Object.assign(hint.style, { borderColor:'#f59e0b', background:'rgba(245,158,11,0.12)', color:'#92400e', display:'block', pointerEvents:'none' });
  setTimeout(() => { hint.style.display = 'none'; }, 5000);
}

function viewAllRoutes() {
  selectedRoute = null;
  renderRoutesList();
  clearMap();
  const editBtn = document.getElementById('edit-route-btn');
  if (editBtn) editBtn.style.display = 'none';
  map.setView([10.6409, -61.3953], 13);
}

// Open mapeditor 
function resetEditorFields() {
  // Clear markers & path
  if (startMarker) { map.removeLayer(startMarker); startMarker = null; }
  if (endMarker)   { map.removeLayer(endMarker);   endMarker   = null; }
  clearRoutingPath();
  startLocation = null;
  endLocation   = null;
  clearLocDisplay('start');
  clearLocDisplay('end');
  isSelectingLocation = false;
  selectingFor = null;
  document.getElementById('map').classList.remove('map-clickable');
  updateMapHint();
}

async function openEditEditor(routeId) {
  selectedRoute = routes.find(r => r.route_id === routeId);
  renderRoutesList();
  await showRouteEditor(true);
}

async function showRouteEditor(editing = false) {
  isEditing = editing;
  resetEditorFields();

  if (editing && selectedRoute) {
    document.getElementById('editor-title').textContent     = 'Edit Route';
    document.getElementById('route-name').value             = selectedRoute.name;
    document.getElementById('route-start-time').value       = selectedRoute.start_time;
    document.getElementById('route-end-time').value         = selectedRoute.end_time;
    document.getElementById('route-description').value      = selectedRoute.description || '';
    setDropdownValue(selectedRoute.day_of_week);
    await loadExistingEndpointsIntoEditor(selectedRoute.route_id);
  } else {
    document.getElementById('editor-title').textContent     = 'New Route';
    document.getElementById('route-name').value             = '';
    document.getElementById('route-start-time').value       = '06:00';
    document.getElementById('route-end-time').value         = '10:00';
    document.getElementById('route-description').value      = '';
    setDropdownValue('Monday');

    // Immediately enter selection mode
    isSelectingLocation = true;
    selectingFor = 'start';
    document.getElementById('map').classList.add('map-clickable');
    updateMapHint();
  }

  showEditorPanel();
}

async function loadExistingEndpointsIntoEditor(routeId) {
  try {
    const res   = await fetch(`/api/owner/routes/${routeId}/stops`);
    const stops = await res.json();

    if (!stops?.length) {
      isSelectingLocation = true; selectingFor = 'start';
      document.getElementById('map').classList.add('map-clickable');
      updateMapHint(); return;
    }

    stops.sort((a, b) => a.stop_order - b.stop_order);
    const first = stops[0], last = stops[stops.length - 1];

    startLocation = { lat:first.lat, lng:first.lng };
    startMarker   = L.marker([first.lat, first.lng], { icon:greenIcon }).addTo(map).bindPopup('<strong>Start</strong>').openPopup();
    setLocDisplay('start', first.lat, first.lng);

    if (stops.length > 1) {
      endLocation = { lat:last.lat, lng:last.lng };
      endMarker   = L.marker([last.lat, last.lng], { icon:redIcon }).addTo(map).bindPopup('<strong>End</strong>');
      setLocDisplay('end', last.lat, last.lng);
      buildRoutingPath(startLocation, endLocation);
    }

    isSelectingLocation = true; selectingFor = 'start';
    document.getElementById('map').classList.add('map-clickable');
    updateMapHint();
  } catch (err) {
    console.error('Could not load stops for editing:', err);
    isSelectingLocation = true; selectingFor = 'start';
    document.getElementById('map').classList.add('map-clickable');
    updateMapHint();
  }
}

function hideRouteEditor() {
  resetEditorFields();
  showListPanel();
  isEditing = false;
}

//Save route
async function saveRoute() {
  const name        = document.getElementById('route-name').value.trim();
  const day         = document.getElementById('route-day').value;
  const startTime   = document.getElementById('route-start-time').value;
  const endTime     = document.getElementById('route-end-time').value;
  const description = document.getElementById('route-description').value.trim();

  if (!name)                           { alert('Please enter a route name'); return; }
  if (!startLocation || !endLocation)  { alert('Please set both start and end locations on the map'); return; }

  const url    = isEditing ? `/api/owner/routes/${selectedRoute.route_id}` : '/api/owner/routes';
  const method = isEditing ? 'PUT' : 'POST';

  try {
    const res = await fetch(url, {
      method, headers: { 'Content-Type':'application/json' },
      body: JSON.stringify({ name, day_of_week:day, start_time:startTime, end_time:endTime, description })
    });
    if (!res.ok) throw new Error(`${res.status}: ${await res.text().catch(()=>'')}`);

    let routeId = isEditing ? selectedRoute.route_id : null;
    if (!routeId) {
      try { const b = await res.clone().json(); routeId = b?.route_id ?? b?.id ?? null; } catch(_){}
      if (!routeId) { await loadRoutes(); routeId = routes[routes.length-1]?.route_id ?? null; }
    }
    if (!routeId) { alert('Route saved but could not store location data.'); hideRouteEditor(); await loadRoutes(); return; }

    await replaceRouteEndpoints(routeId, startLocation, endLocation);

    hideRouteEditor();
    await loadRoutes();
    await selectRoute(routeId);

  } catch (err) {
    console.error('Save failed:', err);
    alert(`Failed to save route\n${err.message}`);
  }
}

async function replaceRouteEndpoints(routeId, start, end) {
  try {
    const res   = await fetch(`/api/owner/routes/${routeId}/stops`);
    const stops = await res.json();
    await Promise.all(
      stops.filter(s => s.stop_order === 0 || s.stop_order === 1)
           .map(s => fetch(`/api/owner/routes/${routeId}/stops/${s.stop_id}`, { method:'DELETE' }).catch(()=>{}))
    );
  } catch(_){}

  for (const stop of [
    { lat:start.lat, lng:start.lng, address:'Start', stop_order:0, estimated_arrival_time:null },
    { lat:end.lat,   lng:end.lng,   address:'End',   stop_order:1, estimated_arrival_time:null }
  ]) {
    try {
      const r = await fetch(`/api/owner/routes/${routeId}/stops`, {
        method:'POST', headers:{ 'Content-Type':'application/json' }, body: JSON.stringify(stop)
      });
      if (!r.ok) console.warn('Stop save failed:', r.status);
    } catch(err) { console.warn('Stop error:', err); }
  }
}

//  Delete route 
async function deleteRoute(routeId, routeName) {
  if (!confirm(`Delete route "${routeName}"?\n\nThis will permanently remove the route and all its stops.`)) return;

  try {
    const res = await fetch(`/api/owner/routes/${routeId}`, { method: 'DELETE' });
    if (!res.ok) throw new Error(`${res.status}: ${await res.text().catch(() => '')}`);

    // If the deleted route was selected, clear the map
    if (selectedRoute?.route_id === routeId) {
      selectedRoute = null;
      clearMap();
      const editBtn = document.getElementById('edit-route-btn');
      if (editBtn) editBtn.style.display = 'none';
    }

    await loadRoutes();
  } catch (err) {
    console.error('Delete failed:', err);
    alert(`Failed to delete route\n${err.message}`);
  }
}

// Init 
document.addEventListener('DOMContentLoaded', async () => {
  initMap();
  initDayDropdown();
  await loadRoutes();

  document.getElementById('add-route-btn').addEventListener('click', () => {
    selectedRoute = null; showRouteEditor(false);
  });
  document.getElementById('edit-route-btn').addEventListener('click', () => {
    if (selectedRoute) showRouteEditor(true);
  });
  document.getElementById('view-routes-btn').addEventListener('click', viewAllRoutes);
  document.getElementById('save-route-btn').addEventListener('click', saveRoute);
});