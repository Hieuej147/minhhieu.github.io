document.addEventListener("DOMContentLoaded", function () {
  const sidebar = document.querySelector(".sidebar");
  const footer = document.querySelector(".footer");
  const documentViewer = document.querySelector(".document-viewer");

  // Hàm cập nhật giao diện
  function updateLayout() {
    if (sidebar.classList.contains("active")) {
      // Khi sidebar thu gọn
      footer.style.left = "92px";
      footer.style.width = "calc(100% - 92px)";
      if (documentViewer) {
        documentViewer.style.width = "calc(100% - 20px)"; // Mở rộng tối đa khi sidebar thu gọn
        documentViewer.style.marginLeft = "10px";
      }
    } else {
      // Khi sidebar mở rộng
      footer.style.left = "256px";
      footer.style.width = "calc(100% - 256px)";
      if (documentViewer) {
        documentViewer.style.width = "calc(100% - 40px)"; // Kích thước bình thường khi sidebar mở rộng
        documentViewer.style.marginLeft = "20px";
      }
    }
  }

  // Kiểm tra trạng thái ban đầu
  updateLayout();

  // Xử lý sự kiện khi người dùng nhấp vào nút thu gọn sidebar
  const menuBtn = document.querySelector(".menu-btn");
  menuBtn.addEventListener("click", function () {
    sidebar.classList.toggle("active");
    updateLayout();
  });

  // Cập nhật lại kích thước khi cửa sổ thay đổi kích thước
  window.addEventListener("resize", updateLayout);
});
