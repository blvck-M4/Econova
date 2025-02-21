document.getElementById("trigger").addEventListener("click", function () {
  document.querySelectorAll(".bouton-f").forEach((btn) => {
    btn.classList.toggle("actif");
  });
});