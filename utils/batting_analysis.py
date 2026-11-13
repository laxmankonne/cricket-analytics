"""
Batting Analysis Utility Module
Provides pure dynamic statistical functions for batting metrics, filters, and player breakdowns.
"""

import numpy as np
import pandas as pd

def get_filtered_batting_summary(deliv_df, season=None, team=None):
    df = deliv_df.copy()
    if season and season != 'All Seasons':
        df = df[df['season'] == str(season)]
    if team and team != 'All Teams':
        df = df[df['batting_team'] == str(team)]

    if df.empty:
        return pd.DataFrame()

    inns_bat = df.groupby(['match_id', 'striker']).agg(
        runs=('runs_off_bat', 'sum'),
        balls=('is_wide', lambda x: (x == 0).sum()),
        fours=('is_four', 'sum'),
        sixes=('is_six', 'sum')
    ).reset_index()

    dismissals = df[df['player_dismissed'].notna()].groupby(['match_id', 'player_dismissed']).size().reset_index()
    dismissals.columns = ['match_id', 'striker', 'out_count']
    inns_bat = inns_bat.merge(dismissals, on=['match_id', 'striker'], how='left')
    inns_bat['is_out'] = inns_bat['out_count'].fillna(0).clip(upper=1).astype(int)

    summary = inns_bat.groupby('striker').agg(
        innings=('runs', 'count'),
        total_runs=('runs', 'sum'),
        balls_faced=('balls', 'sum'),
        highest_score=('runs', 'max'),
        fours=('fours', 'sum'),
        sixes=('sixes', 'sum'),
        total_outs=('is_out', 'sum'),
        hundreds=('runs', lambda x: (x >= 100).sum()),
        fifties=('runs', lambda x: ((x >= 50) & (x < 100)).sum()),
        ducks=('runs', lambda x: (x == 0).sum())
    ).reset_index()

    matches = df.groupby('striker')['match_id'].nunique().reset_index(name='matches')
    summary = summary.merge(matches, on='striker')

    summary['not_outs'] = summary['innings'] - summary['total_outs']
    summary['batting_average'] = np.where(
        summary['total_outs'] > 0,
        (summary['total_runs'] / summary['total_outs']).round(2),
        summary['total_runs'].round(2)
    )
    summary['strike_rate'] = np.where(
        summary['balls_faced'] > 0,
        ((summary['total_runs'] / summary['balls_faced']) * 100).round(2),
        0.0
    )
    summary['boundary_runs'] = (summary['fours'] * 4) + (summary['sixes'] * 6)
    summary['boundary_pct'] = np.where(
        summary['total_runs'] > 0,
        ((summary['boundary_runs'] / summary['total_runs']) * 100).round(2),
        0.0
    )
    summary.rename(columns={'striker': 'player'}, inplace=True)
    return summary.sort_values(by='total_runs', ascending=False).reset_index(drop=True)

def get_highest_individual_innings(deliv_df, top_n=10):
    inns = deliv_df.groupby(['match_id', 'season', 'batting_team', 'bowling_team', 'striker']).agg(
        runs=('runs_off_bat', 'sum'),
        balls=('is_wide', lambda x: (x == 0).sum()),
        fours=('is_four', 'sum'),
        sixes=('is_six', 'sum')
    ).reset_index()
    inns['strike_rate'] = np.where(inns['balls'] > 0, ((inns['runs'] / inns['balls']) * 100).round(2), 0.0)
    inns.rename(columns={'striker': 'player'}, inplace=True)
    return inns.sort_values(by='runs', ascending=False).head(top_n).reset_index(drop=True)

def get_player_season_breakdown(deliv_df, player_name):
    df_p = deliv_df[deliv_df['striker'] == player_name]
    if df_p.empty:
        return pd.DataFrame()
    
    inns = df_p.groupby(['season', 'match_id']).agg(
        runs=('runs_off_bat', 'sum'),
        balls=('is_wide', lambda x: (x == 0).sum()),
        fours=('is_four', 'sum'),
        sixes=('is_six', 'sum')
    ).reset_index()

    season_stats = inns.groupby('season').agg(
        innings=('runs', 'count'),
        runs=('runs', 'sum'),
        balls=('balls', 'sum'),
        highest_score=('runs', 'max'),
        fours=('fours', 'sum'),
        sixes=('sixes', 'sum')
    ).reset_index()

    season_stats['strike_rate'] = np.where(
        season_stats['balls'] > 0,
        ((season_stats['runs'] / season_stats['balls']) * 100).round(2),
        0.0
    )
    return season_stats.sort_values(by='season').reset_index(drop=True)

def get_player_innings_scores(deliv_df, player_name):
    df_p = deliv_df[deliv_df['striker'] == player_name]
    if df_p.empty:
        return pd.DataFrame()
    inns = df_p.groupby('match_id').agg(
        runs=('runs_off_bat', 'sum'),
        balls=('is_wide', lambda x: (x == 0).sum()),
        fours=('is_four', 'sum'),
        sixes=('is_six', 'sum')
    ).reset_index()
    return inns

