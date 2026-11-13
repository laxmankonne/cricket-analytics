"""
Module 9: Advanced Analytics & Machine Learning
Features: Player Consistency Index (PCI), Batting/Bowling Efficiency,
Toss Hypothesis Significance Testing, Correlation Heatmaps, and Machine Learning Win Predictor.
"""

import streamlit as st
import numpy as np
import pandas as pd
from utils.data_loader import load_matches, load_deliveries, load_batting_summary, load_bowling_summary, get_filter_options
from utils.ui_helper import apply_app_styles, render_sidebar_header, render_page_header
from utils.advanced_analytics import (
    calculate_batting_efficiency, calculate_bowling_efficiency,
    perform_toss_significance_test, train_match_outcome_model, predict_match_outcome
)
from utils.visualization import create_horizontal_bar, create_scatter_plot, apply_custom_theme
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Advanced Analytics | Cricket Analytics",
    page_icon="🏏",
    layout="wide"
)

apply_app_styles()
render_sidebar_header()

render_page_header(
    title="Advanced Analytics & Machine Learning",
    subtitle="Mathematical modeling, efficiency rating indices, statistical hypothesis testing, and probabilistic machine learning match predictions.",
    badge_text="MODULE 9 • ADVANCED ANALYTICS"
)

df_matches = load_matches()
df_deliv = load_deliveries()
df_batting = load_batting_summary()
df_bowling = load_bowling_summary()

seasons, teams, venues = get_filter_options(df_matches)

tab1, tab2, tab3, tab4 = st.tabs([
    "🤖 Match Outcome ML Predictor",
    "⚙️ Efficiency & Consistency Indices",
    "📊 Statistical Correlations & Outliers",
    "🧪 Toss Impact Hypothesis Testing"
])

