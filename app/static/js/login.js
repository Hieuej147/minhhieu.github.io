const container = document.querySelector(".containerlogin");
const dk = document.querySelector(".register-btn");
const dn = document.querySelector(".login-btn");

// Kiểm tra URL hiện tại để đặt trạng thái ban đầu
if (window.location.pathname === "/register") {
  container.classList.add("active");
}

// Thêm sự kiện click cho nút "Đăng ký"
dk.addEventListener("click", () => {
  container.classList.add("active");
  // Thay đổi URL mà không reload trang
  window.history.pushState({}, "", "/register");
});

// Thêm sự kiện click cho nút "Đăng nhập"
dn.addEventListener("click", () => {
  container.classList.remove("active");
  // Thay đổi URL mà không reload trang
  window.history.pushState({}, "", "/login");
});
