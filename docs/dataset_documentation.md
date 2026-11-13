# DATASET DOCUMENTATION & PROVENANCE REPORT

## 1. DATASET IDENTIFICATION & LICENSING
- **Official Name:** Cricsheet Indian Premier League Match & Delivery Archive
- **Primary Source:** [Cricsheet (https://cricsheet.org/)](https://cricsheet.org/)
- **Direct Archive URL:** `https://cricsheet.org/downloads/ipl_csv2.zip`
- **License:** [Open Data Commons Open Database License (ODbL) / Creative Commons Attribution (CC-BY 4.0)](https://opendatacommons.org/licenses/odbl/)
- **Data Attribution:** Cricket match records and ball-by-ball delivery event logs are licensed by Stephen Rust (Cricsheet).
- **Data Time Horizon:** 2008 Season through 2024 Season (17+ continuous tournament seasons).

---

## 2. RAW ARCHIVE STRUCTURE
The downloaded Cricsheet `ipl_csv2.zip` archive contains 2,489 files:
1. `all_matches.csv`: Master consolidated ball-by-ball event stream across all matches.
2. `<match_id>_info.csv`: Match-level metadata text files structured in key-value format.
3. `<match_id>.csv`: Individual match delivery records.
4. `README.txt` & `LICENSE.txt`: Provenance and usage terms.

---

## 3. PROCESSED DATASET SCHEMAS

### 3.1 Matches Dataset (`matches_clean.csv`)
- **Total Records:** 1,243 official matches
- **Record Level:** One row per completed or abandoned IPL match

| Column | Data Type | Description | Sample Value |
| :--- | :--- | :--- | :--- |
| `match_id` | Integer | Unique identifier per Cricsheet/Cricinfo | `335982` |
| `season` | String | Tournament season | `2008` |
| `date` | YYYY-MM-DD | Match start date | `2008-04-18` |
| `venue` | String | Standardized stadium name | `M Chinnaswamy Stadium, Bengaluru` |
| `city` | String | Host city | `Bangalore` |
| `team1` | String | Standardized batting/first team | `Royal Challengers Bengaluru` |
| `team2` | String | Standardized second team | `Kolkata Knight Riders` |
| `toss_winner`| String | Team that won the pre-match coin toss | `Royal Challengers Bengaluru` |
| `toss_decision`| String | Decision elected ('bat' or 'field') | `field` |
| `winner` | String | Match winning franchise | `Kolkata Knight Riders` |
| `result` | String | Result outcome type ('runs', 'wickets', 'tie', 'no result') | `runs` |
| `result_margin`| Float | Victory margin (runs scored or wickets in hand) | `140.0` |
| `player_of_match`| String | Official Player of the Match recipient | `BB McCullum` |
| `eliminator` | String | Winner determined via Super Over | `Kings XI Punjab` |
| `method` | String | Match outcome adjustment method (e.g. 'D/L') | `D/L` |

---

### 3.2 Deliveries Dataset (`deliveries_clean.csv`)
- **Total Records:** 295,732 ball deliveries
- **Record Level:** One row per individual legal delivery or extra bowled

| Column | Data Type | Description |
| :--- | :--- | :--- |
| `match_id` | Integer | Foreign key linking to `matches_clean.csv` |
| `season` | String | Tournament season |
| `venue` | String | Standardized stadium |
| `innings` | Integer | Innings number (1 = first innings, 2 = second innings, 3+ = super over) |
| `ball` | Float | Over.Ball notation (e.g., `0.1` = over 1 ball 1) |
| `over` | Integer | Zero-indexed over number (0 to 19) |
| `ball_in_over` | Integer | Delivery number in current over (1 to 6+) |
| `batting_team` | String | Batting team name |
| `bowling_team` | String | Fielding/bowling team name |
| `striker` | String | Batter facing the delivery |
| `non_striker` | String | Batter at non-striker's crease |
| `bowler` | String | Bowler delivering the ball |
| `runs_off_bat` | Integer | Runs scored off the bat (0 to 6) |
| `extras` | Integer | Total extras conceded on delivery |
| `wides` | Integer | Wide delivery extras |
| `noballs` | Integer | No-ball delivery extras |
| `byes` | Integer | Bye extras (fielding error, not bowler's run) |
| `legbyes` | Integer | Leg-bye extras |
| `penalty` | Integer | Penalty runs awarded |
| `total_runs` | Integer | Total runs added to team score (`runs_off_bat + extras`) |
| `is_legal` | Integer | 1 if delivery is legal (not wide, not no-ball); else 0 |
| `is_four` | Integer | 1 if `runs_off_bat == 4`; else 0 |
| `is_six` | Integer | 1 if `runs_off_bat == 6`; else 0 |
| `is_dot` | Integer | 1 if legal delivery resulted in 0 runs off bat and 0 extras |
| `is_wicket` | Integer | 1 if any dismissal occurred on delivery |
| `is_bowler_wicket` | Integer | 1 if wicket is credited to bowler (excludes run outs, retirements) |
| `wicket_type` | String | Method of dismissal ('caught', 'bowled', 'lbw', 'run out', etc.) |
| `player_dismissed`| String | Name of player who was dismissed |
| `bowler_runs` | Integer | Runs debited to bowler (`runs_off_bat + wides + noballs + penalty`) |

---

## 4. PREPROCESSING & CLEANING METHODOLOGY
1. **Team Name Harmonization:**
   Franchises undergoing rebranding were harmonized to their official continuous entities while preserving competitive history:
   - `Rising Pune Supergiants` $\rightarrow$ `Rising Pune Supergiant`
   - `Delhi Daredevils` $\rightarrow$ `Delhi Capitals`
   - `Kings XI Punjab` $\rightarrow$ `Punjab Kings`
   - `Royal Challengers Bangalore` $\rightarrow$ `Royal Challengers Bengaluru`
2. **Stadium Harmonization:**
   Merged ground name variants (e.g., `M Chinnaswamy Stadium, Bangalore` $\rightarrow$ `M Chinnaswamy Stadium, Bengaluru`, `Feroz Shah Kotla` $\rightarrow$ `Arun Jaitley Stadium, Delhi`).
3. **MCC Rule Conformance on Bowler Runs:**
   Byes and Leg-byes are explicitly excluded from `bowler_runs` calculations in strict accordance with Law 21 & Law 22 of the MCC Laws of Cricket.
