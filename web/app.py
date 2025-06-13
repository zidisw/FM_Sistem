import os
import time
import base64
import joblib
import tempfile
import numpy as np
import pandas as pd
from fpdf import FPDF
from PIL import Image
import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt
from matplotlib.path import Path
from matplotlib.patches import PathPatch
from tensorflow.keras.models import load_model

# Load model dan scaler
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
riasec_types_list = ['Realistic', 'Investigative', 'Artistic', 'Social', 'Enterprising', 'Conventional']

# Data pertanyaan RIASEC yang diperbarui
questions = [
    {"question": "Saya suka bekerja dengan alat, mesin, atau tanaman.", "type": "R"},
    {"question": "Saya senang menyelidiki masalah atau memecahkan teka-teki.", "type": "I"},
    {"question": "Saya suka menggambar, melukis, atau menulis cerita.", "type": "A"},
    {"question": "Saya menikmati membantu orang menyelesaikan masalah.", "type": "S"},
    {"question": "Saya suka memimpin proyek atau orang.", "type": "E"},
    {"question": "Saya menikmati bekerja dengan data atau angka.", "type": "C"},
    {"question": "Saya menikmati aktivitas fisik atau pekerjaan lapangan.", "type": "R"},
    {"question": "Saya suka menganalisis informasi dan melakukan eksperimen.", "type": "I"},
    {"question": "Saya suka tampil di depan umum seperti berakting atau menyanyi.", "type": "A"},
    {"question": "Saya senang mengajar atau melatih orang lain.", "type": "S"},
    {"question": "Saya suka menjual atau mempromosikan ide atau produk.", "type": "E"},
    {"question": "Saya suka pekerjaan yang melibatkan rutinitas dan struktur.", "type": "C"},
    {"question": "Saya suka menggunakan alat atau kendaraan.", "type": "R"},
    {"question": "Saya penasaran dengan bagaimana sesuatu bekerja.", "type": "I"},
    {"question": "Saya suka mendesain atau membuat hal kreatif.", "type": "A"},
    {"question": "Saya suka mendengarkan masalah orang dan membantu mereka.", "type": "S"},
    {"question": "Saya suka mengambil keputusan dan mengambil risiko.", "type": "E"},
    {"question": "Saya suka mengatur data atau menyusun informasi.", "type": "C"},
    {"question": "Saya suka membangun atau memperbaiki sesuatu.", "type": "R"},
    {"question": "Saya suka memecahkan masalah menggunakan logika.", "type": "I"},
    {"question": "Saya suka menulis puisi, cerita, atau lagu.", "type": "A"},
    {"question": "Saya suka menjadi sukarelawan dalam kegiatan sosial.", "type": "S"},
    {"question": "Saya suka menjadi pemimpin dalam kelompok.", "type": "E"},
    {"question": "Saya suka bekerja dengan komputer dan angka.", "type": "C"},
    {"question": "Saya senang menggunakan kekuatan atau ketangkasan saya.", "type": "R"},
    {"question": "Saya suka bertanya dan mengeksplorasi hal baru.", "type": "I"},
    {"question": "Saya suka membuat karya seni atau musik.", "type": "A"},
    {"question": "Saya suka mendengarkan dan memberi nasihat.", "type": "S"},
    {"question": "Saya suka mengatur orang untuk mencapai tujuan.", "type": "E"},
    {"question": "Saya suka bekerja dengan detail dan mengikuti instruksi.", "type": "C"},
    {"question": "Saya suka bekerja di luar ruangan.", "type": "R"},
    {"question": "Saya suka meneliti dan menganalisis masalah.", "type": "I"},
    {"question": "Saya suka mengekspresikan diri melalui seni atau drama.", "type": "A"},
    {"question": "Saya suka membimbing dan mengajar orang.", "type": "S"},
    {"question": "Saya suka meyakinkan orang lain untuk membeli sesuatu.", "type": "E"},
    {"question": "Saya suka menyusun laporan atau membuat tabel data.", "type": "C"},
    {"question": "Saya suka menggunakan peralatan atau instrumen.", "type": "R"},
    {"question": "Saya suka memecahkan teka-teki logika.", "type": "I"},
    {"question": "Saya suka bermain musik atau menari.", "type": "A"},
    {"question": "Saya suka membantu orang mengembangkan diri.", "type": "S"},
    {"question": "Saya suka menjadi pemimpin proyek.", "type": "E"},
    {"question": "Saya suka pekerjaan administratif atau perkantoran.", "type": "C"}
]

