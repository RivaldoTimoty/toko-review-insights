import streamlit as st
import subprocess
import os
import glob
import pandas as pd

VENV_PYTHON = r"C:\Users\Asus\OneDrive\Documents\GitHub\Project\.venv\Scripts\python.exe"

st.set_page_config(
    page_title="Tokopedia Review Crawler",
    page_icon="🕷️",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,300&family=DM+Mono:wght@400;500&display=swap');

*, *::before, *::after {
    box-sizing: border-box;
}

html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    color: #e8f5e9 !important;
}

.stApp {
    background-color: #040d06;
    background-image:
        radial-gradient(ellipse 80% 60% at 90% 0%, rgba(0, 200, 120, 0.07) 0%, transparent 60%),
        radial-gradient(ellipse 60% 50% at 10% 100%, rgba(0, 150, 90, 0.06) 0%, transparent 55%),
        repeating-linear-gradient(
            0deg,
            transparent,
            transparent 39px,
            rgba(255,255,255,0.012) 40px
        ),
        repeating-linear-gradient(
            90deg,
            transparent,
            transparent 39px,
            rgba(255,255,255,0.012) 40px
        );
    background-attachment: fixed;
    min-height: 100vh;
}

.block-container {
    padding-top: 2.5rem !important;
    padding-bottom: 4rem !important;
    max-width: 780px !important;
}

.header-wrap {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 0;
    padding: 3.5rem 2rem 3rem;
    margin-bottom: 2.5rem;
    position: relative;
}

.header-wrap::before {
    content: '';
    position: absolute;
    inset: 0;
    border: 1px solid rgba(0, 230, 130, 0.12);
    border-radius: 24px;
    background: linear-gradient(160deg, rgba(0, 200, 100, 0.06) 0%, rgba(0, 0, 0, 0) 60%);
    pointer-events: none;
}

.header-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 0.22em;
    text-transform: uppercase;
    color: rgba(0, 230, 130, 0.6);
    margin-bottom: 1rem;
}

.header-wrap h1 {
    font-size: 2.6rem;
    font-weight: 700;
    letter-spacing: -0.04em;
    line-height: 1.05;
    margin: 0 0 0.75rem;
    color: #e8f5e9;
    text-align: center;
}

.header-wrap h1 em {
    font-style: normal;
    color: #00e682;
}

.header-sub {
    font-size: 0.95rem;
    color: rgba(200, 240, 215, 0.45);
    font-weight: 300;
    letter-spacing: 0.01em;
}

.header-badge {
    margin-top: 1.5rem;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(0, 200, 100, 0.08);
    border: 1px solid rgba(0, 200, 100, 0.2);
    border-radius: 100px;
    padding: 5px 14px 5px 10px;
    font-size: 0.72rem;
    font-family: 'DM Mono', monospace;
    color: rgba(0, 230, 130, 0.8);
    letter-spacing: 0.05em;
}

.header-badge::before {
    content: '';
    display: inline-block;
    width: 6px;
    height: 6px;
    border-radius: 50%;
    background: #00e682;
    box-shadow: 0 0 0 2px rgba(0,230,130,0.25);
}

.stTabs [data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.025) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 16px !important;
    padding: 5px !important;
    gap: 4px !important;
    margin-bottom: 1.5rem;
}

.stTabs [data-baseweb="tab"] {
    border-radius: 11px !important;
    font-weight: 500 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.01em;
    padding: 0.65rem 1.25rem !important;
    color: rgba(200, 240, 215, 0.45) !important;
    transition: color 0.2s ease !important;
    border: none !important;
    background: transparent !important;
}

.stTabs [aria-selected="true"] {
    background: rgba(0, 200, 100, 0.14) !important;
    color: #00e682 !important;
    border: 1px solid rgba(0, 200, 100, 0.25) !important;
}

.stTabs [data-baseweb="tab-highlight"] {
    display: none !important;
}

.info-card {
    background: rgba(0, 200, 100, 0.04);
    border: 1px solid rgba(0, 200, 100, 0.1);
    border-left: 3px solid rgba(0, 200, 100, 0.5);
    border-radius: 12px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 1.5rem;
}

