import streamlit as st
import subprocess
import os

st.set_page_config(page_title="Tokopedia Crawler", page_icon="📦", layout="centered")

st.title("🕷️ Tokopedia Review Crawler")
st.markdown("""
Aplikasi ini memungkinkan Anda melakukan *crawling* ulasan (review) dari Tokopedia.
Browser `agent` akan terbuka di latar belakang untuk menstimulasi *scrolling* dan menangkap data ulasan tersebut. Seluruh data akan disimpan dalam format **Excel (CSV)**.
""")

st.warning("⚠️ **Catatan:** Jangan tutup browser Chrome yang akan otomatis terbuka saat proses *crawling* berlangsung.")

url_input = st.text_input("🔗 Masukkan Link/URL Produk Tokopedia:", 
                          value="https://www.tokopedia.com/xiaomi/xiaomi-mi-tv-stick-android-9-ringan-dan-portable-official-store-1733172492566169113",
                          help="Pastikan URL tersebut valid dan langsung mengarah ke halaman produk")

filename_input = st.text_input("📄 Nama File Output (tanpa ekstensi):", 
                               value="motor",
                               help="Misal: 'motor' -> file output akan menjadi 'motor.csv'")

if st.button("🚀 Mulai Crawling", use_container_width=True):
    if not url_input.strip() or not filename_input.strip():
        st.error("❌ Link Produk dan Nama File tidak boleh kosong!")
    else:
        clean_filename = filename_input.strip()
        if not clean_filename.endswith(".csv"):
            clean_filename += ".csv"
        
        output_path = os.path.join("data", clean_filename)
        st.info("💡 Memulai Engine... Silakan pantau log di bawah ini.")
        log_placeholder = st.empty()
        
        command = ["py", "-u", "engines/agent_ulasan.py", url_input.strip(), output_path]
        
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
