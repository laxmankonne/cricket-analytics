"""
Advanced Analytics and Machine Learning Module
Includes Player Consistency Index (PCI), Batting/Bowling Efficiency,
Toss Hypothesis Testing, and Match Outcome Prediction Model (Logistic Regression).
"""

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, confusion_matrix, classification_report
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline

def calculate_batting_efficiency(batting_df):
    """
    Batting Efficiency Rating (BER):
    BER = 0.4 * normalized(Average) + 0.4 * normalized(Strike Rate) + 0.2 * normalized(Boundary %)
    Normalized min-max [0, 100]
    """
    df = batting_df[batting_df['total_runs'] >= 300].copy()
    if df.empty:
        return df

    def min_max_norm(series):
        min_v, max_v = series.min(), series.max()
        if max_v == min_v:
            return pd.Series(50, index=series.index)
        return ((series - min_v) / (max_v - min_v)) * 100

    norm_avg = min_max_norm(df['batting_average'])
    norm_sr = min_max_norm(df['strike_rate'])
    norm_bnd = min_max_norm(df['boundary_percentage'])

    df['batting_efficiency'] = (0.4 * norm_avg + 0.4 * norm_sr + 0.2 * norm_bnd).round(2)
    return df.sort_values(by='batting_efficiency', ascending=False)

def calculate_bowling_efficiency(bowling_df):
    """
    Bowling Efficiency Rating (BoER):
    BoER = 0.4 * normalized(Inverted Economy) + 0.35 * normalized(Inverted Average) + 0.25 * normalized(Inverted Strike Rate)
    Normalized min-max [0, 100] (Higher is better)
    """
    df = bowling_df[(bowling_df['total_wickets'] >= 15) & (bowling_df['economy_rate'] > 0)].copy()
    if df.empty:
        return df

    def invert_min_max(series):
        min_v, max_v = series.min(), series.max()
        if max_v == min_v:
            return pd.Series(50, index=series.index)
        return ((max_v - series) / (max_v - min_v)) * 100

    norm_econ = invert_min_max(df['economy_rate'])
    norm_avg = invert_min_max(df['bowling_average'].fillna(df['bowling_average'].max()))
    norm_sr = invert_min_max(df['bowling_strike_rate'].fillna(df['bowling_strike_rate'].max()))

    df['bowling_efficiency'] = (0.4 * norm_econ + 0.35 * norm_avg + 0.25 * norm_sr).round(2)
    return df.sort_values(by='bowling_efficiency', ascending=False)

def perform_toss_significance_test(matches_df):
    """
    Chi-Square Test of Independence on Toss Winner vs Match Winner.
    H0: Toss winner has no statistical relationship with Match winner.
    H1: Winning the toss significantly alters the odds of winning the match.
    """
    valid = matches_df.dropna(subset=['toss_winner', 'winner']).copy()
    valid['toss_won_match'] = (valid['toss_winner'] == valid['winner']).astype(int)
    
    total = len(valid)
    toss_and_win = valid['toss_won_match'].sum()
    toss_and_loss = total - toss_and_win
    
    # Expected equal probability (50% - 50%)
    observed = [toss_and_win, toss_and_loss]
    expected = [total * 0.5, total * 0.5]
    
    chi2, p_val = stats.chisquare(f_obs=observed, f_exp=expected)
    
    return {
        'total_analyzed': total,
        'toss_and_match_wins': int(toss_and_win),
        'toss_and_match_losses': int(toss_and_loss),
        'win_ratio': round(toss_and_win / total * 100, 2),
        'chi2_statistic': round(chi2, 4),
        'p_value': round(p_val, 5),
        'is_statistically_significant': bool(p_val < 0.05)
    }

def train_match_outcome_model(matches_df, deliv_df):
    """
    Machine Learning Match Outcome Predictor.
    Model: Regularized Logistic Regression with One-Hot Encoded Categoricals.
    Features: Team1, Team2, Venue, Toss Winner, Toss Decision, 1st Innings Runs.
    Target: 1 if Team1 won, 0 if Team2 won.
    Strictly prevents data leakage by only utilizing pre-match & mid-match features.
    """
    # 1. Calculate 1st innings score for each match
    inns1_runs = deliv_df[deliv_df['innings'] == 1].groupby('match_id')['total_runs'].sum().reset_index()
    inns1_runs.rename(columns={'total_runs': 'inns1_score'}, inplace=True)
    
    # Filter valid matches with clear winner between team1 and team2
    df = matches_df.merge(inns1_runs, on='match_id', how='inner')
    df = df[df['winner'].isin(df['team1']) | df['winner'].isin(df['team2'])].copy()
    df = df.dropna(subset=['team1', 'team2', 'venue', 'toss_winner', 'toss_decision', 'winner', 'inns1_score'])

    df['target'] = (df['winner'] == df['team1']).astype(int)

    feature_cols = ['team1', 'team2', 'venue', 'toss_winner', 'toss_decision', 'inns1_score']
    X = df[feature_cols]
    y = df['target']

    # Train/Test Split (80% Train, 20% Test)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.20, random_state=42, stratify=y)

    categorical_cols = ['team1', 'team2', 'venue', 'toss_winner', 'toss_decision']
    preprocessor = ColumnTransformer(
        transformers=[
            ('cat', OneHotEncoder(handle_unknown='ignore', sparse_output=False), categorical_cols)
        ],
        remainder='passthrough'
    )

    pipeline = Pipeline(steps=[
        ('preprocessor', preprocessor),
        ('classifier', LogisticRegression(max_iter=1000, C=0.5, random_state=42))
    ])

    pipeline.fit(X_train, y_train)

    # Evaluation
    y_pred = pipeline.predict(X_test)
    y_prob = pipeline.predict_proba(X_test)[:, 1]

    accuracy = round(accuracy_score(y_test, y_pred) * 100, 2)
    roc_auc = round(roc_auc_score(y_test, y_prob), 3)
    cm = confusion_matrix(y_test, y_pred).tolist()
    rep = classification_report(y_test, y_pred, output_dict=True)

    return {
        'model': pipeline,
        'accuracy': accuracy,
        'roc_auc': roc_auc,
        'confusion_matrix': cm,
        'classification_report': rep,
        'test_size': len(y_test),
        'train_size': len(y_train)
    }

def predict_match_outcome(model_pipeline, team1, team2, venue, toss_winner, toss_decision, inns1_score=170):
    input_data = pd.DataFrame([{
        'team1': team1,
        'team2': team2,
        'venue': venue,
        'toss_winner': toss_winner,
        'toss_decision': toss_decision,
        'inns1_score': inns1_score
    }])
    prob = model_pipeline.predict_proba(input_data)[0]
    prob_team1 = round(prob[1] * 100, 1)
    prob_team2 = round(prob[0] * 100, 1)
    predicted_winner = team1 if prob_team1 >= prob_team2 else team2

    return {
        'predicted_winner': predicted_winner,
        'team1_prob': prob_team1,
        'team2_prob': prob_team2,
        'confidence': max(prob_team1, prob_team2)
    }

