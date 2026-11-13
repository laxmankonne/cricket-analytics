"""
Module 4: Team Performance Analysis
Features: Franchise standings, historical win percentages, head-to-head records,
toss impact dynamics, and bat first vs chasing performance.
"""

import streamlit as st
import pandas as pd
from utils.data_loader import load_matches, load_deliveries, load_team_summary, get_filter_options
from utils.ui_helper import apply_app_styles, render_sidebar_header, render_page_header
from utils.team_analysis import (
    get_team_standings, get_head_to_head, get_team_season_trend, get_toss_impact_analysis
)
from utils.visualization import (
    create_horizontal_bar, create_vertical_bar,
    create_donut_chart, create_line_chart
)
import plotly.express as px

st.set_page_config(
    page_title="Team Analysis | Cricket Analytics",
    page_icon="🏏",
    layout="wide"
)

apply_app_styles()
render_sidebar_header()

render_page_header(
    title="Team Performance Analysis",
    subtitle="Franchise historical win records, head-to-head comparisons, season trends, and tactical toss biases.",
    badge_text="MODULE 4 • FRANCHISE ANALYTICS"
)

df_matches = load_matches()
df_deliv = load_deliveries()
df_team_summary = load_team_summary()

seasons, teams, _ = get_filter_options(df_matches)

# Sidebar Filter
st.sidebar.markdown("### 🔍 Team Analysis Filters")
selected_season = st.sidebar.selectbox("Filter Standings by Season", ['All Seasons'] + seasons)

# Dynamic or All-time Standings
if selected_season == 'All Seasons':
    standings = df_team_summary.copy()
else:
    standings = get_team_standings(df_matches, season=selected_season)

if standings.empty:
    st.warning("No matches recorded for this season filter.")
else:
    # Team Rankings Table & Charts
    tab1, tab2, tab3, tab4 = st.tabs([
        "🏆 Team Standings & Win Rates",
        "⚔️ Head-to-Head Comparison",
        "🏏 Bat 1st vs. Chasing Bias",
        "🪙 Toss Impact Dynamics"
    ])

    with tab1:
        c1, c2 = st.columns([7, 5])
        with c1:
            fig_wins = create_horizontal_bar(
                standings.head(10),
                x_col='wins',
                y_col='team',
                title=f"Total Match Wins ({selected_season})"
            )
            st.plotly_chart(fig_wins, use_container_width=True)

        with c2:
            fig_win_pct = create_horizontal_bar(
                standings.sort_values(by='win_pct' if 'win_pct' in standings.columns else 'win_percentage', ascending=False).head(10),
                x_col='win_pct' if 'win_pct' in standings.columns else 'win_percentage',
                y_col='team',
                title="Win Percentage (%)"
            )
            st.plotly_chart(fig_win_pct, use_container_width=True)

        st.markdown("#### 📋 Comprehensive Franchise Standings Table")
        st.dataframe(standings, use_container_width=True, hide_index=True)

    with tab2:
        st.markdown("#### ⚔️ Head-to-Head Rivalry Analysis")
        col_h1, col_h2 = st.columns(2)
        with col_h1:
            team_a = st.selectbox("Select Franchise A", teams, index=teams.index('Mumbai Indians') if 'Mumbai Indians' in teams else 0)
        with col_h2:
            team_b_options = [t for t in teams if t != team_a]
            team_b = st.selectbox("Select Franchise B", team_b_options, index=team_b_options.index('Chennai Super Kings') if 'Chennai Super Kings' in team_b_options else 0)

        h2h_data = get_head_to_head(df_matches, team_a, team_b)
        
        hkpi1, hkpi2, hkpi3, hkpi4 = st.columns(4)
        with hkpi1:
            st.metric("Total Encounters", f"{h2h_data['total_matches']}")
        with hkpi2:
            st.metric(f"{team_a} Wins", f"{h2h_data['team1_wins']}")
        with hkpi3:
            st.metric(f"{team_b} Wins", f"{h2h_data['team2_wins']}")
        with hkpi4:
            st.metric("Ties / No Result", f"{h2h_data['ties_or_nr']}")

        # H2H Pie chart
        h2h_pie_df = pd.DataFrame([
            {'Outcome': f"{team_a} Won", 'Count': h2h_data['team1_wins']},
            {'Outcome': f"{team_b} Won", 'Count': h2h_data['team2_wins']},
            {'Outcome': 'Ties / No Result', 'Count': h2h_data['ties_or_nr']}
        ])
        h2h_pie_df = h2h_pie_df[h2h_pie_df['Count'] > 0]
        
        if not h2h_pie_df.empty:
            fig_h2h = create_donut_chart(h2h_pie_df, 'Outcome', 'Count', f"Head-to-Head Win Share: {team_a} vs {team_b}")
            st.plotly_chart(fig_h2h, use_container_width=True)

        st.markdown("##### 📜 Recent Head-to-Head Match Log")
        if not h2h_data['matches_df'].empty:
            st.dataframe(
                h2h_data['matches_df'][['date', 'season', 'venue', 'toss_winner', 'toss_decision', 'winner', 'result', 'result_margin', 'player_of_match']].head(10),
                use_container_width=True,
                hide_index=True
            )

    with tab3:
        st.markdown("#### 🎯 Batting First vs Chasing Success")
        st.caption("Evaluation of whether teams perform better setting a target or pursuing run chases.")

        if 'bat_first_win_pct' in df_team_summary.columns:
            plot_df = df_team_summary[df_team_summary['matches_played'] >= 30].copy()
            fig_bat_chase = px.bar(
                plot_df,
                x='team',
                y=['bat_first_win_pct', 'chase_win_pct'],
                barmode='group',
                title="Batting First Win % vs Chasing Win % (Franchises with 30+ Matches)",
                labels={'value': 'Win Percentage (%)', 'variable': 'Condition'},
                color_discrete_map={'bat_first_win_pct': '#16A34A', 'chase_win_pct': '#38BDF8'},
                template='plotly_dark'
            )
            fig_bat_chase.update_layout(paper_bgcolor='#111C2E', plot_bgcolor='#111C2E', font=dict(color='#F8FAFC'))
            st.plotly_chart(fig_bat_chase, use_container_width=True)

    with tab4:
        st.markdown("#### 🪙 Toss Impact on Match Outcomes")
        toss_focus_team = st.selectbox("Select Team for Toss Analysis", ['All Teams'] + teams)
        toss_res = get_toss_impact_analysis(df_matches, toss_focus_team)

        if toss_res:
            tk1, tk2, tk3 = st.columns(3)
            with tk1:
                st.metric("Total Matches", f"{toss_res['total_matches']:,}")
            with tk2:
                st.metric("Toss & Match Wins", f"{toss_res['toss_and_match_wins']:,}")
            with tk3:
                st.metric("Toss Winner Match Win Rate", f"{toss_res['toss_win_pct']:.2f}%")

            st.markdown("##### Toss Decision Breakdown (Bat vs Field)")
            if 'decision_breakdown' in toss_res and not toss_res['decision_breakdown'].empty:
                st.dataframe(
                    toss_res['decision_breakdown'].rename(columns={'count': 'Times Chosen', 'wins': 'Matches Won', 'win_pct': 'Win Rate (%)'}),
                    use_container_width=True,
                    hide_index=True
                )

