"""
Main Application Entry Point - Cricket Data Analysis & Interactive Visualization
Module 1: Home Dashboard
"""

import streamlit as st
import pandas as pd
from utils.data_loader import (
    load_matches, load_deliveries, load_batting_summary,
    load_bowling_summary, load_team_summary, load_venue_summary
)
from utils.ui_helper import apply_app_styles, render_sidebar_header, render_page_header
from utils.visualization import (
    create_horizontal_bar, create_vertical_bar,
    create_donut_chart, create_line_chart
)

st.set_page_config(
    page_title="Cricket Data Analysis & Interactive Visualization",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

apply_app_styles()
render_sidebar_header()

def render_home_dashboard():
    render_page_header(
        title="Cricket Data Analysis & Interactive Visualization",
        subtitle="An enterprise-grade, academic cricket analytics platform delivering deep statistical insights, performance rankings, and machine learning models from authentic ball-by-ball datasets.",
        badge_text="OFFICIAL CRICSHEET DATASET • 2008 - PRESENT"
    )

    # Load authentic datasets
    with st.spinner("Loading authentic cricket datasets..."):
        df_matches = load_matches()
        df_deliv = load_deliveries()
        df_batting = load_batting_summary()
        df_bowling = load_bowling_summary()
        df_teams = load_team_summary()
        df_venues = load_venue_summary()

    # Core High-Level KPIs
    total_matches = len(df_matches)
    total_deliveries = len(df_deliv)
    total_runs = int(df_deliv['total_runs'].sum())
    total_wickets = int(df_deliv['is_wicket'].sum())
    total_sixes = int(df_deliv['is_six'].sum())
    total_fours = int(df_deliv['is_four'].sum())
    total_teams = len(df_teams)
    total_players = len(set(df_batting['player']).union(set(df_bowling['player'])))
    total_venues = len(df_venues)
    total_seasons = df_matches['season'].nunique()

    # Top KPI Metrics Row
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.metric(label="Total Matches", value=f"{total_matches:,}", delta="17+ Seasons")
    with col2:
        st.metric(label="Balls Bowled", value=f"{total_deliveries:,}", delta="Ball-by-Ball Granularity")
    with col3:
        st.metric(label="Total Runs", value=f"{total_runs:,}", delta=f"{total_fours:,} 4s • {total_sixes:,} 6s")
    with col4:
        st.metric(label="Total Wickets", value=f"{total_wickets:,}", delta=f"{total_players:,} Active Players")
    with col5:
        st.metric(label="Venues Analyzed", value=f"{total_venues}", delta=f"{total_teams} Franchises")

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    # Objectives & Dataset Documentation Accordion
    with st.expander("📌 Project Architecture & Dataset Transparency Statement", expanded=False):
        c_a, c_b = st.columns(2)
        with c_a:
            st.markdown("""
            **Academic Project Scope & Objectives:**
            - **End-to-End Analysis:** Transforming 295,000+ raw ball delivery events into multi-dimensional statistical metrics.
            - **No Synthetic Data:** Every statistic, strike rate, economy rate, and win probability is derived deterministically from historical records.
            - **Predictive Analytics:** Regularized Logistic Regression trained on match conditions to estimate win probabilities.
            """)
        with c_b:
            st.markdown("""
            **Dataset Provenance:**
            - **Source:** Cricsheet (`https://cricsheet.org/`)
            - **License:** Open Data Commons Open Database License (ODbL)
            - **Coverage:** Indian Premier League (2008–Present)
            - **Data Granularity:** Match metadata and ball-by-ball delivery event streams.
            """)

    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)

    # First Visual Row: Season Trends & Match Result Breakdown
    r1_col1, r1_col2 = st.columns([7, 5])
    with r1_col1:
        matches_per_season = df_matches.groupby('season').size().reset_index(name='Matches Played')
        fig_season = create_vertical_bar(
            matches_per_season,
            x_col='season',
            y_col='Matches Played',
            title="Matches Played Per Season (2008 – Present)"
        )
        st.plotly_chart(fig_season, use_container_width=True)

    with r1_col2:
        result_types = df_matches['result'].value_counts().reset_index()
        result_types.columns = ['Result Type', 'Count']
        fig_result = create_donut_chart(
            result_types,
            names_col='Result Type',
            values_col='Count',
            title="Match Outcome Distribution"
        )
        st.plotly_chart(fig_result, use_container_width=True)

    # Second Visual Row: All-Time Top 10 Leaders
    r2_col1, r2_col2 = st.columns(2)
    with r2_col1:
        top_bat = df_batting.head(10)[['player', 'total_runs']].copy()
        fig_bat = create_horizontal_bar(
            top_bat,
            x_col='total_runs',
            y_col='player',
            title="All-Time Leading Run Scorers"
        )
        st.plotly_chart(fig_bat, use_container_width=True)

    with r2_col2:
        top_bowl = df_bowling.head(10)[['player', 'total_wickets']].copy()
        fig_bowl = create_horizontal_bar(
            top_bowl,
            x_col='total_wickets',
            y_col='player',
            title="All-Time Leading Wicket-Takers"
        )
        st.plotly_chart(fig_bowl, use_container_width=True)

    # Third Row: Quick Navigation Cards
    st.markdown("### 🧭 Explore Analytical Modules")
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns(4)
    with nav_col1:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Batting & Bowling</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #F8FAFC; margin-bottom: 8px;">Player Analytics</div>
            <div style="font-size: 0.85rem; color: #94A3B8;">Strike rates, averages, boundaries, best figures, and maiden overs.</div>
        </div>
        """, unsafe_allow_html=True)
    with nav_col2:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Franchises & Matches</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #F8FAFC; margin-bottom: 8px;">Team & Match Reports</div>
            <div style="font-size: 0.85rem; color: #94A3B8;">Win percentages, head-to-head records, over-by-over worm charts.</div>
        </div>
        """, unsafe_allow_html=True)
    with nav_col3:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Stadiums & Trends</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #F8FAFC; margin-bottom: 8px;">Venues & Eras</div>
            <div style="font-size: 0.85rem; color: #94A3B8;">Par scores, chasing advantages, run-rate shifts across decades.</div>
        </div>
        """, unsafe_allow_html=True)
    with nav_col4:
        st.markdown("""
        <div class="kpi-card">
            <div class="kpi-title">Machine Learning</div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #F8FAFC; margin-bottom: 8px;">Advanced Analytics</div>
            <div style="font-size: 0.85rem; color: #94A3B8;">Win probability model, Consistency Index (PCI), and Toss Hypothesis tests.</div>
        </div>
        """, unsafe_allow_html=True)

if __name__ == "__main__":
    render_home_dashboard()