# Indeks pertanyaan untuk setiap tipe RIASEC
riasec_index = {
    'R': [0, 6, 12, 18, 24, 30, 36],
    'I': [1, 7, 13, 19, 25, 31, 37],
    'A': [2, 8, 14, 20, 26, 32, 38],
    'S': [3, 9, 15, 21, 27, 33, 39],
    'E': [4, 10, 16, 22, 28, 34, 40],
    'C': [5, 11, 17, 23, 29, 35, 41]
}

# Deskripsi tipe kepribadian RIASEC
riasec_types = {
    "R": {
        "name": "Realistic",
        "description": "Orang dengan tipe Realistik menyukai kegiatan praktis, bekerja dengan tangan, alat, mesin, atau binatang.",
        "color": "#FF6B6B"  # Merah
    },
    "I": {
        "name": "Investigative",
        "description": "Orang dengan tipe Investigatif menyukai kegiatan yang melibatkan pemikiran, pengamatan, dan pemecahan masalah.",
        "color": "#4ECDC4"  # Cyan
    },
    "A": {
        "name": "Artistic",
        "description": "Orang dengan tipe Artistik menyukai kegiatan yang tidak terstruktur dan kreatif seperti seni, musik, atau menulis.",
        "color": "#FFBE0B"  # Kuning
    },
    "S": {
        "name": "Social",
        "description": "Orang dengan tipe Sosial menikmati membantu, mengajar, atau melayani orang lain.",
        "color": "#A5DD9B"  # Hijau
    },
    "E": {
        "name": "Enterprising",
        "description": "Orang dengan tipe Enterprising menyukai kegiatan memimpin, mempengaruhi orang lain, dan bisnis.",
        "color": "#FF9F1C"  # Oranye
    },
    "C": {
        "name": "Conventional",
        "description": "Orang dengan tipe Konvensional menyukai pekerjaan terstruktur yang melibatkan data dan detail.",
        "color": "#A78AFF"  # Ungu
    }
}

# Warna tema dengan efek neon
theme = {
    "primary": "#00FFCC",  # Neon Cyan
    "secondary": "#FF00FF",  # Neon Pink
    "background": "#0F0F1A",  # Deeper Black
    "card": "#1C2526",  # Dark Slate
    "text": "#FFFFFF",
    "text_secondary": "#B0E0E6",  # Powder Blue
    "border": "#00CED1",  # Dark Turquoise
    "input_background": "#2A2A40",
    "input_text": "#FFFFFF",
    "input_border": "none"
}

