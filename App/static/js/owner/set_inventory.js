let allItems = [];
let vanId = null;
let viewMode = 'today';
let customViewDate = null;
let editingDate = null;
let selectedItems = new Map();
let editingProduct = null;

// Helper: Get unique categories from items
function getUniqueCategories() {
  const categories = [...new Set(allItems.map(item => item.category || 'Uncategorized'))];
  return categories.sort();
}

// Helper: Group items by category
function groupByCategory(items) {
  const grouped = {};
  items.forEach(item => {
    const category = item.category || 'Uncategorized';
    if (!grouped[category]) {
      grouped[category] = [];
    }
    grouped[category].push(item);
  });
  return grouped;
}

// Tab switching
function switchTab(tab) {
  const inventoryTab = document.getElementById('inventory-tab');
  const productsTab = document.getElementById('products-tab');
  const inventoryContent = document.getElementById('inventory-content');
  const productsContent = document.getElementById('products-content');

  if (tab === 'inventory') {
    inventoryTab.classList.add('active');
    productsTab.classList.remove('active');
    inventoryContent.style.display = 'block';
    productsContent.style.display = 'none';
  } else {
    inventoryTab.classList.remove('active');
    productsTab.classList.add('active');
    inventoryContent.style.display = 'none';
    productsContent.style.display = 'block';
    loadProducts();
  }
}

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
    updateCategoryDatalist(); // Update datalist when items load
  } catch (err) {
    console.error('Failed to load items:', err);
  }
}

// Update category datalist for autocomplete
function updateCategoryDatalist() {
  const datalist = document.getElementById('category-options');
  if (!datalist) return;

  const categories = getUniqueCategories();
  datalist.innerHTML = categories.map(cat => `<option value="${cat}">`).join('');
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
    const display = document.getElementById('inventory-display');

    if (inventory.length === 0) {
      display.innerHTML = '<div style="text-align:center; padding:40px; color:#94a3b8;">No inventory set for this date</div>';
      return;
    }

    // Group inventory by category
    const inventoryWithItems = inventory.map(inv => {
      const item = allItems.find(i => i.item_id === inv.item_id);
      return { ...inv, item };
    }).filter(inv => inv.item);

    const grouped = {};
    inventoryWithItems.forEach(inv => {
      const category = inv.item.category || 'Uncategorized';
      if (!grouped[category]) {
        grouped[category] = [];
      }
      grouped[category].push(inv);
    });

    // Render collapsible categories
    let html = '';
    Object.keys(grouped).sort().forEach((category, idx) => {
      const items = grouped[category];
      const categoryId = `category-${category.replace(/\s+/g, '-').toLowerCase()}`;
      html += `
        <div class="category-accordion">
          <div class="category-accordion-header" onclick="toggleCategory('${categoryId}')">
            <div class="category-title">
              <span class="category-icon">▼</span>
              <span>${category}</span>
            </div>
            <span class="category-count">${items.length} items</span>
          </div>
          <div class="category-accordion-content" id="${categoryId}">
            <div class="inventory-grid">
              ${items.map(inv => {
                const displayPrice = inv.price || inv.item.price;
                return `
                  <div class="inventory-card">
                    <div class="inventory-card-name">${inv.item.name}</div>
                    <div class="inventory-card-quantity-row">
                      <div class="inventory-card-quantity">${inv.quantity_in_stock}</div>
                      <div class="inventory-card-label">units</div>
                    </div>
                    <div class="inventory-card-price">$${parseFloat(displayPrice).toFixed(2)} each</div>
                  </div>
                `;
              }).join('')}
            </div>
          </div>
        </div>
      `;
    });

    display.innerHTML = html;

    // Open first category by default
    if (Object.keys(grouped).length > 0) {
      const firstCategory = Object.keys(grouped).sort()[0];
      const firstId = `category-${firstCategory.replace(/\s+/g, '-').toLowerCase()}`;
      toggleCategory(firstId);
    }
  } catch (err) {
    console.error('Failed to load inventory:', err);
    document.getElementById('inventory-display').innerHTML =
      '<div style="text-align:center; padding:40px; color:#94a3b8;">No inventory set for this date</div>';
  }
}

