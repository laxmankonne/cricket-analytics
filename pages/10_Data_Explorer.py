"""
Module 10: Data Explorer
Features: Interactive dataset viewer, search, multi-column filtering,
missing-value analysis, and instant CSV export.
"""

import streamlit as st
import pandas as pd
from utils.data_loader import load_matches, load_deliveries, load_batting_summary, load_bowling_summary, load_team_summary, load_venue_summary
from utils.ui_helper import apply_app_styles, render_sidebar_header, render_page_header
import plotly.express as px

st.set_page_config(
    page_title="Data Explorer | Cricket Analytics",
    page_icon="🏏",
    layout="wide"
)

apply_app_styles()
render_sidebar_header()

render_page_header(
    title="Interactive Data Explorer",
    subtitle="Inspect raw and processed cricket datasets, evaluate data schema & completeness, search records, and export filtered data to CSV.",
    badge_text="MODULE 10 • DATA REPOSITORY"
)

# Dataset Selector
dataset_choice = st.selectbox(
    "Choose Dataset to Explore",
    [
        "Matches Metadata (matches_clean.csv)",
        "Ball-by-Ball Deliveries (deliveries_clean.csv - Sample)",
        "Player Batting Summary (player_batting_summary.csv)",
        "Player Bowling Summary (player_bowling_summary.csv)",
        "Franchise Summary (team_summary.csv)",
        "Venue Summary (venue_summary.csv)"
    ]
)

# Load selected dataframe
if "Matches Metadata" in dataset_choice:
    df_current = load_matches()
elif "Deliveries" in dataset_choice:
    # Deliveries is 295k rows, take first 50k or filter
    st.info("💡 Ball-by-ball dataset contains 295,000+ delivery rows. Displaying the most recent 25,000 deliveries for interactive viewing.")
    df_current = load_deliveries().tail(25000).reset_index(drop=True)
elif "Batting" in dataset_choice:
    df_current = load_batting_summary()
elif "Bowling" in dataset_choice:
    df_current = load_bowling_summary()
elif "Franchise" in dataset_choice:
    df_current = load_team_summary()
else:
    df_current = load_venue_summary()

tab1, tab2, tab3 = st.tabs([
    "🔍 Table Explorer & Filter",
    "📊 Dataset Schema & Completeness",
    "📥 Data Export"
])

with tab1:
    search_query = st.text_input("🔎 Search text across all columns", "")
    
    df_filtered = df_current.copy()
    if search_query:
        mask = df_filtered.astype(str).apply(lambda row: row.str.contains(search_query, case=False).any(), axis=1)
        df_filtered = df_filtered[mask]

    st.markdown(f"**Showing {len(df_filtered):,} of {len(df_current):,} records**")
    
    # Pagination
    page_size = st.selectbox("Rows per page", [25, 50, 100, 250], index=0)
    total_pages = max(1, (len(df_filtered) // page_size) + (1 if len(df_filtered) % page_size > 0 else 0))
    page_num = st.number_input("Page Number", min_value=1, max_value=total_pages, value=1, step=1)
    
    start_idx = (page_num - 1) * page_size
    end_idx = min(start_idx + page_size, len(df_filtered))
    
    st.dataframe(df_filtered.iloc[start_idx:end_idx], use_container_width=True)

with tab2:
    st.markdown("#### 📋 Data Health & Missing Values Audit")
    
    info_c1, info_c2 = st.columns(2)
    with info_c1:
        st.markdown(f"""
        - **Total Rows:** {len(df_current):,}
        - **Total Columns:** {len(df_current.columns)}
        - **Memory Footprint:** {df_current.memory_usage(deep=True).sum() / (1024*1024):.2f} MB
        """)

    with info_c2:
        missing_df = df_current.isnull().sum().reset_index()
        missing_df.columns = ['Column', 'Missing Count']
        missing_df['Missing %'] = (missing_df['Missing Count'] / len(df_current) * 100).round(2)
        st.dataframe(missing_df[missing_df['Missing Count'] > 0], use_container_width=True, hide_index=True)

    # Missing values bar chart
    if missing_df['Missing Count'].sum() > 0:
        fig_miss = px.bar(
            missing_df[missing_df['Missing Count'] > 0],
            x='Column',
            y='Missing %',
            title="Missing Value Percentage by Column",
            color_discrete_sequence=['#EF4444'],
            template='plotly_dark'
        )
        fig_miss.update_layout(paper_bgcolor='#111C2E', plot_bgcolor='#111C2E', font=dict(color='#F8FAFC'))
        st.plotly_chart(fig_miss, use_container_width=True)
    else:
        st.success("✅ Zero missing values in this dataset table!")

with tab3:
    st.markdown("#### 📥 Download Dataset")
    st.caption("Export the current filtered dataset for further offline research or analytical modeling.")

    csv_data = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label=f"⬇️ Download Filtered Data as CSV ({len(df_filtered):,} rows)",
        data=csv_data,
        file_name=f"cricket_analytics_export_{dataset_choice.split()[0].lower()}.csv",
        mime="text/csv",
        use_container_width=True
    )
