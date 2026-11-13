"""
Team Performance Analysis Utility Module
Provides calculations for team standings, win rates, head-to-head records, toss impact, and bat first vs chase.
"""

import numpy as np
import pandas as pd

def get_team_standings(matches_df, season=None):
    df = matches_df.copy()
    if season and season != 'All Seasons':
        df = df[df['season'] == str(season)]

    if df.empty:
        return pd.DataFrame()

    teams = sorted(list(set(df['team1'].dropna()).union(set(df['team2'].dropna()))))
    records = []

    for t in teams:
        t_matches = df[(df['team1'] == t) | (df['team2'] == t)]
        total = len(t_matches)
        if total == 0:
            continue
        wins = len(t_matches[t_matches['winner'] == t])
        losses = len(t_matches[(t_matches['winner'].notna()) & (t_matches['winner'] != t) & (t_matches['result'] != 'tie')])
        ties = len(t_matches[t_matches['result'] == 'tie'])
        no_results = len(t_matches[t_matches['result'] == 'no result'])
        win_pct = round((wins / total) * 100, 2)
        toss_wins = len(t_matches[t_matches['toss_winner'] == t])

        records.append({
            'team': t,
            'matches': total,
            'wins': wins,
            'losses': losses,
            'ties': ties,
            'no_result': no_results,
            'win_pct': win_pct,
            'toss_wins': toss_wins
        })

    standings = pd.DataFrame(records).sort_values(by=['wins', 'win_pct'], ascending=[False, False]).reset_index(drop=True)
    return standings

def get_head_to_head(matches_df, team1, team2):
    h2h = matches_df[
        ((matches_df['team1'] == team1) & (matches_df['team2'] == team2)) |
        ((matches_df['team1'] == team2) & (matches_df['team2'] == team1))
    ].sort_values(by='date', ascending=False)
    
    total = len(h2h)
    team1_wins = len(h2h[h2h['winner'] == team1])
    team2_wins = len(h2h[h2h['winner'] == team2])
    ties_nr = total - (team1_wins + team2_wins)
    
    return {
        'total_matches': total,
        'team1_wins': team1_wins,
        'team2_wins': team2_wins,
        'ties_or_nr': ties_nr,
        'matches_df': h2h
    }

def get_team_season_trend(matches_df, team_name):
    df_t = matches_df[(matches_df['team1'] == team_name) | (matches_df['team2'] == team_name)]
    if df_t.empty:
        return pd.DataFrame()
        
    seasons = sorted(df_t['season'].dropna().unique().tolist())
    trend = []
    for s in seasons:
        s_matches = df_t[df_t['season'] == s]
        total = len(s_matches)
        wins = len(s_matches[s_matches['winner'] == team_name])
        trend.append({
            'season': s,
            'matches': total,
            'wins': wins,
            'win_pct': round((wins / total) * 100, 2) if total > 0 else 0.0
        })
    return pd.DataFrame(trend)

def get_toss_impact_analysis(matches_df, team=None):
    df = matches_df.copy()
    if team and team != 'All Teams':
        df = df[(df['team1'] == team) | (df['team2'] == team)]

    total_matches = len(df.dropna(subset=['toss_winner', 'winner']))
    if total_matches == 0:
        return {}

    toss_and_match_winner = len(df[df['toss_winner'] == df['winner']])
    toss_winner_win_pct = round((toss_and_match_winner / total_matches) * 100, 2)

    # Toss decision breakdown
    decision_grp = df.groupby('toss_decision').size().reset_index(name='count')
    decision_wins = df[df['toss_winner'] == df['winner']].groupby('toss_decision').size().reset_index(name='wins')
    merged_decision = decision_grp.merge(decision_wins, on='toss_decision', how='left').fillna(0)
    merged_decision['win_pct'] = (merged_decision['wins'] / merged_decision['count'] * 100).round(2)

    return {
        'total_matches': total_matches,
        'toss_and_match_wins': toss_and_match_winner,
        'toss_win_pct': toss_winner_win_pct,
        'decision_breakdown': merged_decision
    }

