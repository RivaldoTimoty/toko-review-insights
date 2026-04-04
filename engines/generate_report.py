import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from collections import Counter
from datetime import datetime

STOP_WORDS = {
    "yg", "yang", "dan", "di", "ke", "dari", "untuk", "dengan", "ini", "itu",
    "ada", "adalah", "saja", "tapi", "karena", "kendala", "kualitas", "barang",
    "bermasalah", "pengiriman", "kalau", "tidak", "bisa", "sudah", "nya",
    "kurang", "saya", "buat", "udah", "aja", "belum", "sih", "tp", "ya",
    "kalo", "jd", "gak", "jadi", "juga", "atau", "sama", "kok",
    "terus", "selengkapnya", "banget", "sangat", "lebih", "sekali", "meski",
    "emang", "memang", "pas", "kak", "min", "tolong", "mohon", "produk",
    "seller", "toko", "beli", "bisa", "mau", "lah", "deh", "nih", "gan",
}

def star(n):
    return "⭐" * n

def tokenize(text):
    import re
    words = re.sub(r'[^\w\s]', ' ', text.lower()).split()
    return [w for w in words if w not in STOP_WORDS and len(w) > 2]

def build_ngram_frequencies(tokens, min_count=2):
    freq = Counter()

    # Unigram
    for w in tokens:
        freq[w] += 1

    # Bigram
    for i in range(len(tokens) - 1):
        phrase = f"{tokens[i]} {tokens[i+1]}"
        freq[phrase] += 1

    # Trigram
    for i in range(len(tokens) - 2):
        phrase = f"{tokens[i]} {tokens[i+1]} {tokens[i+2]}"
        freq[phrase] += 1

    # Hapus yang hanya muncul 1x (noise)
    return {k: v for k, v in freq.items() if v >= min_count}

def generate_rating_chart(df, output_path):
    plt.style.use("ggplot")
    plt.figure(figsize=(8, 5))
    rating_counts = df["rating"].value_counts().sort_index()
    colors = ["#ef4444", "#f97316", "#eab308", "#84cc16", "#22c55e"]
    idx = [i - 1 for i in rating_counts.index]
    bar_colors = [colors[i] for i in idx]
    bars = plt.bar(rating_counts.index, rating_counts.values, color=bar_colors, edgecolor="white", linewidth=1.2)
    for bar, val in zip(bars, rating_counts.values):
        plt.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.5,
                 str(val), ha="center", va="bottom", fontsize=11, fontweight="bold")
    plt.title("Distribusi Rating Ulasan", fontsize=14, fontweight="bold")
    plt.xlabel("Rating (Bintang)")
    plt.ylabel("Jumlah Ulasan")
    plt.xticks([1, 2, 3, 4, 5])
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"[OK] Chart rating disimpan: {output_path}")

def generate_varian_chart(df, output_path):
    plt.figure(figsize=(10, 5))
    varian_counts = df["varian"].value_counts().head(10)
    sns.barplot(x=varian_counts.index, y=varian_counts.values, palette="magma")
    plt.title("Top 10 Varian Terlaris", fontsize=14, fontweight="bold")
    plt.xlabel("Varian")
    plt.ylabel("Jumlah Pembelian")
    plt.xticks(rotation=35, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"[OK] Chart varian disimpan: {output_path}")

def generate_wordcloud(df, output_path):
    komplain_df = df[df["rating"] <= 3]
    if komplain_df.empty:
        print("[SKIP] Tidak ada data rating ≤ 3 untuk wordcloud.")
        return False
    raw_text = " ".join(komplain_df["review"].dropna().astype(str).tolist())
    tokens = tokenize(raw_text)
    if not tokens:
        print("[SKIP] Teks kosong setelah filter stop words.")
        return False

    freq = build_ngram_frequencies(tokens, min_count=2)
    if not freq:
        print("[SKIP] Tidak cukup frekuensi n-gram untuk wordcloud.")
        return False

    wc = WordCloud(
        width=1100, height=550,
        background_color="white",
        colormap="Reds",
        max_words=60,
        prefer_horizontal=0.7,
        collocations=False,
    ).generate_from_frequencies(freq)

    plt.figure(figsize=(14, 7))
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    plt.title("Frasa Keluhan Paling Sering (Bigram & Trigram)", fontsize=13, pad=12)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()
    print(f"[OK] Wordcloud (n-gram) disimpan: {output_path}")
    return True