// Toggle category accordion
function toggleCategory(categoryId) {
  const content = document.getElementById(categoryId);
  const header = content.previousElementSibling;
  const icon = header.querySelector('.category-icon');

  if (content.classList.contains('open')) {
    content.classList.remove('open');
    icon.textContent = '▶';
  } else {
    content.classList.add('open');
    icon.textContent = '▼';
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
  renderCatalogByCategory();
  loadExistingInventoryForEdit();
}

function renderCatalogByCategory() {
  const container = document.getElementById('catalog-by-category');
  const grouped = groupByCategory(allItems);

  let html = '<div class="item-selection-area"><h3>Add Items from Catalog</h3>';

  Object.keys(grouped).sort().forEach((category, idx) => {
    const items = grouped[category];
    const categoryId = `edit-category-${category.replace(/\s+/g, '-').toLowerCase()}`;
    html += `
      <div class="catalog-accordion">
        <div class="catalog-accordion-header" onclick="toggleCatalogCategory('${categoryId}')">
          <div class="category-title">
            <span class="category-icon">▼</span>
            <span>${category}</span>
          </div>
          <span class="category-count">${items.length} items</span>
        </div>
        <div class="catalog-accordion-content" id="${categoryId}">
          <div class="catalog-grid">
            ${items.map(item => `
              <div class="catalog-item" data-item-id="${item.item_id}" onclick="toggleItem(${item.item_id})">
                <div class="catalog-item-name">${item.name}</div>
                <div class="catalog-item-price">$${parseFloat(item.price).toFixed(2)}</div>
              </div>
            `).join('')}
          </div>
        </div>
      </div>
    `;
  });

  html += '</div>';
  container.innerHTML = html;

  // Open first category by default
  if (Object.keys(grouped).length > 0) {
    const firstCategory = Object.keys(grouped).sort()[0];
    const firstId = `edit-category-${firstCategory.replace(/\s+/g, '-').toLowerCase()}`;
    toggleCatalogCategory(firstId);
  }
}

function toggleCatalogCategory(categoryId) {
  const content = document.getElementById(categoryId);
  const header = content.previousElementSibling;
  const icon = header.querySelector('.category-icon');

  if (content.classList.contains('open')) {
    content.classList.remove('open');
    icon.textContent = '▶';
  } else {
    content.classList.add('open');
    icon.textContent = '▼';
  }
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
        <div style="font-size:0.9rem; color:#64748b; margin-top:4px;">$${parseFloat(item.price).toFixed(2)} each</div>
      </div>
      <div class="selected-item-controls">
        <label>Quantity:</label>
        <input type="number" min="0" value="${quantity}"
               onchange="updateQuantity(${itemId}, this.value)" />
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
      alert('✅ Inventory saved successfully!');
      exitEditMode();
      await loadInventoryView();
    } else {
      throw new Error('Save failed');
    }
  } catch (err) {
    console.error('Failed to save:', err);
    alert('❌ Failed to save inventory');
  }
}

function exitEditMode() {
  document.getElementById('view-mode').style.display = 'block';
  document.getElementById('edit-mode').style.display = 'none';
  selectedItems.clear();
  editingDate = null;
}

