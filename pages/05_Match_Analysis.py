"""
Module 5: Match Analysis
Features: Comprehensive match scorecards, worm charts, extreme team totals,
closest finishes, and run chase analysis.
"""

import streamlit as st
import pandas as pd
from utils.data_loader import load_matches, load_deliveries, get_filter_options
from utils.ui_helper import apply_app_styles, render_sidebar_header, render_page_header
from utils.match_analysis import (
    get_match_scorecard, get_match_worm_data,
    get_highest_and_lowest_totals, get_closest_finishes
)
from utils.visualization import create_worm_chart, create_horizontal_bar
import plotly.express as px

st.set_page_config(
    page_title="Match Analysis | Cricket Analytics",
    page_icon="🏏",
    layout="wide"
)

apply_app_styles()
render_sidebar_header()

render_page_header(
    title="Match Analysis & Scorecards",
    subtitle="Detailed single-match ball-by-ball scorecards, worm progression charts, extreme team totals, and historic nail-biters.",
    badge_text="MODULE 5 • MATCH ANALYTICS"
)

df_matches = load_matches()
df_deliv = load_deliveries()

seasons, teams, _ = get_filter_options(df_matches)

tab1, tab2, tab3 = st.tabs([
    "📋 Interactive Match Scorecard",
    "📈 Inning Worm & Progression",
    "⚡ Extreme Totals & Closest Finishes"
])

