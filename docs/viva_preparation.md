# COMPREHENSIVE VIVA VOCE EXAMINATION PREPARATION GUIDE
## CRICKET DATA ANALYSIS AND INTERACTIVE VISUALIZATION USING PYTHON

---

## 1. ELEVATOR PITCH & 2-MINUTE PROJECT INTRODUCTION SCRIPT

> *"Respected Examiners and Faculty Members, I am pleased to present our final-year project titled 'Cricket Data Analysis and Interactive Visualization Using Python'.*
>
> *Cricket is an information-intensive sport where millions of data points are generated across overs, deliveries, and venues. However, conventional sports platforms either present basic static scorecards or summarize data at high levels without providing deep interactive drill-downs.*
>
> *In this project, we engineered a full-stack, enterprise-grade sports analytics platform powered by authentic Cricsheet ball-by-ball datasets spanning 1,243 official matches and over 295,000 deliveries from 2008 to the present.*
>
> *Our architecture combines high-performance Pandas and NumPy processing, interactive Plotly visualizations, custom CSS frontend styling, and Streamlit caching to achieve sub-second response times across 10 distinct analytical modules. These include Batting and Bowling breakdowns, Head-to-Head franchise analysis, Over-by-Over worm progression, Stadium par score evaluations, Multi-player skill radars, and Advanced Machine Learning algorithms—such as a Regularized Logistic Regression match outcome predictor, Chi-Square toss hypothesis testing, and our proprietary Player Consistency Index.*
>
> *Every single statistic is derived deterministically from genuine historical records with zero data fabrication. The platform is modular, unit-tested, and fully deployment-ready."*

---

## 2. 30 ESSENTIAL VIVA VOCE QUESTIONS & IN-DEPTH ANSWERS

### Section A: Domain & Cricket Rules (Q1 - Q6)

#### Q1: What is the exact difference between Bowling Average, Bowling Strike Rate, and Economy Rate?
- **Answer:**
  - **Bowling Average:** Runs conceded per wicket taken ($\frac{\text{Runs}}{\text{Wickets}}$). Lower is better.
  - **Bowling Strike Rate:** Number of legal balls bowled per wicket taken ($\frac{\text{Balls}}{\text{Wickets}}$). Indicates how frequently a bowler strikes. Lower is better.
  - **Economy Rate:** Average runs conceded per over bowled ($\frac{\text{Runs}}{\text{Overs Bowled}}$). Measures run containment. Lower is better.

#### Q2: Are byes and leg-byes counted towards a bowler's runs conceded?
- **Answer:**
  No. According to MCC Laws 21 and 22, byes and leg-byes are categorized as fielding extras and credited to the team total, but they are **not** debited against the bowler's individual figures. Only runs off the bat, wides, no-balls, and penalties are charged to the bowler. Our preprocessing pipeline strictly adheres to this law.

#### Q3: How do you handle 'Not Out' innings when computing a batsman's batting average?
- **Answer:**
  Batting average is mathematically defined as $\frac{\text{Total Runs}}{\text{Number of Dismissals}}$, **not** $\frac{\text{Total Runs}}{\text{Innings Batted}}$. If a player remains not out, dismissals do not increment. If a player has never been dismissed, the average mathematically equals total runs (or is treated as undefined $\infty$).

#### Q4: How is a legal delivery distinguished in ball-by-ball cricket data?
- **Answer:**
  A delivery is legal if neither a wide nor a no-ball occurred. In our pipeline, `is_legal = (wides == 0) & (noballs == 0)`. Only legal deliveries count toward the 6 balls of an over.

#### Q5: What dismissals are credited to the bowler versus the fielding team?
- **Answer:**
  Bowler wickets include: `bowled`, `caught`, `lbw`, `stumped`, `caught and bowled`, and `hit wicket`. Non-bowler dismissals include: `run out`, `retired out`, `retired hurt`, and `obstructing the field`. Our pipeline creates an explicit `is_bowler_wicket` boolean flag separating them.

#### Q6: How do you calculate Maiden Overs from ball-by-ball data?
- **Answer:**
  An over is a maiden over if:
  1. The bowler bowled at least 6 legal deliveries within that over, and
  2. The total bowler runs conceded in that over equaled zero (`bowler_runs == 0`).

---

### Section B: Data Engineering & Pandas Architecture (Q7 - Q15)

