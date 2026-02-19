const navBtns = document.querySelectorAll(".nav-btn");
navBtns.forEach((btn) => {
  btn.addEventListener("click", function () {
    navBtns.forEach((b) => b.classList.remove("active"));
    this.classList.add("active");
    const tab = this.dataset.tab;
    console.log("Switched to:", tab);
  });
});