def recommend_jobs(user_scores, top_n=5):
    user_df = pd.DataFrame([user_scores], columns=riasec_types_list)
    scaled = st.session_state.scaler.transform(user_df)
    user_embed = st.session_state.model.predict(scaled)
    job_embed = st.session_state.model.predict(st.session_state.scaler.transform(st.session_state.df_pivot[riasec_types_list].values))

    user_norm = np.linalg.norm(user_embed, axis=1, keepdims=True)
    job_norm = np.linalg.norm(job_embed, axis=1, keepdims=True)
    sim = np.dot(job_embed, user_embed.T) / (job_norm * user_norm.T + 1e-8)
    sim = sim.flatten()
    
    top_idx = sim.argsort()[-top_n:][::-1]
    result = st.session_state.df_pivot.iloc[top_idx][['Title', 'Job Family']].copy()
    result['Similarity Score'] = sim[top_idx]
    result['Similarity Score'] = result['Similarity Score'].round(3)
    
    # Mapping alasan berdasarkan job family
    job_family_reasons = {
    'Management': "Skor tinggi Anda pada dimensi Enterprising dan Conventional cocok untuk peran strategis dan pengambilan keputusan di bidang manajemen.",
    'Business and Financial Operations': "Skor tinggi Anda pada dimensi Conventional dan Investigative cocok untuk analisis data, perencanaan bisnis, dan pengelolaan keuangan.",
    'Computer and Mathematical': "Skor tinggi Anda pada dimensi Investigative dan Conventional mendukung pemecahan masalah logis dan analisis sistem teknologi.",
    'Architecture and Engineering': "Skor tinggi Anda pada dimensi Realistic dan Investigative menunjukkan ketertarikan pada desain teknis dan solusi rekayasa.",
    'Life, Physical, and Social Science': "Skor tinggi Anda pada dimensi Investigative dan Realistic sesuai untuk riset ilmiah dan eksplorasi alam maupun sosial.",
    'Community and Social Service': "Skor tinggi Anda pada dimensi Social dan Enterprising cocok untuk membantu, membimbing, dan mendukung kesejahteraan masyarakat.",
    'Legal': "Skor tinggi Anda pada dimensi Enterprising dan Investigative menunjukkan kemampuan analitis dan ketegasan dalam bidang hukum.",
    'Educational Instruction and Library': "Skor tinggi Anda pada dimensi Social dan Investigative cocok untuk mengajar, mendidik, dan mengelola pengetahuan.",
    'Arts, Design, Entertainment, Sports, and Media': "Skor tinggi Anda pada dimensi Artistic dan Enterprising menunjukkan ekspresi kreatif dan kemampuan komunikasi publik.",
    'Healthcare Practitioners and Technical': "Skor tinggi Anda pada dimensi Social dan Investigative cocok untuk pekerjaan klinis yang memerlukan analisis dan empati.",
    'Healthcare Support': "Skor tinggi Anda pada dimensi Social dan Conventional sesuai untuk membantu tenaga medis dalam merawat pasien.",
    'Protective Service': "Skor tinggi Anda pada dimensi Realistic dan Social cocok untuk menjaga keamanan dan memberikan pelayanan perlindungan.",
    'Food Preparation and Serving Related': "Skor tinggi Anda pada dimensi Realistic dan Social sesuai untuk pekerjaan cepat, praktis, dan pelayanan pelanggan.",
    'Building and Grounds Cleaning and Maintenance': "Skor tinggi Anda pada dimensi Realistic dan Conventional cocok untuk pekerjaan fisik yang terstruktur.",
    'Personal Care and Service': "Skor tinggi Anda pada dimensi Social dan Realistic menunjukkan ketertarikan dalam membantu dan melayani kebutuhan pribadi orang lain.",
    'Sales and Related': "Skor tinggi Anda pada dimensi Enterprising dan Social cocok untuk menjalin relasi, mempromosikan, dan menjual produk atau jasa.",
    'Office and Administrative Support': "Skor tinggi Anda pada dimensi Conventional dan Social sesuai untuk pekerjaan administratif yang rapi dan terkoordinasi.",
    'Farming, Fishing, and Forestry': "Skor tinggi Anda pada dimensi Realistic dan Investigative cocok untuk pekerjaan berbasis alam, praktik langsung, dan observasi.",
    'Construction and Extraction': "Skor tinggi Anda pada dimensi Realistic dan Conventional sesuai untuk pekerjaan teknis yang membutuhkan kekuatan fisik dan presisi.",
    'Installation, Maintenance, and Repair': "Skor tinggi Anda pada dimensi Realistic dan Investigative cocok untuk perbaikan teknis dan analisis perangkat.",
    'Production': "Skor tinggi Anda pada dimensi Realistic dan Conventional cocok untuk pekerjaan manufaktur yang memerlukan ketelitian dan prosedur tetap.",
    'Transportation and Material Moving': "Skor tinggi Anda pada dimensi Realistic dan Conventional sesuai untuk peran pengoperasian kendaraan dan logistik barang."
    }

    top_dim = user_df.iloc[0].sort_values(ascending=False).head(2).index.tolist()
    # Menambahkan alasan berdasarkan job family
    result['Alasan'] = result['Job Family'].apply(
    lambda x: job_family_reasons.get(x, f"Skor tertinggi Anda pada dimensi {top_dim[0]} dan {top_dim[1]} cocok untuk pekerjaan ini.")
    )

    return result.reset_index(drop=True)

