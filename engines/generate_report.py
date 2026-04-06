"""
Modul Penghasil Laporan Analisis Data (EDA)
------------------------------------------
Skrip ini digunakan untuk membaca dataset ulasan, melakukan pemrosesan bahasa alami dasar 
untuk mengekstraksi keluhan, menghasilkan visualisasi data, dan menyusun laporan berbasis Markdown.
"""

import sys
import os
import logging
import re
from typing import List, Dict, Tuple
from collections import Counter
from datetime import datetime

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

STOP_WORDS = frozenset([
    "yg", "yang", "dan", "di", "ke", "dari", "untuk", "dengan", "ini", "itu",
    "ada", "adalah", "saja", "tapi", "karena", "kendala", "kualitas", "barang",
    "bermasalah", "pengiriman", "kalau", "tidak", "bisa", "sudah", "nya",
    "kurang", "saya", "buat", "udah", "aja", "belum", "sih", "tp", "ya",
    "kalo", "jd", "gak", "jadi", "juga", "atau", "sama", "kok",
    "terus", "selengkapnya", "banget", "sangat", "lebih", "sekali", "meski",
    "emang", "memang", "pas", "kak", "min", "tolong", "mohon", "produk",
    "seller", "toko", "beli", "mau", "lah", "deh", "nih", "gan"
])


def format_rating(n: int) -> str:
    """Format angka rating ke dalam representasi teks standar."""
    return f"Rating {n}"


def tokenize_text(text: str) -> List[str]:
    """Membersihkan dan memecah teks menjadi token, serta menghapus stopwords."""
    cleaned_text = re.sub(r'[^\w\s]', ' ', str(text).lower())
    words = cleaned_text.split()
    return [w for w in words if w not in STOP_WORDS and len(w) > 2]


def build_ngram_frequencies(tokens: List[str], min_count: int = 2) -> Dict[str, int]:
    """Menghitung frekuensi kemunculan kata tunggal, bigram, dan trigram."""
    freq = Counter()

    for w in tokens:
        freq[w] += 1

    for i in range(len(tokens) - 1):
        phrase = f"{tokens[i]} {tokens[i+1]}"
        freq[phrase] += 1

    for i in range(len(tokens) - 2):
        phrase = f"{tokens[i]} {tokens[i+1]} {tokens[i+2]}"
        freq[phrase] += 1

    return {k: v for k, v in freq.items() if v >= min_count}


def generate_rating_distribution_chart(df: pd.DataFrame, output_path: str) -> None:
    """Menghasilkan grafik distribusi matriks rating dan menyimpannya sebagai gambar."""
    plt.style.use("ggplot")
    plt.figure(figsize=(8, 5))
    
    rating_counts = df["rating"].value_counts().sort_index()
    
    colors = ["#d73027", "#fc8d59", "#fee08b", "#d9ef8b", "#1a9850"]
    indices = [int(i) - 1 for i in rating_counts.index if 1 <= int(i) <= 5]
    bar_colors = [colors[i] for i in indices]
    
    bars = plt.bar(
        rating_counts.index, 
        rating_counts.values, 
        color=bar_colors, 
        edgecolor="w", 
        linewidth=1.2
    )
    
    for bar, val in zip(bars, rating_counts.values):
        plt.text(
            bar.get_x() + bar.get_width() / 2, 
            bar.get_height() + (max(rating_counts.values) * 0.01),
            str(val), 
            ha="center", 
            va="bottom", 
            fontsize=10,
            fontweight="bold"
        )
        
    plt.title("Distribusi Tingkat Kepuasan (Rating)", fontsize=13, pad=15)
    plt.xlabel("Tingkat Rating")
    plt.ylabel("Frekuensi Ulasan")
    plt.xticks([1, 2, 3, 4, 5])
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Grafik distribusi rating berhasil disimpan: {output_path}")


def generate_variant_distribution_chart(df: pd.DataFrame, output_path: str) -> None:
    """Menghasilkan grafik untuk varian produk dengan keterlibatan tertinggi."""
    plt.figure(figsize=(10, 5))
    variant_counts = df["varian"].value_counts().head(10)
    
    sns.barplot(
        x=variant_counts.index, 
        y=variant_counts.values, 
        palette="crest"
    )
    
    plt.title("10 Varian dengan Volume Aktivitas Tertinggi", fontsize=13, pad=15)
    plt.xlabel("Label Varian")
    plt.ylabel("Frekuensi Tercatat")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Grafik distribusi varian berhasil disimpan: {output_path}")


