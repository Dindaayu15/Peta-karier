document.addEventListener("DOMContentLoaded", function () {
    // Cek halaman mana yang sedang dibuka
    const path = window.location.pathname;

    if (path.includes("admin.html")) {
        loadAdminTable();
    } else if (path.includes("riwayat.html")) {
        loadRiwayatTable();
    }
});

// Load data mahasiswa untuk halaman Admin
function loadAdminTable() {
    fetch("http://127.0.0.1:5000/riwayat")
        .then(response => response.json())
        .then(data => {
            let table = document.getElementById("adminTable");
            table.innerHTML = ""; // Kosongkan tabel sebelum diisi ulang
            data.forEach((row, index) => {
                let newRow = table.insertRow();
                newRow.innerHTML = `
                    <td>${index + 1}</td>
                    <td>${row.nama}</td>
                    <td>${row.nim}</td>
                    <td>${row.ipk}</td>
                    <td>${row.pendapatan_orangtua}</td>
                    <td>${row.prediksi_jabatan}</td>
                    <td><button class="btn btn-danger btn-sm" onclick="hapusData(${row.id})">
                        <i class="fas fa-trash"></i> Hapus</button></td>
                `;
            });
        })
        .catch(error => console.error("Error fetching data:", error));
}

// Load riwayat prediksi untuk halaman Riwayat
function loadRiwayatTable() {
    fetch("http://127.0.0.1:5000/riwayat")
        .then(response => response.json())
        .then(data => {
            let table = document.getElementById("riwayatTable");
            table.innerHTML = ""; // Kosongkan tabel sebelum diisi ulang
            data.forEach((row, index) => {
                let newRow = table.insertRow();
                newRow.innerHTML = `
                    <td>${index + 1}</td>
                    <td>${row.nama}</td>
                    <td>${row.ipk}</td>
                    <td>${row.pendapatan_orangtua}</td>
                    <td>${row.prediksi_jabatan}</td>
                `;
            });
        })
        .catch(error => console.error("Error fetching data:", error));
}

// Hapus data mahasiswa berdasarkan ID
function hapusData(id) {
    if (confirm("Yakin ingin menghapus data ini?")) {
        fetch(`http://127.0.0.1:5000/hapus/${id}`, { method: "DELETE" })
            .then(response => response.json())
            .then(() => {
                alert("Data berhasil dihapus!");
                loadAdminTable(); // Muat ulang tabel
            })
            .catch(error => console.error("Error deleting data:", error));
    }
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
