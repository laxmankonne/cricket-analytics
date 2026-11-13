"""
Bowling Analysis Utility Module
Provides dynamic calculations for bowling stats, economy, strike rates, best figures, and season trends.
"""

import numpy as np
import pandas as pd

def get_filtered_bowling_summary(deliv_df, season=None, team=None):
    df = deliv_df.copy()
    if season and season != 'All Seasons':
        df = df[df['season'] == str(season)]
    if team and team != 'All Teams':
        df = df[df['bowling_team'] == str(team)]

    if df.empty:
        return pd.DataFrame()

    match_bowl = df.groupby(['match_id', 'bowler']).agg(
        runs_conceded=('bowler_runs', 'sum'),
        legal_balls=('is_legal', 'sum'),
        wickets=('is_bowler_wicket', 'sum')
    ).reset_index()

    # Best bowling figure
    match_bowl['fig_str'] = match_bowl['wickets'].astype(str) + '/' + match_bowl['runs_conceded'].astype(str)
    sorted_figs = match_bowl.sort_values(by=['wickets', 'runs_conceded'], ascending=[False, True])
    best_fig = sorted_figs.groupby('bowler').first().reset_index()[['bowler', 'fig_str']]
    best_fig.columns = ['bowler', 'best_bowling_figure']

    # Maiden overs
    over_bowl = df.groupby(['match_id', 'innings', 'over', 'bowler']).agg(
        over_runs=('bowler_runs', 'sum'),
        legal_balls=('is_legal', 'sum')
    ).reset_index()
    maidens = over_bowl[(over_bowl['legal_balls'] >= 6) & (over_bowl['over_runs'] == 0)].groupby('bowler').size().reset_index(name='maiden_overs')

    summary = match_bowl.groupby('bowler').agg(
        innings=('runs_conceded', 'count'),
        total_runs_conceded=('runs_conceded', 'sum'),
        legal_balls_bowled=('legal_balls', 'sum'),
        total_wickets=('wickets', 'sum'),
        four_wickets=('wickets', lambda x: (x == 4).sum()),
        five_wickets=('wickets', lambda x: (x >= 5).sum())
    ).reset_index()

    matches = df.groupby('bowler')['match_id'].nunique().reset_index(name='matches')
    summary = summary.merge(matches, on='bowler')
    summary = summary.merge(best_fig, on='bowler', how='left')
    summary = summary.merge(maidens, on='bowler', how='left')
    summary['maiden_overs'] = summary['maiden_overs'].fillna(0).astype(int)

    summary['overs_bowled'] = (summary['legal_balls_bowled'] // 6) + ((summary['legal_balls_bowled'] % 6) / 10)
    exact_overs = summary['legal_balls_bowled'] / 6.0
    summary['economy_rate'] = np.where(
        exact_overs > 0,
        (summary['total_runs_conceded'] / exact_overs).round(2),
        0.0
    )
    summary['bowling_average'] = np.where(
        summary['total_wickets'] > 0,
        (summary['total_runs_conceded'] / summary['total_wickets']).round(2),
        np.nan
    )
    summary['bowling_strike_rate'] = np.where(
        summary['total_wickets'] > 0,
        (summary['legal_balls_bowled'] / summary['total_wickets']).round(2),
        np.nan
    )
    summary.rename(columns={'bowler': 'player'}, inplace=True)
    return summary.sort_values(by='total_wickets', ascending=False).reset_index(drop=True)

def get_best_match_bowling_figures(deliv_df, top_n=10):
    match_bowl = deliv_df.groupby(['match_id', 'season', 'bowling_team', 'batting_team', 'bowler']).agg(
        runs=('bowler_runs', 'sum'),
        balls=('is_legal', 'sum'),
        wickets=('is_bowler_wicket', 'sum')
    ).reset_index()
    match_bowl['overs'] = (match_bowl['balls'] // 6) + ((match_bowl['balls'] % 6) / 10)
    match_bowl['economy'] = np.where(match_bowl['balls'] > 0, ((match_bowl['runs'] / (match_bowl['balls'] / 6.0))).round(2), 0.0)
    match_bowl['figure'] = match_bowl['wickets'].astype(str) + '/' + match_bowl['runs'].astype(str)
    
    sorted_df = match_bowl.sort_values(by=['wickets', 'runs'], ascending=[False, True]).head(top_n).reset_index(drop=True)
    sorted_df.rename(columns={'bowler': 'player'}, inplace=True)
    return sorted_df

def get_bowler_season_breakdown(deliv_df, player_name):
    df_p = deliv_df[deliv_df['bowler'] == player_name]
    if df_p.empty:
        return pd.DataFrame()
        
    season_stats = df_p.groupby('season').agg(
        matches=('match_id', 'nunique'),
        balls=('is_legal', 'sum'),
        runs=('bowler_runs', 'sum'),
        wickets=('is_bowler_wicket', 'sum')
    ).reset_index()
    
    season_stats['overs'] = (season_stats['balls'] // 6) + ((season_stats['balls'] % 6) / 10)
    exact_overs = season_stats['balls'] / 6.0
    season_stats['economy'] = np.where(exact_overs > 0, (season_stats['runs'] / exact_overs).round(2), 0.0)
    season_stats['average'] = np.where(season_stats['wickets'] > 0, (season_stats['runs'] / season_stats['wickets']).round(2), np.nan)
    return season_stats.sort_values(by='season').reset_index(drop=True)
