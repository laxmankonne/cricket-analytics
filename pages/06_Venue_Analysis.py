"""
Module 6: Venue Analysis
Features: Stadium matches played, average 1st innings scores, chasing vs defending win rates,
highest/lowest stadium totals, and venue comparisons.
"""

import streamlit as st
import pandas as pd
from utils.data_loader import load_matches, load_deliveries, load_venue_summary
from utils.ui_helper import apply_app_styles, render_sidebar_header, render_page_header
from utils.venue_analysis import get_venue_scoring_patterns, get_venue_team_records
from utils.visualization import (
    create_horizontal_bar, create_vertical_bar,
    create_donut_chart, create_scatter_plot
)
import plotly.express as px

st.set_page_config(
    page_title="Venue Analysis | Cricket Analytics",
    page_icon="🏏",
    layout="wide"
)

apply_app_styles()
render_sidebar_header()

render_page_header(
    title="Venue & Stadium Analysis",
    subtitle="Evaluating ground dimensions, pitch scoring behavior, average 1st innings par totals, and toss chasing advantages.",
    badge_text="MODULE 6 • VENUE ANALYTICS"
)

df_matches = load_matches()
df_deliv = load_deliveries()
df_venues = load_venue_summary()

# Top KPIs Row
vkpi1, vkpi2, vkpi3, vkpi4 = st.columns(4)
with vkpi1:
    st.metric("Total Venues Analyzed", f"{len(df_venues)}")
with vkpi2:
    top_venue = df_venues.iloc[0]
    st.metric("Most Matches Hosted", top_venue['venue'].split(',')[0], f"{int(top_venue['matches_played'])} matches")
with vkpi3:
    highest_avg = df_venues[df_venues['matches_played'] >= 15].sort_values(by='avg_first_innings_score', ascending=False).iloc[0]
    st.metric("Highest Avg 1st Inns Score", f"{highest_avg['avg_first_innings_score']:.1f}", highest_avg['venue'].split(',')[0])
with vkpi4:
    chase_bias_venue = df_venues[df_venues['matches_played'] >= 20].sort_values(by='chase_win_pct', ascending=False).iloc[0]
    st.metric("Highest Chasing Win Rate", f"{chase_bias_venue['chase_win_pct']:.1f}%", chase_bias_venue['venue'].split(',')[0])

st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs([
    "🏟️ Stadium Par Scores & Matches",
    "🎯 Chasing vs Defending Bias",
    "🔍 Stadium Ground Deep-Dive"
])

with tab1:
    v_c1, v_c2 = st.columns(2)
    with v_c1:
        top_grounds = df_venues.head(10)[['venue', 'matches_played']].copy()
        fig_grounds = create_horizontal_bar(
            top_grounds,
            x_col='matches_played',
            y_col='venue',
            title="Top 10 Most Active Cricket Stadiums"
        )
        st.plotly_chart(fig_grounds, use_container_width=True)

    with v_c2:
        top_par = df_venues[df_venues['matches_played'] >= 10].sort_values(by='avg_first_innings_score', ascending=False).head(10)
        fig_par = create_horizontal_bar(
            top_par,
            x_col='avg_first_innings_score',
            y_col='venue',
            title="Average 1st Innings Par Score (Min 10 Matches)"
        )
        st.plotly_chart(fig_par, use_container_width=True)

    st.markdown("#### 📋 Comprehensive Venue Summary Table")
    st.dataframe(df_venues, use_container_width=True, hide_index=True)

with tab2:
    st.markdown("#### ⚖️ Ground Bias: Batting First vs Chasing Win Rates")
    st.caption("Comparison of win ratios at prominent stadiums (Min 15 matches hosted).")
    
    qual_v = df_venues[df_venues['matches_played'] >= 15].head(12).copy()
    fig_bias = px.bar(
        qual_v,
        x='venue',
        y=['bat_first_win_pct', 'chase_win_pct'],
        barmode='group',
        title="Win % Batting 1st vs Chasing by Stadium",
        labels={'value': 'Win Percentage (%)', 'variable': 'Condition'},
        color_discrete_map={'bat_first_win_pct': '#16A34A', 'chase_win_pct': '#38BDF8'},
        template='plotly_dark'
    )
    fig_bias.update_layout(paper_bgcolor='#111C2E', plot_bgcolor='#111C2E', font=dict(color='#F8FAFC'))
    st.plotly_chart(fig_bias, use_container_width=True)

with tab3:
    st.markdown("#### 📍 Individual Stadium Scoring Profile")
    all_v_names = df_venues['venue'].tolist()
    sel_venue = st.selectbox("Select Ground", all_v_names, index=0)

    v_details = df_venues[df_venues['venue'] == sel_venue].iloc[0]
    
    sv1, sv2, sv3, sv4 = st.columns(4)
    with sv1:
        st.metric("Matches Hosted", f"{int(v_details['matches_played'])}")
    with sv2:
        st.metric("Avg 1st Inns Score", f"{v_details['avg_first_innings_score']:.1f}")
    with sv3:
        st.metric("Highest Match Score", f"{int(v_details['highest_innings_score'])}")
    with sv4:
        st.metric("Chasing Win %", f"{v_details['chase_win_pct']:.1f}%")

    st.markdown("##### 🏆 Team Records at this Stadium")
    v_teams = get_venue_team_records(df_matches, sel_venue)
    if not v_teams.empty:
        st.dataframe(v_teams, use_container_width=True, hide_index=True)
    else:
        st.info("No team match data available for this venue.")