with tab1:
    st.markdown("#### 🤖 Machine Learning Match Outcome Predictor")
    st.caption("Trained on historical match features: Franchise identity, venue ground conditions, toss strategy, and 1st innings score.")

    # Train model (cached via Streamlit session state)
    if 'ml_model' not in st.session_state:
        with st.spinner("Training Logistic Regression Model on 1,200+ matches..."):
            st.session_state['ml_model'] = train_match_outcome_model(df_matches, df_deliv)

    model_res = st.session_state['ml_model']

    # Model Evaluation Metrics Cards
    ev_c1, ev_c2, ev_c3, ev_c4 = st.columns(4)
    with ev_c1:
        st.metric("Test Accuracy", f"{model_res['accuracy']:.1f}%")
    with ev_c2:
        st.metric("ROC-AUC Score", f"{model_res['roc_auc']:.3f}")
    with ev_c3:
        st.metric("Training Set Size", f"{model_res['train_size']:,} matches")
    with ev_c4:
        st.metric("Testing Set Size", f"{model_res['test_size']:,} matches")

    st.markdown("---")
    st.markdown("##### 🎮 Interactive Match Outcome Simulator")
    
    sim_c1, sim_c2 = st.columns(2)
    with sim_c1:
        sim_team1 = st.selectbox("Franchise 1 (Batting 1st)", teams, index=teams.index('Mumbai Indians') if 'Mumbai Indians' in teams else 0)
        sim_venue = st.selectbox("Match Stadium", venues, index=0)
        sim_toss_winner = st.selectbox("Toss Winner", [sim_team1, 'Franchise 2'], index=0)
    
    with sim_c2:
        t2_opts = [t for t in teams if t != sim_team1]
        sim_team2 = st.selectbox("Franchise 2 (Chasing)", t2_opts, index=t2_opts.index('Chennai Super Kings') if 'Chennai Super Kings' in t2_opts else 0)
        sim_toss_decision = st.selectbox("Toss Decision", ['field', 'bat'])
        sim_inns1_score = st.slider("Projected / Actual 1st Innings Total", min_value=100, max_value=260, value=175, step=5)

    actual_toss_winner = sim_team1 if sim_toss_winner == sim_team1 else sim_team2

    if st.button("🔮 Calculate Match Win Probability", use_container_width=True):
        pred = predict_match_outcome(
            model_res['model'],
            team1=sim_team1,
            team2=sim_team2,
            venue=sim_venue,
            toss_winner=actual_toss_winner,
            toss_decision=sim_toss_decision,
            inns1_score=sim_inns1_score
        )

        st.markdown(f"""
        <div class="section-card" style="text-align: center; border-color: #16A34A;">
            <div style="font-size: 0.9rem; color: #94A3B8; text-transform: uppercase;">Predicted Winning Probability</div>
            <div style="font-size: 2.2rem; font-weight: 800; color: #F8FAFC; margin: 8px 0;">
                🏆 Most Probable Winner: <span style="color: #38BDF8;">{pred['predicted_winner']}</span>
            </div>
            <div style="font-size: 1.15rem; color: #16A34A; font-weight: 700;">
                {sim_team1}: {pred['team1_prob']}%  •  {sim_team2}: {pred['team2_prob']}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    with st.expander("⚠️ Machine Learning Methodology & Academic Limitations Notice"):
        st.markdown("""
        - **Algorithm:** Regularized Logistic Regression with L2 Penalty and One-Hot Encoding for categorical features.
        - **Data Leakage Prevention:** Only pre-match data (teams, venue, toss) and mid-match target (1st innings runs) are provided to the model.
        - **Limitations:** Cricket match outcomes are inherently stochastic. Match trajectory depends heavily on in-game events such as dropped catches, individual brilliance, pitch deterioration, dew factor, and weather, which cannot be captured entirely by static historical features. Predictions should be interpreted as probabilistic tendencies, never guaranteed results.
        """)

with tab2:
    st.markdown("#### ⚙️ Performance Indices & Efficiency Ratings")
    
    idx_col1, idx_col2 = st.columns(2)
    with idx_col1:
        st.markdown("##### 🏏 Batting Efficiency Rating (BER)")
        st.latex(r"\text{BER} = 0.4 \cdot \text{Norm}(\text{Avg}) + 0.4 \cdot \text{Norm}(\text{SR}) + 0.2 \cdot \text{Norm}(\text{Boundary}\%)")
        bat_eff = calculate_batting_efficiency(df_batting).head(10)
        st.dataframe(
            bat_eff[['player', 'batting_efficiency', 'batting_average', 'strike_rate', 'boundary_percentage', 'total_runs']],
            use_container_width=True,
            hide_index=True
        )

    with idx_col2:
        st.markdown("##### 🎯 Bowling Efficiency Rating (BoER)")
        st.latex(r"\text{BoER} = 0.4 \cdot \text{InvNorm}(\text{Econ}) + 0.35 \cdot \text{InvNorm}(\text{Avg}) + 0.25 \cdot \text{InvNorm}(\text{SR})")
        bowl_eff = calculate_bowling_efficiency(df_bowling).head(10)
        st.dataframe(
            bowl_eff[['player', 'bowling_efficiency', 'economy_rate', 'bowling_average', 'bowling_strike_rate', 'total_wickets']],
            use_container_width=True,
            hide_index=True
        )

    st.markdown("##### 📐 Player Consistency Index (PCI)")
    st.latex(r"\text{PCI} = \max\left(0, 100 - \frac{\sigma_{\text{runs}}}{\mu_{\text{runs}}} \times 100\right)")
    st.caption("Evaluates how reliably a batsman scores around their expected mean across innings (Min 500 Runs).")
    
    top_pci = df_batting[df_batting['total_runs'] >= 500].sort_values(by='consistency_index', ascending=False).head(10)
    fig_pci = create_horizontal_bar(
        top_pci,
        x_col='consistency_index',
        y_col='player',
        title="Top 10 Most Consistent Batsmen (PCI Score out of 100)"
    )
    st.plotly_chart(fig_pci, use_container_width=True)

with tab3:
    st.markdown("#### 📊 Statistical Correlations & Outlier Detection")

    c_bat_corr = df_batting[['total_runs', 'innings', 'batting_average', 'strike_rate', 'fours', 'sixes', 'boundary_percentage', 'consistency_index']].corr()
    
    fig_corr = px.imshow(
        c_bat_corr,
        text_auto=".2f",
        aspect="auto",
        title="Correlation Matrix of Batting Metrics",
        color_continuous_scale="Viridis",
        template="plotly_dark"
    )
    fig_corr.update_layout(paper_bgcolor='#111C2E', plot_bgcolor='#111C2E', font=dict(color='#F8FAFC'))
    st.plotly_chart(fig_corr, use_container_width=True)

    st.markdown("##### 📦 Outlier Detection: Batting Strike Rates & Averages Boxplots")
    box_df = df_batting[df_batting['total_runs'] >= 300]
    fig_box = px.box(
        box_df,
        y=['strike_rate', 'batting_average'],
        points="outliers",
        title="Distribution & Outliers: Strike Rate vs Batting Average (Min 300 Runs)",
        template="plotly_dark",
        color_discrete_sequence=['#16A34A', '#38BDF8']
    )
    fig_box.update_layout(paper_bgcolor='#111C2E', plot_bgcolor='#111C2E', font=dict(color='#F8FAFC'))
    st.plotly_chart(fig_box, use_container_width=True)

with tab4:
    st.markdown("#### 🧪 Statistical Hypothesis Testing: The Toss Impact")
    st.markdown("""
    **Hypothesis Formulation:**
    - **Null Hypothesis ($H_0$):** Winning the toss has no statistically significant influence on winning the match ($P(\text{Win}) = 0.5$).
    - **Alternative Hypothesis ($H_1$):** Winning the toss confers a significant strategic advantage altering match win probability ($P(\text{Win}) \ne 0.5$).
    """)

    test_res = perform_toss_significance_test(df_matches)

    t_k1, t_k2, t_k3, t_k4 = st.columns(4)
    with t_k1:
        st.metric("Total Matches Sampled", f"{test_res['total_analyzed']:,}")
    with t_k2:
        st.metric("Toss & Match Win Rate", f"{test_res['win_ratio']}%")
    with t_k3:
        st.metric(r"Chi-Square ($\chi^2$) Stat", f"{test_res['chi2_statistic']}")
    with t_k4:
        st.metric("p-value", f"{test_res['p_value']}")

    if test_res['is_statistically_significant']:
        st.success(f"✅ Result: Statistically Significant ($p < 0.05$). We reject the null hypothesis $H_0$. Toss winning provides a measurable advantage.")
    else:
        st.info(rf"ℹ️ Result: Not Statistically Significant ($p \ge 0.05$, $p = {test_res['p_value']}$). We fail to reject $H_0$. Overall across 17+ seasons, winning the toss alone does not guarantee match outcome without taking ground conditions and chasing bias into account.")