// CSV Import
async function handleCSVUpload(event) {
  const file = event.target.files[0];
  if (!file) return;
  const reader = new FileReader();
  reader.onload = async (e) => {
    try {
      const text = e.target.result;
      const lines = text.split('\n').map(line => line.trim()).filter(line => line);
      if (lines.length < 2) {
        alert('CSV file is empty or invalid');
        return;
      }
      const header = lines[0].toLowerCase();
      if (!header.includes('name') || !header.includes('quantity')) {
        alert('CSV must have "name" and "quantity" columns');
        return;
      }
      const nameIdx = header.split(',').findIndex(h => h.includes('name'));
      const qtyIdx = header.split(',').findIndex(h => h.includes('quantity'));
      selectedItems.clear();
      for (let i = 1; i < lines.length; i++) {
        const cols = lines[i].split(',').map(c => c.trim());
        const name = cols[nameIdx];
        const quantity = parseInt(cols[qtyIdx]) || 0;
        const item = allItems.find(it => it.name.toLowerCase() === name.toLowerCase());
        if (item) {
          selectedItems.set(item.item_id, quantity);
        }
      }
      if (viewMode === 'today') {
        alert('Please select Tomorrow or Custom date to import CSV');
        return;
      }
      if (viewMode === 'tomorrow') {
        const tomorrow = new Date();
        tomorrow.setDate(tomorrow.getDate() + 1);
        editingDate = tomorrow.toISOString().split('T')[0];
        document.getElementById('editing-date-label').textContent = "Tomorrow's";
        document.getElementById('selected-date-label').textContent = "Tomorrow";
      } else if (viewMode === 'custom') {
        if (!customViewDate) {
          alert('Please select a custom date first');
          return;
        }
        editingDate = customViewDate;
        const dateObj = new Date(editingDate + 'T00:00:00');
        document.getElementById('editing-date-label').textContent = dateObj.toLocaleDateString();
        document.getElementById('selected-date-label').textContent = dateObj.toLocaleDateString();
      }
      document.getElementById('view-mode').style.display = 'none';
      document.getElementById('edit-mode').style.display = 'block';
      renderCatalogByCategory();
      renderSelectedItems();
      alert('✅ Imported ${selectedItems.size} items from CSV');
    } catch (err) {
      console.error('CSV parse error:', err);
      alert('❌ Failed to parse CSV file');
    }
  };
  reader.readAsText(file);
  event.target.value = '';
}

// Product Management
async function loadProducts() {
  try {
    const res = await fetch('/api/inventory/items');
    const products = await res.json();
    renderProducts(products);
  } catch (err) {
    console.error('Failed to load products:', err);
  }
}

function renderProducts(products) {
  const grid = document.getElementById('products-grid');
  if (products.length === 0) {
    grid.innerHTML = '<div style="text-align:center; padding:40px; color:#94a3b8; grid-column: 1/-1;">No products yet. Click "+ Add Product".</div>';
    return;
  }
  grid.innerHTML = products.map(product => `
    <div class="product-item">
      <div class="product-item-header">
        <div class="product-item-name">${product.name}</div>
        <div class="product-item-price">$${parseFloat(product.price).toFixed(2)}</div>
      </div>
      ${product.category ? `<div class="product-item-category">${product.category}</div>` : ''}
      <div class="product-item-description">${product.description || 'No description'}</div>
      <div class="product-actions">
        <button class="product-action-btn edit-product-btn" onclick="editProduct(${product.item_id})">Edit</button>
        <button class="product-action-btn delete-product-btn" onclick="deleteProduct(${product.item_id}, '${product.name}')">Delete</button>
      </div>
    </div>
  `).join('');
}

function showProductModal(editing = false) {
  const modal = document.getElementById('product-modal');
  const title = document.getElementById('product-modal-title');
  if (editing && editingProduct) {
    title.textContent = 'Edit Product';
    document.getElementById('product-name').value = editingProduct.name;
    document.getElementById('product-price').value = parseFloat(editingProduct.price);
    document.getElementById('product-category').value = editingProduct.category || '';
    document.getElementById('product-description').value = editingProduct.description || '';
  } else {
    title.textContent = 'Add Product';
    document.getElementById('product-name').value = '';
    document.getElementById('product-price').value = '';
    document.getElementById('product-category').value = '';
    document.getElementById('product-description').value = '';
    editingProduct = null;
  }
  modal.style.display = 'flex';
}

function hideProductModal() {
  document.getElementById('product-modal').style.display = 'none';
  editingProduct = null;
}

async function editProduct(itemId) {
  editingProduct = allItems.find(item => item.item_id === itemId);
  showProductModal(true);
}

async function deleteProduct(itemId, name) {
  if (!confirm(`Are you sure you want to delete "${name}"? This cannot be undone.`)) {
    return;
  }
  try {
    const res = await fetch(`/api/inventory/items/${itemId}`, { method: 'DELETE' });
    if (res.ok) {
      alert('✅ Product deleted successfully!');
      await loadAllItems();
      await loadProducts();
      if (document.getElementById('edit-mode').style.display !== 'none') {
        renderCatalogByCategory();
      }
    } else {
      throw new Error('Delete failed');
    }
  } catch (err) {
    console.error('Failed to delete product:', err);
    alert('❌ Failed to delete product');
  }
}