.info-card .card-title {
    font-weight: 600;
    font-size: 0.9rem;
    color: #00e682;
    margin-bottom: 4px;
    display: flex;
    align-items: center;
    gap: 7px;
}

.info-card .card-desc {
    font-size: 0.83rem;
    color: rgba(200, 240, 215, 0.5);
    font-weight: 300;
    line-height: 1.55;
    margin: 0;
}

label,
[data-testid="stWidgetLabel"] p,
.stTextInput label,
.stSelectbox label {
    color: rgba(200, 240, 215, 0.75) !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    margin-bottom: 6px !important;
}

.stTextInput > div > div > input,
.stSelectbox > div > div > div {
    background: rgba(255, 255, 255, 0.03) !important;
    border: 1px solid rgba(255, 255, 255, 0.08) !important;
    border-radius: 12px !important;
    color: #c8f0d7 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.82rem !important;
    padding: 0.7rem 1rem !important;
    transition: border-color 0.25s ease, background 0.25s ease !important;
}

.stTextInput > div > div > input:focus {
    background: rgba(0, 200, 100, 0.05) !important;
    border-color: rgba(0, 200, 100, 0.45) !important;
    box-shadow: 0 0 0 3px rgba(0, 200, 100, 0.08) !important;
    outline: none !important;
}

.stTextInput input::placeholder {
    color: rgba(200, 240, 215, 0.2) !important;
    font-style: italic;
}

.stButton > button {
    background: rgba(0, 200, 100, 0.1) !important;
    color: #00e682 !important;
    border: 1px solid rgba(0, 200, 100, 0.35) !important;
    border-radius: 12px !important;
    font-weight: 600 !important;
    font-size: 0.87rem !important;
    letter-spacing: 0.04em !important;
    padding: 0.75rem 2rem !important;
    width: 100% !important;
    transition: all 0.25s ease !important;
    font-family: 'DM Sans', sans-serif !important;
    position: relative;
    overflow: hidden;
}

.stButton > button:hover {
    background: rgba(0, 200, 100, 0.18) !important;
    border-color: rgba(0, 200, 100, 0.6) !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 24px rgba(0, 200, 100, 0.15) !important;
}

.stButton > button:active {
    transform: translateY(0px) !important;
    box-shadow: none !important;
}

.stAlert {
    background: rgba(255, 255, 255, 0.03) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(255,255,255,0.07) !important;
}

[data-testid="stAlertContainer"] p {
    color: rgba(200, 240, 215, 0.8) !important;
    font-size: 0.87rem !important;
}

div[data-testid="stAlertContainer"][data-baseweb="notification"] {
    background: rgba(0, 200, 100, 0.06) !important;
    border-color: rgba(0, 200, 100, 0.2) !important;
}

[data-testid="stDataFrame"] {
    background: rgba(0,0,0,0.25) !important;
    border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    overflow: hidden;
}

[data-testid="stExpander"] {
    background: rgba(0,0,0,0.2) !important;
    border: 1px solid rgba(255, 255, 255, 0.07) !important;
    border-radius: 14px !important;
    overflow: hidden !important;
}

[data-testid="stExpander"] summary {
    padding: 0.9rem 1.2rem !important;
    background: rgba(255,255,255,0.02) !important;
}

[data-testid="stExpander"] summary:hover {
    background: rgba(0, 200, 100, 0.04) !important;
}

[data-testid="stExpander"] summary span,
[data-testid="stExpander"] summary p {
    color: rgba(200, 240, 215, 0.8) !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
}

.stCodeBlock, code, pre {
    background: rgba(0, 0, 0, 0.45) !important;
    border: 1px solid rgba(255,255,255,0.06) !important;
    border-radius: 12px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.75rem !important;
    color: rgba(150, 230, 180, 0.8) !important;
}

.stSelectbox [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.03) !important;
    border: 1px solid rgba(255,255,255,0.08) !important;
    border-radius: 12px !important;
    color: #c8f0d7 !important;
}

