# Toko-Review-Insights

A practical review intelligence tool built on top of Tokopedia's product pages. It combines browser automation with lightweight NLP to help you understand what customers are actually saying — especially the unhappy ones.

---

## Background

Most product analytics pipelines focus on aggregate metrics: average rating, order volume, conversion rate. What they often miss is the unstructured signal sitting inside customer reviews — the *why* behind a 2-star rating, the recurring complaint pattern that a dashboard won't surface, the exact phrase that shows up in 40 different complaints about sizing.

This project started as a personal utility to quickly pull review data from Tokopedia and generate a digestible summary without having to open a Jupyter notebook every time.

---

## What It Does

There are three independent apps in this repo, each solving a different step of the workflow:

**`app.py`** — Crawls all reviews from a given product URL across all paginated pages.

**`app_bad.py`** — Same, but applies Tokopedia's built-in rating filter (1–3 stars) before crawling. Useful when you only care about negative feedback and don't want to filter post-hoc.

**`app_report.py`** — Takes any crawled CSV file and generates a full EDA report: rating distribution, top-selling variants, and a word cloud built from bigrams and trigrams extracted from low-rating reviews.

Each app exposes a minimal Streamlit UI — no notebooks required.

---

## How the Crawler Works

Tokopedia aggressively blocks headless browsers. The engine launches a visible Chromium window (`headless=False`) and mimics a real user: scrolling slowly, waiting for GraphQL calls to resolve, and paginating through the review section. Star ratings are extracted by inspecting SVG fill colors (`#FFD45F`) in the DOM rather than relying on text, which is more stable across Tokopedia's periodic UI updates.

For the bad-review crawler specifically, the filter panel is clicked programmatically after the review tab loads — targeting checkboxes for ratings 1, 2, and 3 the same way a user would.

---

## Report Output

When you run the report generator on a CSV, it produces the following inside `reports/<filename>/`:

```
reports/
└── sendal/
    ├── report_sendal.md
    └── assets/
        ├── rating_distribution.png
        ├── varian_distribution.png
        └── wordcloud_komplain.png
```

The word cloud is generated from **n-gram frequencies** (bigrams and trigrams), not raw word counts. This means you'll see phrases like *"ukuran tidak sesuai"* or *"cepat rusak"* instead of isolated words like *"ukuran"* or *"rusak"* — which tells you a lot more about the actual problem.

---

## Project Structure

```
.
├── app.py                  # Crawl all reviews
├── app_bad.py              # Crawl 1–3 star reviews only
├── app_report.py           # EDA report generator UI
├── engines/
│   ├── agent_ulasan.py     # Core Playwright crawler (all ratings)
│   ├── agent_ulasan_bad.py # Crawler with rating filter applied
│   └── generate_report.py  # Report + chart generation logic
├── data/                   # CSV output from crawls
├── reports/                # Generated markdown reports
├── assets/                 # Standalone chart exports
└── scripts/
    └── generate_plots.py   # Standalone plot script (optional CLI use)
```

---

## Setup

Python 3.10+ is recommended. Install dependencies into a virtual environment:

```bash
python -m venv .venv
.venv\Scripts\Activate.ps1        # Windows PowerShell
pip install streamlit playwright wordcloud pandas matplotlib seaborn
playwright install chromium
```

---

## Usage

Activate the environment, then navigate to the project root:

```bash
# Crawl all reviews
streamlit run app.py

# Crawl negative reviews only (1–3 stars)
streamlit run app_bad.py

# Generate EDA report from an existing CSV
streamlit run app_report.py
```

Paste a Tokopedia product URL into the input field, give the output file a name, and let it run. Don't close the Chromium window that opens — it's not a bug, it's how we get past the bot detection.

---

## Limitations

- **DOM volatility.** Tokopedia updates its frontend periodically. If the crawler stops working, the first thing to check is the SVG color attribute used for star detection and the `aria-label` selectors for pagination buttons.
- **Rate and CAPTCHA.** On products with a very large number of reviews, Tokopedia may serve a CAPTCHA mid-session. If that happens, the crawl stops naturally. Consider running in shorter bursts with a manual review.
- **Single-language NLP.** The stop word list and n-gram extraction are tuned for Indonesian product review language. It won't generalize well to English-language content without adjusting the stop word dictionary.

---

## Stack

| Layer | Tool |
|---|---|
| Browser Automation | Playwright (Chromium, headful) |
| Data Processing | pandas, collections |
| NLP / Text | Custom n-gram tokenizer, WordCloud |
| Visualization | matplotlib, seaborn |
| UI | Streamlit |

---

> Built for personal use. Works until Tokopedia changes something, then needs a small fix.
