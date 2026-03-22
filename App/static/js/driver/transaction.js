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

function addToTransaction() {}
