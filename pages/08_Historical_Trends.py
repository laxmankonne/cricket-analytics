"""
Module 8: Historical Trends
Features: Longitudinal trends across 17+ tournament seasons, evolution of run rates,
boundary explosion (fours and sixes per match), and era dominance.
"""

import streamlit as st
import pandas as pd
from utils.data_loader import load_matches, load_deliveries
from utils.ui_helper import apply_app_styles, render_sidebar_header, render_page_header
from utils.visualization import create_line_chart, create_vertical_bar, apply_custom_theme
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Historical Trends | Cricket Analytics",
    page_icon="🏏",
    layout="wide"
)

apply_app_styles()
render_sidebar_header()

render_page_header(
    title="Historical Trends & Evolution",
    subtitle="Analyzing the statistical evolution of T20 cricket from 2008 to the present day: scoring velocity, boundary density, and era dominance.",
    badge_text="MODULE 8 • HISTORICAL ANALYTICS"
)

df_matches = load_matches()
df_deliv = load_deliveries()

# Aggregate Season Historical Statistics
season_trends = df_deliv.groupby('season').agg(
    matches=('match_id', 'nunique'),
    total_runs=('total_runs', 'sum'),
    legal_balls=('is_legal', 'sum'),
    total_wickets=('is_wicket', 'sum'),
    fours=('is_four', 'sum'),
    sixes=('is_six', 'sum')
).reset_index()

season_trends['overs'] = season_trends['legal_balls'] / 6.0
season_trends['run_rate'] = (season_trends['total_runs'] / season_trends['overs']).round(2)
season_trends['runs_per_match'] = (season_trends['total_runs'] / season_trends['matches']).round(1)
season_trends['sixes_per_match'] = (season_trends['sixes'] / season_trends['matches']).round(1)
season_trends['fours_per_match'] = (season_trends['fours'] / season_trends['matches']).round(1)
season_trends['wickets_per_match'] = (season_trends['total_wickets'] / season_trends['matches']).round(1)

# Sort chronologically
season_trends = season_trends.sort_values(by='season').reset_index(drop=True)

tab1, tab2, tab3 = st.tabs([
    "📈 Scoring Velocity & Run Rates",
    "💣 The Boundary Explosion (6s & 4s)",
    "🏆 Era Dominance by Franchise"
])

with tab1:
    st.markdown("#### ⚡ Overall Tournament Run Rate (Runs per Over) Across Seasons")
    fig_rr = create_line_chart(
        season_trends,
        x_col='season',
        y_col='run_rate',
        title="Tournament Average Run Rate (Runs Per Over: 2008 – Present)"
    )
    st.plotly_chart(fig_rr, use_container_width=True)

    c_r1, c_r2 = st.columns(2)
    with c_r1:
        fig_rpm = create_line_chart(
            season_trends,
            x_col='season',
            y_col='runs_per_match',
            title="Average Total Runs Scored Per Match by Season"
        )
        st.plotly_chart(fig_rpm, use_container_width=True)

    with c_r2:
        fig_wpm = create_line_chart(
            season_trends,
            x_col='season',
            y_col='wickets_per_match',
            title="Average Wickets Lost Per Match by Season"
        )
        st.plotly_chart(fig_wpm, use_container_width=True)

with tab2:
    st.markdown("#### 💣 Growth of Sixes and Fours per Match")
    fig_bnd = go.Figure()
    fig_bnd.add_trace(go.Bar(
        x=season_trends['season'],
        y=season_trends['sixes_per_match'],
        name='Sixes per Match',
        marker_color='#16A34A'
    ))
    fig_bnd.add_trace(go.Bar(
        x=season_trends['season'],
        y=season_trends['fours_per_match'],
        name='Fours per Match',
        marker_color='#38BDF8'
    ))
    fig_bnd.update_layout(barmode='group')
    st.plotly_chart(apply_custom_theme(fig_bnd, "Boundary Frequency Evolution (Fours & Sixes per Match)"), use_container_width=True)

with tab3:
    st.markdown("#### 🏆 Franchise Wins Distribution Across Eras")
    st.caption("Tracking title and match-winning eras across franchises over 17+ seasons.")

    team_season_wins = df_matches[df_matches['winner'].notna()].groupby(['season', 'winner']).size().reset_index(name='wins')
    
    # Filter to top historical teams
    top_historical_teams = ['Mumbai Indians', 'Chennai Super Kings', 'Kolkata Knight Riders', 'Royal Challengers Bengaluru', 'Delhi Capitals', 'Rajasthan Royals']
    plot_tsw = team_season_wins[team_season_wins['winner'].isin(top_historical_teams)]

    fig_eras = px.line(
        plot_tsw,
        x='season',
        y='wins',
        color='winner',
        markers=True,
        title="Season Match Wins for Major Franchises",
        template='plotly_dark'
    )
    fig_eras.update_layout(paper_bgcolor='#111C2E', plot_bgcolor='#111C2E', font=dict(color='#F8FAFC'))
    st.plotly_chart(fig_eras, use_container_width=True)

