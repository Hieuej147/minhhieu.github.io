// Lắng nghe sự kiện scroll trên cửa sổ trình duyệt
window.addEventListener("scroll", function () {
  const header = document.getElementById("header");

  // Nếu cuộn trang xuống quá 100px, thêm class "scrolled"
  if (window.scrollY > 100) {
    header.classList.add("scrolled");
  } else {
    header.classList.remove("scrolled");
  }
});
