let allItems = [];
let vanId = null;
let viewMode = 'today';
let customViewDate = null;
let editingDate = null;
let selectedItems = new Map(); // item_id -> quantity

// API Functions
async function loadVan() {
  try {
    const res = await fetch('/api/owner/vans');
    const vans = await res.json();
    if (vans.length > 0) {
      vanId = vans[0].van_id;
    }
  } catch (err) {
    console.error('Failed to load van:', err);
  }
}

async function loadAllItems() {
  try {
    const res = await fetch('/api/inventory/items');
    allItems = await res.json();
  } catch (err) {
    console.error('Failed to load items:', err);
  }
}

function getTargetDate() {
  if (viewMode === 'today') {
    return new Date().toISOString().split('T')[0];
  } else if (viewMode === 'tomorrow') {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
  } else {
    return customViewDate;
  }
}

async function loadInventoryView() {
  if (!vanId) return;
  const targetDate = getTargetDate();
  if (!targetDate) return;
  try {
    const res = await fetch(`/api/owner/vans/${vanId}/inventory?date=${targetDate}`);
    const inventory = await res.json();
    const grid = document.getElementById('inventory-grid');

    if (inventory.length === 0) {
      grid.innerHTML = '<div style="text-align:center; padding:40px; grid-column: 1/-1; color:#94a3b8;">No inventory set for this date</div>';
    } else {
      grid.innerHTML = inventory.map(inv => {
        const item = allItems.find(i => i.item_id === inv.item_id);
        return `
          <div class="inventory-card">
            <div class="inventory-card-name">${item ? item.name : 'Unknown'}</div>
            <div class="inventory-card-quantity">${inv.quantity_in_stock}</div>
            <div class="inventory-card-label">units</div>
          </div>
        `;
      }).join('');
    }
  } catch (err) {
    console.error('Failed to load inventory:', err);
    document.getElementById('inventory-grid').innerHTML = '<div style="text-align:center; padding:40px; grid-column: 1/-1; color:#94a3b8;">No inventory set for this date</div>';
  }
}

// Edit Mode Functions
function enterEditMode() {
  if (viewMode === 'tomorrow') {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    editingDate = tomorrow.toISOString().split('T')[0];
    document.getElementById('editing-date-label').textContent = "Tomorrow's";
    document.getElementById('selected-date-label').textContent = "Tomorrow";
  } else if (viewMode === 'custom') {
    editingDate = customViewDate;
    const dateObj = new Date(editingDate + 'T00:00:00');
    document.getElementById('editing-date-label').textContent = dateObj.toLocaleDateString();
    document.getElementById('selected-date-label').textContent = dateObj.toLocaleDateString();
  } else {
    alert("Cannot edit today's inventory. Please select Tomorrow or a Custom date.");
    return;
  }
  document.getElementById('view-mode').style.display = 'none';
  document.getElementById('edit-mode').style.display = 'block';
  renderCatalog();
  loadExistingInventoryForEdit();
}

function renderCatalog() {
  const catalog = document.getElementById('catalog-grid');
  catalog.innerHTML = allItems.map(item => 
    `<div class="catalog-item" data-item-id="${item.item_id}" onclick="toggleItem(${item.item_id})">
      <div class="catalog-item-name">${item.name}</div>
      <div class="catalog-item-price">$${parseFloat(item.price).toFixed(2)}</div>
    </div>`
  ).join('');
}

async function loadExistingInventoryForEdit() {
  if (!vanId || !editingDate) return;
  try {
    const res = await fetch(`/api/owner/vans/${vanId}/inventory?date=${editingDate}`);
    const inventory = await res.json();
    selectedItems.clear();
    inventory.forEach(inv => {
      selectedItems.set(inv.item_id, inv.quantity_in_stock);
    });
    renderSelectedItems();
  } catch (err) {
    console.error('No existing inventory:', err);
    selectedItems.clear();
    renderSelectedItems();
  }
}

function toggleItem(itemId) {
  if (selectedItems.has(itemId)) {
    selectedItems.delete(itemId);
  } else {
    selectedItems.set(itemId, 10);
  }
  document.querySelector(`[data-item-id="${itemId}"]`).classList.toggle('selected');
  renderSelectedItems();
}

function renderSelectedItems() {
  const list = document.getElementById('selected-items-list');
  if (selectedItems.size === 0) {
    list.innerHTML = '<div style="text-align:center; padding:20px; color:#94a3b8;">No items selected yet</div>';
    return;
  }
  list.innerHTML = Array.from(selectedItems.entries()).map(([itemId, quantity]) => {
    const item = allItems.find(i => i.item_id === itemId);
    return `<div class="selected-item">
      <div class="selected-item-info">
        <div class="selected-item-name">${item.name}</div>
      </div>
      <div class="selected-item-controls">
        <label>Quantity:</label>
        <input type="number" min="0" value="${quantity}" onchange="updateQuantity(${itemId}, this.value)" />
        <button class="remove-btn" onclick="removeItem(${itemId})">Remove</button>
      </div>
    </div>`;
  }).join('');
  document.querySelectorAll('.catalog-item').forEach(el => {
    const id = parseInt(el.dataset.itemId);
    el.classList.toggle('selected', selectedItems.has(id));
  });
}

