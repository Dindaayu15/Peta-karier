import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib
from sqlalchemy import create_engine

engine = create_engine("mysql+pymysql://root:@localhost/peta_karier")

# Query untuk mengambil data dari mahasiswa dan prediksi_karier
query = """
SELECT m.*, p.prediksi_jabatan, p.probabilitas
FROM mahasiswa m
LEFT JOIN prediksi_karier p ON m.id = p.mahasiswa_id
"""

# Load Data
df = pd.read_sql(query, engine)

print("Jumlah data:", len(df))
print(df.head()) 

# Jika data kosong, hentikan program dengan pesan error
if df.empty:
    raise ValueError("Dataset kosong! Pastikan database sudah diisi.")

# Preprocessing
X = df[['ipk', 'pendapatan_orangtua', 'tahun_masuk']]
y = df[['prediksi_jabatan']]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.1, random_state=42)

# Model Training
model = RandomForestClassifier()
model.fit(X_train, y_train)


# Simpan Model
joblib.dump(model, '../backend/model_karier.pkl')