import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from wordcloud import WordCloud

file_path = "data/mini_proyektor.csv"
output_dir = "assets"

try:
    if not os.path.exists(file_path):
        print(f"ERROR: File {file_path} not found")
        exit(1)
        
    df = pd.read_csv(file_path)
    plt.style.use('ggplot')
    
    plt.figure(figsize=(8, 5))
    rating_counts = df['rating'].value_counts().sort_index()
    sns.barplot(x=rating_counts.index, y=rating_counts.values, palette='viridis')
    plt.title('Distribusi Rating')
    plt.xlabel('Rating (Bintang)')
    plt.ylabel('Jumlah Ulasan')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'rating_distribution.png'), dpi=150)
    plt.close()
    
    plt.figure(figsize=(8, 5))
    varian_counts = df['varian'].value_counts()
    sns.barplot(x=varian_counts.index, y=varian_counts.values, palette='magma')
    plt.title('Distribusi Pembelian per Varian')
    plt.xlabel('Varian')
    plt.ylabel('Jumlah Pembelian')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'varian_distribution.png'), dpi=150)
    plt.close()
    
    komplain_df = df[df['rating'] <= 3]
    text = " ".join(komplain_df['review'].dropna().astype(str).tolist()).lower()
    
    stop_words = ["yg", "yang", "dan", "di", "ke", "dari", "untuk", "dengan", "ini", "itu", 
                  "ada", "adalah", "saja", "tapi", "karena", "kendala", "kualitas", "barang", 
                  "bermasalah", "pengiriman", "kalau", "tidak", "bisa", "sudah", "nya", 
                  "kurang", "saya", "buat", "udah", "aja", "belum", "sih", "tp", "ya",
                  "kalo", "jd", "gak", "jadi", "juga", "atau", "sama", "kok", "nya", 
                  "terus", "selengkapnya"]
                  
    for stop_word in stop_words:
        text = text.replace(f" {stop_word} ", " ")

    wc = WordCloud(width=800, height=400, background_color='white', colormap='Reds', collocations=False).generate(text)
    
    plt.figure(figsize=(10, 5))
    plt.imshow(wc, interpolation='bilinear')
    plt.axis('off')
    plt.title('Word Cloud Keluhan Utama (Rating 1-3)', fontsize=15)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, 'wordcloud_komplain.png'), dpi=150)
    plt.close()
    
    print("PLOTS_GENERATED_SUCCESSFULLY")
except Exception as e:
    print(f"ERROR: {str(e)}")
