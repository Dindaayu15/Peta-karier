from flask import Flask, render_template, request, jsonify, redirect, url_for, session, send_file
import mysql.connector
import pickle
import numpy as np
import pandas as pd
import smtplib
import matplotlib.pyplot as plt
import io
import csv

app = Flask(__name__)
app.secret_key = "secret123"

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

# 🏠 Halaman Login Admin
@app.route('/')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    username = request.form['username']
    password = request.form['password']
    
    if username == "admin" and password == "admin123":
        session['admin'] = True
        return redirect(url_for('admin'))
    else:
        return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

# 📜 Halaman Admin
@app.route('/admin')
def admin():
    if 'admin' not in session:
        return redirect(url_for('login'))

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

# 🚀 Prediksi Karier Mahasiswa + Kirim Email
@app.route('/predict', methods=['POST'])
def predict():
    mahasiswa_id = request.form['mahasiswa_id']
    email = request.form['email']
    
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

    # Kirim Email Hasil Prediksi
    send_email(email, prediksi_jabatan, probabilitas)

    return redirect(url_for('riwayat'))

# 📩 Fungsi Kirim Email
def send_email(email, prediksi, prob):
    sender_email = "youremail@gmail.com"
    sender_password = "yourpassword"
    subject = "Hasil Prediksi Karier Anda"
    message = f"Halo,\n\nBerdasarkan analisis kami, prediksi karier Anda adalah: {prediksi}\nDengan probabilitas: {prob:.2f}\n\nTerima kasih."

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(sender_email, sender_password)
    server.sendmail(sender_email, email, f"Subject: {subject}\n\n{message}")
    server.quit()

# 📊 Grafik Data
@app.route('/chart')
def chart():
    cursor.execute("SELECT ipk, pendapatan_orangtua FROM mahasiswa")
    data = cursor.fetchall()
    
    df = pd.DataFrame(data, columns=['IPK', 'Pendapatan'])
    plt.figure(figsize=(8, 4))
    plt.scatter(df['IPK'], df['Pendapatan'], color='blue')
    plt.xlabel("IPK")
    plt.ylabel("Pendapatan Orang Tua")
    plt.title("Hubungan IPK & Pendapatan Orang Tua")
    
    img = io.BytesIO()
    plt.savefig(img, format="png")
    img.seek(0)
    
    return send_file(img, mimetype="image/png")

# 📥 Export Data ke CSV
@app.route('/export')
def export():
    cursor.execute("SELECT m.nama, p.prediksi_jabatan, p.probabilitas FROM prediksi_karier p JOIN mahasiswa m ON p.mahasiswa_id = m.id")
    data = cursor.fetchall()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Nama", "Prediksi Jabatan", "Probabilitas"])
    writer.writerows(data)
    
    output.seek(0)
    return send_file(io.BytesIO(output.getvalue().encode()), mimetype="text/csv", as_attachment=True, download_name="data_prediksi.csv")

# 📜 Halaman Riwayat Prediksi + Filter
@app.route('/riwayat', methods=['GET'])
def riwayat():
    search = request.args.get('search', '')

    query = """
        SELECT m.nama, p.prediksi_jabatan, p.probabilitas 
        FROM prediksi_karier p 
        JOIN mahasiswa m ON p.mahasiswa_id = m.id
    """
    if search:
        query += " WHERE m.nama LIKE %s"
        cursor.execute(query, ('%' + search + '%',))
    else:
        cursor.execute(query)

    riwayat_prediksi = cursor.fetchall()
    
    return render_template('riwayat.html', riwayat=riwayat_prediksi, search=search)

# 🔄 Reset Database
@app.route('/reset')
def reset():
    cursor.execute("DELETE FROM prediksi_karier")
    db.commit()
    return redirect(url_for('admin'))

# 🔥 Jalankan Aplikasi
if __name__ == '__main__':
    app.run(debug=True)
