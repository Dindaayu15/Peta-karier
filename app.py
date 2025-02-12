from flask import Flask, render_template, request, jsonify, redirect, url_for
import mysql.connector
import pickle
import numpy as np
import pandas as pd

app = Flask(__name__)

# 🔌 Koneksi ke Database MySQL
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="peta_karier"
)
cursor = db.cursor()

# 📦 Load Model Prediksi
with open("model/model.pkl", "rb") as file:
    model = pickle.load(file)

# 🏠 Halaman Utama
@app.route('/')
def index():
    return render_template('index.html')

# 📜 Halaman Admin
@app.route('/admin')
def admin():
    cursor.execute("SELECT * FROM mahasiswa")
    mahasiswa = cursor.fetchall()
    
    cursor.execute("SELECT * FROM prediksi_karier")
    prediksi = cursor.fetchall()
    
    return render_template('admin.html', mahasiswa=mahasiswa, prediksi=prediksi)

# 📌 Tambah Mahasiswa
@app.route('/add_mahasiswa', methods=['POST'])
def add_mahasiswa():
    nama = request.form['nama']
    nim = request.form['nim']
    ipk = float(request.form['ipk'])
    pendapatan_orangtua = int(request.form['pendapatan_orangtua'])
    
    cursor.execute("INSERT INTO mahasiswa (nama, nim, ipk, pendapatan_orangtua) VALUES (%s, %s, %s, %s)",
                   (nama, nim, ipk, pendapatan_orangtua))
    db.commit()
    
    return redirect(url_for('admin'))

# ❌ Hapus Mahasiswa
@app.route('/delete_mahasiswa/<int:id>')
def delete_mahasiswa(id):
    cursor.execute("DELETE FROM mahasiswa WHERE id = %s", (id,))
    db.commit()
    return redirect(url_for('admin'))

# 🚀 Prediksi Karier Mahasiswa
@app.route('/predict', methods=['POST'])
def predict():
    mahasiswa_id = request.form['mahasiswa_id']
    
    cursor.execute("SELECT ipk, pendapatan_orangtua FROM mahasiswa WHERE id = %s", (mahasiswa_id,))
    data = cursor.fetchone()
    
    if not data:
        return jsonify({"error": "Mahasiswa tidak ditemukan"}), 404

    ipk, pendapatan_orangtua = data
    input_data = np.array([[ipk, pendapatan_orangtua]])

    prediksi_jabatan = model.predict(input_data)[0]
    probabilitas = model.predict_proba(input_data).max()

    cursor.execute("INSERT INTO prediksi_karier (mahasiswa_id, prediksi_jabatan, probabilitas) VALUES (%s, %s, %s)",
                   (mahasiswa_id, prediksi_jabatan, probabilitas))
    db.commit()

    return redirect(url_for('riwayat'))

# 📜 Halaman Riwayat Prediksi
@app.route('/riwayat')
def riwayat():
    cursor.execute("""
        SELECT m.nama, p.prediksi_jabatan, p.probabilitas 
        FROM prediksi_karier p 
        JOIN mahasiswa m ON p.mahasiswa_id = m.id
    """)
    riwayat_prediksi = cursor.fetchall()
    
    return render_template('riwayat.html', riwayat=riwayat_prediksi)

# 🔄 Reset Database (Opsional)
@app.route('/reset')
def reset():
    cursor.execute("DELETE FROM prediksi_karier")
    db.commit()
    return redirect(url_for('admin'))

# 🔥 Jalankan Aplikasi
if __name__ == '__main__':
    app.run(debug=True)
