CREATE DATABASE peta_karier;

USE peta_karier;

CREATE TABLE mahasiswa (
    id INT AUTO_INCREMENT PRIMARY KEY,
    nama VARCHAR(100),
    nim VARCHAR(20) UNIQUE,
    tahun_masuk INT,
    ipk FLOAT,
    beasiswa ENUM('Ya', 'Tidak'),
    pekerjaan_orangtua VARCHAR(100),
    pendapatan_orangtua INT
);

CREATE TABLE prediksi_karier (
    id INT AUTO_INCREMENT PRIMARY KEY,
    mahasiswa_id INT,
    prediksi_jabatan VARCHAR(100),
    probabilitas FLOAT,
    FOREIGN KEY (mahasiswa_id) REFERENCES mahasiswa(id) ON DELETE CASCADE
);
