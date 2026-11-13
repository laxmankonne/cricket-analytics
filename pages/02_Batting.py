"""
Module 2: Batting Analysis
Features: Top run scorers, highest individual innings, strike rates, averages,
boundaries (4s vs 6s), season breakdowns, and player consistency analysis.
"""

import streamlit as st
import pandas as pd
from utils.data_loader import load_matches, load_deliveries, load_batting_summary, get_filter_options
from utils.ui_helper import apply_app_styles, render_sidebar_header, render_page_header
from utils.batting_analysis import (
    get_filtered_batting_summary, get_highest_individual_innings,
    get_player_season_breakdown, get_player_innings_scores
)
from utils.visualization import (
    create_horizontal_bar, create_vertical_bar,
    create_line_chart, create_scatter_plot
)
import plotly.express as px

st.set_page_config(
    page_title="Batting Analysis | Cricket Analytics",
    page_icon="🏏",
    layout="wide"
)

apply_app_styles()
render_sidebar_header()

render_page_header(
    title="Batting Performance Analysis",
    subtitle="In-depth evaluation of batting metrics, strike rates, boundary distribution, and historical player consistency.",
    badge_text="MODULE 2 • BATTING ANALYTICS"
)

# Load data
df_matches = load_matches()
df_deliv = load_deliveries()
df_batting_all = load_batting_summary()

seasons, teams, _ = get_filter_options(df_matches)

# Sidebar Interactive Filters
st.sidebar.markdown("### 🔍 Batting Filters")
selected_season = st.sidebar.selectbox("Select Season", ['All Seasons'] + seasons)
selected_team = st.sidebar.selectbox("Select Batting Team", ['All Teams'] + teams)
min_runs_filter = st.sidebar.slider("Minimum Total Runs", min_value=0, max_value=2000, value=200, step=50)

# Filtered Batting Dataset
if selected_season == 'All Seasons' and selected_team == 'All Teams':
    df_bat = df_batting_all[df_batting_all['total_runs'] >= min_runs_filter].copy()
else:
    df_bat_raw = get_filtered_batting_summary(df_deliv, season=selected_season, team=selected_team)
    df_bat = df_bat_raw[df_bat_raw['total_runs'] >= min_runs_filter].copy() if not df_bat_raw.empty else pd.DataFrame()

if df_bat.empty:
    st.warning("No batting records found matching the selected filters.")
