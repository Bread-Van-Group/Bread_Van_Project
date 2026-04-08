let allItems    = [];     // All catalogue products
let allRoutes   = [];     // Owner's routes
let selectedRouteId = null;  // Currently viewed route
let selectedItems   = new Map();  // itemId -> quantity (edit mode)
let deletedItems    = new Set();  // itemIds removed during this edit session
let editingProduct  = null;

// ── Helpers ──────────────────────────────────────────────────────

function getUniqueCategories() {
  return [...new Set(allItems.map(i => i.category || 'Uncategorized'))].sort();
}

function groupByCategory(items) {
  return items.reduce((acc, item) => {
    const cat = item.category || 'Uncategorized';
    (acc[cat] = acc[cat] || []).push(item);
    return acc;
  }, {});
}

// ── Tab switching ────────────────────────────────────────────────

function switchTab(tab) {
  const isInventory = tab === 'inventory';
  document.getElementById('inventory-tab').classList.toggle('active', isInventory);
  document.getElementById('products-tab').classList.toggle('active', !isInventory);
  document.getElementById('inventory-content').style.display = isInventory ? 'block' : 'none';
  document.getElementById('products-content').style.display  = isInventory ? 'none'  : 'block';
  if (!isInventory) loadProducts();
}

// ── Data loading ─────────────────────────────────────────────────

async function loadRoutes() {
  try {
    const res = await fetch('/api/owner/routes');
    if (!res.ok) throw new Error('Failed to fetch routes');
    allRoutes = await res.json();
    buildRouteDropdown();
  } catch (err) {
    console.error('Failed to load routes:', err);
    document.getElementById('selected-route-text').textContent = 'Error loading routes';
  }
}

async function loadAllItems() {
  try {
    const res = await fetch('/api/inventory/items');
    if (!res.ok) throw new Error('Failed to fetch items');
    allItems = await res.json();
    updateCategoryDatalist();
  } catch (err) {
    console.error('Failed to load items:', err);
  }
}

// ── Route dropdown ────────────────────────────────────────────────

function buildRouteDropdown() {
  const optionsList = document.getElementById('route-options-list');
  const triggerText = document.getElementById('selected-route-text');
  const noRoutes    = document.getElementById('no-routes-state');
  const display     = document.getElementById('inventory-display');

  if (allRoutes.length === 0) {
    triggerText.textContent = 'No routes available';
    noRoutes.style.display  = 'block';
    display.style.display   = 'none';
    document.getElementById('edit-btn').style.display        = 'none';
    document.getElementById('import-csv-btn').style.display  = 'none';
    return;
  }

  noRoutes.style.display = 'none';
  display.style.display  = 'block';

  optionsList.innerHTML = allRoutes.map(r => `
    <span class="custom-option" data-value="${r.route_id}">
      ${r.name}
      <small style="display:block; font-size:0.8rem; color:#7a5a3e; font-style:italic;">
        ${r.day_of_week} · ${r.start_time} – ${r.end_time}
      </small>
    </span>
  `).join('');

  // Bind option clicks
  optionsList.querySelectorAll('.custom-option').forEach(opt => {
    opt.addEventListener('click', e => {
      e.stopPropagation();
      optionsList.querySelectorAll('.custom-option').forEach(o => o.classList.remove('selected'));
      opt.classList.add('selected');
      triggerText.textContent = opt.firstChild.textContent.trim();
      selectRoute(parseInt(opt.dataset.value));
      document.getElementById('route-select-dropdown').classList.remove('custom-select--open');
    });
  });

  // Auto-select first route
  const first = allRoutes[0];
  optionsList.querySelector('.custom-option')?.classList.add('selected');
  triggerText.textContent = first.name;
  selectRoute(first.route_id);
}

function selectRoute(routeId) {
  selectedRouteId = routeId;
  const route = allRoutes.find(r => r.route_id === routeId);

  // Show route metadata badges
  const meta = document.getElementById('route-meta');
  if (route) {
    document.getElementById('route-day-badge').textContent  = route.day_of_week;
    document.getElementById('route-time-badge').textContent = `${route.start_time} – ${route.end_time}`;
    meta.style.display = 'flex';
  } else {
    meta.style.display = 'none';
  }

  document.getElementById('edit-btn').style.display       = 'block';
  document.getElementById('import-csv-btn').style.display = 'block';

  loadInventoryView();
}

