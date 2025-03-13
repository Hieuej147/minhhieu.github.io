document.addEventListener("DOMContentLoaded", function () {
  const sidebar = document.querySelector(".sidebar");
  const footer = document.querySelector(".footer");
  const main = document.querySelector("main");
  const documentViewer = document.querySelector(".document-viewer");

  // Hàm cập nhật giao diện
  function updateLayout() {
    if (sidebar && sidebar.classList.contains("active")) {
      // Khi sidebar thu gọn (active)
      if (main) main.style.marginLeft = "92px";
      if (footer) {
        footer.style.left = "92px";
        footer.style.width = "calc(100% - 92px)";
      }
      if (documentViewer) {
        documentViewer.style.width = "calc(100% - 40px)";
        documentViewer.style.marginLeft = "20px";
      }
    } else {
      // Khi sidebar mở rộng
      if (main) main.style.marginLeft = "256px";
      if (footer) {
        footer.style.left = "256px";
        footer.style.width = "calc(100% - 256px)";
      }
      if (documentViewer) {
        documentViewer.style.width = "calc(100% - 40px)";
        documentViewer.style.marginLeft = "20px";
      }
    }
  }

  // Kiểm tra trạng thái ban đầu
  updateLayout();

  // Xử lý sự kiện khi người dùng nhấp vào nút thu gọn sidebar
  const menuBtn = document.querySelector(".menu-btn");
  if (menuBtn) {
    menuBtn.addEventListener("click", function () {
      sidebar.classList.toggle("active");
      updateLayout();
    });
  }

  // Cập nhật lại kích thước khi cửa sổ thay đổi kích thước
  window.addEventListener("resize", updateLayout);
});
