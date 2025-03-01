const container = document.querySelector(".containerlogin");
const dk = document.querySelector(".register-btn");
const dn = document.querySelector(".login-btn");

dk.addEventListener("click", () => {
  container.classList.add("active");
});

dn.addEventListener("click", () => {
  container.classList.remove("active");
});
