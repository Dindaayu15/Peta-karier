import pandas as pd
import joblib
from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_mysqldb import MySQL
from config import Config

app = Flask(__name__)
CORS(app)

# Konfigurasi Database
app.config["MYSQL_HOST"] = Config.MYSQL_HOST
app.config["MYSQL_USER"] = Config.MYSQL_USER
app.config["MYSQL_PASSWORD"] = Config.MYSQL_PASSWORD
app.config["MYSQL_DB"] = Config.MYSQL_DB

mysql = MySQL(app)

# Load Model Prediksi
model = joblib.load("model_karier.pkl")

# API Prediksi Karier
@app.route('/prediksi', methods=['POST'])
def prediksi():
    data = request.get_json()
    ipk = data.get('ipk')
    pendapatan_orangtua = data.get('pendapatan_orangtua')
    
    df = pd.DataFrame([data])
    prediksi = model.predict(df)[0]
    prob = model.predict_proba(df)[0].max()

    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO prediksi_karier (mahasiswa_id, prediksi_jabatan, probabilitas) VALUES (%s, %s, %s)",
                (data['mahasiswa_id'], prediksi, prob))
    mysql.connection.commit()
    cur.close()

    return jsonify({'prediksi': prediksi, 'probabilitas': prob})

# API Riwayat Prediksi Mahasiswa
@app.route('/riwayat/<int:mahasiswa_id>', methods=['GET'])
def riwayat(mahasiswa_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, prediksi_jabatan, probabilitas FROM prediksi_karier WHERE mahasiswa_id = %s", (mahasiswa_id,))
    hasil = cur.fetchall()
    cur.close()

    riwayat = [{'id': row[0], 'jabatan': row[1], 'probabilitas': row[2]} for row in hasil]

    return jsonify(riwayat)

# API Dashboard Admin - Semua Data Mahasiswa & Prediksi
@app.route('/dashboard', methods=['GET'])
def dashboard():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT m.id, m.nama, m.nim, m.ipk, m.pendapatan_orangtua, p.prediksi_jabatan, p.probabilitas
        FROM mahasiswa m
        LEFT JOIN prediksi_karier p ON m.id = p.mahasiswa_id
    """)
    hasil = cur.fetchall()
    cur.close()

    data = [{'id': row[0], 'nama': row[1], 'nim': row[2], 'ipk': row[3], 'pendapatan_orangtua': row[4], 'jabatan': row[5], 'probabilitas': row[6]} for row in hasil]

    return jsonify(data)

if __name__ == '__main__':
    app.run(debug=True)
