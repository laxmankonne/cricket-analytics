"""
Module 3: Bowling Analysis
Features: Top wicket takers, best bowling figures, economy rates, bowling strike rates,
bowling averages, maiden overs, season-by-season breakdowns, and player rankings.
"""

import streamlit as st
import pandas as pd
from utils.data_loader import load_matches, load_deliveries, load_bowling_summary, get_filter_options
from utils.ui_helper import apply_app_styles, render_sidebar_header, render_page_header
from utils.bowling_analysis import (
    get_filtered_bowling_summary, get_best_match_bowling_figures,
    get_bowler_season_breakdown
)
from utils.visualization import (
    create_horizontal_bar, create_vertical_bar,
    create_line_chart, create_scatter_plot
)
import plotly.express as px

st.set_page_config(
    page_title="Bowling Analysis | Cricket Analytics",
    page_icon="🏏",
    layout="wide"
)

apply_app_styles()
render_sidebar_header()

render_page_header(
    title="Bowling Performance Analysis",
    subtitle="Comprehensive statistical metrics evaluating wicket productivity, run containment (economy), and efficiency.",
    badge_text="MODULE 3 • BOWLING ANALYTICS"
)

df_matches = load_matches()
df_deliv = load_deliveries()
df_bowling_all = load_bowling_summary()

seasons, teams, _ = get_filter_options(df_matches)

# Sidebar Filters
st.sidebar.markdown("### 🔍 Bowling Filters")
selected_season = st.sidebar.selectbox("Select Season", ['All Seasons'] + seasons)
selected_team = st.sidebar.selectbox("Select Bowling Team", ['All Teams'] + teams)
min_wickets_filter = st.sidebar.slider("Minimum Total Wickets", min_value=0, max_value=100, value=10, step=5)

# Filtered dataset
if selected_season == 'All Seasons' and selected_team == 'All Teams':
    df_bowl = df_bowling_all[df_bowling_all['total_wickets'] >= min_wickets_filter].copy()
else:
    df_bowl_raw = get_filtered_bowling_summary(df_deliv, season=selected_season, team=selected_team)
    df_bowl = df_bowl_raw[df_bowl_raw['total_wickets'] >= min_wickets_filter].copy() if not df_bowl_raw.empty else pd.DataFrame()

if df_bowl.empty:
    st.warning("No bowling records match the specified filters.")