def generate_complaint_wordcloud(df: pd.DataFrame, output_path: str) -> bool:
    """Menghasilkan WordCloud asosiasi kata berdasarkan ulasan dengan sentimen negatif."""
    negative_df = df[df["rating"] <= 3]
    if negative_df.empty:
        logger.info("Volume ulasan negatif tidak mencukupi untuk generasi Wordcloud.")
        return False
        
    raw_text = " ".join(negative_df["review"].dropna().astype(str).tolist())
    tokens = tokenize_text(raw_text)
    
    if not tokens:
        logger.info("Teks kosong pasca proses penyaringan stopword.")
        return False

    freq = build_ngram_frequencies(tokens, min_count=2)
    if not freq:
        logger.info("Frekuensi korpus N-gram berada di bawah batas minimum.")
        return False

    wc = WordCloud(
        width=1200, 
        height=600,
        background_color="white",
        colormap="Reds",
        max_words=60,
        prefer_horizontal=0.8,
        collocations=False,
    ).generate_from_frequencies(freq)

    plt.figure(figsize=(14, 7))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.title("Peta Frekuensi Keluhan Spesifik (N-Gram)", fontsize=14, pad=15)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300)
    plt.close()
    logger.info(f"Aset visual Wordcloud berhasil disimpan: {output_path}")
    return True


