document.addEventListener("DOMContentLoaded", function () {
    const fileLinks = document.querySelectorAll("#file-container a");
    const pdfViewer = document.getElementById("pdf-viewer");
    const closeBtn = document.getElementById("close-pdf");
    const overlay = document.getElementById("pdf-overlay");

    fileLinks.forEach(link => {
        link.addEventListener("click", function (event) {
            event.preventDefault();
            const pdfUrl = this.href;
            const pdfName = this.textContent; // Lấy tên file từ nội dung thẻ <a>
            const timestamp = new Date().toLocaleString(); // Lấy thời gian hiện tại

            // Lấy lịch sử cũ từ localStorage (nếu có)
            let history = JSON.parse(localStorage.getItem("pdfHistory")) || [];

            // Thêm tài liệu mới vào đầu danh sách, tránh trùng lặp
            history = history.filter(entry => entry.url !== pdfUrl);
            history.unshift({ url: pdfUrl, name: pdfName, time: timestamp });

            // Giới hạn chỉ lưu 10 tài liệu gần nhất
            if (history.length > 10) history.pop();

            // Lưu lại vào localStorage
            localStorage.setItem("pdfHistory", JSON.stringify(history));

            // Hiển thị tài liệu
            pdfViewer.src = pdfUrl;
            overlay.classList.remove("hidden");
        });
    });

    // Xử lý khi bấm nút đóng
    closeBtn.addEventListener("click", function () {
        overlay.classList.add("hidden");
        pdfViewer.src = "";
    });

    // Hiển thị lịch sử ngay khi tải trang
    displayHistory();
});

function displayHistory() {
    const history = JSON.parse(localStorage.getItem("pdfHistory")) || [];
    const historyContainer = document.getElementById("historyList");

    historyContainer.innerHTML = history.length === 0
        ? "<li>Chưa có tài liệu nào được xem.</li>"
        : "";

    history.forEach(item => {
        const li = document.createElement("li");
        const link = document.createElement("a");
        link.href = "#";
        link.textContent = `${item.name}`;
        link.classList.add("pdf-link");

        const timeSpan = document.createElement("span");
        timeSpan.textContent = ` (Xem lúc: ${item.time})`;
        timeSpan.classList.add("text-gray-500", "ml-2");

        // Khi bấm vào file trong lịch sử
        link.addEventListener("click", function (event) {
            event.preventDefault();
            document.getElementById("pdf-viewer").src = item.url;
        });

        li.appendChild(link);
        li.appendChild(timeSpan);
        historyContainer.appendChild(li);
    });
}
