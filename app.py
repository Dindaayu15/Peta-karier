from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import mysql.connector
import numpy as np
import pickle

app = Flask(__name__)
app.secret_key = 'supersecretkey'

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="",
    database="peta_karier"
)
cursor = db.cursor()

with open('model.pkl', 'rb') as file:
    model = pickle.load(file)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        cursor.execute("SELECT * FROM admin WHERE username=%s AND password=%s", (username, password))
        admin = cursor.fetchone()
        if admin:
            session['admin'] = username
            return redirect(url_for('admin_dashboard'))
        return "Login Gagal!"

    return render_template('login.html')

@app.route('/admin')
def admin_dashboard():
    if 'admin' not in session:
        return redirect(url_for('login'))

    cursor.execute("SELECT mahasiswa.id, mahasiswa.nama, mahasiswa.nim, mahasiswa.ipk, mahasiswa.pendapatan_orangtua, prediksi_karier.prediksi_jabatan FROM mahasiswa LEFT JOIN prediksi_karier ON mahasiswa.id = prediksi_karier.mahasiswa_id")
    data = cursor.fetchall()
    return render_template('admin.html', data=data)

@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect(url_for('login'))

@app.route('/predict', methods=['POST'])
def predict():
    nama = request.form['nama']
    nim = request.form['nim']
    ipk = float(request.form['ipk'])
    pendapatan_orangtua = int(request.form['pendapatan_orangtua'])

    input_data = np.array([[ipk, pendapatan_orangtua]])
    prediksi_jabatan = model.predict(input_data)[0]

    cursor.execute("INSERT INTO mahasiswa (nama, nim, ipk, pendapatan_orangtua) VALUES (%s, %s, %s, %s)", (nama, nim, ipk, pendapatan_orangtua))
    db.commit()
    mahasiswa_id = cursor.lastrowid

    cursor.execute("INSERT INTO prediksi_karier (mahasiswa_id, prediksi_jabatan, probabilitas) VALUES (%s, %s, %s)", (mahasiswa_id, prediksi_jabatan, 0.95))
    db.commit()

    return jsonify({"status": "success", "jabatan": prediksi_jabatan})

if __name__ == '__main__':
    app.run(debug=True)
