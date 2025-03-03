document.addEventListener("DOMContentLoaded", function () {
  const sidebar = document.querySelector(".sidebar");
  const footer = document.querySelector(".footer");

  // Kiểm tra trạng thái ban đầu của sidebar
  if (sidebar.classList.contains("active")) {
    footer.style.left = "92px";
    footer.style.width = "calc(100% - 92px)";
  } else {
    footer.style.left = "256px";
    footer.style.width = "calc(100% - 256px)";
  }

  // Xử lý sự kiện khi người dùng nhấp vào nút thu gọn sidebar
  const menuBtn = document.querySelector(".menu-btn");
  menuBtn.addEventListener("click", function () {
    sidebar.classList.toggle("active");
    if (sidebar.classList.contains("active")) {
      footer.style.left = "92px";
      footer.style.width = "calc(100% - 92px)";
    } else {
      footer.style.left = "256px";
      footer.style.width = "calc(100% - 256px)";
    }
  });
});