function updateQuantity(itemId, newQuantity) {
  selectedItems.set(itemId, parseInt(newQuantity) || 0);
}

function removeItem(itemId) {
  selectedItems.delete(itemId);
  renderSelectedItems();
}

async function saveInventory() {
  if (!vanId || !editingDate) return;
  const items = Array.from(selectedItems.entries()).map(([item_id, quantity]) => ({
    item_id: parseInt(item_id),
    quantity: parseInt(quantity)
  }));
  try {
    const res = await fetch(`/api/owner/vans/${vanId}/inventory`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ date: editingDate, items })
    });
    if (res.ok) {
      alert('Inventory saved!');
      exitEditMode();
      await loadInventoryView();
    } else {
      throw new Error('Save failed');
    }
  } catch (err) {
    console.error('Failed to save:', err);
    alert('Failed to save inventory');
  }
}

function exitEditMode() {
  document.getElementById('view-mode').style.display = 'block';
  document.getElementById('edit-mode').style.display = 'none';
  selectedItems.clear();
  editingDate = null;
}

//  Custom Dropdown Event Handlers
function updateViewMode(newValue) {
  viewMode = newValue;
  const customGroup = document.getElementById('custom-date-group');
  const editBtn = document.getElementById('edit-btn');
  
  if (viewMode === 'custom') {
    customGroup.style.display = 'flex';
    customViewDate = document.getElementById('custom-date').value;
  } else {
    customGroup.style.display = 'none';
  }

  if (viewMode === 'today') {
    document.getElementById('display-title').textContent = "Today's Inventory";
    document.getElementById('edit-target').textContent = "Tomorrow's";
    editBtn.style.display = 'none';
  } else if (viewMode === 'tomorrow') {
    document.getElementById('display-title').textContent = "Tomorrow's Inventory";
    document.getElementById('edit-target').textContent = "Tomorrow's";
    editBtn.style.display = 'block';
  } else {
    document.getElementById('display-title').textContent = "Custom Date Inventory";
    document.getElementById('edit-target').textContent = "This Date's";
    editBtn.style.display = customViewDate ? 'block' : 'none';
  }

  if (viewMode !== 'custom' || customViewDate) {
    loadInventoryView();
  }
}

// Event Handlers
document.addEventListener('DOMContentLoaded', async () => {
  await loadVan();
  await loadAllItems();
  await loadInventoryView();
  

  const customSelectTrigger = document.querySelector('.custom-select__trigger');
  const customSelect = document.querySelector('.custom-select');
  const customOptions = document.querySelectorAll('.custom-option');
  
  // Toggle dropdown on click
  if (customSelectTrigger) {
    customSelectTrigger.addEventListener('click', (e) => {
      e.stopPropagation();
      customSelect.classList.toggle('custom-select--open');
    });
  }
  
  // Handle option selection
  customOptions.forEach(option => {
    option.addEventListener('click', function(e) {
      e.stopPropagation();
      
      // Update selected state
      customOptions.forEach(opt => opt.classList.remove('selected'));
      this.classList.add('selected');
      
      // Update displayed text
      const selectedText = document.getElementById('selected-view-text');
      if (selectedText) {
        selectedText.textContent = this.textContent;
      }
      
      // Update view mode
      const value = this.getAttribute('data-value');
      updateViewMode(value);
      
      // Close dropdown
      customSelect.classList.remove('custom-select--open');
    });
  });
  
  // Close dropdown when clicking outside
  document.addEventListener('click', (e) => {
    if (customSelect && !customSelect.contains(e.target)) {
      customSelect.classList.remove('custom-select--open');
    }
  });

  
  // Custom date
  document.getElementById('custom-date').addEventListener('change', async (e) => {
    customViewDate = e.target.value;
    document.getElementById('edit-btn').style.display = customViewDate ? 'block' : 'none';
    await loadInventoryView();
  });
  
  // Edit button
  document.getElementById('edit-btn').addEventListener('click', enterEditMode);
  
  // Cancel and Save
  document.getElementById('cancel-btn').addEventListener('click', exitEditMode);
  document.getElementById('save-btn').addEventListener('click', saveInventory);
  
  // Hide edit button for today
  document.getElementById('edit-btn').style.display = 'none';

});
