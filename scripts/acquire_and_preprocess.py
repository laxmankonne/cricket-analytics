"""
Dataset Acquisition and Preprocessing Pipeline
Source: Cricsheet (https://cricsheet.org/downloads/ipl_csv2.zip)
License: Open Data Commons Open Database License (ODbL)
"""

import os
import io
import csv
import urllib.request
import zipfile
import numpy as np
import pandas as pd

RAW_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'raw')
PROCESSED_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed')
ZIP_PATH = os.path.join(RAW_DIR, 'ipl_csv2.zip')
CRICSHEET_URL = 'https://cricsheet.org/downloads/ipl_csv2.zip'

TEAM_STANDARDIZATION = {
    'Rising Pune Supergiants': 'Rising Pune Supergiant',
    'Delhi Daredevils': 'Delhi Capitals',
    'Kings XI Punjab': 'Punjab Kings',
    'Royal Challengers Bangalore': 'Royal Challengers Bengaluru',
}

VENUE_STANDARDIZATION = {
    'M Chinnaswamy Stadium': 'M Chinnaswamy Stadium, Bengaluru',
    'M. Chinnaswamy Stadium': 'M Chinnaswamy Stadium, Bengaluru',
    'M Chinnaswamy Stadium, Bangalore': 'M Chinnaswamy Stadium, Bengaluru',
    'Feroz Shah Kotla': 'Arun Jaitley Stadium, Delhi',
    'Arun Jaitley Stadium': 'Arun Jaitley Stadium, Delhi',
    'Arun Jaitley Stadium, Delhi': 'Arun Jaitley Stadium, Delhi',
    'Wankhede Stadium': 'Wankhede Stadium, Mumbai',
    'Wankhede Stadium, Mumbai': 'Wankhede Stadium, Mumbai',
    'MA Chidambaram Stadium': 'MA Chidambaram Stadium, Chepauk, Chennai',
    'MA Chidambaram Stadium, Chepauk': 'MA Chidambaram Stadium, Chepauk, Chennai',
    'MA Chidambaram Stadium, Chepauk, Chennai': 'MA Chidambaram Stadium, Chepauk, Chennai',
    'Eden Gardens': 'Eden Gardens, Kolkata',
    'Eden Gardens, Kolkata': 'Eden Gardens, Kolkata',
    'Rajiv Gandhi International Stadium': 'Rajiv Gandhi International Stadium, Uppal, Hyderabad',
    'Rajiv Gandhi International Stadium, Uppal': 'Rajiv Gandhi International Stadium, Uppal, Hyderabad',
    'Rajiv Gandhi International Stadium, Uppal, Hyderabad': 'Rajiv Gandhi International Stadium, Uppal, Hyderabad',
    'Punjab Cricket Association Stadium, Mohali': 'Punjab Cricket Association IS Bindra Stadium, Mohali',
    'Punjab Cricket Association IS Bindra Stadium': 'Punjab Cricket Association IS Bindra Stadium, Mohali',
    'Punjab Cricket Association IS Bindra Stadium, Mohali': 'Punjab Cricket Association IS Bindra Stadium, Mohali',
    'Sawai Mansingh Stadium': 'Sawai Mansingh Stadium, Jaipur',
    'Sawai Mansingh Stadium, Jaipur': 'Sawai Mansingh Stadium, Jaipur',
    'Narendra Modi Stadium, Ahmedabad': 'Narendra Modi Stadium, Ahmedabad',
    'Sardar Patel Stadium, Motera': 'Narendra Modi Stadium, Ahmedabad',
}

def standardize_team(name):
    if pd.isna(name):
        return name
    return TEAM_STANDARDIZATION.get(str(name).strip(), str(name).strip())

def standardize_venue(name):
    if pd.isna(name):
        return name
    return VENUE_STANDARDIZATION.get(str(name).strip(), str(name).strip())

def standardize_season(val):
    if pd.isna(val):
        return val
    s = str(val).strip()
    if '/' in s:
        # e.g., '2007/08' -> '2008', '2009/10' -> '2010'
        parts = s.split('/')
        if len(parts) == 2:
            base = parts[0]
            end = parts[1]
            if len(end) == 2:
                century = base[:2]
                return century + end
            return end
    return s

