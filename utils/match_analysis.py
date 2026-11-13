"""
Match Analysis Utility Module
Provides scorecard generation, over-by-over progression, extreme totals, and close finishes.
"""

import numpy as np
import pandas as pd

def get_match_scorecard(deliv_df, match_id):
    df_m = deliv_df[deliv_df['match_id'] == match_id]
    if df_m.empty:
        return None, None, None, None

    innings_list = sorted(df_m['innings'].unique())
    innings_data = []

    for inn in innings_list:
        df_inn = df_m[df_m['innings'] == inn]
        bat_team = df_inn['batting_team'].iloc[0]
        bowl_team = df_inn['bowling_team'].iloc[0]
        
        # Batting card
        bat_card = df_inn.groupby('striker').agg(
            runs=('runs_off_bat', 'sum'),
            balls=('is_wide', lambda x: (x == 0).sum()),
            fours=('is_four', 'sum'),
            sixes=('is_six', 'sum')
        ).reset_index()
        bat_card['strike_rate'] = np.where(bat_card['balls'] > 0, ((bat_card['runs'] / bat_card['balls']) * 100).round(2), 0.0)

        # Dismissal info
        out_info = df_inn[df_inn['player_dismissed'].notna()][['player_dismissed', 'wicket_type', 'bowler', 'fielder_1']].drop_duplicates(subset=['player_dismissed'])
        out_info.columns = ['striker', 'wicket_type', 'bowler', 'fielder']
        bat_card = bat_card.merge(out_info, on='striker', how='left')
        bat_card['dismissal'] = np.where(
            bat_card['wicket_type'].notna(),
            bat_card['wicket_type'] + ' b ' + bat_card['bowler'].fillna(''),
            'not out'
        )

        # Bowling card
        bowl_card = df_inn.groupby('bowler').agg(
            runs=('bowler_runs', 'sum'),
            balls=('is_legal', 'sum'),
            wickets=('is_bowler_wicket', 'sum')
        ).reset_index()
        bowl_card['overs'] = (bowl_card['balls'] // 6) + ((bowl_card['balls'] % 6) / 10)
        bowl_card['economy'] = np.where(bowl_card['balls'] > 0, (bowl_card['runs'] / (bowl_card['balls'] / 6.0)).round(2), 0.0)

        # Innings summary totals
        total_runs = df_inn['total_runs'].sum()
        total_wickets = df_inn['is_wicket'].sum()
        total_balls = df_inn['is_legal'].sum()
        overs_str = f"{total_balls // 6}.{total_balls % 6}"
        extras_sum = df_inn['extras'].sum()

        innings_data.append({
            'innings_num': inn,
            'batting_team': bat_team,
            'bowling_team': bowl_team,
            'total_runs': total_runs,
            'total_wickets': total_wickets,
            'overs': overs_str,
            'extras': extras_sum,
            'batting_card': bat_card.sort_values(by='runs', ascending=False),
            'bowling_card': bowl_card.sort_values(by=['wickets', 'runs'], ascending=[False, True])
        })

    return innings_data

def get_match_worm_data(deliv_df, match_id):
    df_m = deliv_df[deliv_df['match_id'] == match_id].sort_values(by=['innings', 'ball'])
    if df_m.empty:
        return None, None

    inns1 = df_m[df_m['innings'] == 1].copy()
    inns2 = df_m[df_m['innings'] == 2].copy()

    for df_inn in [inns1, inns2]:
        if not df_inn.empty:
            df_inn['cumulative_runs'] = df_inn['total_runs'].cumsum()
            df_inn['over_ball'] = df_inn['ball']

    return inns1, inns2

def get_highest_and_lowest_totals(deliv_df, matches_df, top_n=10):
    totals = deliv_df.groupby(['match_id', 'innings', 'batting_team', 'bowling_team']).agg(
        runs=('total_runs', 'sum'),
        wickets=('is_wicket', 'sum'),
        balls=('is_legal', 'sum')
    ).reset_index()
    totals = totals.merge(matches_df[['match_id', 'season', 'date', 'venue']], on='match_id')
    totals['overs'] = (totals['balls'] // 6) + ((totals['balls'] % 6) / 10)
    totals['score_str'] = totals['runs'].astype(str) + '/' + totals['wickets'].astype(str) + f" ({totals['overs']})"

    highest = totals.sort_values(by='runs', ascending=False).head(top_n).reset_index(drop=True)
    # Lowest totals (excluding rain-shortened matches with < 10 overs unless all out)
    valid_low = totals[(totals['balls'] >= 60) | (totals['wickets'] >= 10)]
    lowest = valid_low.sort_values(by='runs', ascending=True).head(top_n).reset_index(drop=True)

    return highest, lowest

def get_closest_finishes(matches_df, top_n=10):
    # Runs margin <= 5 or Wickets margin == 1 or Tie
    runs_close = matches_df[(matches_df['result'] == 'runs') & (matches_df['result_margin'] <= 5)].sort_values(by='result_margin')
    wickets_close = matches_df[(matches_df['result'] == 'wickets') & (matches_df['result_margin'] == 1)].sort_values(by='date', ascending=False)
    ties = matches_df[matches_df['result'] == 'tie'].sort_values(by='date', ascending=False)
    return runs_close.head(top_n), wickets_close.head(top_n), ties

