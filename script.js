document.addEventListener("DOMContentLoaded", function () {
    const path = window.location.pathname;

    if (path.includes("admin.html")) {
        loadAdminTable();
        setupSearchFilter();
        renderCharts();
    } else if (path.includes("riwayat.html")) {
        loadRiwayatTable();
        setupSearchFilter();
    }
});

// Load data mahasiswa untuk halaman Admin
function loadAdminTable() {
    fetch("http://127.0.0.1:5000/riwayat")
        .then(response => response.json())
        .then(data => {
            renderTable(data, "adminTable");
            updateCharts(data);
        })
        .catch(error => console.error("Error fetching data:", error));
}

// Load riwayat prediksi untuk halaman Riwayat
function loadRiwayatTable() {
    fetch("http://127.0.0.1:5000/riwayat")
        .then(response => response.json())
        .then(data => {
            renderTable(data, "riwayatTable");
        })
        .catch(error => console.error("Error fetching data:", error));
}

// Render tabel dinamis
function renderTable(data, tableId) {
    let table = document.getElementById(tableId);
    table.innerHTML = "";
    data.forEach((row, index) => {
        let newRow = table.insertRow();
        newRow.innerHTML = `
            <td>${index + 1}</td>
            <td>${row.nama}</td>
            <td>${row.nim}</td>
            <td>${row.ipk}</td>
            <td>${row.pendapatan_orangtua}</td>
            <td>${row.prediksi_jabatan}</td>
            ${tableId === "adminTable" ? `<td><button class="btn btn-danger btn-sm" onclick="hapusData(${row.id})">
                <i class="fas fa-trash"></i> Hapus</button></td>` : ""}
        `;
    });
}

// Hapus data mahasiswa berdasarkan ID
function hapusData(id) {
    if (confirm("Yakin ingin menghapus data ini?")) {
        fetch(`http://127.0.0.1:5000/hapus/${id}`, { method: "DELETE" })
            .then(response => response.json())
            .then(() => {
                alert("Data berhasil dihapus!");
                loadAdminTable();
            })
            .catch(error => console.error("Error deleting data:", error));
    }
}

// Fitur 🔍 Pencarian dan Filter
function setupSearchFilter() {
    document.getElementById("search").addEventListener("input", function () {
        let keyword = this.value.toLowerCase();
        let rows = document.querySelectorAll("tbody tr");
        rows.forEach(row => {
            let text = row.innerText.toLowerCase();
            row.style.display = text.includes(keyword) ? "" : "none";
        });
    });
}

// 📊 Grafik Statistik
function renderCharts() {
    fetch("http://127.0.0.1:5000/riwayat")
        .then(response => response.json())
        .then(data => {
            updateCharts(data);
        })
        .catch(error => console.error("Error fetching chart data:", error));
}

function updateCharts(data) {
    let ipkData = data.map(row => row.ipk);
    let jabatanData = data.map(row => row.prediksi_jabatan);

    let ipkChart = document.getElementById("ipkChart").getContext("2d");
    new Chart(ipkChart, {
        type: "bar",
        data: {
            labels: data.map(row => row.nama),
            datasets: [{ label: "IPK Mahasiswa", data: ipkData, backgroundColor: "blue" }]
        }
    });

    let jabatanCount = jabatanData.reduce((acc, val) => (acc[val] = (acc[val] || 0) + 1, acc), {});
    let jabatanChart = document.getElementById("jabatanChart").getContext("2d");
    new Chart(jabatanChart, {
        type: "pie",
        data: {
            labels: Object.keys(jabatanCount),
            datasets: [{ data: Object.values(jabatanCount), backgroundColor: ["red", "green", "blue", "yellow"] }]
        }
    });
}

// 📥 Export Data ke CSV
function exportCSV() {
    fetch("http://127.0.0.1:5000/riwayat")
        .then(response => response.json())
        .then(data => {
            let csv = "Nama,NIM,IPK,Pendapatan Orangtua,Prediksi Jabatan\n";
            data.forEach(row => {
                csv += `${row.nama},${row.nim},${row.ipk},${row.pendapatan_orangtua},${row.prediksi_jabatan}\n`;
            });

            let blob = new Blob([csv], { type: "text/csv" });
            let link = document.createElement("a");
            link.href = URL.createObjectURL(blob);
            link.download = "riwayat_prediksi.csv";
            link.click();
        })
        .catch(error => console.error("Error exporting CSV:", error));
}

// 📧 Kirim Email Hasil Prediksi
function kirimEmail() {
    fetch("http://127.0.0.1:5000/kirim_email", { method: "POST" })
        .then(response => response.json())
        .then(() => alert("Email berhasil dikirim!"))
        .catch(error => console.error("Error sending email:", error));
}

// 📸 Screenshot Hasil Prediksi
function screenshotTable() {
    html2canvas(document.getElementById("riwayatTable")).then(canvas => {
        let link = document.createElement("a");
        link.href = canvas.toDataURL();
        link.download = "riwayat_prediksi.png";
        link.click();
    });
}

// Animasi loading sederhana
document.addEventListener("DOMContentLoaded", function () {
    let fadeElements = document.querySelectorAll(".fade-in");
    fadeElements.forEach((element) => {
        element.style.opacity = 0;
        element.style.transition = "opacity 1s ease-in-out";
        setTimeout(() => {
            element.style.opacity = 1;
        }, 300);
    });
});