async function saveProduct() {
  const name = document.getElementById('product-name').value.trim();
  const price = parseFloat(document.getElementById('product-price').value);
  const category = document.getElementById('product-category').value.trim();
  const description = document.getElementById('product-description').value.trim();

  if (!name || !price || price < 0) {
    alert('Please enter a valid name and price');
    return;
  }

  const productData = { name, price, category, description };

  try {
    const url = editingProduct ? `/api/inventory/items/${editingProduct.item_id}` : '/api/inventory/items';
    const res = await fetch(url, {
      method: editingProduct ? 'PUT' : 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(productData)
    });
    if (res.ok) {
      alert('✓ Product saved successfully!');
      hideProductModal();
      await loadAllItems();
      await loadProducts();
      if (document.getElementById('edit-mode').style.display !== 'none') {
        renderCatalogByCategory();
      }
    } else {
      throw new Error('Save failed');
    }
  } catch (err) {
    console.error('Failed to save product:', err);
    alert('❌ Failed to save product');
  }
}

// Custom Dropdown
function updateViewMode(newValue) {
  viewMode = newValue;
  const customGroup = document.getElementById('custom-date-group');
  const editBtn = document.getElementById('edit-btn');
  const importBtn = document.getElementById('import-csv-btn');
  if (viewMode === 'custom') {
    customGroup.style.display = 'flex';
    customViewDate = document.getElementById('custom-date').value;
  } else {
    customGroup.style.display = 'none';
  }
  if (viewMode === 'today') {
    document.getElementById('edit-target').textContent = "Tomorrow's";
    editBtn.style.display = 'none';
    importBtn.style.display = 'none';
  } else if (viewMode === 'tomorrow') {
    document.getElementById('edit-target').textContent = "Tomorrow's";
    editBtn.style.display = 'block';
    importBtn.style.display = 'block';
  } else {
    document.getElementById('edit-target').textContent = "This Date's";
    editBtn.style.display = customViewDate ? 'block' : 'none';
    importBtn.style.display = customViewDate ? 'block' : 'none';
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

  if (customSelectTrigger) {
    customSelectTrigger.addEventListener('click', (e) => {
      e.stopPropagation();
      customSelect.classList.toggle('custom-select--open');
    });
  }

  customOptions.forEach(option => {
    option.addEventListener('click', function(e) {
      e.stopPropagation();
      customOptions.forEach(opt => opt.classList.remove('selected'));
      this.classList.add('selected');
      const selectedText = document.getElementById('selected-view-text');
      if (selectedText) {
        selectedText.textContent = this.textContent;
      }
      const value = this.getAttribute('data-value');
      updateViewMode(value);
      customSelect.classList.remove('custom-select--open');
    });
  });

  document.addEventListener('click', (e) => {
    if (customSelect && !customSelect.contains(e.target)) {
      customSelect.classList.remove('custom-select--open');
    }
  });

  document.getElementById('custom-date').addEventListener('change', async (e) => {
    customViewDate = e.target.value;
    const editBtn = document.getElementById('edit-btn');
    const importBtn = document.getElementById('import-csv-btn');
    editBtn.style.display = customViewDate ? 'block' : 'none';
    importBtn.style.display = customViewDate ? 'block' : 'none';
    await loadInventoryView();
  });

  document.getElementById('csv-upload').addEventListener('change', handleCSVUpload);
  document.getElementById('edit-btn').addEventListener('click', enterEditMode);
  document.getElementById('cancel-btn').addEventListener('click', exitEditMode);
  document.getElementById('save-btn').addEventListener('click', saveInventory);
  document.getElementById('edit-btn').style.display = 'none';
  document.getElementById('import-csv-btn').style.display = 'none';

  document.getElementById('add-product-btn').addEventListener('click', () => showProductModal(false));
  document.getElementById('save-product-btn').addEventListener('click', saveProduct);
});