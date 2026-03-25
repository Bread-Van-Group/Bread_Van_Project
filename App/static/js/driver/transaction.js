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

function removeQuantity(id) {
  const quantity = document.querySelector("#item-quantity_" + String(id));

  quantity.innerHTML = Math.max(Number(quantity.innerHTML) - 1, 1);
}

function addQuantity(id, availableStock) {
  const quantity = document.querySelector("#item-quantity_" + String(id));

  quantity.innerHTML = Math.min(Number(quantity.innerHTML) + 1, availableStock);
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
