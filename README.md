# Toko-Review-Insights: Automated E-Commerce Sentiment & NLP Pipeline 🕷️

## Overview
Toko-Review-Insights is an end-to-end data extraction and analysis pipeline designed to scrape, structure, and analyze product reviews from Tokopedia. By combining robust browser automation (Playwright) with Natural Language Processing (NLP), this tool bypasses traditional aggregate metrics to uncover actionable consumer insights, recurring pain points, and product deficit areas. 

## Business Value
Standard e-commerce dashboards focus on top-level metrics (e.g., 4.5 average rating). However, the underlying qualitative data—the root cause of negative sentiment—is largely unstructured. This project automates the ETL (Extract, Transform, Load) process and directly performs Exploratory Data Analysis (EDA) on textual feedback, highlighting critical n-gram anomalies (complaints) efficiently.

## Core Architecture
The system features a unified premium frontend interface wrapping three core data engines:
1. **Comprehensive Extraction Engine (All Reviews)**: Crawls paginated product reviews indiscriminately, building a complete textual and categorical dataset.
2. **Deficit/Negative Sentiment Engine (1-3★)**: Pre-filters the DOM to isolate lower-quartile ratings. Ideal for root-cause analysis of negative sentiment.
3. **Automated EDA & NLP Reporting System**: Consumes extracted CSVs to synthesize a markdown-based analytical report. Generates frequency distributions, top variant metrics, and complaint-driven WordClouds utilizing custom Bigram/Trigram tokenization.

## Technical Methodology
- **Headful Web Scraping**: Adapts to strict bot-mitigation mechanisms by utilizing Playwright headful operations, introducing realistic human interactions (scroll jitters, DOM observation delays).
- **DOM-based Rating Extraction**: Bypasses missing text labels by algorithmically scoring SVG node properties (`aria-label`, matrix color signatures `#FFD45F`) for robust star-rating calculations.
- **Stopword & Tokenization Tuning**: Custom textual pipeline configured specifically for Indonesian e-commerce conversational linguistics (e.g., removing stop words like "gan", "yg", "kalo").

## Project Directory
```text
.
├── app.py                  # Streamlit Unified Analytics Interface
├── engines/
│   ├── agent_ulasan.py     # Unfiltered Web Scraper
│   ├── agent_ulasan_bad.py # Negative Sentiment Web Scraper
│   └── generate_report.py  # NLP & Statistical Reporting Engine
├── data/                   # Target directory for CSV datasets
├── reports/                # Target directory for generated Markdown EDA
└── assets/                 # Supporting CSS/Visual rendering assets
```

## System Requirements & Setup
Requires Python 3.10 or higher.

```bash
# 1. Initialize Virtual Environment
python -m venv .venv
source .venv/Scripts/activate

# 2. Install Pipeline Dependencies
pip install streamlit playwright wordcloud pandas matplotlib seaborn

# 3. Provision Browser Binaries
playwright install chromium
```

## Execution
Launch the primary GUI application:
```bash
streamlit run app.py
```
*Note: Do not minimize or interact heavily with the Chromium instance spawned during extraction. It relies on page visibility and viewport heuristics to maintain session validity.*

## Analytics Output
The report synthesis module outputs an analysis payload in `./reports/<dataset_name>/`:
- `report_<dataset_name>.md`: Comprehensive NLP & Sentiment Markdown Report.
- `/assets`: Vectorized distributions and N-gram visualizations.

**Why N-Grams?** The WordCloud methodology isolates **Bigrams** and **Trigrams** instead of Unigrams. Identifying pairs like "layar pecah" (broken screen) or "pengiriman lama" (late delivery) is exponentially more actionable than single words like "layar" or "pengiriman".

## Technical Constraints & Considerations
- **Frontend Mutability**: E-commerce platforms deploy A/B tests and aggressive UI changes. Element selectors (`data-testid`, SVG color palettes) may require periodic calibration.
- **Rate-Limiting (CAPTCHA)**: Extreme data extraction constraints may invoke physical CAPTCHAs. Session pausing is currently handled manually if detected.
- **Geolinguistics**: The hardcoded Text Processor is strictly optimized for the Indonesian localization.

## Tech Stack
| Component | Implementation |
|---|---|
| **Extraction Automation** | Playwright (Chromium) |
| **Data Orchestration** | Pandas, Collections API |
| **NLP Vectorization** | Custom N-Gram Tokenizer, WordCloud ecosystem |
| **Statistical Visualization** | Matplotlib, Seaborn |
| **Application Layer** | Streamlit (Glassmorphism Framework) |