// ── View mode ────────────────────────────────────────────────────

async function loadInventoryView() {
  if (!selectedRouteId) return;
  const display = document.getElementById('inventory-display');
  display.innerHTML = '<div style="text-align:center; padding:40px; color:#94a3b8;">Loading inventory…</div>';

  try {
    const res = await fetch(`/api/owner/routes/${selectedRouteId}/inventory`);
    if (!res.ok) throw new Error('Fetch failed');
    const inventory = await res.json();

    if (inventory.length === 0) {
      display.innerHTML = `
        <div style="text-align:center; padding:60px;">
          <div style="font-size:2.5rem; margin-bottom:12px;">📦</div>
          <div style="font-family:'Caveat Brush',cursive; font-size:1.3rem; color:#c8a98a;">
            No inventory set for this route yet.
          </div>
          <div style="margin-top:8px; font-family:'Shadows Into Light Two',cursive; font-size:0.95rem; color:#94a3b8;">
            Click "Edit Inventory" to load items onto this van.
          </div>
        </div>`;
      return;
    }

    // Group by category
    const grouped = {};
    inventory.forEach(inv => {
      const cat = inv.item?.category || 'Uncategorized';
      (grouped[cat] = grouped[cat] || []).push(inv);
    });

    let html = '';
    Object.keys(grouped).sort().forEach(category => {
      const items   = grouped[category];
      const catId   = `cat-${category.replace(/\s+/g, '-').toLowerCase()}`;
      const total   = items.reduce((s, i) => s + i.quantity_in_stock, 0);

      html += `
        <div class="category-accordion">
          <div class="category-accordion-header" onclick="toggleCategory('${catId}')">
            <div class="category-title">
              <span class="category-icon">▼</span>
              <span>${category}</span>
            </div>
            <div style="display:flex; gap:12px; align-items:center;">
              <span style="font-family:'Shadows Into Light Two',cursive; font-size:0.9rem; color:#7a5a3e;">
                ${total} units total
              </span>
              <span class="category-count">${items.length} items</span>
            </div>
          </div>
          <div class="category-accordion-content" id="${catId}">
            <div class="inventory-grid">
              ${items.map(inv => `
                <div class="inventory-card">
                  <div class="inventory-card-name">${inv.item.name}</div>
                  <div class="inventory-card-quantity-row">
                    <div class="inventory-card-quantity">${inv.quantity_in_stock}</div>
                    <div class="inventory-card-label">units</div>
                  </div>
                  <div class="inventory-card-price">$${parseFloat(inv.item.price).toFixed(2)} each</div>
                </div>
              `).join('')}
            </div>
          </div>
        </div>`;
    });

    display.innerHTML = html;

    // Open first category by default
    const firstCat = Object.keys(grouped).sort()[0];
    toggleCategory(`cat-${firstCat.replace(/\s+/g, '-').toLowerCase()}`);

  } catch (err) {
    console.error('Failed to load inventory:', err);
    display.innerHTML = '<div style="text-align:center; padding:40px; color:#e74c3c;">Failed to load inventory.</div>';
  }
}

function toggleCategory(catId) {
  const content = document.getElementById(catId);
  if (!content) return;
  const icon = content.previousElementSibling?.querySelector('.category-icon');
  const isOpen = content.classList.toggle('open');
  if (icon) icon.textContent = isOpen ? '▼' : '▶';
}

// ── Edit mode ────────────────────────────────────────────────────

function enterEditMode() {
  if (!selectedRouteId) return;
  const route = allRoutes.find(r => r.route_id === selectedRouteId);

  document.getElementById('editing-route-label').textContent = route ? route.name : 'Route';
  document.getElementById('editing-route-meta').textContent  =
    route ? `${route.day_of_week} · ${route.start_time} – ${route.end_time}` : '';

  document.getElementById('view-mode').style.display = 'none';
  document.getElementById('edit-mode').style.display  = 'block';

  renderCatalogByCategory();
  loadExistingInventoryForEdit();
}

