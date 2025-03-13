document.addEventListener("DOMContentLoaded", function () {
    const historyListNhu2 = document.getElementById("historyListNhu2");
    const historyList = document.getElementById("history-list");
    const pdfViewer = document.getElementById("pdfViewer");

    // Lấy lịch sử từ localStorage
    const history = JSON.parse(localStorage.getItem("pdfHistory")) || [];

    // Nếu có file PDF được truyền qua URL, mở nó
    const urlParams = new URLSearchParams(window.location.search);
    const fileUrl = urlParams.get("file");
    if (fileUrl && pdfViewer) {
        pdfViewer.src = fileUrl;
    }

    // Hiển thị lịch sử trên trang nhu2.html
    if (historyListNhu2) {
        displayHistory(history, historyListNhu2, true);
    }

    // Hiển thị lịch sử trên trang chính
    if (historyList) {
        displayHistory(history, historyList, false);
    }
});

// Hàm hiển thị lịch sử
function displayHistory(history, container, isNhu2) {
    container.innerHTML = history.length === 0
        ? "<li>Chưa có tài liệu nào được xem.</li>"
        : "";

    history.forEach(item => {
        const li = document.createElement("li");
        const link = document.createElement("a");
        link.href = isNhu2 ? "#" : item.url;
        link.textContent = `${item.name}`;
        link.classList.add("pdf-link");

        const timeSpan = document.createElement("span");
        timeSpan.textContent = ` (Xem lúc: ${formatTime(item.time)})`;
        timeSpan.classList.add("text-gray-500", "ml-2");

        if (isNhu2) {
            link.addEventListener("click", function (event) {
                event.preventDefault();
                document.getElementById("pdfViewer").src = item.url;
            });
        }

        li.appendChild(link);
        li.appendChild(timeSpan);
        container.appendChild(li);
    });
}

// Hàm định dạng thời gian
function formatTime(timeString) {
    const date = new Date(timeString);
    return date.toLocaleString("vi-VN", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
        hour: "2-digit",
        minute: "2-digit",
        second: "2-digit",
        hour12: false
    });
}
