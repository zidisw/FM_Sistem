import joblib
import numpy as np
import pandas as pd
from tensorflow.keras.models import load_model

# ========================
# LOAD MODEL DAN SCALER
# ========================
model = load_model("model/embedding_model.h5")
scaler = joblib.load("model/scaler.pkl")
df_pivot = pd.read_csv("Dataset/job_with_family.csv")  # sudah digabungkan dengan Job Family
riasec_types = ['Realistic', 'Investigative', 'Artistic', 'Social', 'Enterprising', 'Conventional']
riasec_data = df_pivot[riasec_types].values

# ========================
# FUNGSI KUESIONER RIASEC
# ========================
def get_user_riasec_scores():
    questions = [
        "Saya suka bekerja dengan alat, mesin, atau tanaman.",
        "Saya senang menyelidiki masalah atau memecahkan teka-teki.",
        "Saya suka menggambar, melukis, atau menulis cerita.",
        "Saya menikmati membantu orang menyelesaikan masalah.",
        "Saya suka memimpin proyek atau orang.",
        "Saya menikmati bekerja dengan data atau angka.",
        "Saya menikmati aktivitas fisik atau pekerjaan lapangan.",
        "Saya suka menganalisis informasi dan melakukan eksperimen.",
        "Saya suka tampil di depan umum seperti berakting atau menyanyi.",
        "Saya senang mengajar atau melatih orang lain.",
        "Saya suka menjual atau mempromosikan ide atau produk.",
        "Saya suka pekerjaan yang melibatkan rutinitas dan struktur.",
        "Saya suka menggunakan alat atau kendaraan.",
        "Saya penasaran dengan bagaimana sesuatu bekerja.",
        "Saya suka mendesain atau membuat hal kreatif.",
        "Saya suka mendengarkan masalah orang dan membantu mereka.",
        "Saya suka mengambil keputusan dan mengambil risiko.",
        "Saya suka mengatur data atau menyusun informasi.",
        "Saya suka membangun atau memperbaiki sesuatu.",
        "Saya suka memecahkan masalah menggunakan logika.",
        "Saya suka menulis puisi, cerita, atau lagu.",
        "Saya suka menjadi sukarelawan dalam kegiatan sosial.",
        "Saya suka menjadi pemimpin dalam kelompok.",
        "Saya suka bekerja dengan komputer dan angka.",
        "Saya senang menggunakan kekuatan atau ketangkasan saya.",
        "Saya suka bertanya dan mengeksplorasi hal baru.",
        "Saya suka membuat karya seni atau musik.",
        "Saya suka mendengarkan dan memberi nasihat.",
        "Saya suka mengatur orang untuk mencapai tujuan.",
        "Saya suka bekerja dengan detail dan mengikuti instruksi.",
        "Saya suka bekerja di luar ruangan.",
        "Saya suka meneliti dan menganalisis masalah.",
        "Saya suka mengekspresikan diri melalui seni atau drama.",
        "Saya suka membimbing dan mengajar orang.",
        "Saya suka meyakinkan orang lain untuk membeli sesuatu.",
        "Saya suka menyusun laporan atau membuat tabel data.",
        "Saya suka menggunakan peralatan atau instrumen.",
        "Saya suka memecahkan teka-teki logika.",
        "Saya suka bermain musik atau menari.",
        "Saya suka membantu orang mengembangkan diri.",
        "Saya suka menjadi pemimpin proyek.",
        "Saya suka pekerjaan administratif atau perkantoran."
    ]

    riasec_index = {
        'Realistic': [0, 6, 12, 18, 24, 30, 36],
        'Investigative': [1, 7, 13, 19, 25, 31, 37],
        'Artistic': [2, 8, 14, 20, 26, 32, 38],
        'Social': [3, 9, 15, 21, 27, 33, 39],
        'Enterprising': [4, 10, 16, 22, 28, 34, 40],
        'Conventional': [5, 11, 17, 23, 29, 35, 41]
    }

    scores = {k: 0 for k in riasec_index}
    print("\nSilakan isi kuesioner RIASEC berikut dari 1 (sangat tidak setuju) sampai 5 (sangat setuju):\n")

    for i, q in enumerate(questions):
        while True:
            try:
                val = int(input(f"{i+1}. {q} [1-5]: "))
                if 1 <= val <= 5:
                    for key, idxs in riasec_index.items():
                        if i in idxs:
                            scores[key] += val
                    break
                else:
                    print("Masukkan hanya angka 1-5.")
            except:
                print("Input tidak valid. Coba lagi.")

    final_scores = [round(scores[k]/7, 2) for k in riasec_types]
    return final_scores

# ========================
# FUNGSI REKOMENDASI
# ========================
def recommend_jobs(user_scores, top_n=5):
    user_df = pd.DataFrame([user_scores], columns=riasec_types)
    scaled = scaler.transform(user_df)
    user_embed = model.predict(scaled)
    job_embed = model.predict(scaler.transform(pd.DataFrame(riasec_data, columns=riasec_types)))

    # cosine similarity
    user_norm = np.linalg.norm(user_embed, axis=1, keepdims=True)
    job_norm = np.linalg.norm(job_embed, axis=1, keepdims=True)
    sim = np.dot(job_embed, user_embed.T) / (job_norm * user_norm.T + 1e-8)
    sim = sim.flatten()
    
    top_idx = sim.argsort()[-top_n:][::-1]
    result = df_pivot.iloc[top_idx][['Title', 'Job Family']].copy()
    result['Similarity Score'] = sim[top_idx]
    top_dim = user_df.iloc[0].sort_values(ascending=False).head(2).index.tolist()
    result['Alasan'] = f"Skor tertinggi Anda pada dimensi {top_dim[0]} dan {top_dim[1]}"
    return result

# ========================
# MAIN LOGIC
# ========================
if __name__ == "__main__":
    scores = get_user_riasec_scores()
    hasil = recommend_jobs(scores)
    print("\nRekomendasi Karier untuk Anda:")
    print(hasil.to_string(index=False))