else:
    # Key Summary Metrics Row
    m_col1, m_col2, m_col3, m_col4, m_col5 = st.columns(5)
    with m_col1:
        st.metric("Total Batsmen", f"{len(df_bat):,}")
    with m_col2:
        top_batsman = df_bat.iloc[0]
        st.metric("Leading Scorer", top_batsman['player'], f"{int(top_batsman['total_runs']):,} runs")
    with m_col3:
        st.metric("Top Strike Rate", f"{df_bat['strike_rate'].max():.2f}")
    with m_col4:
        st.metric("Total 4s Hit", f"{int(df_bat['fours'].sum()):,}")
    with m_col5:
        st.metric("Total 6s Hit", f"{int(df_bat['sixes'].sum()):,}")

    st.markdown("<div style='margin-top: 20px;'></div>", unsafe_allow_html=True)

    # Tabs for Structured Navigation
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏆 Leaderboards & Rankings",
        "💥 Strike Rate vs Average",
        "🎯 Boundaries (4s vs 6s)",
        "👤 Individual Player Deep-Dive"
    ])

    with tab1:
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            top_10_runs = df_bat.head(10)[['player', 'total_runs']].copy()
            fig_top_runs = create_horizontal_bar(
                top_10_runs,
                x_col='total_runs',
                y_col='player',
                title="Top 10 Run Scorers"
            )
            st.plotly_chart(fig_top_runs, use_container_width=True)

        with col_t2:
            top_avg = df_bat[(df_bat['total_outs'] >= 10)].sort_values(by='batting_average', ascending=False).head(10)
            if not top_avg.empty:
                fig_avg = create_horizontal_bar(
                    top_avg,
                    x_col='batting_average',
                    y_col='player',
                    title="Highest Batting Averages (Min. 10 Dismissals)"
                )
                st.plotly_chart(fig_avg, use_container_width=True)
            else:
                st.info("Insufficient dismissal data for batting average ranking under current filters.")

        st.markdown("#### 🌟 All-Time Highest Individual Innings")
        high_inns = get_highest_individual_innings(df_deliv, top_n=10)
        st.dataframe(
            high_inns[['player', 'runs', 'balls', 'strike_rate', 'fours', 'sixes', 'season', 'batting_team', 'bowling_team']],
            use_container_width=True,
            hide_index=True
        )

    with tab2:
        st.markdown("#### 📊 Batting Efficiency: Strike Rate vs Batting Average")
        st.caption("Circle size represents Total Runs scored. Hover to inspect individual batsman performance.")
        
        scatter_df = df_bat[(df_bat['total_runs'] >= 300) & (df_bat['strike_rate'] > 0)].copy()
        if not scatter_df.empty:
            fig_scatter = create_scatter_plot(
                scatter_df,
                x_col='strike_rate',
                y_col='batting_average',
                size_col='total_runs',
                color_col='total_runs',
                hover_name='player',
                title="Strike Rate vs. Batting Average (Min 300 Runs)"
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("No players meet the 300+ runs threshold for this scatter visualization.")

    with tab3:
        b_col1, b_col2 = st.columns(2)
        with b_col1:
            top_sixes = df_bat.sort_values(by='sixes', ascending=False).head(10)
            fig_sixes = create_horizontal_bar(
                top_sixes,
                x_col='sixes',
                y_col='player',
                title="Top 10 Six Hitters (Maximums)"
            )
            st.plotly_chart(fig_sixes, use_container_width=True)

        with b_col2:
            top_fours = df_bat.sort_values(by='fours', ascending=False).head(10)
            fig_fours = create_horizontal_bar(
                top_fours,
                x_col='fours',
                y_col='player',
                title="Top 10 Four Hitters (Boundaries)"
            )
            st.plotly_chart(fig_fours, use_container_width=True)

        st.markdown("#### 📈 Boundary Percentage Comparison")
        boundary_df = df_bat.sort_values(by='total_runs', ascending=False).head(15).copy()
        boundary_df['boundary_runs'] = (boundary_df['fours'] * 4) + (boundary_df['sixes'] * 6)
        boundary_df['non_boundary_runs'] = boundary_df['total_runs'] - boundary_df['boundary_runs']
        
        fig_stacked = px.bar(
            boundary_df,
            x='player',
            y=['non_boundary_runs', 'boundary_runs'],
            title="Runs from Boundaries vs Running Between Wickets (Top 15 Batsmen)",
            labels={'value': 'Runs', 'variable': 'Run Source'},
            color_discrete_map={'non_boundary_runs': '#0284C7', 'boundary_runs': '#16A34A'},
            template='plotly_dark'
        )
        fig_stacked.update_layout(paper_bgcolor='#111C2E', plot_bgcolor='#111C2E', font=dict(color='#F8FAFC'))
        st.plotly_chart(fig_stacked, use_container_width=True)

    with tab4:
        st.markdown("#### 🔍 Individual Player Career Analysis")
        all_batsmen = sorted(df_batting_all['player'].dropna().unique().tolist())
        selected_player = st.selectbox("Select Player for Detailed Career Breakdown", all_batsmen, index=all_batsmen.index('V Kohli') if 'V Kohli' in all_batsmen else 0)

        p_summary = df_batting_all[df_batting_all['player'] == selected_player]
        if not p_summary.empty:
            p_data = p_summary.iloc[0]
            pkpi1, pkpi2, pkpi3, pkpi4, pkpi5 = st.columns(5)
            with pkpi1:
                st.metric("Total Runs", f"{int(p_data['total_runs']):,}")
            with pkpi2:
                st.metric("Innings Batted", f"{int(p_data['innings'])}")
            with pkpi3:
                st.metric("Batting Average", f"{p_data['batting_average']:.2f}")
            with pkpi4:
                st.metric("Strike Rate", f"{p_data['strike_rate']:.2f}")
            with pkpi5:
                st.metric("PCI (Consistency Index)", f"{p_data['consistency_index']:.1f}/100")

            # Season breakdown chart
            season_df = get_player_season_breakdown(df_deliv, selected_player)
            if not season_df.empty:
                c_s1, c_s2 = st.columns(2)
                with c_s1:
                    fig_p_season = create_vertical_bar(
                        season_df,
                        x_col='season',
                        y_col='runs',
                        title=f"{selected_player}: Runs Scored by Season"
                    )
                    st.plotly_chart(fig_p_season, use_container_width=True)

                with c_s2:
                    fig_p_sr = create_line_chart(
                        season_df,
                        x_col='season',
                        y_col='strike_rate',
                        title=f"{selected_player}: Strike Rate Trend by Season"
                    )
                    st.plotly_chart(fig_p_sr, use_container_width=True)

            # Innings score distribution histogram
            inns_df = get_player_innings_scores(df_deliv, selected_player)
            if not inns_df.empty:
                st.markdown(f"##### 🎯 {selected_player}: Innings Score Distribution Histogram")
                fig_hist = px.histogram(
                    inns_df,
                    x='runs',
                    nbins=20,
                    title=f"Distribution of Innings Scores for {selected_player}",
                    color_discrete_sequence=['#16A34A'],
                    template='plotly_dark'
                )
                fig_hist.update_layout(paper_bgcolor='#111C2E', plot_bgcolor='#111C2E', font=dict(color='#F8FAFC'))
                st.plotly_chart(fig_hist, use_container_width=True)
