import tensorflow as tf
import joblib
import numpy as np
import pandas as pd

# ========================
# 1. Load Model dan Scaler
# ========================
embedding_model = tf.keras.models.load_model("embedding_model.h5")
scaler = joblib.load("scaler.pkl")

# Load data pekerjaan
riasec_df = pd.read_csv("Dataset/interests_riasec_dataset.csv")
df_pivot = riasec_df[['O*NET-SOC Code', 'Title', 'Element Name', 'Data Value']] \
    .pivot_table(index=['O*NET-SOC Code', 'Title'], columns='Element Name', values='Data Value') \
    .reset_index()

riasec_types = ['Realistic', 'Investigative', 'Artistic', 'Social', 'Enterprising', 'Conventional']
df_pivot = df_pivot[['O*NET-SOC Code', 'Title'] + riasec_types]
riasec_scaled = scaler.transform(df_pivot[riasec_types])

# ========================
# 2. Fungsi Rekomendasi
# ========================
def recommend_jobs(user_riasec_scores, top_n=5):
    sample_user_df = pd.DataFrame([user_riasec_scores], columns=riasec_types)
    user_scores_scaled = scaler.transform(sample_user_df)
    user_embedding = embedding_model.predict(user_scores_scaled)
    job_embeddings = embedding_model.predict(riasec_scaled)

    user_norm = np.linalg.norm(user_embedding, axis=1, keepdims=True)
    job_norm = np.linalg.norm(job_embeddings, axis=1, keepdims=True)
    similarities = np.dot(job_embeddings, user_embedding.T) / (job_norm * user_norm.T + 1e-8)
    similarities = similarities.flatten()

    top_indices = similarities.argsort()[-top_n:][::-1]
    recommendations = df_pivot.iloc[top_indices][['O*NET-SOC Code', 'Title']].copy()
    recommendations['Similarity Score'] = similarities[top_indices]
    top_riasec = sample_user_df.iloc[0].sort_values(ascending=False).head(2).index.tolist()
    reason = f"Karena skor RIASEC tertinggi Anda adalah pada dimensi {top_riasec[0]} dan {top_riasec[1]}"
    recommendations['Alasan Rekomendasi'] = reason
    return recommendations

# ========================
# 3. Gunakan skor dari form PDF (misal dari variabel user_riasec_array)
# ========================
# Contoh saja, sesuaikan dari output notebook sebelumnya
user_riasec_array = [3.0, 4.43, 4.0, 4.71, 4.14, 4.43]

# Jalankan rekomendasi
hasil_rekomendasi = recommend_jobs(user_riasec_array, top_n=5)
print(hasil_rekomendasi)
