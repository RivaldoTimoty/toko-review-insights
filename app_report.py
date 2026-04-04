import streamlit as st
import subprocess
import os
import glob

st.set_page_config(page_title="EDA Report Generator", page_icon="📊", layout="centered")

st.title("📊 Auto EDA Report Generator")
st.markdown("""
Pilih file CSV hasil crawling, lalu klik **Generate**. 
Laporan Markdown lengkap beserta grafik akan otomatis dibuat di folder `reports/`.
""")

csv_files = glob.glob("data/*.csv")
csv_labels = [os.path.basename(f) for f in csv_files]

if not csv_files:
    st.warning("⚠️ Belum ada file CSV di folder `data/`. Lakukan crawling terlebih dahulu.")
else:
    col1, col2 = st.columns([2, 1])

    with col1:
        selected_label = st.selectbox("📁 Pilih file CSV:", csv_labels)
        selected_path  = csv_files[csv_labels.index(selected_label)]

    with col2:
        st.metric("File Terpilih", selected_label)

    st.info(f"📂 Path lengkap: `{selected_path}`")

    if st.button("🚀 Generate Report", use_container_width=True):
        log_placeholder = st.empty()
        custom_env = os.environ.copy()
        custom_env["PYTHONIOENCODING"] = "utf-8"

        command = ["py", "-u", "engines/generate_report.py", selected_path]

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
                basename   = os.path.splitext(selected_label)[0]
                report_dir = os.path.join("reports", basename)
                report_md  = os.path.join(report_dir, f"report_{basename}.md")

                st.success(f"🎉 Laporan berhasil dibuat!")

                if os.path.exists(report_md):
                    with open(report_md, "r", encoding="utf-8") as f:
                        content = f.read()

                    with st.expander("📄 Preview Laporan", expanded=True):
                        st.markdown(content)

                    with open(report_md, "rb") as f:
                        st.download_button(
                            label=f"⬇️ Download report_{basename}.md",
                            data=f,
                            file_name=f"report_{basename}.md",
                            mime="text/markdown"
                        )
            else:
                st.error("❌ Terjadi kesalahan saat generate laporan.")

        except Exception as e:
            st.error(f"❌ Gagal: {e}")