def create_riasec_chart(scores, dark_mode=False):
    types = ['R', 'I', 'A', 'S', 'E', 'C']
    labels = [riasec_types[t]['name'] for t in types]
    colors = [riasec_types[t]['color'] for t in types]
    values = [scores[t] for t in types]
    
    angles = np.linspace(0, 2*np.pi, len(types), endpoint=False).tolist()
    angles += angles[:1]
    
    fig, ax = plt.subplots(figsize=(8, 8), subplot_kw=dict(polar=True))
    fig.patch.set_facecolor('#0F0F1A' if dark_mode else '#FFFFFF')
    ax.set_facecolor('#0F0F1A' if dark_mode else '#FFFFFF')
    
    values += values[:1]
    ax.fill(angles, values, color=riasec_types[types[0]]['color'], alpha=0.3)
    ax.plot(angles, values, color='#00FFCC' if dark_mode else '#FF00FF', linewidth=2, linestyle='--')
    
    ax.set_theta_offset(np.pi/2)
    ax.set_theta_direction(-1)
    ax.set_thetagrids(np.degrees(angles[:-1]), labels)
    
    ax.set_rlabel_position(0)
    plt.yticks([1, 2, 3, 4, 5], ["1", "2", "3", "4", "5"], color="#B0E0E6" if dark_mode else "#1A1A2E", size=10)
    plt.ylim(1, 5)
    
    for label in ax.get_xticklabels():
        label.set_color("#B0E0E6" if dark_mode else "#1A1A2E")
    
    ax.grid(color="#00CED1" if dark_mode else "#1A1A2E", alpha=0.3, linestyle='--')
    
    temp_file = tempfile.NamedTemporaryFile(suffix='.png', delete=False)
    plt.savefig(temp_file.name, bbox_inches='tight', facecolor=fig.get_facecolor())
    plt.close()
    
    return temp_file.name

def set_page_style():
    st.markdown(f"""
    <style>
        :root {{
            --primary: {theme['primary']};
            --secondary: {theme['secondary']};
            --background: {theme['background']};
            --card: {theme['card']};
            --text: {theme['text']};
            --text-secondary: {theme['text_secondary']};
            --border: {theme['border']};
            --input-background: {theme['input_background']};
            --input-text: {theme['input_text']};
            --input-border: {theme['input_border']};
        }}
        
        .stApp {{
            background-color: var(--background);
            color: var(--text);
            font-family: 'Arial', sans-serif;
            overflow-x: hidden;
        }}
        
        header {{
            visibility: hidden;
        }}

        .stButton>button {{
            border: 2px solid var(--primary);
            color: white;
            background: linear-gradient(45deg, var(--primary), #FF00FF);
            border-radius: 20px;
            padding: 0.7rem 1.5rem;
            box-shadow: 0 0 10px var(--primary);
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .stButton>button:hover {{
            background: linear-gradient(45deg, #FF00FF, var(--primary));
            box-shadow: 0 0 20px #FF00FF;
            transform: scale(1.05);
        }}
        
        .question-card {{
            background: linear-gradient(135deg, var(--card), #2A4066);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 0 15px rgba(0, 255, 204, 0.3);
            margin-bottom: 2rem;
            border: 1px solid var(--border);
            animation: float 3s ease-in-out infinite;
        }}
        
        @keyframes float {{
            0%, 100% {{ transform: translateY(0); }}
            50% {{ transform: translateY(-10px); }}
        }}
        
        .result-card {{
            background: linear-gradient(135deg, var(--card), #2A4066);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 0 15px rgba(0, 255, 204, 0.3);
            margin-bottom: 2rem;
            border: 1px solid var(--border);
            animation: pulse 2s infinite;
        }}
        
        @keyframes pulse {{
            0% {{ box-shadow: 0 0 5px var(--border); }}
            50% {{ box-shadow: 0 0 20px var(--primary); }}
            100% {{ box-shadow: 0 0 5px var(--border); }}
        }}
        
        .progress-bar {{
            height: 15px;
            background: linear-gradient(90deg, #1A1A2E, #2A4066);
            border-radius: 10px;
            margin-bottom: 2rem;
            overflow: hidden;
        }}
        
        .progress-fill {{
            height: 100%;
            border-radius: 10px;
            background: linear-gradient(90deg, var(--primary), #FF00FF);
            transition: width 0.5s;
            box-shadow: 0 0 10px var(--primary);
        }}
        
        .mode-toggle {{
            position: fixed;
            top: 15px;
            right: 15px;
            z-index: 999;
        }}
        
        .stTextInput>div>div>input {{
            background: linear-gradient(135deg, var(--input-background), #2A4066);
            color: var(--input-text) !important;
            border: var(--input-border) !important;
            border-radius: 20px !important;
            padding: 0.7rem 1.5rem !important;
            box-shadow: 0 0 10px rgba(0, 255, 204, 0.3);
            width: 100%; /* Ensure full width */
            height: 100%; /* Ensure full height */
        }}
        
        .st-bd {{
            background: linear-gradient(135deg, var(--card), #2A4066) !important;
            border: 1px solid var(--border) !important;
            border-radius: 20px !important;
            box-shadow: 0 0 15px rgba(0, 255, 204, 0.3);
        }}
        
        h1, h2, h3, h4, h5, h6, p, label, .stMarkdown {{
            color: var(--text) !important;
            text-shadow: 0 0 5px var(--text-secondary);
        }}
        
        .download-link {{
            display: inline-block;
            padding: 0.7rem 1.5rem;
            background: linear-gradient(45deg, var(--primary), #FF00FF);
            color: white !important;
            border-radius: 20px;
            text-decoration: none !important;
            box-shadow: 0 0 10px var(--primary);
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        
        .download-link:hover {{
            background: linear-gradient(45deg, #FF00FF, var(--primary));
            box-shadow: 0 0 20px #FF00FF;
            transform: scale(1.05);
        }}
        
        .home-button {{
            position: fixed;
            top: 15px;
            left: 15px;
            z-index: 999;
            width: 80px; /* Fixed width for home button */
            text-align: center;
            padding: 0.5rem 0; /* Adjusted padding */
        }}
        
        .answer-options {{
            display: flex;
            flex-direction: column;
            gap: 1rem;
            margin-top: 1rem;
        }}
        
        .answer-btn {{
            border: 2px solid var(--primary);
            color: white;
            background: linear-gradient(45deg, var(--primary), #FF00FF);
            border-radius: 20px;
            padding: 0.7rem 1.5rem;
            box-shadow: 0 0 10px var(--primary);
            transition: all 0.3s;
            text-transform: uppercase;
            letter-spacing: 1px;
            width: 100%;
            text-align: center;
        }}
        
        .answer-btn:hover {{
            background: linear-gradient(45deg, #FF00FF, var(--primary));
            box-shadow: 0 0 20px #FF00FF;
            transform: scale(1.05);
        }}
    </style>
    """, unsafe_allow_html=True)

