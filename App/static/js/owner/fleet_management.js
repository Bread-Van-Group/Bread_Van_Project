// ============================================
// FLEET MANAGEMENT - Driver & Van Management
// ============================================

let drivers = [];
let vans = [];

// ── Data loading ────────────────────────────────────────────────

async function loadAll() {
  await Promise.all([loadDrivers(), loadVans()]);
}

async function loadDrivers() {
  try {
    const res = await fetch('/api/owner/drivers');
    if (!res.ok) throw new Error('Failed');
    drivers = await res.json();
    renderDriversList();
    refreshQuickAssignDropdowns();
  } catch (error) {
    console.error('Error loading drivers:', error);
    document.getElementById('drivers-list').innerHTML =
      '<div class="empty-state">Failed to load drivers</div>';
  }
}

async function loadVans() {
  try {
    const res = await fetch('/api/owner/vans');
    if (!res.ok) throw new Error('Failed');
    vans = await res.json();
    renderVansList();
    refreshQuickAssignDropdowns();
  } catch (error) {
    console.error('Error loading vans:', error);
    document.getElementById('vans-list').innerHTML =
      '<div class="empty-state">Failed to load vans</div>';
  }
}

// ── Render lists ────────────────────────────────────────────────

function renderDriversList() {
  const container = document.getElementById('drivers-list');
  if (drivers.length === 0) {
    container.innerHTML = '<div class="empty-state">No drivers yet. Add one above!</div>';
    return;
  }
  container.innerHTML = drivers.map(driver => `
    <div class="fleet-item">
      <div class="fleet-item-header">
        <div class="fleet-item-title">${driver.name}</div>
        <div class="fleet-item-badge ${driver.assigned_van_id ? 'active' : 'inactive'}">
          ${driver.assigned_van_id ? 'Assigned' : 'Unassigned'}
        </div>
      </div>
      <div class="fleet-item-details">
        <div class="detail-row">
          <span class="detail-label">Email:</span>
          <span class="detail-value">${driver.email}</span>
        </div>
        ${driver.phone ? `
        <div class="detail-row">
          <span class="detail-label">Phone:</span>
          <span class="detail-value">${driver.phone}</span>
        </div>` : ''}
        ${driver.assigned_van_plate ? `
        <div class="detail-row">
          <span class="detail-label">Van:</span>
          <span class="detail-value">${driver.assigned_van_plate}</span>
        </div>` : ''}
      </div>
    </div>
  `).join('');
}

function renderVansList() {
  const container = document.getElementById('vans-list');
  if (vans.length === 0) {
    container.innerHTML = '<div class="empty-state">No vans yet. Add one above!</div>';
    return;
  }
  container.innerHTML = vans.map(van => `
    <div class="fleet-item">
      <div class="fleet-item-header">
        <div class="fleet-item-title">${van.license_plate}</div>
        <div class="fleet-item-badge ${van.current_driver_id ? 'active' : 'inactive'}">
          ${van.current_driver_id ? 'In Use' : 'Available'}
        </div>
      </div>
      <div class="fleet-item-details">
        ${van.current_driver_name ? `
        <div class="detail-row">
          <span class="detail-label">Driver:</span>
          <span class="detail-value">${van.current_driver_name}</span>
        </div>` : ''}
        <div class="detail-row">
          <span class="detail-label">Status:</span>
          <span class="detail-value">${van.status || 'Inactive'}</span>
        </div>
      </div>
      <div class="fleet-item-actions">
        ${van.current_driver_id ? `
          <button class="action-btn remove-btn" onclick="unassignDriver(${van.van_id})">
            Unassign Driver
          </button>
        ` : `
          <button class="action-btn assign-btn-small" onclick="showAssignModal(${van.van_id})">
            Assign Driver
          </button>
        `}
      </div>
    </div>
  `).join('');
}

// ── Custom dropdowns ────────────────────────────────────────────

function initQuickAssignDropdowns() {
  initCustomDropdown({
    wrapperId:  'qa-driver-select',
    triggerId:  'qa-driver-trigger',
    labelId:    'qa-driver-label',
    menuId:     'qa-driver-menu',
    hiddenId:   'assign-driver-select',
    placeholder: '-- Select Driver --',
  });

  initCustomDropdown({
    wrapperId:  'qa-van-select',
    triggerId:  'qa-van-trigger',
    labelId:    'qa-van-label',
    menuId:     'qa-van-menu',
    hiddenId:   'assign-van-select',
    placeholder: '-- Select Van --',
  });
}

function initCustomDropdown({ wrapperId, triggerId, menuId, placeholder }) {
  const wrapper = document.getElementById(wrapperId);
  const trigger = document.getElementById(triggerId);
  if (!wrapper || !trigger) return;

  trigger.addEventListener('click', e => {
    e.stopPropagation();
    // Close all other open dropdowns first
    document.querySelectorAll('.custom-select.open').forEach(el => {
      if (el !== wrapper) el.classList.remove('open');
    });
    const open = wrapper.classList.toggle('open');
    trigger.setAttribute('aria-expanded', open);
  });

  document.addEventListener('click', e => {
    if (!wrapper.contains(e.target)) {
      wrapper.classList.remove('open');
      trigger.setAttribute('aria-expanded', false);
    }
  });
}

