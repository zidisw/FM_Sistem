# ========================
# RIASEC FORM 42 PERNYATAAN (Bahasa Indonesia dari PDF)
# ========================

questions = [
    "Saya suka memperbaiki mobil.",
    "Saya suka mengerjakan teka-teki.",
    "Saya pandai menggunakan alat atau mesin.",
    "Saya suka bekerja dalam tim.",
    "Saya adalah orang yang ambisius, saya berusaha menjadi yang terbaik.",
    "Saya suka mengatur segala sesuatu (file, meja kerja).",
    "Saya suka bekerja di luar ruangan.",
    "Saya suka menyelidiki sesuatu.",
    "Saya pandai membuat karya seni.",
    "Saya suka membantu orang lain.",
    "Saya suka menjual sesuatu atau memengaruhi orang lain.",
    "Saya menyukai pekerjaan yang membutuhkan perhatian pada detail.",
    "Saya tidak keberatan bekerja dengan tangan saya.",
    "Saya suka mencari tahu bagaimana sesuatu bekerja.",
    "Saya suka tampil di depan orang (bernyanyi, menari, berbicara).",
    "Saya peduli dengan orang lain.",
    "Saya menyukai kompetisi.",
    "Saya pandai mengisi dokumen atau mengikuti prosedur.",
    "Saya suka bekerja dengan hewan.",
    "Saya suka melakukan eksperimen ilmiah.",
    "Saya suka menulis cerita atau puisi.",
    "Saya suka menjadi sukarelawan di masyarakat.",
    "Saya suka memimpin.",
    "Saya senang bekerja dengan angka atau data.",
    "Saya suka menggunakan alat berkebun atau alat pertukangan.",
    "Saya suka menganalisis masalah.",
    "Saya suka menggambar atau melukis.",
    "Saya suka bekerja dengan anak-anak.",
    "Saya suka meyakinkan orang untuk menerima ide saya.",
    "Saya menyukai tugas yang membutuhkan akurasi.",
    "Saya menikmati kegiatan fisik.",
    "Saya suka memecahkan masalah atau pertanyaan ilmiah.",
    "Saya suka menghadiri acara budaya atau seni.",
    "Saya senang mendengarkan masalah orang lain.",
    "Saya suka mengambil risiko.",
    "Saya suka bekerja dengan sistem organisasi.",
    "Saya suka bekerja di pertanian atau bidang alam.",
    "Saya suka membaca buku ilmiah atau teknis.",
    "Saya suka kegiatan seperti fotografi, menulis, atau desain grafis.",
    "Saya senang mengajari atau melatih orang lain.",
    "Saya suka memulai proyek saya sendiri.",
    "Saya suka bekerja dengan data dan angka secara sistematis."
]

riasec_types = ['Realistic', 'Investigative', 'Artistic', 'Social', 'Enterprising', 'Conventional']
riasec_index = {
    'Realistic':     [0, 6, 12, 18, 24, 30, 36],
    'Investigative': [1, 7, 13, 19, 25, 31, 37],
    'Artistic':      [2, 8, 14, 20, 26, 32, 38],
    'Social':        [3, 9, 15, 21, 27, 33, 39],
    'Enterprising':  [4, 10, 16, 22, 28, 34, 40],
    'Conventional':  [5, 11, 17, 23, 29, 35, 41]
}

riasec_scores = {k: 0 for k in riasec_types}

print("\nSilakan isi kuesioner berikut dari 1 (sangat tidak setuju) sampai 5 (sangat setuju):\n")

for i, q in enumerate(questions):
    while True:
        try:
            ans = int(input(f"{i+1}. {q} [1-5]: "))
            if 1 <= ans <= 5:
                for dim, idxs in riasec_index.items():
                    if i in idxs:
                        riasec_scores[dim] += ans
                break
            else:
                print("Masukkan harus antara 1 dan 5.")
        except:
            print("Input tidak valid. Masukkan angka 1 sampai 5.")

normalized_scores = [round(riasec_scores[k]/7, 2) for k in riasec_types]
print("\nSkor RIASEC Anda (rata-rata):")
for k, v in zip(riasec_types, normalized_scores):
    print(f"{k}: {v}")

print("\nArray skor untuk input model:")
print(normalized_scores)

user_riasec_array = normalized_scores
