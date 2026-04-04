import streamlit as st
import subprocess
import os

st.set_page_config(page_title="Tokopedia Crawler", page_icon="📦", layout="centered")

st.title("🕷️ Tokopedia Bad Review Crawler (Bintang 1-3)")
st.markdown("""
Aplikasi ini memungkinkan Anda melakukan *crawling* ulasan berating rendah (bintang 1, 2, dan 3) dari Tokopedia.
Browser `agent` akan secara otomatis menerapkan filter "Rating 1, 2, 3" sebelum mengambil data ulasan.
""")

st.warning("⚠️ **Catatan:** Jangan tutup browser Chrome yang akan otomatis terbuka saat proses *crawling* berlangsung.")

url_input = st.text_input("🔗 Masukkan Link/URL Produk Tokopedia:", 
                          value="https://www.tokopedia.com/xiaomi/xiaomi-mi-tv-stick-android-9-ringan-dan-portable-official-store-1733172492566169113",
                          help="Pastikan URL tersebut valid dan langsung mengarah ke halaman produk")

filename_input = st.text_input("📄 Nama File Output (tanpa ekstensi):", 
                               value="motor_bad",
                               help="Misal: 'motor' -> file output akan menjadi 'motor.csv'")

if st.button("🚀 Mulai Crawling", use_container_width=True):
    if not url_input.strip() or not filename_input.strip():
        st.error("❌ Link Produk dan Nama File tidak boleh kosong!")
    else:
        clean_filename = filename_input.strip()
        if not clean_filename.endswith(".csv"):
            clean_filename += ".csv"
        
        output_path = os.path.join("data", clean_filename)
        st.info("💡 Memulai Engine (Filter 1-3)... Silakan pantau log di bawah ini.")
        log_placeholder = st.empty()
        
        command = ["py", "-u", "engines/agent_ulasan_bad.py", url_input.strip(), output_path]
        
        custom_env = os.environ.copy()
        custom_env["PYTHONIOENCODING"] = "utf-8"
        
        try:
            process = subprocess.Popen(
                command, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.STDOUT, 
                text=True, 
                bufsize=1,
                encoding="utf-8",
                env=custom_env
            )
            
            full_logs = ""
            for line in iter(process.stdout.readline, ""):
                full_logs += line
                log_placeholder.code(full_logs, language="bash")
                
            process.stdout.close()
            process.wait()
            
            if process.returncode == 0:
                st.success(f"🎉 Selesai! Data disimpan di: **{output_path}**")
                if os.path.exists(output_path):
                    with open(output_path, "rb") as file:
                        st.download_button(
                            label=f"⬇️ Download {clean_filename}",
                            data=file,
                            file_name=clean_filename,
                            mime="text/csv"
                        )
            else:
                st.error("❌ Terjadi kesalahan pada eksekusi.")
        except Exception as e:
            st.error(f"❌ Gagal: {e}")