function exitEditMode() {
  document.getElementById('view-mode').style.display = 'block';
  document.getElementById('edit-mode').style.display  = 'none';
  selectedItems.clear();
  deletedItems.clear();
}

function renderCatalogByCategory() {
  const container = document.getElementById('catalog-by-category');
  const grouped   = groupByCategory(allItems);

  let html = '<div class="item-selection-area"><h3>Add Items from Catalog</h3>';

  Object.keys(grouped).sort().forEach(category => {
    const items  = grouped[category];
    const catId  = `edit-cat-${category.replace(/\s+/g, '-').toLowerCase()}`;

    html += `
      <div class="catalog-accordion">
        <div class="catalog-accordion-header" onclick="toggleCatalogCategory('${catId}')">
          <div class="category-title">
            <span class="category-icon">▼</span>
            <span>${category}</span>
          </div>
          <span class="category-count">${items.length} items</span>
        </div>
        <div class="catalog-accordion-content" id="${catId}">
          <div class="catalog-grid">
            ${items.map(item => `
              <div class="catalog-item" data-item-id="${item.item_id}" onclick="toggleItem(${item.item_id})">
                <div class="catalog-item-name">${item.name}</div>
                <div class="catalog-item-price">$${parseFloat(item.price).toFixed(2)}</div>
              </div>
            `).join('')}
          </div>
        </div>
      </div>`;
  });

  html += '</div>';
  container.innerHTML = html;

  // Open first category
  const firstCat = Object.keys(grouped).sort()[0];
  if (firstCat) toggleCatalogCategory(`edit-cat-${firstCat.replace(/\s+/g, '-').toLowerCase()}`);
}

function toggleCatalogCategory(catId) {
  const content = document.getElementById(catId);
  if (!content) return;
  const icon = content.previousElementSibling?.querySelector('.category-icon');
  const isOpen = content.classList.toggle('open');
  if (icon) icon.textContent = isOpen ? '▼' : '▶';
}

async function loadExistingInventoryForEdit() {
  if (!selectedRouteId) return;
  try {
    const res = await fetch(`/api/owner/routes/${selectedRouteId}/inventory`);
    if (!res.ok) throw new Error('Fetch failed');
    const inventory = await res.json();

    selectedItems.clear();
    inventory.forEach(inv => selectedItems.set(inv.item_id, inv.quantity_in_stock));
    renderSelectedItems();
  } catch (err) {
    console.error('Could not load existing inventory for edit:', err);
    selectedItems.clear();
    renderSelectedItems();
  }
}

function toggleItem(itemId) {
  if (selectedItems.has(itemId)) {
    selectedItems.delete(itemId);
    deletedItems.add(itemId);
  } else {
    selectedItems.set(itemId, 10);
    deletedItems.delete(itemId);
  }
  const card = document.querySelector(`[data-item-id="${itemId}"]`);
  if (card) card.classList.toggle('selected', selectedItems.has(itemId));
  renderSelectedItems();
}

function updateQuantity(itemId, value) {
  const qty = parseInt(value);
  if (!isNaN(qty) && qty >= 0) selectedItems.set(itemId, qty);
}

function removeItem(itemId) {
  selectedItems.delete(itemId);
  deletedItems.add(itemId);
  renderSelectedItems();
}

function renderSelectedItems() {
  const list = document.getElementById('selected-items-list');

  if (selectedItems.size === 0) {
    list.innerHTML = '<div style="text-align:center; padding:20px; color:#94a3b8;">No items selected yet</div>';
  } else {
    list.innerHTML = Array.from(selectedItems.entries()).map(([itemId, qty]) => {
      const item = allItems.find(i => i.item_id === itemId);
      if (!item) return '';
      return `
        <div class="selected-item">
          <div class="selected-item-info">
            <div class="selected-item-name">${item.name}</div>
            <div style="font-size:0.9rem; color:#64748b; margin-top:4px;">$${parseFloat(item.price).toFixed(2)} each</div>
          </div>
          <div class="selected-item-controls">
            <label>Quantity:</label>
            <input type="number" min="0" value="${qty}"
                   onchange="updateQuantity(${itemId}, this.value)" />
            <button class="remove-btn" onclick="removeItem(${itemId})">Remove</button>
          </div>
        </div>`;
    }).join('');
  }

  // Sync catalog highlights
  document.querySelectorAll('.catalog-item').forEach(el => {
    const id = parseInt(el.dataset.itemId);
    el.classList.toggle('selected', selectedItems.has(id));
  });
}

