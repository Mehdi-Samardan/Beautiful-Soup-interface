document.addEventListener("DOMContentLoaded", function () {
  console.log("Page loaded – custom JavaScript is active.");
  const spinnerOverlay = document.getElementById("spinner-overlay");
  if (spinnerOverlay) {
    document.querySelectorAll("form").forEach((form) => {
      form.addEventListener("submit", function () {
        spinnerOverlay.style.display = "flex";
      });
    });
  }
});