else:
    # Bowling KPIs Row
    bkpi1, bkpi2, bkpi3, bkpi4, bkpi5 = st.columns(5)
    with bkpi1:
        st.metric("Total Bowlers", f"{len(df_bowl):,}")
    with bkpi2:
        lead_bowler = df_bowl.iloc[0]
        st.metric("Top Wicket Taker", lead_bowler['player'], f"{int(lead_bowler['total_wickets']):,} wickets")
    with bkpi3:
        best_econ = df_bowl[df_bowl['legal_balls_bowled'] >= 120]['economy_rate'].min()
        st.metric("Best Economy (Min 20 Overs)", f"{best_econ:.2f}" if pd.notna(best_econ) else "N/A")
    with bkpi4:
        st.metric("Total Maiden Overs", f"{int(df_bowl['maiden_overs'].sum()):,}")
    with bkpi5:
        st.metric("5-Wicket Hauls", f"{int(df_bowl['five_wickets'].sum()):,}")

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Leading Wicket Takers",
        "🛡️ Economy & Containment",
        "⚡ Best Bowling Figures",
        "👤 Bowler Career Deep-Dive"
    ])

    with tab1:
        w_col1, w_col2 = st.columns(2)
        with w_col1:
            top_wickets = df_bowl.head(10)[['player', 'total_wickets']].copy()
            fig_wickets = create_horizontal_bar(
                top_wickets,
                x_col='total_wickets',
                y_col='player',
                title="Top 10 Wicket Takers"
            )
            st.plotly_chart(fig_wickets, use_container_width=True)

        with w_col2:
            top_maidens = df_bowl.sort_values(by='maiden_overs', ascending=False).head(10)[['player', 'maiden_overs']].copy()
            fig_maidens = create_horizontal_bar(
                top_maidens,
                x_col='maiden_overs',
                y_col='player',
                title="Most Maiden Overs Bowled"
            )
            st.plotly_chart(fig_maidens, use_container_width=True)

        st.markdown("#### 📋 Comprehensive Bowling Leaderboard")
        st.dataframe(
            df_bowl[['player', 'matches', 'overs_bowled', 'total_runs_conceded', 'total_wickets', 'bowling_average', 'economy_rate', 'bowling_strike_rate', 'best_bowling_figure', 'maiden_overs']].head(20),
            use_container_width=True,
            hide_index=True
        )

    with tab2:
        st.markdown("#### 📉 Bowling Economy vs Bowling Strike Rate")
        st.caption("Circle size represents Total Wickets taken. Top-performing bowlers occupy the lower-left quadrant (low economy, low balls-per-wicket).")
        
        qual_bowlers = df_bowl[(df_bowl['total_wickets'] >= 20) & (df_bowl['economy_rate'] > 0)].copy()
        if not qual_bowlers.empty:
            fig_bowl_scatter = create_scatter_plot(
                qual_bowlers,
                x_col='economy_rate',
                y_col='bowling_strike_rate',
                size_col='total_wickets',
                color_col='total_wickets',
                hover_name='player',
                title="Economy Rate vs Bowling Strike Rate (Min 20 Wickets)"
            )
            st.plotly_chart(fig_bowl_scatter, use_container_width=True)
        else:
            st.info("Insufficient qualifying bowlers under current filter threshold.")

    with tab3:
        st.markdown("#### 🌟 All-Time Best Single-Match Bowling Figures")
        best_figures = get_best_match_bowling_figures(df_deliv, top_n=10)
        st.dataframe(
            best_figures[['player', 'figure', 'overs', 'runs', 'wickets', 'economy', 'season', 'bowling_team', 'batting_team']],
            use_container_width=True,
            hide_index=True
        )

    with tab4:
        st.markdown("#### 🔍 Individual Bowler Season-by-Season Analysis")
        all_bowlers = sorted(df_bowling_all['player'].dropna().unique().tolist())
        selected_bowler = st.selectbox("Select Bowler", all_bowlers, index=all_bowlers.index('YS Chahal') if 'YS Chahal' in all_bowlers else 0)

        b_summary = df_bowling_all[df_bowling_all['player'] == selected_bowler]
        if not b_summary.empty:
            b_data = b_summary.iloc[0]
            bk1, bk2, bk3, bk4, bk5 = st.columns(5)
            with bk1:
                st.metric("Total Wickets", f"{int(b_data['total_wickets'])}")
            with bk2:
                st.metric("Overs Bowled", f"{b_data['overs_bowled']:.1f}")
            with bk3:
                st.metric("Economy Rate", f"{b_data['economy_rate']:.2f}")
            with bk4:
                st.metric("Bowling Average", f"{b_data['bowling_average']:.2f}" if pd.notna(b_data['bowling_average']) else "N/A")
            with bk5:
                st.metric("Best Bowling Figure", str(b_data['best_bowling_figure']))

            b_season_df = get_bowler_season_breakdown(df_deliv, selected_bowler)
            if not b_season_df.empty:
                b_s1, b_s2 = st.columns(2)
                with b_s1:
                    fig_b_w = create_vertical_bar(
                        b_season_df,
                        x_col='season',
                        y_col='wickets',
                        title=f"{selected_bowler}: Wickets by Season"
                    )
                    st.plotly_chart(fig_b_w, use_container_width=True)

                with b_s2:
                    fig_b_econ = create_line_chart(
                        b_season_df,
                        x_col='season',
                        y_col='economy',
                        title=f"{selected_bowler}: Economy Rate Trend by Season"
                    )
                    st.plotly_chart(fig_b_econ, use_container_width=True)