.stDownloadButton > button {
    background: rgba(255,255,255,0.04) !important;
    border: 1px solid rgba(255,255,255,0.1) !important;
    color: rgba(200, 240, 215, 0.7) !important;
    border-radius: 10px !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    transition: all 0.2s ease !important;
}

.stDownloadButton > button:hover {
    background: rgba(0, 200, 100, 0.08) !important;
    border-color: rgba(0, 200, 100, 0.3) !important;
    color: #00e682 !important;
}

h3 {
    font-size: 0.9rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.06em !important;
    text-transform: uppercase !important;
    color: rgba(200, 240, 215, 0.5) !important;
    margin-bottom: 0.75rem !important;
    padding-bottom: 0.5rem !important;
    border-bottom: 1px solid rgba(255,255,255,0.05) !important;
}

hr {
    border: none !important;
    border-top: 1px solid rgba(255,255,255,0.06) !important;
    margin: 2rem 0 1rem !important;
}

.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 0.75rem;
    padding: 3rem 2rem;
    border: 1px dashed rgba(255,255,255,0.1);
    border-radius: 16px;
    text-align: center;
}

.empty-state .icon {
    font-size: 2.2rem;
    opacity: 0.35;
}

.empty-state p {
    color: rgba(200, 240, 215, 0.35) !important;
    font-size: 0.88rem;
    max-width: 280px;
    line-height: 1.6;
}

small {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.7rem !important;
    color: rgba(200, 240, 215, 0.3) !important;
}

[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] li {
    color: rgba(200, 240, 215, 0.7) !important;
    font-size: 0.92rem !important;
}

::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0, 200, 100, 0.15); border-radius: 10px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0, 200, 100, 0.3); }

