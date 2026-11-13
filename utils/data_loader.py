"""
Data Loader Utility Module
Provides high-performance cached loaders for clean matches, ball-by-ball deliveries,
and pre-aggregated summaries using Streamlit cache.
"""

import os
import streamlit as st
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')

MATCHES_PATH = os.path.join(PROCESSED_DIR, 'matches_clean.csv')
DELIVERIES_PATH = os.path.join(PROCESSED_DIR, 'deliveries_clean.csv')
BATTING_PATH = os.path.join(PROCESSED_DIR, 'player_batting_summary.csv')
BOWLING_PATH = os.path.join(PROCESSED_DIR, 'player_bowling_summary.csv')
TEAM_PATH = os.path.join(PROCESSED_DIR, 'team_summary.csv')
VENUE_PATH = os.path.join(PROCESSED_DIR, 'venue_summary.csv')

@st.cache_data(show_spinner=False)
def load_matches():
    if not os.path.exists(MATCHES_PATH):
        raise FileNotFoundError(f"Missing processed dataset: {MATCHES_PATH}. Please run scripts/acquire_and_preprocess.py.")
    df = pd.read_csv(MATCHES_PATH)
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['season'] = df['season'].astype(str)
    return df

@st.cache_data(show_spinner=False)
def load_deliveries():
    if not os.path.exists(DELIVERIES_PATH):
        raise FileNotFoundError(f"Missing processed dataset: {DELIVERIES_PATH}. Please run scripts/acquire_and_preprocess.py.")
    df = pd.read_csv(DELIVERIES_PATH, low_memory=False)
    df['season'] = df['season'].astype(str)
    return df

@st.cache_data(show_spinner=False)
def load_batting_summary():
    if not os.path.exists(BATTING_PATH):
        raise FileNotFoundError(f"Missing summary file: {BATTING_PATH}")
    return pd.read_csv(BATTING_PATH)

@st.cache_data(show_spinner=False)
def load_bowling_summary():
    if not os.path.exists(BOWLING_PATH):
        raise FileNotFoundError(f"Missing summary file: {BOWLING_PATH}")
    return pd.read_csv(BOWLING_PATH)

@st.cache_data(show_spinner=False)
def load_team_summary():
    if not os.path.exists(TEAM_PATH):
        raise FileNotFoundError(f"Missing summary file: {TEAM_PATH}")
    return pd.read_csv(TEAM_PATH)

@st.cache_data(show_spinner=False)
def load_venue_summary():
    if not os.path.exists(VENUE_PATH):
        raise FileNotFoundError(f"Missing summary file: {VENUE_PATH}")
    return pd.read_csv(VENUE_PATH)

def get_filter_options(matches_df):
    seasons = sorted(matches_df['season'].dropna().unique().tolist())
    teams = sorted(list(set(matches_df['team1'].dropna()).union(set(matches_df['team2'].dropna()))))
    venues = sorted(matches_df['venue'].dropna().unique().tolist())
    return seasons, teams, venues