def create_pdf(name, scores, dominant_type, recommended_jobs, chart_path):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    logo_path = os.path.join(BASE_DIR, "../Logo/FM_logo_full.png")
    if os.path.exists(logo_path):
        pdf.image(logo_path, x=10, y=8, w=40)
    
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(0, 10, "Hasil Tes Kepribadian RIASEC", 0, 1, 'C')
    pdf.ln(5)
    
    pdf.set_font("Arial", '', 12)
    pdf.cell(0, 10, f"Nama: {name}", 0, 1)
    pdf.cell(0, 10, f"Tanggal: {datetime.now().strftime('%d/%m/%Y %H:%M')}", 0, 1)
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Skor Anda:", 0, 1)
    pdf.ln(5)
    
    pdf.set_font("Arial", '', 12)
    for type_code, score in scores.items():
        pdf.cell(0, 10, f"{riasec_types[type_code]['name']}: {score}", 0, 1)
    
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Profil Kepribadian:", 0, 1)
    pdf.ln(5)
    img = Image.open(chart_path)
    width, height = img.size
    aspect_ratio = width / height
    new_height = 120
    new_width = int(aspect_ratio * new_height)
    pdf.image(chart_path, x=(210 - new_width) // 2, w=new_width, h=new_height)
    pdf.ln(10)
    img.close()
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, f"Tipe Dominan: {riasec_types[dominant_type]['name']}", 0, 1)
    pdf.ln(5)
    
    pdf.set_font("Arial", '', 12)
    pdf.multi_cell(0, 10, riasec_types[dominant_type]['description'])
    pdf.ln(10)
    
    pdf.set_font("Arial", 'B', 14)
    pdf.cell(0, 10, "Rekomendasi Pekerjaan:", 0, 1)
    pdf.ln(5)
    
    pdf.set_font("Arial", '', 12)
    for job in recommended_jobs:
        pdf.cell(0, 10, f"- {job}", 0, 1)
    
    os.unlink(chart_path)
    
    return pdf.output(dest='S').encode('latin1')

def get_pdf_download_link(pdf_output, name):
    b64 = base64.b64encode(pdf_output).decode()
    current_date = datetime.now().strftime("%Y%m%d")
    filename = f"hasil_tes_riasec_{name}_{current_date}.pdf"
    return f'<a class="download-link" style="text-decoration: none !important;" href="data:application/octet-stream;base64,{b64}" download="{filename}">Download Hasil Tes (PDF)</a>'