function refreshQuickAssignDropdowns() {
  populateDropdown({
    menuId:      'qa-driver-menu',
    labelId:     'qa-driver-label',
    hiddenId:    'assign-driver-select',
    placeholder: '-- Select Driver --',
    items: drivers.filter(d => !d.assigned_van_id).map(d => ({
      value: String(d.driver_id),
      label: d.name,
    })),
  });

  populateDropdown({
    menuId:      'qa-van-menu',
    labelId:     'qa-van-label',
    hiddenId:    'assign-van-select',
    placeholder: '-- Select Van --',
    items: vans.filter(v => !v.current_driver_id).map(v => ({
      value: String(v.van_id),
      label: v.license_plate,
    })),
  });
}

function populateDropdown({ menuId, labelId, hiddenId, placeholder, items }) {
  const menu   = document.getElementById(menuId);
  const label  = document.getElementById(labelId);
  const hidden = document.getElementById(hiddenId);
  if (!menu) return;

  // Reset label/value
  if (label)  label.textContent = placeholder;
  if (hidden) hidden.value = '';

  // Build items
  menu.innerHTML = `<li data-value="">${placeholder}</li>` +
    items.map(item => `<li data-value="${item.value}">${item.label}</li>`).join('');

  // Bind click handlers
  menu.querySelectorAll('li').forEach(li => {
    li.addEventListener('click', () => {
      menu.querySelectorAll('li').forEach(x => x.classList.remove('selected'));
      li.classList.add('selected');
      if (label)  label.textContent = li.textContent;
      if (hidden) hidden.value = li.dataset.value;
      // Close
      const wrapper = menu.closest('.custom-select');
      if (wrapper) {
        wrapper.classList.remove('open');
        wrapper.querySelector('.custom-select-trigger')
               ?.setAttribute('aria-expanded', false);
      }
    });
  });
}

// ── Quick assign ────────────────────────────────────────────────

async function quickAssign() {
  const driverId = document.getElementById('assign-driver-select').value;
  const vanId    = document.getElementById('assign-van-select').value;

  if (!driverId || !vanId) {
    alert('Please select both a driver and a van');
    return;
  }

  try {
    const res = await fetch(`/api/owner/vans/${vanId}/assign-driver`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ driver_id: parseInt(driverId) })
    });

    if (res.ok) {
      await loadAll();
    } else {
      alert('Failed to assign driver');
    }
  } catch (error) {
    console.error('Error assigning driver:', error);
    alert('Error assigning driver');
  }
}

// ── Unassign driver ─────────────────────────────────────────────

async function unassignDriver(vanId) {
  if (!confirm('Unassign driver from this van?')) return;

  try {
    const res = await fetch(`/api/owner/vans/${vanId}/unassign-driver`, {
      method: 'POST'
    });

    if (res.ok) {
      await loadAll();
    } else {
      alert('Failed to unassign driver');
    }
  } catch (error) {
    console.error('Error unassigning driver:', error);
  }
}

// ── Driver modal ────────────────────────────────────────────────

function showDriverModal() {
  document.getElementById('driver-modal').style.display = 'flex';
}

function hideDriverModal() {
  document.getElementById('driver-modal').style.display = 'none';
  ['driver-name','driver-email','driver-password','driver-phone','driver-address']
    .forEach(id => { document.getElementById(id).value = ''; });
}

async function saveDriver() {
  const data = {
    name:     document.getElementById('driver-name').value.trim(),
    email:    document.getElementById('driver-email').value.trim(),
    password: document.getElementById('driver-password').value,
    phone:    document.getElementById('driver-phone').value.trim(),
    address:  document.getElementById('driver-address').value.trim(),
  };

  if (!data.name || !data.email || !data.password) {
    alert('Please fill in all required fields');
    return;
  }

  try {
    const res = await fetch('/api/owner/drivers', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    if (res.ok) {
      hideDriverModal();
      await loadAll();
    } else {
      const err = await res.json().catch(() => ({}));
      alert(err.message || `Failed to add driver (${res.status})`);
    }
  } catch (error) {
    console.error('Error adding driver:', error);
    alert('Network error — could not reach server');
  }
}

// ── Van modal ───────────────────────────────────────────────────

function showVanModal() {
  document.getElementById('van-modal').style.display = 'flex';
}

function hideVanModal() {
  document.getElementById('van-modal').style.display = 'none';
  ['van-license-plate','van-model'].forEach(id => {
    document.getElementById(id).value = '';
  });
}

async function saveVan() {
  const data = {
    license_plate: document.getElementById('van-license-plate').value.trim(),
    model:         document.getElementById('van-model').value.trim(),
  };

  if (!data.license_plate) {
    alert('Please enter a license plate');
    return;
  }

  try {
    const res = await fetch('/api/owner/vans', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });

    if (res.ok) {
      hideVanModal();
      await loadAll();
    } else {
      alert('Failed to add van');
    }
  } catch (error) {
    console.error('Error adding van:', error);
  }
}

// ── Event listeners & init ──────────────────────────────────────

document.getElementById('add-driver-btn')?.addEventListener('click', showDriverModal);
document.getElementById('add-van-btn')?.addEventListener('click', showVanModal);
document.getElementById('save-driver-btn')?.addEventListener('click', saveDriver);
document.getElementById('save-van-btn')?.addEventListener('click', saveVan);
document.getElementById('quick-assign-btn')?.addEventListener('click', quickAssign);

(async () => {
  initQuickAssignDropdowns();
  await loadAll();
})();