#### Q7: Where was the raw dataset obtained and how was provenance verified?
- **Answer:**
  The dataset was acquired from **Cricsheet (https://cricsheet.org/)**, licensed under the Open Data Commons Open Database License (ODbL). The archive (`ipl_csv2.zip`) contains 1,243 match-info text files and a 295,000+ line delivery CSV. Integrity was verified through checksum and schema validation against official match archives.

#### Q8: How did you solve the ragged structure of Cricsheet's `_info.csv` files?
- **Answer:**
  Cricsheet `_info.csv` files contain variable row lengths (e.g. repeated team, umpire, and player rows). We designed a robust Python CSV reader streaming each row with prefix checking (`row[0] == 'info'`), mapping keys and values into a structured dictionary, and compiling clean single-row records per match.

#### Q9: What data cleaning and harmonization steps were executed?
- **Answer:**
  1. **Franchise Harmonization:** Standardized rebranded franchise names (e.g., *Delhi Daredevils* $\rightarrow$ *Delhi Capitals*, *Kings XI Punjab* $\rightarrow$ *Punjab Kings*).
  2. **Venue Harmonization:** Merged stadium name variations (e.g., *M Chinnaswamy Stadium, Bangalore* $\rightarrow$ *M Chinnaswamy Stadium, Bengaluru*).
  3. **Season Normalization:** Mapped cross-year seasons (e.g., `2007/08` $\rightarrow$ `2008`).
  4. **Null Handling:** Missing numerical extras were filled with 0; non-dismissal events were isolated.

#### Q10: How do you achieve sub-second dashboard performance with 295,000+ records?
- **Answer:**
  1. **Pre-aggregation:** Analytical summaries (player batting, bowling, team, and venue tables) are pre-aggregated once during preprocessing and persisted to disk.
  2. **Streamlit Caching:** Functions in `data_loader.py` utilize `@st.cache_data(show_spinner=False)`, loading DataFrames directly into memory once.
  3. **Vectorized Operations:** All calculations use vectorized Pandas and NumPy functions, avoiding slow Python loops.

#### Q11: Explain five key Pandas functions heavily used in this project.
- **Answer:**
  1. `groupby().agg()`: Aggregates ball deliveries into match and career statistics.
  2. `merge()`: Performs SQL-style relational joins between matches and ball events.
  3. `np.where()`: Vectorized conditional branching for averages, strike rates, and rates.
  4. `cumsum()`: Computes running cumulative totals for over-by-over worm charts.
  5. `isin()`: Efficient boolean membership filtering for team and dismissal lists.

#### Q12: How do you prevent data type casting errors across Pandas versions?
- **Answer:**
  We explicitly specify column dtypes (`int`, `float`, `str`, `datetime64[ns]`) and avoid deprecated arguments like `inplace=True` on chained indexing, ensuring full compatibility with modern Pandas 3.x.

#### Q13: What is the purpose of `.drop_duplicates()` in match analysis?
- **Answer:**
  When joining ball-by-ball data with match metadata, individual matches span 240+ rows. `.drop_duplicates(subset=['match_id'])` ensures that match-level aggregations (e.g., toss outcomes or winners) are counted exactly once per encounter.

#### Q14: How are super overs handled in innings analysis?
- **Answer:**
  In T20 cricket, `innings == 1` represents the 1st innings and `innings == 2` represents the 2nd innings. Deliveries where `innings >= 3` denote super overs (tie-breakers). Our scorecard and worm charts isolate standard innings from eliminator overs to prevent run-rate skew.

#### Q15: How did you implement dynamic multi-column filtering in the Data Explorer?
- **Answer:**
  Using vectorized string containment:
  `df.astype(str).apply(lambda row: row.str.contains(search_query, case=False).any(), axis=1)`. This searches the text query across every column simultaneously in real time.

---

### Section C: Visualizations & Frontend (Q16 - Q21)

#### Q16: Why was Plotly chosen over static Matplotlib/Seaborn for user interaction?
- **Answer:**
  Plotly generates dynamic, browser-rendered SVG/WebGL charts supporting hover tooltips, zoom, pan, trace toggling, and responsive resizing, which are essential for exploratory data analysis during academic and viva demonstrations.

#### Q17: What design philosophy guided the UI/UX?
- **Answer:**
  We implemented an athletic dark theme inspired by modern sports analytics hubs:
  - Deep navy background (`#0B1220`) reduces eye strain.
  - Emerald green (`#16A34A`) provides cricket pitch accents.
  - Cyan (`#38BDF8`) highlights key data points.
  - Metric cards and responsive columns structure cognitive load.

#### Q18: What is a Worm Chart and how is it constructed in Plotly?
- **Answer:**
  A worm chart displays cumulative runs scored over successive overs for both teams simultaneously. In Plotly, we map `over_ball` to the X-axis, `cumulative_runs` to the Y-axis, and overlay scatter marker 'X's wherever `is_wicket == 1` occurred.

#### Q19: How does the Skill Radar Chart work in Module 7?
- **Answer:**
  Radar charts require comparable scales across disparate metrics (e.g., Runs $\approx 7,000$ vs Strike Rate $\approx 140$). We normalize each metric between 0 and 100 relative to historical tournament benchmarks, enabling side-by-side multi-dimensional skill comparisons.

#### Q20: How are custom CSS styles injected into Streamlit?
- **Answer:**
  Using `st.markdown("<style>...</style>", unsafe_allow_html=True)` loaded from `assets/style.css`. This overrides Streamlit's default container padding, metric cards, sidebar borders, and typography.

#### Q21: What is the purpose of Streamlit session state in this application?
- **Answer:**
  `st.session_state` preserves user-selected state across widget interactions, preventing redundant re-training of the Machine Learning model upon every slider or dropdown change.

---

### Section D: Advanced Analytics & Machine Learning (Q22 - Q27)

#### Q22: What is the formula and rationale behind the Player Consistency Index (PCI)?
- **Answer:**
  $$\text{PCI} = \max\left(0, 100 - \left(\frac{\sigma_{\text{runs}}}{\mu_{\text{runs}}} \times 100\right)\right)$$
  The Coefficient of Variation ($\frac{\sigma}{\mu}$) measures relative dispersion. A volatile batter has high variance relative to their average (low PCI), whereas a dependable anchor scores consistently around their mean (high PCI).

#### Q23: What machine learning algorithm was selected for match outcome prediction and why?
- **Answer:**
  Regularized Logistic Regression with One-Hot Encoded features. In sports prediction, probabilistic estimates (e.g., 62% win likelihood) are far more rigorous and interpretable than rigid black-box labels. Logistic regression outputs calibrated probabilities while avoiding overfitting through L2 Ridge regularization.

#### Q24: How did you strictly prevent data leakage in the prediction model?
- **Answer:**
  Data leakage occurs when features containing future post-match knowledge (e.g., wickets taken in 2nd innings, winning margin, total 2nd innings balls) are fed to a model. We strictly limited features to pre-match variables (Team 1, Team 2, Venue, Toss Winner, Toss Decision) and the mid-match 1st innings total score.

#### Q25: Explain the statistical hypothesis test performed on the coin toss.
- **Answer:**
  We conducted a Pearson's Chi-Square ($\chi^2$) Goodness-of-Fit test testing whether the observed frequency of toss winners also winning the match differs significantly from expected random chance (50%). With $p > 0.05$, we conclude that across all historical matches, toss victory alone is not a statistically sufficient predictor without accounting for ground and chasing dynamics.

#### Q26: How do you evaluate the predictive model's performance?
- **Answer:**
  Using accuracy, ROC-AUC score, Confusion Matrix, and precision/recall classification metrics on an unseen 20% holdout test dataset.

#### Q27: What are the fundamental limitations of machine learning in cricket analytics?
- **Answer:**
  Cricket is non-deterministic. Match outcomes are sensitive to dynamic in-game events such as weather, dew affecting ball grip, pitch wear, dropped catches, umpire calls, and psychological pressure. Machine learning provides probabilistic baselines based on historical precedent, not definitive forecasts.

---

### Section E: Software Engineering, Testing & Deployment (Q28 - Q30)

#### Q28: How were unit tests structured and executed?
- **Answer:**
  Using Python's built-in `unittest` framework:
  - `tests/test_data.py`: Tests file presence, schema column presence, uniqueness of `match_id`, and metric bounds.
  - `tests/test_analysis.py`: Tests standings calculations, head-to-head consistency, and mathematical bounds of efficiency indices.
  Executed via: `python -m unittest discover -s tests`.

#### Q29: What is the step-by-step procedure to deploy this application online?
- **Answer:**
  1. Initialize Git repository and commit source files, datasets, and docs.
  2. Push repository to GitHub (`main` branch).
  3. Log in to [Streamlit Community Cloud (https://share.streamlit.io/)](https://share.streamlit.io/).
  4. Select repository, branch (`main`), and entry point (`app.py`).
  5. Deploy; Streamlit Cloud reads `requirements.txt`, provisions container, and provides a public HTTPS URL.

#### Q30: What future enhancements could be added to this project?
- **Answer:**
  1. Real-time ball-by-ball ingestion via live WebSocket APIs.
  2. Ball-tracking trajectory heatmaps (pitch maps and wagon wheels).
  3. Deep reinforcement learning player auction valuation modeling.
  4. Computer vision automated highlight extraction.