def render_home_button():
    if st.session_state.page != "start":
        if st.button("🏠 Home", key="home_button"):
            st.session_state.page = "start"
            st.session_state.answers = {}
            st.rerun()

def main():
    st.set_page_config(page_title="Tes Kepribadian RIASEC", page_icon="👩‍🎓", layout="wide")
    
    if 'page' not in st.session_state:
        st.session_state.page = "start"
    if 'answers' not in st.session_state:
        st.session_state.answers = {}
    if 'name' not in st.session_state:
        st.session_state.name = ""

    set_page_style()
    
    with st.container():
        render_home_button()
    
    if st.session_state.page == "start":
        render_start_page()
    
    elif st.session_state.page == "test":
        render_test_page()
    
    elif st.session_state.page == "results":
        if 'model' not in st.session_state:
            try:
                with st.spinner('Memproses hasil tes...'):
                    st.session_state.model = load_model(os.path.join(BASE_DIR, "../model/embedding_model.h5"), compile=False)
                    st.session_state.scaler = joblib.load(os.path.join(BASE_DIR, "../model/scaler.pkl"))
                    st.session_state.df_pivot = pd.read_csv(os.path.join(BASE_DIR, "../dataset/job_with_family.csv"))
            except Exception as e:
                st.error(f"Failed to load resources: {str(e)}")
                st.stop()
        
        render_results_page()

def render_start_page():
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        logo_path = os.path.join(BASE_DIR, "../Logo/FM_logo_full.png")
        st.image(logo_path)
        st.markdown(f"<h1 style='color: var(--primary); text-shadow: 0 0 10px var(--primary);'>FutureMinded: Make Your Own Choice</h1>", unsafe_allow_html=True)
        st.markdown(f"<p style='font-size: 18px; color: var(--text); text-shadow: 0 0 5px var(--text-secondary);'>FutureMinded merupakan platform pengembangan diri yang membantu Anda menemukan minat dan potensi karir melalui Tes Kepribadian RIASEC. Temukan tipe kepribadian dan rekomendasi karir yang sesuai untuk masa depan Anda.</p>", unsafe_allow_html=True)
        
        st.session_state.name = st.text_input("Masukkan nama Anda:", placeholder="Nama Anda")
        
        if st.button("Mulai Tes", key="start_test"):
            if st.session_state.name.strip() == "":
                st.warning("Silakan masukkan nama Anda terlebih dahulu.")
            else:
                st.session_state.page = "test"
                st.rerun()

