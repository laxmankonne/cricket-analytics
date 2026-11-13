"""
Module 7: Player Comparison
Features: Head-to-head multi-player radar charts, normalized KPI matrices,
and side-by-side batting and bowling statistical evaluations.
"""

import streamlit as st
import numpy as np
import pandas as pd
from utils.data_loader import load_batting_summary, load_bowling_summary, load_deliveries
from utils.ui_helper import apply_app_styles, render_sidebar_header, render_page_header
from utils.batting_analysis import get_player_season_breakdown
from utils.visualization import create_radar_chart, apply_custom_theme
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Player Comparison | Cricket Analytics",
    page_icon="🏏",
    layout="wide"
)

apply_app_styles()
render_sidebar_header()

render_page_header(
    title="Head-to-Head Player Comparison",
    subtitle="Interactive radar evaluations, career milestone side-by-sides, and longitudinal performance trajectories.",
    badge_text="MODULE 7 • COMPARATIVE ANALYTICS"
)

df_batting = load_batting_summary()
df_bowling = load_bowling_summary()
df_deliv = load_deliveries()

all_players = sorted(list(set(df_batting['player']).union(set(df_bowling['player']))))

st.markdown("### 👥 Select Players to Compare")
p_col1, p_col2 = st.columns(2)
with p_col1:
    default_p1 = 'V Kohli' if 'V Kohli' in all_players else all_players[0]
    player1 = st.selectbox("Select Player 1", all_players, index=all_players.index(default_p1))
with p_col2:
    default_p2 = 'RG Sharma' if 'RG Sharma' in all_players else all_players[1]
    player2_opts = [p for p in all_players if p != player1]
    player2 = st.selectbox("Select Player 2", player2_opts, index=player2_opts.index(default_p2) if default_p2 in player2_opts else 0)

# Fetch stats for both
p1_bat = df_batting[df_batting['player'] == player1]
p2_bat = df_batting[df_batting['player'] == player2]

p1_bowl = df_bowling[df_bowling['player'] == player1]
p2_bowl = df_bowling[df_bowling['player'] == player2]

tab_bat, tab_bowl, tab_radar = st.tabs([
    "🏏 Batting Comparison",
    "🎯 Bowling Comparison",
    "🕸️ Normalized Radar Evaluation"
])

with tab_bat:
    st.markdown("#### 🏏 Career Batting Metrics")
    metrics_list = [
        ('Total Runs', 'total_runs', '{:,.0f}'),
        ('Innings Batted', 'innings', '{:,.0f}'),
        ('Batting Average', 'batting_average', '{:.2f}'),
        ('Strike Rate', 'strike_rate', '{:.2f}'),
        ('Highest Score', 'highest_score', '{:,.0f}'),
        ('Fours (4s)', 'fours', '{:,.0f}'),
        ('Sixes (6s)', 'sixes', '{:,.0f}'),
        ('Boundary %', 'boundary_percentage', '{:.2f}%'),
        ('Hundreds (100s)', 'hundreds', '{:,.0f}'),
        ('Fifties (50s)', 'fifties', '{:,.0f}'),
        ('Consistency Index (PCI)', 'consistency_index', '{:.1f}')
    ]

    comp_rows = []
    for label, col, fmt in metrics_list:
        v1 = p1_bat[col].iloc[0] if not p1_bat.empty else 0
        v2 = p2_bat[col].iloc[0] if not p2_bat.empty else 0
        comp_rows.append({
            'Metric': label,
            player1: fmt.format(v1) if pd.notna(v1) else '0',
            player2: fmt.format(v2) if pd.notna(v2) else '0'
        })

    st.dataframe(pd.DataFrame(comp_rows), use_container_width=True, hide_index=True)

    # Season trajectory comparison
    s1_df = get_player_season_breakdown(df_deliv, player1)
    s2_df = get_player_season_breakdown(df_deliv, player2)

    if not s1_df.empty or not s2_df.empty:
        st.markdown("##### 📈 Runs Scored by Season Comparison")
        fig_comp_season = go.Figure()
        if not s1_df.empty:
            fig_comp_season.add_trace(go.Bar(x=s1_df['season'], y=s1_df['runs'], name=player1, marker_color='#16A34A'))
        if not s2_df.empty:
            fig_comp_season.add_trace(go.Bar(x=s2_df['season'], y=s2_df['runs'], name=player2, marker_color='#38BDF8'))
            
        fig_comp_season.update_layout(barmode='group')
        st.plotly_chart(apply_custom_theme(fig_comp_season, "Season-by-Season Runs"), use_container_width=True)

