import streamlit as st
import pandas as pd
from langdetect import detect
import matplotlib.pyplot as plt
from datetime import datetime
import re

import logging

# Konfigurasi logging
logging.basicConfig(
    level=logging.DEBUG,  # Level log
    format="%(asctime)s - %(levelname)s - %(message)s",  # Format log
    handlers=[
        logging.StreamHandler(),  # Log ke console
        logging.FileHandler("app_debug.log")  # Simpan log ke file
    ]
)

# Debug untuk modul langdetect
try:
    from langdetect import detect
    logging.info("Pustaka 'langdetect' berhasil dimuat.")
except ModuleNotFoundError:
    logging.critical("Pustaka 'langdetect' tidak ditemukan! Pastikan diinstal dengan benar.")
    raise  # Untuk menghentikan program jika dependensi penting tidak ada


# Kamus kata positif dan negatif untuk analisis Bahasa Indonesia
positive_words = ["baik", "puas", "hebat", "bagus", "indah", "terima kasih", "senang", "suka", "luar biasa", "memuaskan", "ramah", "cepat", "mantap", "bagus sekali", "menyenangkan"]
negative_words = ["buruk", "jelek", "kecewa", "benci", "sedih", "marah", "tidak puas", "payah", "mengecewakan", "parah", "lambat", "sombong", "melelahkan", "tidak ramah", "parah sekali"]

def preprocess_text(text):
    # Membersihkan teks dari tanda baca dan karakter khusus
    text = re.sub(r'[^\w\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip().lower()
    return text

def analyze_sentiment_id(text):
    text = preprocess_text(text)
    positive_score = sum(1 for word in positive_words if word in text)
    negative_score = sum(1 for word in negative_words if word in text)

    if positive_score > negative_score:
        return "Positif", positive_score - negative_score
    elif negative_score > positive_score:
        return "Negatif", negative_score - positive_score
    else:
        return "Netral", 0

# Fungsi untuk mendeteksi bahasa
def detect_language(text):
    try:
        lang = detect(text)
        return lang
    except:
        return "unknown"

# Fungsi untuk menyimpan data ke CSV
def log_analysis(user_input, sentiment, score, lang):
    log_data = {
        "Timestamp": [datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        "Input": [user_input],
        "Sentiment": [sentiment],
        "Score": [score],
        "Language": [lang]
    }
    log_df = pd.DataFrame(log_data)
    try:
        log_df.to_csv("user_analysis_log.csv", mode="a", index=False, header=False)
    except Exception as e:
        st.error(f"Gagal menyimpan log: {e}")

# Desain Tampilan dengan Streamlit
st.set_page_config(page_title="Aplikasi Analisis Sentimen", page_icon="📊", layout="wide")

# Header
st.title("📊 Analisis Sentimen Aplikasi Gojek Indonesia")
st.markdown("""
Aplikasi ini memungkinkan Anda untuk menganalisis sentimen teks baik secara manual maupun dari file CSV yang diunggah.
**Mendukung Bahasa Indonesia!**
""")

# Input teks manual
st.subheader("1. Masukkan Teks untuk Analisis")
input_text = st.text_area("Masukkan teks untuk dianalisis:", height=150)

if input_text:
    lang = detect_language(input_text)
    if lang == "id":
        sentiment, score = analyze_sentiment_id(input_text)
    else:
        sentiment, score = "Tidak Diketahui", "N/A"

    # Tampilkan hasil
    st.markdown("**Hasil Analisis Sentimen:**")
    st.write(f"Sentimen: **{sentiment}**")
    st.write(f"Skor Sentimen (nilai numerik): **{score}**")
    st.write(f"Bahasa yang terdeteksi: **{lang}**")

    # Simpan hasil ke log
    log_analysis(input_text, sentiment, score, lang)

    # Visualisasi hasil sentimen individu
    if score != "N/A":
        colors = {"Positif": "green", "Negatif": "red", "Netral": "gray"}
        fig, ax = plt.subplots()
        ax.bar([sentiment], [score], color=colors.get(sentiment, "blue"))
        ax.set_title("Hasil Analisis Sentimen")
        ax.set_ylabel("Skor")
        st.pyplot(fig)

# Unggah file CSV untuk analisis
st.subheader("2. Unggah File CSV untuk Analisis Sentimen")
uploaded_file = st.file_uploader("Pilih file CSV", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.markdown("**Data yang Diupload:**")
    st.dataframe(df)  # Menampilkan semua baris data dari file CSV

    # Meminta pengguna memilih kolom teks jika tidak ada kolom 'review'
    text_column = st.selectbox("Pilih kolom teks untuk dianalisis:", df.columns)

    if text_column:
        st.write(f"Menganalisis sentimen pada kolom '{text_column}'...")
        df[['sentiment', 'sentiment_score']] = df[text_column].apply(lambda x: pd.Series(analyze_sentiment_id(x)))

        st.markdown("**Hasil Analisis Sentimen:**")
        st.dataframe(df[[text_column, 'sentiment', 'sentiment_score']])  # Menampilkan hasil analisis

        # Simpan hasil ke log
        for _, row in df.iterrows():
            log_analysis(row[text_column], row['sentiment'], row['sentiment_score'], "id")

        # Visualisasi distribusi sentimen
        sentiment_counts = df['sentiment'].value_counts()
        fig, ax = plt.subplots()
        sentiment_counts.plot(kind='bar', color=['green', 'red', 'gray'], ax=ax)
        ax.set_title("Distribusi Sentimen")
        ax.set_xlabel("Sentimen")
        ax.set_ylabel("Jumlah")
        st.pyplot(fig)
    else:
        st.warning("Kolom teks tidak dipilih. Pastikan memilih kolom yang berisi teks.")