.footer-text {
    text-align: center;
    color: rgba(200, 240, 215, 0.18);
    font-size: 0.75rem;
    font-family: 'DM Mono', monospace;
    letter-spacing: 0.08em;
    margin-top: 1.5rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="header-wrap">
    <span class="header-eyebrow">scraping engine</span>
    <h1>Tokopedia<br><em>Review Crawler</em></h1>
    <p class="header-sub">Extract product reviews automatically into structured CSV</p>
    <span class="header-badge">Playwright + Streamlit</span>
</div>
""", unsafe_allow_html=True)

tab_all, tab_bad, tab_report = st.tabs([
    "🛒  All Reviews",
    "📉  Bad Reviews (1–3★)",
    "📊  Generate Report"
])

def run_crawler(script_name, url, output_path):
    st.info(f"Starting engine — output: `{output_path}`")
    log_placeholder = st.empty()
    
    cmd_python = VENV_PYTHON if os.path.exists(VENV_PYTHON) else "py"
    
    command = [cmd_python, "-u", f"engines/{script_name}", url.strip(), output_path]
    
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
            env=custom_env,
            cwd=os.path.dirname(os.path.abspath(__file__))
        )
        
        full_logs = ""
        for line in iter(process.stdout.readline, ""):
            full_logs += line
            log_placeholder.code(full_logs, language="bash")
            
        process.stdout.close()
        process.wait()
        
        if process.returncode == 0:
            st.success(f"Done — data saved to `{output_path}`")
            if os.path.exists(output_path):
                with open(output_path, "rb") as file:
                    st.download_button(
                        label=f"⬇  Download {os.path.basename(output_path)}",
                        data=file,
                        file_name=os.path.basename(output_path),
                        mime="text/csv"
                    )
                
                try:
                    df = pd.read_csv(output_path)
                    st.markdown("### Data Preview")
                    st.dataframe(df.head(10), use_container_width=True)
                except:
                    pass
        else:
            st.error("Execution failed — check logs above.")
    except Exception as e:
        st.error(f"Failed to run engine: {e}")

with tab_all:
    st.markdown("""
    <div class="info-card">
        <div class="card-title">All Reviews Mode</div>
        <p class="card-desc">
            Crawls every available review for the product — no rating filters applied.
            Results are exported as a clean CSV file ready for analysis.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    url_all = st.text_input("Product URL", 
                           value="https://www.tokopedia.com/xiaomi/xiaomi-mi-tv-stick-android-9-ringan-dan-portable-official-store-1733172492566169113",
                           key="url_all",
                           placeholder="https://www.tokopedia.com/...")
    
    fn_all = st.text_input("Output Filename", value="full_reviews", key="fn_all",
                           placeholder="e.g. full_reviews")
    
    if st.button("Run Crawler", use_container_width=True, key="btn_all"):
        if not url_all.strip() or not fn_all.strip():
            st.error("Inputs cannot be empty.")
        else:
            clean_fn = fn_all.strip()
            if not clean_fn.endswith(".csv"): clean_fn += ".csv"
            output_path = os.path.join("data", clean_fn)
            os.makedirs("data", exist_ok=True)
            run_crawler("agent_ulasan.py", url_all, output_path)

with tab_bad:
    st.markdown("""
    <div class="info-card">
        <div class="card-title">Bad Reviews Mode (1–3★)</div>
        <p class="card-desc">
            Browser will automatically apply 1, 2, and 3-star filters before collecting data —
            useful for isolating negative sentiment for analysis.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    url_bad = st.text_input("Product URL", 
                           value="https://www.tokopedia.com/xiaomi/xiaomi-mi-tv-stick-android-9-ringan-dan-portable-official-store-1733172492566169113",
                           key="url_bad",
                           placeholder="https://www.tokopedia.com/...")
    
    fn_bad = st.text_input("Output Filename", value="bad_reviews", key="fn_bad",
                           placeholder="e.g. bad_reviews")
    
    if st.button("Run Crawler", use_container_width=True, key="btn_bad"):
        if not url_bad.strip() or not fn_bad.strip():
            st.error("Inputs cannot be empty.")
        else:
            clean_fn = fn_bad.strip()
            if not clean_fn.endswith(".csv"): clean_fn += ".csv"
            output_path = os.path.join("data", clean_fn)
            os.makedirs("data", exist_ok=True)
            run_crawler("agent_ulasan_bad.py", url_bad, output_path)

with tab_report:
    st.markdown("### Select CSV File")
    
    csv_files = glob.glob("data/*.csv")
    csv_labels = [os.path.basename(f) for f in csv_files]
    
    if not csv_files:
        st.markdown("""
        <div class="empty-state">
            <span class="icon">📭</span>
            <p>No CSV files found in <code>data/</code>.<br>Run a crawl first to generate data.</p>
        </div>
        """, unsafe_allow_html=True)
    else:
        selected_label = st.selectbox("CSV File", options=csv_labels, label_visibility="collapsed")
        selected_path = os.path.join("data", selected_label)
        
        st.markdown(f"<small>{selected_path}</small>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        if st.button("Generate Report", use_container_width=True, key="btn_report"):
            log_placeholder = st.empty()
            cmd_python = VENV_PYTHON if os.path.exists(VENV_PYTHON) else "py"
            command = [cmd_python, "-u", "engines/generate_report.py", selected_path]
            
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
                    env=custom_env,
                    cwd=os.path.dirname(os.path.abspath(__file__))
                )
                
                full_logs = ""
                for line in iter(process.stdout.readline, ""):
                    full_logs += line
                    log_placeholder.code(full_logs, language="bash")
                
                process.stdout.close()
                process.wait()
                
                if process.returncode == 0:
                    basename = os.path.splitext(selected_label)[0]
                    report_path = os.path.join("reports", basename, f"report_{basename}.md")
                    st.success("Report generated successfully.")
                    
                    if os.path.exists(report_path):
                        with open(report_path, "r", encoding="utf-8") as f:
                            report_content = f.read()
                        
                        with st.expander("Report Preview", expanded=True):
                            st.markdown(report_content)
                            
                        st.download_button(
                            label="⬇  Download Markdown Report",
                            data=report_content,
                            file_name=f"report_{basename}.md",
                            mime="text/markdown"
                        )
                else:
                    st.error("Failed to generate report — check logs above.")
            except Exception as e:
                st.error(f"Error: {e}")

st.markdown("---")
st.markdown("""
<p class="footer-text">tokopedia review crawler &nbsp;·&nbsp; playwright + streamlit</p>
""", unsafe_allow_html=True)