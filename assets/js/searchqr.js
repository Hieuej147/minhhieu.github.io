document.querySelector('.search-input').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
      const query = this.value.trim();
      if (query) {
        alert(`You searched for: ${query}`); // Thay thế bằng logic tìm kiếm của bạn
      }
    }
  });
  