def extract_top_phrases(df, n=10):
    komplain_df = df[df["rating"] <= 3]
    if komplain_df.empty:
        return []
    raw = " ".join(komplain_df["review"].dropna().astype(str).tolist())
    tokens = tokenize(raw)
    freq   = build_ngram_frequencies(tokens, min_count=2)
    # Prioritaskan frasa (bigram/trigram) di depan unigram
    phrases = {k: v for k, v in freq.items() if " " in k}
    singles = {k: v for k, v in freq.items() if " " not in k}
    ranked  = sorted(phrases.items(), key=lambda x: x[1], reverse=True)[:n//2 + 2]
    ranked += sorted(singles.items(), key=lambda x: x[1], reverse=True)[:n//2]
    return sorted(ranked, key=lambda x: x[1], reverse=True)[:n]

def generate_report(csv_path):
    if not os.path.exists(csv_path):
        print(f"[ERROR] File tidak ditemukan: {csv_path}")
        sys.exit(1)

    df = pd.read_csv(csv_path)

    required_cols = {"rating", "review", "varian"}
    if not required_cols.issubset(df.columns):
        print(f"[ERROR] Kolom wajib tidak ditemukan. Dibutuhkan: {required_cols}")
        sys.exit(1)

    print(f"[OK] Data dimuat: {len(df):,} ulasan")

    basename = os.path.splitext(os.path.basename(csv_path))[0]
    report_dir = os.path.join("reports", basename)
    assets_dir = os.path.join(report_dir, "assets")
    os.makedirs(assets_dir, exist_ok=True)

    chart_rating  = os.path.join(assets_dir, "rating_distribution.png")
    chart_varian  = os.path.join(assets_dir, "varian_distribution.png")
    chart_wc      = os.path.join(assets_dir, "wordcloud_komplain.png")

    generate_rating_chart(df, chart_rating)
    generate_varian_chart(df, chart_varian)
    wc_ok = generate_wordcloud(df, chart_wc)

    total        = len(df)
    avg_rating   = df["rating"].mean()
    rating_counts = df["rating"].value_counts().sort_index()
    varian_counts = df["varian"].value_counts().head(10)
    top_words    = extract_top_phrases(df, 10)
    bad_reviews  = df[df["rating"] <= 3]
    good_reviews = df[df["rating"] >= 4]
    bad_pct      = len(bad_reviews) / total * 100
    good_pct     = len(good_reviews) / total * 100

    sample_bad  = bad_reviews["review"].dropna().head(3).tolist()
    sample_good = good_reviews["review"].dropna().head(3).tolist()

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    rating_table_rows = ""
    for r in range(1, 6):
        count = rating_counts.get(r, 0)
        pct   = count / total * 100
        rating_table_rows += f"| {star(r)} | {count:,} | {pct:.1f}% |\n"

    varian_table_rows = ""
    for v, c in varian_counts.items():
        varian_table_rows += f"| {v} | {c:,} |\n"

    top_words_text = ", ".join(f"**{w}** ({c}x)" for w, c in top_words) if top_words else "_Tidak ada._"

    top_phrases_only = [(w, c) for w, c in top_words if " " in w]
    top_phrases_text = ", ".join(f"**{w}** ({c}x)" for w, c in top_phrases_only) if top_phrases_only else top_words_text

    bad_samples_text = ""
    for s in sample_bad:
        bad_samples_text += f'> *"{s[:150]}..."*\n>\n'

    good_samples_text = ""
    for s in sample_good:
        good_samples_text += f'> *"{s[:150]}..."*\n>\n'

    wc_section = ""
    if wc_ok:
        wc_section = f"""
## ☁️ 3. Word Cloud Keluhan (Rating 1–3)

Frasa dan kata yang paling sering muncul pada ulasan bintang 1–3 (bigram & trigram):

![Word Cloud](assets/wordcloud_komplain.png)

**Frasa keluhan terbanyak:** {top_phrases_text}
"""

    report_md = f"""# 📊 Laporan EDA — `{basename}`
> Dihasilkan secara otomatis pada **{now}**  
> Sumber data: `{csv_path}` · Total: **{total:,} ulasan**

---

## 📈 Ringkasan Utama

| Metrik | Nilai |
|--------|-------|
| Total Ulasan | {total:,} |
| Rata-rata Rating | {avg_rating:.2f} ⭐ |
| Ulasan Positif (≥ 4 ⭐) | {len(good_reviews):,} ({good_pct:.1f}%) |
| Ulasan Negatif (≤ 3 ⭐) | {len(bad_reviews):,} ({bad_pct:.1f}%) |
| Jumlah Varian | {df["varian"].nunique()} |

---

## ⭐ 1. Distribusi Rating

![Distribusi Rating](assets/rating_distribution.png)

| Rating | Jumlah | Persentase |
|--------|--------|------------|
{rating_table_rows}

---

## 🎨 2. Distribusi Varian Terlaris

![Distribusi Varian](assets/varian_distribution.png)

| Varian | Jumlah Penjualan |
|--------|-----------------|
{varian_table_rows}

---
{wc_section}
---

## 💬 4. Contoh Ulasan

### 👍 Ulasan Positif (Bintang 4–5)

{good_samples_text}

### 👎 Ulasan Negatif (Bintang 1–3)

{bad_samples_text}

---

> [!TIP]
> **Insight Positif**
> - Produk mendapatkan rating rata-rata **{avg_rating:.2f}** dari skala 5.
> - **{good_pct:.1f}%** pembeli memberikan rating tinggi (bintang 4 atau 5).

> [!WARNING]
> **Insight Negatif**
> - **{bad_pct:.1f}%** pembeli memberikan rating rendah (bintang 1–3).
> - Frasa keluhan paling sering: {top_phrases_text}

---
*Laporan ini dihasilkan otomatis oleh `engines/generate_report.py`*
"""

    report_path = os.path.join(report_dir, f"report_{basename}.md")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_md)

    print(f"\n[DONE] Laporan berhasil dibuat!")
    print(f"       → {report_path}")
    return report_path

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: py engines/generate_report.py <path_ke_csv>")
        print("Contoh: py engines/generate_report.py data/mini_proyektor.csv")
        sys.exit(1)

    generate_report(sys.argv[1])