def download_raw_data():
    os.makedirs(RAW_DIR, exist_ok=True)
    if not os.path.exists(ZIP_PATH):
        print(f"Downloading authentic Cricsheet dataset from {CRICSHEET_URL}...")
        req = urllib.request.Request(CRICSHEET_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as resp, open(ZIP_PATH, 'wb') as out_f:
            out_f.write(resp.read())
        print(f"Downloaded raw dataset: {os.path.getsize(ZIP_PATH) / (1024*1024):.2f} MB")
    else:
        print(f"Found existing raw zip archive at {ZIP_PATH}")

def parse_match_info(z):
    print("Parsing match info metadata files...")
    info_files = [f for f in z.namelist() if f.endswith('_info.csv')]
    matches_records = []
    
    for fname in info_files:
        try:
            content = z.open(fname).read().decode('utf-8', errors='replace').splitlines()
            reader = csv.reader(content)
            data = {}
            teams = []
            player_of_match = []
            
            for row in reader:
                if len(row) >= 3 and row[0] == 'info':
                    k, v = row[1].strip(), row[2].strip()
                    if k == 'team':
                        teams.append(v)
                    elif k == 'player_of_match':
                        player_of_match.append(v)
                    else:
                        data[k] = v
            
            match_id = data.get('match_id')
            if not match_id:
                # Extract from filename e.g. '335982_info.csv'
                base_name = os.path.basename(fname)
                match_id = base_name.replace('_info.csv', '')
                
            team1 = teams[0] if len(teams) > 0 else np.nan
            team2 = teams[1] if len(teams) > 1 else np.nan
            
            # Determine result format and margin
            result_margin = np.nan
            result_type = 'unknown'
            if 'winner_runs' in data:
                result_type = 'runs'
                try:
                    result_margin = int(data['winner_runs'])
                except:
                    result_margin = np.nan
            elif 'winner_wickets' in data:
                result_type = 'wickets'
                try:
                    result_margin = int(data['winner_wickets'])
                except:
                    result_margin = np.nan
            elif data.get('outcome') == 'tie':
                result_type = 'tie'
                result_margin = 0
            elif data.get('outcome') == 'no result':
                result_type = 'no result'
                result_margin = np.nan
            
            winner = data.get('winner')
            if not winner and data.get('eliminator'):
                winner = data.get('eliminator')
            
            matches_records.append({
                'match_id': int(match_id),
                'season': data.get('season'),
                'date': data.get('date'),
                'venue': data.get('venue'),
                'city': data.get('city'),
                'team1': team1,
                'team2': team2,
                'toss_winner': data.get('toss_winner'),
                'toss_decision': data.get('toss_decision'),
                'winner': winner,
                'result': result_type,
                'result_margin': result_margin,
                'player_of_match': player_of_match[0] if player_of_match else np.nan,
                'eliminator': data.get('eliminator'),
                'method': data.get('method'),
                'target_runs': data.get('target_runs'),
                'target_overs': data.get('target_overs')
            })
        except Exception as e:
            continue
            
    df_matches = pd.DataFrame(matches_records)
    print(f"Successfully parsed {len(df_matches)} matches metadata records.")
    return df_matches

def process_datasets():
    download_raw_data()
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    with zipfile.ZipFile(ZIP_PATH, 'r') as z:
        # 1. Parse matches metadata
        df_matches = parse_match_info(z)
        
        # 2. Read all_matches deliveries
        print("Reading all_matches.csv deliveries...")
        with z.open('all_matches.csv') as f:
            df_deliv = pd.read_csv(f, low_memory=False)
        print(f"Read {len(df_deliv):,} ball delivery rows.")

    # Standardize Seasons
    df_matches['season'] = df_matches['season'].apply(standardize_season)
    df_deliv['season'] = df_deliv['season'].apply(standardize_season)

    # Standardize Teams
    for col in ['team1', 'team2', 'toss_winner', 'winner', 'eliminator']:
        df_matches[col] = df_matches[col].apply(standardize_team)
    
    for col in ['batting_team', 'bowling_team']:
        df_deliv[col] = df_deliv[col].apply(standardize_team)

    # Standardize Venues
    df_matches['venue'] = df_matches['venue'].apply(standardize_venue)
    df_deliv['venue'] = df_deliv['venue'].apply(standardize_venue)

    # Add derived columns to deliveries
    print("Deriving ball-by-ball delivery statistics...")
    df_deliv['over'] = df_deliv['ball'].astype(int)
    df_deliv['ball_in_over'] = ((df_deliv['ball'] - df_deliv['over']) * 10).round().astype(int)
    
    # Extras fillna
    for ex in ['wides', 'noballs', 'byes', 'legbyes', 'penalty']:
        if ex in df_deliv.columns:
            df_deliv[ex] = df_deliv[ex].fillna(0).astype(int)
        else:
            df_deliv[ex] = 0
            
    df_deliv['is_wide'] = (df_deliv['wides'] > 0).astype(int)
    df_deliv['is_noball'] = (df_deliv['noballs'] > 0).astype(int)
    df_deliv['is_legal'] = ((df_deliv['is_wide'] == 0) & (df_deliv['is_noball'] == 0)).astype(int)
    df_deliv['runs_off_bat'] = df_deliv['runs_off_bat'].fillna(0).astype(int)
    df_deliv['extras'] = df_deliv['extras'].fillna(0).astype(int)
    df_deliv['total_runs'] = df_deliv['runs_off_bat'] + df_deliv['extras']
    
    df_deliv['is_four'] = (df_deliv['runs_off_bat'] == 4).astype(int)
    df_deliv['is_six'] = (df_deliv['runs_off_bat'] == 6).astype(int)
    df_deliv['is_dot'] = ((df_deliv['is_legal'] == 1) & (df_deliv['total_runs'] == 0)).astype(int)
    
    df_deliv['is_wicket'] = df_deliv['wicket_type'].notna().astype(int)
    non_bowler_dismissals = ['run out', 'retired hurt', 'retired out', 'obstructing the field']
    df_deliv['is_bowler_wicket'] = (
        (df_deliv['is_wicket'] == 1) & 
        (~df_deliv['wicket_type'].isin(non_bowler_dismissals))
    ).astype(int)
    
    # Bowler runs conceded: runs off bat + wides + noballs + penalty (byes/legbyes excluded per MCC laws)
    df_deliv['bowler_runs'] = df_deliv['runs_off_bat'] + df_deliv['wides'] + df_deliv['noballs'] + df_deliv['penalty']

    # Sort matches chronologically
    df_matches['date'] = pd.to_datetime(df_matches['date'], errors='coerce')
    df_matches = df_matches.sort_values(by=['date', 'match_id']).reset_index(drop=True)

    # Save cleaned core datasets
    matches_path = os.path.join(PROCESSED_DIR, 'matches_clean.csv')
    deliv_path = os.path.join(PROCESSED_DIR, 'deliveries_clean.csv')
    print(f"Saving matches to {matches_path}...")
    df_matches.to_csv(matches_path, index=False)
    print(f"Saving deliveries to {deliv_path}...")
    df_deliv.to_csv(deliv_path, index=False)

    # 3. Generate Analytical Summaries
    print("Generating pre-aggregated analytical summaries...")
    generate_batting_summary(df_deliv, df_matches)
    generate_bowling_summary(df_deliv, df_matches)
    generate_team_summary(df_matches, df_deliv)
    generate_venue_summary(df_matches, df_deliv)

    print("Data acquisition and preprocessing pipeline completed successfully!")

def generate_batting_summary(df_deliv, df_matches):
    # Innings-level scores for highest score and 50s/100s
    inns_bat = df_deliv.groupby(['match_id', 'striker']).agg(
        runs=('runs_off_bat', 'sum'),
        balls=('is_wide', lambda x: (x == 0).sum()),
        fours=('is_four', 'sum'),
        sixes=('is_six', 'sum')
    ).reset_index()
    
    # Out/Not-out status
    dismissals = df_deliv[df_deliv['player_dismissed'].notna()].groupby(['match_id', 'player_dismissed']).size().reset_index()
    dismissals.rename(columns={'player_dismissed': 'striker', 0: 'out_count'}, inplace=True)
    inns_bat = inns_bat.merge(dismissals, on=['match_id', 'striker'], how='left')
    inns_bat['is_out'] = inns_bat['out_count'].fillna(0).clip(upper=1).astype(int)

    # Aggregating player batting stats
    bat_summary = inns_bat.groupby('striker').agg(
        innings=('runs', 'count'),
        total_runs=('runs', 'sum'),
        balls_faced=('balls', 'sum'),
        highest_score=('runs', 'max'),
        fours=('fours', 'sum'),
        sixes=('sixes', 'sum'),
        total_outs=('is_out', 'sum'),
        hundreds=('runs', lambda x: (x >= 100).sum()),
        fifties=('runs', lambda x: ((x >= 50) & (x < 100)).sum()),
        ducks=('runs', lambda x: (x == 0).sum()),
        score_std=('runs', 'std')
    ).reset_index()

    # Matches played
    matches_played = df_deliv.groupby('striker')['match_id'].nunique().reset_index(name='matches')
    bat_summary = bat_summary.merge(matches_played, on='striker')

    # Derived metrics
    bat_summary['not_outs'] = bat_summary['innings'] - bat_summary['total_outs']
    bat_summary['batting_average'] = np.where(
        bat_summary['total_outs'] > 0,
        (bat_summary['total_runs'] / bat_summary['total_outs']).round(2),
        bat_summary['total_runs'].round(2)
    )
    bat_summary['strike_rate'] = np.where(
        bat_summary['balls_faced'] > 0,
        ((bat_summary['total_runs'] / bat_summary['balls_faced']) * 100).round(2),
        0.0
    )
    bat_summary['boundary_runs'] = (bat_summary['fours'] * 4) + (bat_summary['sixes'] * 6)
    bat_summary['boundary_percentage'] = np.where(
        bat_summary['total_runs'] > 0,
        ((bat_summary['boundary_runs'] / bat_summary['total_runs']) * 100).round(2),
        0.0
    )
    # Player Consistency Index (PCI): 100 - Coefficient of Variation (capped [0, 100])
    mean_score = bat_summary['total_runs'] / bat_summary['innings']
    cv = (bat_summary['score_std'].fillna(0) / mean_score.replace(0, np.nan)) * 100
    bat_summary['consistency_index'] = np.clip(100 - cv.fillna(50), 0, 100).round(2)

    bat_summary.rename(columns={'striker': 'player'}, inplace=True)
    bat_summary = bat_summary.sort_values(by='total_runs', ascending=False).reset_index(drop=True)
    
    out_file = os.path.join(PROCESSED_DIR, 'player_batting_summary.csv')
    bat_summary.to_csv(out_file, index=False)
    print(f"Saved batting summary to {out_file} ({len(bat_summary)} players)")

def generate_bowling_summary(df_deliv, df_matches):
    # Match-innings bowling figures
    match_bowl = df_deliv.groupby(['match_id', 'bowler']).agg(
        runs_conceded=('bowler_runs', 'sum'),
        legal_balls=('is_legal', 'sum'),
        wickets=('is_bowler_wicket', 'sum')
    ).reset_index()
    
    # Format match figures string e.g., '4/21'
    match_bowl['figure_str'] = match_bowl['wickets'].astype(str) + '/' + match_bowl['runs_conceded'].astype(str)
    # Sort key to find best figure (max wickets, then min runs)
    match_bowl = match_bowl.sort_values(by=['wickets', 'runs_conceded'], ascending=[False, True])
    best_fig = match_bowl.groupby('bowler').first().reset_index()[['bowler', 'figure_str']]
    best_fig.rename(columns={'figure_str': 'best_bowling_figure'}, inplace=True)

    # Maiden overs calculation (overs bowled with 0 bowler runs)
    over_bowl = df_deliv.groupby(['match_id', 'innings', 'over', 'bowler']).agg(
        over_runs=('bowler_runs', 'sum'),
        legal_balls=('is_legal', 'sum')
    ).reset_index()
    maidens = over_bowl[(over_bowl['legal_balls'] >= 6) & (over_bowl['over_runs'] == 0)].groupby('bowler').size().reset_index(name='maiden_overs')

    # Aggregating career bowling
    bowl_summary = match_bowl.groupby('bowler').agg(
        innings=('runs_conceded', 'count'),
        total_runs_conceded=('runs_conceded', 'sum'),
        legal_balls_bowled=('legal_balls', 'sum'),
        total_wickets=('wickets', 'sum'),
        four_wickets=('wickets', lambda x: (x == 4).sum()),
        five_wickets=('wickets', lambda x: (x >= 5).sum())
    ).reset_index()

    matches_played = df_deliv.groupby('bowler')['match_id'].nunique().reset_index(name='matches')
    bowl_summary = bowl_summary.merge(matches_played, on='bowler')
    bowl_summary = bowl_summary.merge(best_fig, on='bowler', how='left')
    bowl_summary = bowl_summary.merge(maidens, on='bowler', how='left')
    bowl_summary['maiden_overs'] = bowl_summary['maiden_overs'].fillna(0).astype(int)

    # Derived metrics
    bowl_summary['overs_bowled'] = (bowl_summary['legal_balls_bowled'] // 6) + ((bowl_summary['legal_balls_bowled'] % 6) / 10)
    exact_overs = bowl_summary['legal_balls_bowled'] / 6.0
    bowl_summary['economy_rate'] = np.where(
        exact_overs > 0,
        (bowl_summary['total_runs_conceded'] / exact_overs).round(2),
        0.0
    )
    bowl_summary['bowling_average'] = np.where(
        bowl_summary['total_wickets'] > 0,
        (bowl_summary['total_runs_conceded'] / bowl_summary['total_wickets']).round(2),
        np.nan
    )
    bowl_summary['bowling_strike_rate'] = np.where(
        bowl_summary['total_wickets'] > 0,
        (bowl_summary['legal_balls_bowled'] / bowl_summary['total_wickets']).round(2),
        np.nan
    )

    bowl_summary.rename(columns={'bowler': 'player'}, inplace=True)
    bowl_summary = bowl_summary.sort_values(by='total_wickets', ascending=False).reset_index(drop=True)
    
    out_file = os.path.join(PROCESSED_DIR, 'player_bowling_summary.csv')
    bowl_summary.to_csv(out_file, index=False)
    print(f"Saved bowling summary to {out_file} ({len(bowl_summary)} bowlers)")

def generate_team_summary(df_matches, df_deliv):
    teams = sorted(list(set(df_matches['team1'].dropna()).union(set(df_matches['team2'].dropna()))))
    records = []
    
    for t in teams:
        t_matches = df_matches[(df_matches['team1'] == t) | (df_matches['team2'] == t)]
        total = len(t_matches)
        if total == 0:
            continue
        wins = len(t_matches[t_matches['winner'] == t])
        losses = len(t_matches[(t_matches['winner'].notna()) & (t_matches['winner'] != t) & (t_matches['result'] != 'tie')])
        ties = len(t_matches[t_matches['result'] == t])
        no_results = len(t_matches[t_matches['result'] == 'no result'])
        win_pct = round((wins / total) * 100, 2)
        
        toss_wins = len(t_matches[t_matches['toss_winner'] == t])
        
        # Bat first wins vs Chase wins
        bat_first_matches = df_matches[
            ((df_matches['team1'] == t) & (df_matches['toss_winner'] == t) & (df_matches['toss_decision'] == 'bat')) |
            ((df_matches['team2'] == t) & (df_matches['toss_winner'] != t) & (df_matches['toss_decision'] == 'field')) |
            ((df_matches['team1'] == t) & (df_matches['toss_winner'] != t) & (df_matches['toss_decision'] == 'field'))
        ]
        # More direct check from deliveries innings 1
        t_inns1_matches = df_deliv[(df_deliv['innings'] == 1) & (df_deliv['batting_team'] == t)]['match_id'].unique()
        bat_first_wins = len(df_matches[(df_matches['match_id'].isin(t_inns1_matches)) & (df_matches['winner'] == t)])
        bat_first_total = len(df_matches[df_matches['match_id'].isin(t_inns1_matches)])
        
        t_inns2_matches = df_deliv[(df_deliv['innings'] == 2) & (df_deliv['batting_team'] == t)]['match_id'].unique()
        chase_wins = len(df_matches[(df_matches['match_id'].isin(t_inns2_matches)) & (df_matches['winner'] == t)])
        chase_total = len(df_matches[df_matches['match_id'].isin(t_inns2_matches)])
        
        # Runs scored & conceded
        runs_scored = df_deliv[df_deliv['batting_team'] == t]['total_runs'].sum()
        runs_conceded = df_deliv[df_deliv['bowling_team'] == t]['total_runs'].sum()
        
        records.append({
            'team': t,
            'matches_played': total,
            'wins': wins,
            'losses': losses,
            'ties': ties,
            'no_results': no_results,
            'win_percentage': win_pct,
            'toss_wins': toss_wins,
            'bat_first_matches': bat_first_total,
            'bat_first_wins': bat_first_wins,
            'bat_first_win_pct': round((bat_first_wins / bat_first_total * 100), 2) if bat_first_total > 0 else 0.0,
            'chase_matches': chase_total,
            'chase_wins': chase_wins,
            'chase_win_pct': round((chase_wins / chase_total * 100), 2) if chase_total > 0 else 0.0,
            'total_runs_scored': int(runs_scored),
            'total_runs_conceded': int(runs_conceded)
        })
        
    df_team_summary = pd.DataFrame(records).sort_values(by='wins', ascending=False).reset_index(drop=True)
    out_file = os.path.join(PROCESSED_DIR, 'team_summary.csv')
    df_team_summary.to_csv(out_file, index=False)
    print(f"Saved team summary to {out_file} ({len(df_team_summary)} teams)")

def generate_venue_summary(df_matches, df_deliv):
    # Innings totals
    inns_totals = df_deliv.groupby(['match_id', 'innings'])['total_runs'].sum().reset_index()
    inns_totals = inns_totals.merge(df_matches[['match_id', 'venue', 'winner']], on='match_id')

    inns1 = inns_totals[inns_totals['innings'] == 1]
    inns2 = inns_totals[inns_totals['innings'] == 2]

    venue_stats = []
    venues = sorted(df_matches['venue'].dropna().unique())
    
    for v in venues:
        m_venue = df_matches[df_matches['venue'] == v]
        total_m = len(m_venue)
        if total_m == 0:
            continue
            
        v_inns1 = inns1[inns1['venue'] == v]
        v_inns2 = inns2[inns2['venue'] == v]
        
        avg_1st_inns = round(v_inns1['total_runs'].mean(), 1) if len(v_inns1) > 0 else 0.0
        highest_score = int(inns_totals[inns_totals['venue'] == v]['total_runs'].max()) if len(inns_totals[inns_totals['venue'] == v]) > 0 else 0
        lowest_score = int(inns_totals[inns_totals['venue'] == v]['total_runs'].min()) if len(inns_totals[inns_totals['venue'] == v]) > 0 else 0

        # Chasing vs Defending wins at venue
        # Defending win = winner is the team that batted 1st
        deliv_inns1 = df_deliv[(df_deliv['match_id'].isin(m_venue['match_id'])) & (df_deliv['innings'] == 1)][['match_id', 'batting_team']].drop_duplicates()
        m_merged = m_venue.merge(deliv_inns1, on='match_id', how='left')
        
        bat_first_wins = (m_merged['winner'] == m_merged['batting_team']).sum()
        chase_wins = (m_merged['winner'].notna() & (m_merged['winner'] != m_merged['batting_team']) & (m_merged['result'] != 'no result')).sum()
        
        venue_stats.append({
            'venue': v,
            'matches_played': total_m,
            'avg_first_innings_score': avg_1st_inns,
            'highest_innings_score': highest_score,
            'lowest_innings_score': lowest_score,
            'bat_first_wins': int(bat_first_wins),
            'bat_first_win_pct': round((bat_first_wins / total_m) * 100, 2),
            'chase_wins': int(chase_wins),
            'chase_win_pct': round((chase_wins / total_m) * 100, 2)
        })
        
    df_venue = pd.DataFrame(venue_stats).sort_values(by='matches_played', ascending=False).reset_index(drop=True)
    out_file = os.path.join(PROCESSED_DIR, 'venue_summary.csv')
    df_venue.to_csv(out_file, index=False)
    print(f"Saved venue summary to {out_file} ({len(df_venue)} venues)")

if __name__ == '__main__':
    process_datasets()

