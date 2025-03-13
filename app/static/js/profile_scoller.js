// static/js/profile_scoller.js
document.addEventListener("DOMContentLoaded", function () {
  const sidebar = document.querySelector(".sidebar");
  const categoriesSection = document.querySelector(".categories-section");

  function updateCategoriesSection() {
    if (sidebar && sidebar.classList.contains("active")) {
      // Khi sidebar thu gọn (92px)
      categoriesSection.style.width = "100%";
    } else {
      // Khi sidebar mở rộng (256px)
      categoriesSection.style.width = "100%";
    }
  }

  // Kiểm tra trạng thái ban đầu
  updateCategoriesSection();

  // Xử lý sự kiện khi nhấp vào nút thu gọn sidebar
  const menuBtn = document.querySelector(".menu-btn");
  if (menuBtn) {
    menuBtn.addEventListener("click", function () {
      sidebar.classList.toggle("active");
      updateCategoriesSection();
    });
  }

  // Cập nhật khi thay đổi kích thước cửa sổ
  window.addEventListener("resize", updateCategoriesSection);
});
