window.addEventListener("scroll", function () {
  const header = document.querySelector("header");
  const logoText = document.querySelector(".logoname h1");
  const scrollPosition = window.scrollY || document.documentElement.scrollTop;

  // Kích hoạt khi cuộn qua 100px
  if (scrollPosition > 100) {
    header.classList.add("scrolled");
    logoText.classList.add("scrolled");
    // Thêm logic ẩn các phần tử khác
  } else {
    header.classList.remove("scrolled");
    logoText.classList.remove("scrolled");
    // Khôi phục các phần tử
  }
});