async function saveInventory() {
  if (!selectedRouteId) return;

  const items = [];

  selectedItems.forEach((quantity, item_id) => {
    items.push({ item_id: parseInt(item_id), quantity: parseInt(quantity) });
  });

  // Send removed items with quantity 0 so they get deleted server-side
  deletedItems.forEach(item_id => {
    if (!selectedItems.has(item_id)) {
      items.push({ item_id: parseInt(item_id), quantity: 0 });
    }
  });

  // Always send today's date so the backend stores against the right day
  const today = new Date().toISOString().split('T')[0];

  try {
    const res = await fetch(`/api/owner/routes/${selectedRouteId}/inventory`, {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ date: today, items }),
    });

    if (res.ok) {
      alert('✅ Inventory saved successfully!');
      deletedItems.clear();
      exitEditMode();
      await loadInventoryView();
    } else if (res.status === 422) {

      const body = await res.json().catch(() => ({}));
      alert('⚠️ ' + (body.message || 'No van is assigned to this route. Go to Fleet Management and assign a van first.'));
    } else {
      const body = await res.json().catch(() => ({}));
      alert('❌ Failed to save inventory: ' + (body.message || res.status));
    }
  } catch (err) {
    console.error('Failed to save inventory:', err);
    alert('❌ Network error — could not reach server');
  }
}

// ── CSV Import ────────────────────────────────────────────────────

async function handleCSVUpload(event) {
  const file = event.target.files[0];
  if (!file) return;

  if (!selectedRouteId) {
    alert('Please select a route before importing a CSV.');
    return;
  }

  const reader = new FileReader();
  reader.onload = async e => {
    try {
      const lines = e.target.result.split('\n').map(l => l.trim()).filter(Boolean);
      if (lines.length < 2) { alert('CSV file is empty or invalid'); return; }

      const headers = lines[0].toLowerCase().split(',');
      const nameIdx = headers.findIndex(h => h.includes('name'));
      const qtyIdx  = headers.findIndex(h => h.includes('quantity') || h.includes('qty'));

      if (nameIdx < 0 || qtyIdx < 0) {
        alert('CSV must have "name" and "quantity" columns');
        return;
      }

      selectedItems.clear();
      for (let i = 1; i < lines.length; i++) {
        const cols     = lines[i].split(',').map(c => c.trim());
        const name     = cols[nameIdx];
        const quantity = parseInt(cols[qtyIdx]) || 0;
        const item     = allItems.find(it => it.name.toLowerCase() === name.toLowerCase());
        if (item) selectedItems.set(item.item_id, quantity);
      }

      enterEditMode();
      renderSelectedItems();
      alert(`✅ Imported ${selectedItems.size} item(s) from CSV`);
    } catch (err) {
      console.error('CSV parse error:', err);
      alert('❌ Failed to parse CSV file');
    }
  };
  reader.readAsText(file);
  event.target.value = '';
}

// ── Product management ────────────────────────────────────────────

function updateCategoryDatalist() {
  const datalist = document.getElementById('category-options');
  if (!datalist) return;
  datalist.innerHTML = getUniqueCategories().map(c => `<option value="${c}">`).join('');
}

async function loadProducts() {
  try {
    const res      = await fetch('/api/inventory/items');
    const products = await res.json();
    renderProducts(products);
  } catch (err) {
    console.error('Failed to load products:', err);
  }
}

function renderProducts(products) {
  const grid = document.getElementById('products-grid');
  if (products.length === 0) {
    grid.innerHTML = '<div style="text-align:center; padding:40px; color:#94a3b8; grid-column:1/-1;">No products yet. Click "+ Add Product".</div>';
    return;
  }
  grid.innerHTML = products.map(p => `
    <div class="product-item">
      <div class="product-item-header">
        <div class="product-item-name">${p.name}</div>
        <div class="product-item-price">$${parseFloat(p.price).toFixed(2)}</div>
      </div>
      ${p.category ? `<div class="product-item-category">${p.category}</div>` : ''}
      <div class="product-item-description">${p.description || 'No description'}</div>
      <div class="product-actions">
        <button class="product-action-btn edit-product-btn" onclick="editProduct(${p.item_id})">Edit</button>
        <button class="product-action-btn delete-product-btn" onclick="deleteProduct(${p.item_id}, '${p.name.replace(/'/g, "\\'")}')">Delete</button>
      </div>
    </div>
  `).join('');
}

