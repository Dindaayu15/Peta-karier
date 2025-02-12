async function prediksiKarier() {
    let data = {
        mahasiswa_id: document.getElementById("mahasiswa_id").value,
        ipk: parseFloat(document.getElementById("ipk").value),
        pendapatan_orangtua: parseInt(document.getElementById("pendapatan").value)
    };

    let response = await fetch("http://localhost:5000/prediksi", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data)
    });

    let result = await response.json();
    document.getElementById("hasil").innerText = `Jabatan: ${result.prediksi} (${(result.probabilitas * 100).toFixed(2)}%)`;
}

async function getRiwayat() {
    let mahasiswa_id = document.getElementById("mahasiswa_id").value;
    let response = await fetch(`http://localhost:5000/riwayat/${mahasiswa_id}`);
    let data = await response.json();

    document.getElementById("riwayat-table").innerHTML = data.map(row =>
        `<tr><td>${row.jabatan}</td><td>${(row.probabilitas * 100).toFixed(2)}%</td></tr>`
    ).join("");
}

async function loadDashboard() {
    let response = await fetch("http://localhost:5000/dashboard");
    let data = await response.json();
    // Tampilkan data ke Chart.js
}
window.onload = loadDashboard;