def extract_top_phrases(df: pd.DataFrame, limit: int = 10) -> List[Tuple[str, int]]:
    """Mengekstraksi istilah dan frasa keluhan utama berdasarkan statistik kemunculan."""
    negative_df = df[df["rating"] <= 3]
    if negative_df.empty:
        return []
        
    raw_text = " ".join(negative_df["review"].dropna().astype(str).tolist())
    tokens = tokenize_text(raw_text)
    freq = build_ngram_frequencies(tokens, min_count=2)
    
    phrases = {k: v for k, v in freq.items() if " " in k}
    singles = {k: v for k, v in freq.items() if " " not in k}
    
    ranked_phrases = sorted(phrases.items(), key=lambda x: x[1], reverse=True)[:limit // 2 + 2]
    ranked_singles = sorted(singles.items(), key=lambda x: x[1], reverse=True)[:limit // 2]
    
    combined_ranking = sorted(ranked_phrases + ranked_singles, key=lambda x: x[1], reverse=True)
    return combined_ranking[:limit]


def generate_report(csv_path: str) -> str:
    """Rutinitas utama: Memproses data input dan merangkai laporan Markdown lengkap."""
    if not os.path.isfile(csv_path):
        logger.error(f"Kegagalan I/O: Berkas tidak ditemukan pada jalur '{csv_path}'")
        sys.exit(1)

    try:
        df = pd.read_csv(csv_path)
    except Exception as err:
        logger.error(f"Kegagalan pemuatan DataFrame parsing CSV: {err}")
        sys.exit(1)

    required_cols = {"rating", "review", "varian"}
    missing_cols = required_cols - set(df.columns)
    if missing_cols:
        logger.error(f"Integritas data parsial: Skema kekurangan kolom obligatori {missing_cols}")
        sys.exit(1)

    total_reviews = len(df)
    logger.info(f"Dataset berhasil dimuat. Total rekaman data: {total_reviews:,}")

    basename = os.path.splitext(os.path.basename(csv_path))[0]
    report_dir = os.path.join("reports", basename)
    assets_dir = os.path.join(report_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    chart_rating = os.path.join(assets_dir, "rating_distribution.png")
    chart_variant = os.path.join(assets_dir, "variant_distribution.png")
    chart_wc = os.path.join(assets_dir, "wordcloud_complaint.png")

    generate_rating_distribution_chart(df, chart_rating)
    generate_variant_distribution_chart(df, chart_variant)
    has_wordcloud = generate_complaint_wordcloud(df, chart_wc)

    avg_rating = df["rating"].mean()
    rating_counts = df["rating"].value_counts().sort_index()
    variant_counts = df["varian"].value_counts().head(10)
    top_words = extract_top_phrases(df, limit=10)
    
    negative_reviews = df[df["rating"] <= 3]
    positive_reviews = df[df["rating"] >= 4]
    
    negative_pct = (len(negative_reviews) / total_reviews) * 100 if total_reviews else 0.0
    positive_pct = (len(positive_reviews) / total_reviews) * 100 if total_reviews else 0.0

    sample_negative = negative_reviews["review"].dropna().head(4).tolist()
    sample_positive = positive_reviews["review"].dropna().head(4).tolist()

    report_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rating_rows = "".join(
        f"| {format_rating(r)} | {rating_counts.get(r, 0):,} | {rating_counts.get(r, 0)/total_reviews*100:.1f}% |\n"
        for r in range(1, 6)
    )
    
    variant_rows = "".join(
        f"| {v} | {c:,} |\n" for v, c in variant_counts.items()
    )

    top_words_str = ", ".join(f"**{w}** ({c}x)" for w, c in top_words) if top_words else "_Data tidak relevan_"
    
    top_phrases = [(w, c) for w, c in top_words if " " in w]
    top_phrases_str = ", ".join(f"**{w}** ({c}x)" for w, c in top_phrases) if top_phrases else top_words_str

    def format_samples(samples: List[str]) -> str:
        return "".join(f'> *"{s[:160]}..."*\n>\n' for s in samples) if samples else "> _Sampel tidak disuplai._\n"

    negative_samples_str = format_samples(sample_negative)
    positive_samples_str = format_samples(sample_positive)

    wordcloud_section = f"""
## 3. Analisis Tekstual Keluhan (Objek Sentimen Negatif)

Pemetaan frasa dan leksikon dominan dari pengulas dengan kepuasan minim:

![Peta Visual Keluhan](assets/wordcloud_complaint.png)

**Inspeksi Frasa Anomali Terbanyak:** {top_phrases_str}
""" if has_wordcloud else ""

    markdown_content = f"""# Laporan Analisis Data Eksploratif (EDA)

*Dokumen ini bersifat kuantitatif, disusun untuk melakukan tinjauan tingkat kepuasan terhadap subjek `{(basename)}`.*

> **Tanggal Sintesis:** {report_timestamp}  
> **Unit Sumber:** `{csv_path}`  
> **Volume Populasi:** {total_reviews:,} Entri

---

## Ringkasan Eksekutif

Tabel berikut menunjukkan parameter kesehatan matriks pada korpus ini.

| Parameter Evaluasi | Indikator |
|-------------------|-----------|
| Agregat Entri Pengujian | {total_reviews:,} |
| Rerata Skor Kinerja | {avg_rating:.2f} / 5.00 |
| Margin Persetujuan Publik (Rating ≥ 4) | {len(positive_reviews):,} ({positive_pct:.1f}%) |
| Tingkat Penolakan/Atribut Isu (Rating ≤ 3) | {len(negative_reviews):,} ({negative_pct:.1f}%) |
| Total Keragaman Varian Identifikasi | {df["varian"].nunique()} |

---

## 1. Indikator Sentimen Kepuasan

Representasi dari penilaian publik melalui skor 1-5 tanpa kompresi.

![Histogram Rating](assets/rating_distribution.png)

| Klasifikasi | Frekuensi | Persentil |
|-------------|-----------|-----------|
{rating_rows}

---

## 2. Peringkat Keterlibatan Berdasarkan Varian

Metrik ini memecah distribusi adopsi pengguna terfokus pada 10 unit varian tertinggi.

![Peringkat Varian](assets/variant_distribution.png)

| Klasifikasi Varian | Intensitas Volume |
|--------------------|-------------------|
{variant_rows}

---
{wordcloud_section}

## 4. Log Ekstraksi Anotasi Publik

Bagian ini menyorot respon natural secara sekuensial yang mendukung data statistik utama.

### 4.1 Kuadran Positif (Rating 4-5)

{positive_samples_str}

### 4.2 Kuadran Negatif / Defisit (Rating 1-3)

{negative_samples_str}

---

> [!TIP]
> **Korelasi Evaluasi Operasional**
> - Tren sentimen positif terkontrol mengasumsikan keberterimaan produk publik di indikator **{positive_pct:.1f}%**.
> - Peringkat dasar berada pada titik ketetapan koefisien rating **{avg_rating:.2f}** agregat.

> [!WARNING]
> **Kerawanan Resiliensi Sistem/Produk**
> - Titik deviasi kelemahan yang perlu diinvestigasi menunjuk ke persentase minor **{negative_pct:.1f}%**.
> - Frasa bergejala masalah secara komputasi menunjuk tendensi pada: {top_phrases_str}.

---
*Dokumen ini merupakan hasil komputasi model pipeline `generate_report.py`*.
"""

    report_path = os.path.join(report_dir, f"report_{basename}.md")
    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        logger.info(f"Integrasi laporan operasional berhasil ditulis ulang pada node: {report_path}")
    except Exception as err:
        logger.error(f"Kegagalan subsistem file komit Markdown final: {err}")
        sys.exit(1)

    return report_path


if __name__ == "__main__":
    if len(sys.argv) < 2:
        logger.warning(
            "Kegagalan Sintaks. Konstruksi perintah: "
            "python engines/generate_report.py <jalur_relatif_csv>"
        )
        sys.exit(1)

    target_dataset_path = sys.argv[1]
    logger.info("Memulai alur inisialisasi modul...")
    generate_report(target_dataset_path)
