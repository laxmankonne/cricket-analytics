"""
Venue Analysis Utility Module
Provides analytics on stadium scoring trends, first innings par scores, and chasing biases.
"""

import numpy as np
import pandas as pd

def get_venue_scoring_patterns(deliv_df, venue_name):
    df_v = deliv_df[deliv_df['venue'] == venue_name]
    if df_v.empty:
        return pd.DataFrame()

    inns_totals = df_v.groupby(['match_id', 'innings'])['total_runs'].sum().reset_index()
    inns1 = inns_totals[inns_totals['innings'] == 1]['total_runs']
    inns2 = inns_totals[inns_totals['innings'] == 2]['total_runs']

    return {
        'inns1_scores': inns1,
        'inns2_scores': inns2,
        'avg_inns1': round(inns1.mean(), 1) if not inns1.empty else 0.0,
        'avg_inns2': round(inns2.mean(), 1) if not inns2.empty else 0.0,
        'max_inns1': int(inns1.max()) if not inns1.empty else 0,
        'min_inns1': int(inns1.min()) if not inns1.empty else 0,
        'matches_count': len(inns1)
    }

def get_venue_team_records(matches_df, venue_name):
    df_v = matches_df[matches_df['venue'] == venue_name]
    if df_v.empty:
        return pd.DataFrame()

    teams = sorted(list(set(df_v['team1'].dropna()).union(set(df_v['team2'].dropna()))))
    records = []

    for t in teams:
        t_m = df_v[(df_v['team1'] == t) | (df_v['team2'] == t)]
        total = len(t_m)
        if total == 0:
            continue
        wins = len(t_m[t_m['winner'] == t])
        records.append({
            'team': t,
            'matches': total,
            'wins': wins,
            'losses': total - wins,
            'win_pct': round((wins / total) * 100, 2)
        })

    return pd.DataFrame(records).sort_values(by='wins', ascending=False).reset_index(drop=True)
