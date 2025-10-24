# TMDB 5000 Movie Visualization and Analysis (Streamlit)

This project is an interactive data analysis app built with Streamlit around the TMDB 5000 movie dataset. It provides sidebar filters, KPI cards, targeted business question analyses, and multiple EDA views to help you understand movies across budget, revenue, rating, genre, country, and language.

- Tech stack: Python + Streamlit + Altair + Pandas
- Data source: Kaggle public dataset (auto-downloaded via kagglehub)
- Runtime: Verified on macOS, Python 3.13 (if dependency issues arise, try Python 3.11/3.12)

---

## Highlights

- Sidebar filters: year range, genres, languages, rating range, runtime range, minimum ROI, minimum vote count, exclude zero/missing revenue, title keyword.
- KPI cards: number of movies, average rating, median revenue, median ROI under current filters.
- Key questions:
  - Q1: Do bigger budgets lead to higher revenue/ratings? (budget–revenue regression, budget–rating regression, popularity–revenue)
  - Q2: Which genres have higher ROI? (ranked by median ROI)
- Question Hub offers many charts you can switch via a dropdown:
  - Runtime vs Rating (faceted by genre with LOESS)
  - Genre tag count vs Rating
  - Country × Language × ROI heatmap / faceted bar
  - Release month seasonality for revenue/rating (bar/heatmap)
  - Decade trends: budget/revenue/rating
  - Sequel vs Original comparison (median ROI)
  - Vote count binning vs rating stability
  - High-ROI Top-K vs Low-ROI Bottom-K profile comparison (bars / normalized lines)
  - ROI turning point across budget bins
  - Genre × Country heatmap
  - Popularity vs Revenue
  - Production country ROI / Production company ROI
  - Genre share by decade
- EDA: rating histogram, yearly trend (rating and popularity), runtime box plot by popular genres, correlation heatmap among numeric features.
- Smart fallback: when filters yield no plottable data for a view, the app falls back to the full dataset with a notice.

---

## Project Structure

```
streamlit_app/
├── app.py                # Entry: page frame and main flow
├── constants.py          # Page title/description constants
├── data_loader.py        # Data loading & cleaning (kagglehub + feature engineering)
├── filters.py            # Sidebar filters and filtering logic
├── components.py         # Reusable UI components like KPI cards
├── charts.py             # All Altair charts
├── sections.py           # Page sections and Question Hub
├── requirements.txt      # Dependencies
└── README.md             # This document
```

---

## Data Source & Cleaning

- Dataset: `tmdb/tmdb-movie-metadata` (Kaggle)
- Download via: `kagglehub.dataset_download("tmdb/tmdb-movie-metadata")`
- Auto-detected CSVs: `tmdb_5000_movies.csv` (or compatibility with `tmdb_5000_movies_2.csv`)
- Cleaning and feature engineering (`data_loader.clean_movies`):
  - Date parsing: `release_date` → `release_year`
  - Parse JSON-like string columns into lists: `genres_list`, `production_countries_list`, `production_companies_list`, `spoken_languages_list`
  - Convert numeric columns: `budget`, `revenue`, `runtime`, `vote_average`, `popularity`, `vote_count`
  - Derived metrics: `profit = revenue - budget`, `roi = revenue / budget` (budget of 0 treated as missing)
  - Outlier clipping for charts: `budget_clip` and `revenue_clip` at 99th percentile
- Caching: `@st.cache_data` stores downloaded and cleaned DataFrame to improve performance.

---

## Interaction & Page Layout

- Top: title and description (`constants.PAGE_TITLE` / `PAGE_DESC`)
- Sidebar: build filters via `filters.build_sidebar(df)` and apply with `filters.apply_filters(df, f)`
- KPI: `components.kpi_cards(df_filtered)`
- Analysis sections:
  - `section_question_1/2`: budget–revenue/rating and genre ROI
  - `section_questions_hub`: all switchable charts
  - `section_eda`: common EDA views
  - `section_leaderboard`: ranking table by revenue or ROI (configurable Top N)
- Smart fallback: `st.session_state["df_full"]` holds the full dataset for fallback when filtered data is insufficient.

---

## Installation & Run

Below is for macOS; other systems are similar.

- Requirements:
  - Python 3.11–3.13 (verified on 3.13; if some libs fail, try 3.11/3.12)
  - Network access to Kaggle (first download requires browser authorization)

- Create and activate a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
```

- Install dependencies:

```bash
pip install -U pip
pip install -r requirements.txt
```

- Run the app:

```bash
streamlit run app.py
```

- First run notes (kagglehub auth & download):
  - On the first `dataset_download`, kagglehub may open a browser for Kaggle account authorization and then cache the data locally.
  - If network/permissions are restricted, the app will show an error in “Data Loading (KaggleHub)” and stop.

---

## FAQ

- Charts are blank or missing?
  - Your filters may be too strict. The app falls back to full data with a notice; try relaxing filters.

- kagglehub download fails (network or permissions)?
  - Ensure Kaggle is accessible and complete the browser authorization when prompted.
  - Configure a proxy if needed (e.g., `HTTPS_PROXY`).
  - Alternatively, pre-download the CSV locally and replace `data_loader.load_tmdb_via_kagglehub()` with a direct `pd.read_csv(<local_path>)`.

- Altair charts fail to render in some environments?
  - Open the Streamlit page in a standard browser (avoid embedded WebView limitations).
  - Update your browser and Streamlit; check terminal logs for errors.

- Python version compatibility
  - If some libs have issues on Python 3.13, try 3.11/3.12.

---

## Configuration

- `constants.py`
  - `PAGE_TITLE`: page title
  - `PAGE_DESC`: page caption on the landing page

- `filters.py`
  - Adjust default ranges/controls like ROI minimum and vote count.

---

## Development Notes

- Add a new chart (recommended workflow):
  1. Implement a chart function in `charts.py` that takes a filtered DataFrame and returns an `alt.Chart`/`alt.VConcatChart`.
  2. Call it from `sections.py`:
     - For generic EDA, add to `section_questions_hub` options.
     - For a focused question, place it under `section_question_1/2`.
  3. If new cleaning/features are required, extend `data_loader.clean_movies`.

- Add new filters:
  1. Add controls in `filters.build_sidebar` and extend the `Filters` dataclass.
  2. Update `filters.apply_filters` accordingly.

- Replace/extend data sources:
  - For a local CSV or other datasets, add a “local-first” branch in `load_tmdb_via_kagglehub` or create a new loader.

---

## Deployment

- Streamlit Community Cloud:
  - Push to a Git repo and choose it on the Cloud dashboard.
  - Note: External downloads may be blocked; kagglehub’s first-time download can fail. Consider:
    - Option A: Commit CSV files to the repo (observe data license).
    - Option B: Pre-download during build or switch to a public CDN.

- Container/server deployment:
  - Install dependencies from `requirements.txt` and expose port 8501.
  - Configure proxy/certificates as needed.

---

## License and Acknowledgements

- Code license: No explicit license file is provided. Add a suitable one (e.g., MIT) if you plan to open-source.
- Data license: TMDB 5000 dataset from Kaggle; follow the dataset terms and TMDB policies.
- Thanks to kagglehub, Streamlit, Altair, Pandas, and NumPy.