function showProductModal(editing = false) {
  const modal = document.getElementById('product-modal');
  document.getElementById('product-modal-title').textContent = editing ? 'Edit Product' : 'Add Product';
  if (editing && editingProduct) {
    document.getElementById('product-name').value        = editingProduct.name;
    document.getElementById('product-price').value       = parseFloat(editingProduct.price);
    document.getElementById('product-category').value    = editingProduct.category || '';
    document.getElementById('product-description').value = editingProduct.description || '';
  } else {
    ['product-name','product-price','product-category','product-description']
      .forEach(id => { document.getElementById(id).value = ''; });
    editingProduct = null;
  }
  modal.style.display = 'flex';
}

function hideProductModal() {
  document.getElementById('product-modal').style.display = 'none';
  editingProduct = null;
}

function editProduct(itemId) {
  editingProduct = allItems.find(i => i.item_id === itemId);
  showProductModal(true);
}

async function deleteProduct(itemId, name) {
  if (!confirm(`Are you sure you want to delete "${name}"? This cannot be undone.`)) return;
  try {
    const res = await fetch(`/api/inventory/items/${itemId}`, { method: 'DELETE' });
    if (res.ok) {
      alert('✅ Product deleted successfully!');
      await loadAllItems();
      await loadProducts();
      if (document.getElementById('edit-mode').style.display !== 'none') renderCatalogByCategory();
    } else {
      alert('❌ Failed to delete product');
    }
  } catch (err) {
    console.error('Failed to delete product:', err);
    alert('❌ Network error');
  }
}

async function saveProduct() {
  const name        = document.getElementById('product-name').value.trim();
  const price       = parseFloat(document.getElementById('product-price').value);
  const category    = document.getElementById('product-category').value.trim();
  const description = document.getElementById('product-description').value.trim();

  if (!name || isNaN(price) || price < 0) {
    alert('Please enter a valid name and price');
    return;
  }

  const payload = { name, price, category, description };
  const url     = editingProduct ? `/api/inventory/items/${editingProduct.item_id}` : '/api/inventory/items';
  const method  = editingProduct ? 'PUT' : 'POST';

  try {
    const res = await fetch(url, {
      method,
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify(payload),
    });

    if (res.ok) {
      alert('✅ Product saved successfully!');
      hideProductModal();
      await loadAllItems();
      await loadProducts();
      if (document.getElementById('edit-mode').style.display !== 'none') renderCatalogByCategory();
    } else {
      alert('❌ Failed to save product');
    }
  } catch (err) {
    console.error('Failed to save product:', err);
    alert('❌ Network error');
  }
}

// ── Custom dropdown (route selector) ─────────────────────────────

function initRouteDropdown() {
  const dropdown = document.getElementById('route-select-dropdown');
  const trigger  = document.getElementById('route-select-trigger');

  trigger.addEventListener('click', e => {
    e.stopPropagation();
    dropdown.classList.toggle('custom-select--open');
  });

  document.addEventListener('click', e => {
    if (!dropdown.contains(e.target)) dropdown.classList.remove('custom-select--open');
  });
}

// ── Init ──────────────────────────────────────────────────────────

document.addEventListener('DOMContentLoaded', async () => {
  initRouteDropdown();
  await Promise.all([loadRoutes(), loadAllItems()]);

  document.getElementById('csv-upload').addEventListener('change', handleCSVUpload);
  document.getElementById('edit-btn').addEventListener('click', enterEditMode);
  document.getElementById('cancel-btn').addEventListener('click', exitEditMode);
  document.getElementById('save-btn').addEventListener('click', saveInventory);
  document.getElementById('add-product-btn').addEventListener('click', () => showProductModal(false));
  document.getElementById('save-product-btn').addEventListener('click', saveProduct);
});