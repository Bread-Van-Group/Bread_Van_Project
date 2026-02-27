//This stores the current order to be passed to the checkout page
const order = [];
//Order Update Function
function updateOrder(id, itemPrice, itemName, action) {
  const item = order.find((obj) => obj.inventory_id === id);

  switch (action) {
    case "add":
      //Add item quantity from order
      if (item) {
        item.quantity += 1;
      } else {
        //Add the item to the order if not already in array
        order.push({
          inventory_id: id,
          quantity: 1,
          name: itemName,
          price: itemPrice,
        });
      }
      break;
    case "minus":
      //Minus item quantity from order
      if (item) {
        item.quantity -= 1;
      }

      //If the item has a quanity of 0, remove from order
      if (item.quantity === 0) {
        const index = order.findIndex((obj) => obj.inventory_id === id);

        order.splice(index, 1);
      }
      break;
  }
}

//Close Cart
function closeCart() {
  const cartDetailsContainer = document.querySelector(
    "#cart-details-container",
  );

  cartDetailsContainer.style.opacity = 0;
}

//Display Cart
function openCart() {
  const cartDetailsContainer = document.querySelector(
    "#cart-details-container",
  );

  cartDetailsContainer.style.opacity = 1;
}

//This code changes the actual order html
function changeOrder() {
  const cartDetails = document.querySelector("#cart-details");
  const cartMarker = document.querySelector("#cart-marker");

  cartMarker.innerHTML = order.length;

  var itemsHtml = ``;

  if (order.length == 0) {
    cartDetails.innerHTML = `No items in cart`;
    return;
  }

  order.forEach((item) => {
    itemsHtml += `
      <div class="cart-item">
        <div class="cart-item-name">${item.name}</div>
        <div class="cart-item-price">$${item.price.toFixed(2)}</div>
        <div class="cart-item-qty-section">
          <button
            id="qty-btn"
            class="cart-adjust-btn"
            onclick="changeQuantity(${item.inventory_id}, 'minus')"
          >
            -
          </button>
          <p id="cart-item-qty-${item.inventory_id}" class="cart-item-quantity">${item.quantity}</p>
          <button
            id="qty-btn"
            class="cart-adjust-btn"
            onclick="changeQuantity(${item.inventory_id},'plus')"
          >
            +
          </button>
        </div>
      </div>
    `;
  });

  cartDetails.innerHTML = itemsHtml;
}

// Quantity selector functionality
function changeQuantity(id, operation) {
  const elementId = "#" + "ordered-qty-" + String(id);
  const cardId = "#" + "store-card-" + String(id);

  const quantity = document.querySelector(elementId);

  const card = document.querySelector(cardId);

  const totalElement = document.querySelector("#order-total");

  const availableStock = Number(card.dataset.available);
  const price = Number(card.dataset.price);
  const itemName = String(card.dataset.name);
  var total = Number(String(totalElement.innerHTML).slice(1));

  if (String(operation) === "plus") {
    //Change total
    if (Number(quantity.innerHTML) != availableStock) {
      //Add to Order
      updateOrder(id, price, itemName, "add");

      total += price;
    }

    quantity.innerHTML = Math.min(
      Number(quantity.innerHTML) + 1,
      availableStock,
    );
  } else {
    //Change total
    if (Number(quantity.innerHTML) != 0) {
      //Minus from Order
      updateOrder(id, price, itemName, "minus");

      total -= price;
    }

    quantity.innerHTML = Math.max(Number(quantity.innerHTML) - 1, 0);
  }

  totalElement.innerHTML = "$" + total.toFixed(2);
  changeOrder();
}

// Search functionality
const searchInput = document.getElementById("search-bar");
searchInput.addEventListener("input", function () {
  const searchTerm = this.value.toLowerCase();
  document.querySelectorAll(".store-card").forEach((card) => {
    const name = card
      .querySelector(".store-card-name")
      .textContent.toLowerCase();

    if (name.includes(searchTerm)) {
      card.style.display = "flex";
    } else {
      card.style.display = "none";
    }
  });
});

// Filter functionality
document
  .querySelector("#category-filter")
  .addEventListener("change", function () {
    const category = this.value;

    document.querySelectorAll(".store-card").forEach((card) => {
      if (category === "all" || card.dataset.category === category) {
        card.style.display = "flex";
      } else {
        card.style.display = "none";
      }
    });
  });
