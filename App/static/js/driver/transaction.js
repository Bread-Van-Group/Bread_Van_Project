function hideCatalogue() {
  const dimmer = document.querySelector("#dimmer-overlay");
  const catalogue = document.querySelector("#catalogue-container");

  dimmer.style.opacity = 0;
  dimmer.style.zIndex = "-9";

  catalogue.style.opacity = 0;
  catalogue.style.zIndex = "-10";
}

function showCatalogue() {
  const dimmer = document.querySelector("#dimmer-overlay");
  const catalogue = document.querySelector("#catalogue-container");

  dimmer.style.opacity = 1;
  dimmer.style.zIndex = "9";

  catalogue.style.opacity = 1;
  catalogue.style.zIndex = "10";
}

function updateSession(inventory_id, quantity, total) {
  fetch("/api/driver/update-session-item", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      inventory_id: inventory_id,
      quantity: quantity,
      total: total,
    }),
  });
}

function updateTransactionTotal() {
  const total = document.querySelector("#total-amount");
  let newTotal = 0;

  document.querySelectorAll(".transaction-item").forEach((item) => {
    newTotal += Number(item.dataset.total);
  });

  total.innerHTML = "$" + newTotal.toFixed(2);
}

function updateItemTotal(id, quantity, price) {
  const itemTotal = document.querySelector("#item-total_" + String(id));
  const item = document.querySelector("#transaction-item_" + String(id));

  const total = (Number(quantity) * price).toFixed(2);
  item.dataset.total = total;
  itemTotal.innerHTML = "$" + total;

  updateSession(id, quantity, total);
}

function removeQuantity(id, price) {
  const quantity = document.querySelector("#item-quantity_" + String(id));

  const newQuantity = Math.max(Number(quantity.innerHTML) - 1, 1);
  quantity.innerHTML = newQuantity;

  updateItemTotal(id, newQuantity, price);
  updateTransactionTotal();
}

function addQuantity(id, availableStock, price) {
  const quantity = document.querySelector("#item-quantity_" + String(id));

  const newQuantity = Math.min(Number(quantity.innerHTML) + 1, availableStock);
  quantity.innerHTML = newQuantity;

  updateItemTotal(id, newQuantity, price);
  updateTransactionTotal();
}

// Search functionality
const searchInput = document.getElementById("search-bar");
searchInput.addEventListener("input", function () {
  const searchTerm = this.value.toLowerCase();
  document.querySelectorAll(".catalogue-item").forEach((item) => {
    const name = item
      .querySelector(".catalogue-item-name")
      .textContent.toLowerCase();

    if (name.includes(searchTerm)) {
      item.style.display = "flex";
    } else {
      item.style.display = "none";
    }
  });
});

// Filter functionality
document
  .querySelector("#category-filter")
  .addEventListener("change", function () {
    const category = this.value;

    document.querySelectorAll(".catalogue-item").forEach((item) => {
      if (category === "all" || item.dataset.category === category) {
        item.style.display = "flex";
      } else {
        item.style.display = "none";
      }
    });
  });
