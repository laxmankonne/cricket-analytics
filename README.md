# 🏏 CRIC ANALYTICS: Cricket Data Analysis & Interactive Visualization Using Python

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Streamlit App](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B.svg)](https://streamlit.io/)
[![Plotly Interactive](https://img.shields.io/badge/Plotly-Interactive-38BDF8.svg)](https://plotly.com/)
[![License: ODbL](https://img.shields.io/badge/Data_License-ODbL-16A34A.svg)](https://opendatacommons.org/licenses/odbl/)
[![Tests](https://img.shields.io/badge/Unit_Tests-9%20Passing-brightgreen.svg)]()

An enterprise-grade, academic-standard sports data analytics platform engineered with Python, Streamlit, and Plotly. Built entirely upon authentic Cricsheet ball-by-ball delivery logs covering **1,243 official matches** and **295,732 deliveries** from 2008 to the present day.

---

## 🌟 Key Platform Modules

| Module | Description | Key Features |
| :--- | :--- | :--- |
| **01. Home Dashboard** | Executive summary & tournament KPIs | 17+ seasons, total runs, wickets, season distribution, outcome donut |
| **02. Batting Analysis** | Player batting efficiency & scoring | Top run scorers, strike rate vs average, 4s/6s boundary breakdown, PCI |
| **03. Bowling Analysis** | Wicket-taking & run containment | Top wicket takers, economy vs strike rate quadrant, best figures, maidens |
| **04. Team Performance** | Franchise standings & rivalries | Historical win %, head-to-head records, bat first vs chasing bias, toss patterns |
| **05. Match Analysis** | Single-match ball-by-ball cards | Over-by-over worm charts, fall of wickets, closest finishes, extreme totals |
| **06. Venue Analysis** | Stadium pitch behavior & par scores | Chasing vs defending ground bias, average 1st innings scores, venue records |
| **07. Player Comparison** | Multi-player head-to-head | Normalized 6-skill radar charts, career milestone tables, season comparisons |
| **08. Historical Trends** | Longitudinal format evolution | Scoring velocity (run rate) growth, boundary explosion, franchise era dominance |
| **09. Advanced Analytics** | Machine Learning & Statistics | Regularized Logistic Regression win predictor, $\chi^2$ toss hypothesis test, BER/BoER |
| **10. Data Explorer** | Repository browser & exporter | Full-text search, multi-column filters, data health audit, instant CSV export |

---

## 🏗️ System Architecture

```
cricket-analytics/
├── app.py                     # Entry point & Home Dashboard (Module 1)
├── requirements.txt           # Python dependency specifications
├── README.md                  # Project overview & documentation
├── .gitignore                 # Version control exclusions
│
├── pages/                     # Streamlit Multi-Page Directory
│   ├── 01_Home.py             # Home Dashboard router
│   ├── 02_Batting.py          # Module 2: Batting Analysis
│   ├── 03_Bowling.py          # Module 3: Bowling Analysis
│   ├── 04_Team_Analysis.py    # Module 4: Franchise Performance & H2H
│   ├── 05_Match_Analysis.py   # Module 5: Match Scorecards & Worm Charts
│   ├── 06_Venue_Analysis.py   # Module 6: Stadium Par Scores & Biases
│   ├── 07_Player_Comparison.py# Module 7: Radar Charts & Side-by-Side
│   ├── 08_Historical_Trends.py# Module 8: Scoring Evolution & Eras
│   ├── 09_Advanced_Analytics.py# Module 9: ML Outcome Predictor & Hypothesis Testing
│   └── 10_Data_Explorer.py    # Module 10: Interactive Table Explorer & CSV Export
│
├── data/
│   ├── raw/                   # Raw Cricsheet archive
│   └── processed/             # Cleaned core datasets & summary tables
│       ├── matches_clean.csv
│       ├── deliveries_clean.csv
│       ├── player_batting_summary.csv
│       ├── player_bowling_summary.csv
│       ├── team_summary.csv
│       └── venue_summary.csv
│
├── utils/                     # Modular Analytical Utilities
│   ├── data_loader.py         # High-performance Streamlit caching loader
│   ├── batting_analysis.py    # Pure batting statistical calculations
│   ├── bowling_analysis.py    # Pure bowling statistical calculations
│   ├── team_analysis.py       # Standings, H2H, and toss dynamics
│   ├── match_analysis.py      # Scorecards, worm generator, extreme totals
│   ├── venue_analysis.py      # Ground metrics & par totals
│   ├── advanced_analytics.py  # ML Logistic Regression, Chi-Square test, Efficiency ratings
│   ├── visualization.py       # Standardized cricket-themed Plotly charts
│   └── ui_helper.py           # Custom CSS injector & header components
│
├── assets/
│   └── style.css              # Custom athletic dark CSS theme
│
├── tests/                     # Automated Unit Testing Suite
│   ├── test_data.py           # Dataset integrity & schema validation tests
│   └── test_analysis.py       # Statistical correctness & ML bounds tests
│
└── docs/                      # University Academic Documentation
    ├── project_report.md      # Full 30-section IEEE / University project report
    ├── methodology.md         # Mathematical formulas & pipeline architecture
    ├── dataset_documentation.md# Cricsheet licensing, provenance & schema
    └── viva_preparation.md    # 30 Viva questions & answers + presentation script
```

---

## 🚀 Quickstart & Installation

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/cricket-analytics.git
cd cricket-analytics
```

### 2. Set Up Virtual Environment (Recommended)
```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. (Optional) Run Data Preprocessing Pipeline
*The processed datasets are already included in `data/processed/`. To re-download and re-process fresh raw archives:*
```bash
python scripts/acquire_and_preprocess.py
```

### 5. Launch the Platform
```bash
streamlit run app.py
```
Open your browser at `http://localhost:8501`.

---

## 🧪 Running Unit Tests

Run the full automated test suite using Python's built-in `unittest` runner:
```bash
python -m unittest discover -s tests -p "test_*.py"
```
*Output: 9 tests run across data integrity and statistical calculations with 100% pass rate.*

---

## ☁️ Deployment Instructions (Streamlit Community Cloud)

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "feat: complete cricket analytics platform with 10 modules"
   git branch -M main
   git remote add origin https://github.com/your-username/cricket-analytics.git
   git push -u origin main
   ```
2. **Deploy on Streamlit Cloud:**
   - Log into [Streamlit Community Cloud (https://share.streamlit.io/)](https://share.streamlit.io/) with your GitHub account.
   - Click **New app**.
   - Select your repository (`cricket-analytics`), branch (`main`), and set the main file path to `app.py`.
   - Click **Deploy!**
3. **Public Access:**
   Your application will be live at `https://<your-app-name>.streamlit.app` with zero server management required.

---

## 📊 Dataset Provenance & Attribution
All statistics are computed from official, authentic cricket records:
- **Provider:** [Cricsheet (https://cricsheet.org/)](https://cricsheet.org/)
- **License:** Open Data Commons Open Database License (ODbL)
- **Time Horizon:** 2008 – Present (17+ Seasons, 1,243 Matches, 295,732 Balls)
- **Zero Fabrication Guarantee:** No placeholder metrics, random numbers, or artificial records.

---

## 🎓 Academic Presentation & Viva Voce
Consult the comprehensive guides in `docs/`:
- **Full Academic Project Report:** [`docs/project_report.md`](docs/project_report.md)
- **Mathematical Formulations:** [`docs/methodology.md`](docs/methodology.md)
- **30 Viva Questions & Answers:** [`docs/viva_preparation.md`](docs/viva_preparation.md)