with tab_bowl:
    st.markdown("#### 🎯 Career Bowling Metrics")
    bowl_metrics = [
        ('Total Wickets', 'total_wickets', '{:,.0f}'),
        ('Overs Bowled', 'overs_bowled', '{:.1f}'),
        ('Bowling Average', 'bowling_average', '{:.2f}'),
        ('Economy Rate', 'economy_rate', '{:.2f}'),
        ('Bowling Strike Rate', 'bowling_strike_rate', '{:.2f}'),
        ('Maiden Overs', 'maiden_overs', '{:,.0f}'),
        ('Best Bowling Figure', 'best_bowling_figure', '{}'),
        ('5-Wicket Hauls', 'five_wickets', '{:,.0f}')
    ]

    bowl_comp_rows = []
    for label, col, fmt in bowl_metrics:
        v1 = p1_bowl[col].iloc[0] if not p1_bowl.empty else 0
        v2 = p2_bowl[col].iloc[0] if not p2_bowl.empty else 0
        bowl_comp_rows.append({
            'Metric': label,
            player1: fmt.format(v1) if pd.notna(v1) and v1 != 0 else 'N/A',
            player2: fmt.format(v2) if pd.notna(v2) and v2 != 0 else 'N/A'
        })

    st.dataframe(pd.DataFrame(bowl_comp_rows), use_container_width=True, hide_index=True)

with tab_radar:
    st.markdown("#### 🕸️ Multi-Dimensional Skill Radar Chart")
    st.caption("Normalized relative skill dimensions (0 to 100 benchmarked against all-time tournament maximums).")

    # Benchmarks for normalization
    max_runs = df_batting['total_runs'].max()
    max_avg = 50.0
    max_sr = 175.0
    max_bnd = 80.0
    max_wkts = df_bowling['total_wickets'].max()

    def get_radar_vector(p_bat, p_bowl):
        runs_val = (p_bat['total_runs'].iloc[0] / max_runs * 100) if not p_bat.empty else 0
        avg_val = min(100, (p_bat['batting_average'].iloc[0] / max_avg * 100)) if not p_bat.empty else 0
        sr_val = min(100, (p_bat['strike_rate'].iloc[0] / max_sr * 100)) if not p_bat.empty else 0
        bnd_val = min(100, (p_bat['boundary_percentage'].iloc[0] / max_bnd * 100)) if not p_bat.empty else 0
        pci_val = p_bat['consistency_index'].iloc[0] if not p_bat.empty else 0
        wkt_val = (p_bowl['total_wickets'].iloc[0] / max_wkts * 100) if not p_bowl.empty else 0
        return [runs_val, avg_val, sr_val, bnd_val, pci_val, wkt_val]

    categories = ['Volume (Runs)', 'Batting Average', 'Strike Rate', 'Boundary %', 'Consistency (PCI)', 'Wickets']
    vals_p1 = get_radar_vector(p1_bat, p1_bowl)
    vals_p2 = get_radar_vector(p2_bat, p2_bowl)

    fig_radar = create_radar_chart(
        categories=categories,
        player1_name=player1,
        player1_vals=vals_p1,
        player2_name=player2,
        player2_vals=vals_p2,
        title=f"Skill Footprint: {player1} vs {player2}"
    )
    st.plotly_chart(fig_radar, use_container_width=True)