with tab1:
    st.markdown("#### 🔍 Select Match for Detailed Scorecard")
    c_m1, c_m2 = st.columns(2)
    with c_m1:
        s_season = st.selectbox("Select Season", seasons, index=len(seasons) - 1)
    
    season_matches = df_matches[df_matches['season'] == s_season].sort_values(by='date', ascending=False)
    match_options = {
        row['match_id']: f"{row['date'].strftime('%Y-%m-%d') if pd.notna(row['date']) else ''}: {row['team1']} vs {row['team2']} ({row['venue'][:25]}...)"
        for _, row in season_matches.iterrows()
    }
    
    with c_m2:
        selected_match_id = st.selectbox(
            "Select Match",
            options=list(match_options.keys()),
            format_func=lambda x: match_options[x]
        )

    # Match Header Summary Card
    m_info = df_matches[df_matches['match_id'] == selected_match_id].iloc[0]
    
    st.markdown(f"""
    <div class="section-card">
        <div style="font-size: 1.4rem; font-weight: 800; color: #F8FAFC;">
            {m_info['team1']} vs {m_info['team2']}
        </div>
        <div style="color: #38BDF8; font-weight: 600; margin: 6px 0;">
            🏆 Result: {m_info['winner']} won by {int(m_info['result_margin']) if pd.notna(m_info['result_margin']) else ''} {m_info['result']}
        </div>
        <div style="font-size: 0.85rem; color: #94A3B8;">
            📅 Date: {m_info['date'].strftime('%d %B %Y') if pd.notna(m_info['date']) else 'N/A'} • 
            🏟️ Venue: {m_info['venue']} • 
            🪙 Toss: {m_info['toss_winner']} decided to {m_info['toss_decision']} • 
            ⭐ Player of the Match: <b>{m_info['player_of_match']}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Scorecard Display
    inns_data = get_match_scorecard(df_deliv, selected_match_id)
    if inns_data:
        for inn in inns_data:
            st.markdown(f"### 🏏 {inn['batting_team']} — {inn['total_runs']}/{inn['total_wickets']} in {inn['overs']} overs (Extras: {inn['extras']})")
            
            c_bat, c_bowl = st.columns([7, 5])
            with c_bat:
                st.markdown("**Batting Card**")
                st.dataframe(
                    inn['batting_card'][['striker', 'dismissal', 'runs', 'balls', 'fours', 'sixes', 'strike_rate']].rename(columns={'striker': 'Batter', 'dismissal': 'Dismissal', 'runs': 'R', 'balls': 'B', 'fours': '4s', 'sixes': '6s', 'strike_rate': 'SR'}),
                    use_container_width=True,
                    hide_index=True
                )
            with c_bowl:
                st.markdown("**Bowling Card**")
                st.dataframe(
                    inn['bowling_card'][['bowler', 'overs', 'runs', 'wickets', 'economy']].rename(columns={'bowler': 'Bowler', 'overs': 'O', 'runs': 'R', 'wickets': 'W', 'economy': 'Econ'}),
                    use_container_width=True,
                    hide_index=True
                )
            st.markdown("---")

with tab2:
    st.markdown("#### 🐛 Worm Chart: Over-by-Over Cumulative Runs & Fall of Wickets")
    if selected_match_id:
        inns1_w, inns2_w = get_match_worm_data(df_deliv, selected_match_id)
        t1 = m_info['team1']
        t2 = m_info['team2']
        fig_worm = create_worm_chart(inns1_w, inns2_w, t1, t2, title=f"Run Progression: {t1} vs {t2}")
        st.plotly_chart(fig_worm, use_container_width=True)

        # Over-by-over run rate comparison
        st.markdown("##### 📊 Over-by-Over Scoring Comparison")
        deliv_m = df_deliv[df_deliv['match_id'] == selected_match_id]
        over_runs = deliv_m.groupby(['innings', 'over', 'batting_team'])['total_runs'].sum().reset_index()
        over_runs['Over Number'] = over_runs['over'] + 1
        
        fig_over_bar = px.bar(
            over_runs,
            x='Over Number',
            y='total_runs',
            color='batting_team',
            barmode='group',
            title="Runs Scored in Each Over (1 to 20)",
            labels={'total_runs': 'Runs in Over'},
            color_discrete_sequence=['#16A34A', '#38BDF8'],
            template='plotly_dark'
        )
        fig_over_bar.update_layout(paper_bgcolor='#111C2E', plot_bgcolor='#111C2E', font=dict(color='#F8FAFC'))
        st.plotly_chart(fig_over_bar, use_container_width=True)

with tab3:
    st.markdown("#### ⚡ Historical Extreme Team Totals")
    high_tot, low_tot = get_highest_and_lowest_totals(df_deliv, df_matches, top_n=10)
    
    col_hi, col_lo = st.columns(2)
    with col_hi:
        st.markdown("##### 🔥 Highest Innings Totals")
        st.dataframe(
            high_tot[['score_str', 'batting_team', 'bowling_team', 'season', 'venue']].rename(columns={'score_str': 'Score', 'batting_team': 'Batting', 'bowling_team': 'Opponent'}),
            use_container_width=True,
            hide_index=True
        )
    with col_lo:
        st.markdown("##### ❄️ Lowest Innings Totals (Min 10 Overs or All Out)")
        st.dataframe(
            low_tot[['score_str', 'batting_team', 'bowling_team', 'season', 'venue']].rename(columns={'score_str': 'Score', 'batting_team': 'Batting', 'bowling_team': 'Opponent'}),
            use_container_width=True,
            hide_index=True
        )

    st.markdown("#### 🤏 Closest Finishes in Tournament History")
    close_runs, close_wkts, ties = get_closest_finishes(df_matches, top_n=5)
    
    c_f1, c_f2 = st.columns(2)
    with c_f1:
        st.markdown(r"##### 🏃 Closest Defending Wins (Runs Margin $\le$ 3)")
        st.dataframe(
            close_runs[['date', 'season', 'winner', 'result_margin', 'team1', 'team2']].head(5).rename(columns={'result_margin': 'Won By (Runs)'}),
            use_container_width=True,
            hide_index=True
        )
    with c_f2:
        st.markdown("##### 🎯 1-Wicket Chasing Victories & Super Overs")
        st.dataframe(
            close_wkts[['date', 'season', 'winner', 'result_margin', 'team1', 'team2']].head(5).rename(columns={'result_margin': 'Margin (Wickets)'}),
            use_container_width=True,
            hide_index=True
        )