def render_test_page():
    st.markdown(f"<h1 style='color: var(--primary); text-shadow: 0 0 10px var(--primary);'>Tes Kepribadian RIASEC</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: var(--text); text-shadow: 0 0 5px var(--text-secondary);'>Halo, {st.session_state.name}!</h3>", unsafe_allow_html=True)
    st.markdown(f"<p style='color: var(--text); text-shadow: 0 0 5px var(--text-secondary);'>Silakan jawab pertanyaan berikut dengan skala 1 (Sangat Tidak Setuju) sampai 5 (Sangat Setuju):</p>", unsafe_allow_html=True)
    
    answered_count = len(st.session_state.answers)
    total_questions = len(questions)
    progress = answered_count / total_questions
    
    current_question = min(answered_count + 1, total_questions)
    
    st.markdown(f"""
    <div class="progress-bar">
        <div class="progress-fill" style="width: {progress * 100}%;"></div>
    </div>
    <p style="text-align: center; color: var(--text); text-shadow: 0 0 5px var(--text-secondary);">Pertanyaan {current_question} dari {total_questions}</p>
    """, unsafe_allow_html=True)
    
    
    unanswered = [q for i, q in enumerate(questions) if i not in st.session_state.answers]
    
    if unanswered:
        current_q = unanswered[0]
        current_index = questions.index(current_q)
        
        st.markdown(f"""
        <div class="question-card">
            <h3 style='color: var(--text); text-shadow: 0 0 5px var(--text-secondary);'>{current_q['question']}</h3>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(
        """
        <style>
        .stButton>button {
            width: 100% !important;
            min-width: 120px;
            padding: 0.7rem 0 !important;
            font-size: 1.2rem;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
        
        cols = st.columns(5)
        for i in range(1, 6):
            with cols[i-1]:
                if st.button(str(i), key=f"{i}_{current_index}"):
                    st.session_state.answers[current_index] = i
                    st.rerun()


        st.markdown("""
        <div style="text-align: center; margin-top: 10px; color: var(--text-secondary); text-shadow: 0 0 5px var(--text-secondary);">
            <small>
                1: Sangat Tidak Setuju | 
                2: Tidak Setuju | 
                3: Netral | 
                4: Setuju | 
                5: Sangat Setuju
            </small>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.session_state.page = "results"
        st.rerun()

def render_results_page():
    st.markdown(f"<h1 style='color: var(--primary); text-shadow: 0 0 10px var(--primary);'>Hasil Tes Kepribadian RIASEC</h1>", unsafe_allow_html=True)
    st.markdown(f"<h3 style='color: var(--text); text-shadow: 0 0 5px var(--text-secondary);'>Untuk {st.session_state.name}</h3>", unsafe_allow_html=True)
    
    scores = {"R": 0, "I": 0, "A": 0, "S": 0, "E": 0, "C": 0}
    
    for idx, answer in st.session_state.answers.items():
        q_type = questions[idx]["type"]
        scores[q_type] += answer
    
    for k in scores:
        question_count = len([q for q in questions if q["type"] == k])
        if question_count > 0:
            scores[k] = round(scores[k] / question_count, 2)
    
    user_scores = [scores['R'], scores['I'], scores['A'], scores['S'], scores['E'], scores['C']]
    
    st.markdown("<h3 style='color: var(--text); text-shadow: 0 0 5px var(--text-secondary);'>Skor Anda:</h3>", unsafe_allow_html=True)
    
    cols = st.columns(6)
    for i, (type_code, score) in enumerate(scores.items()):
        with cols[i]:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {riasec_types[type_code]['color']}30, #2A4066); 
                        border-radius: 20px; 
                        padding: 1rem; 
                        text-align: center;
                        border-left: 5px solid {riasec_types[type_code]['color']};
                        color: var(--text);
                        box-shadow: 0 0 10px {riasec_types[type_code]['color']};">
                <h4>{riasec_types[type_code]['name']}</h4>
                <h3>{score}</h3>
            </div>
            """, unsafe_allow_html=True)
    
    st.markdown("<h3 style='color: var(--text); text-shadow: 0 0 5px var(--text-secondary);'>Profil Kepribadian:</h3>", unsafe_allow_html=True)
    chart_path = create_riasec_chart(scores, st.session_state)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.image(chart_path)
    
    dominant_type = max(scores.items(), key=lambda x: x[1])[0]
    st.markdown(f"""
    <div class="result-card">
        <h3 style='color: var(--text); text-shadow: 0 0 5px var(--text-secondary);'>Tipe Dominan: {riasec_types[dominant_type]['name']}</h3>
        <p style='color: var(--text); text-shadow: 0 0 5px var(--text-secondary);'>{riasec_types[dominant_type]['description']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    recommended_jobs_df = recommend_jobs(user_scores)
    
    st.markdown("<h3 style='color: var(--text); text-shadow: 0 0 5px var(--text-secondary);'>Rekomendasi Karier untuk Anda:</h3>", unsafe_allow_html=True)

    st.markdown("""
    <style>
        .job-table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        .job-table th {
            background: linear-gradient(45deg, var(--primary), #FF00FF);
            color: white;
            padding: 12px;
            text-align: left;
            text-shadow: 0 0 5px white;
        }
        .job-table td {
            padding: 10px;
            border-bottom: 1px solid var(--border);
            background: linear-gradient(135deg, var(--card), #2A4066);
        }
        .job-table tr:hover {
            background: linear-gradient(135deg, #2A4066, var(--card));
            box-shadow: 0 0 15px var(--primary);
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown(
        recommended_jobs_df.to_html(classes="job-table", index=False, escape=False),
        unsafe_allow_html=True
    )
    
    pdf_output = create_pdf(
        st.session_state.name, 
        scores, 
        dominant_type, 
        recommended_jobs_df['Title'].tolist(),
        chart_path
    )
    st.markdown(get_pdf_download_link(pdf_output, st.session_state.name), unsafe_allow_html=True)

if __name__ == "__main__":
    main()