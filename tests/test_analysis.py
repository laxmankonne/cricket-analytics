"""
Unit Tests for Statistical Analysis and Machine Learning
Tests batting analysis, bowling analysis, team standings, head-to-head, and ML model.
"""

import os
import unittest
import pandas as pd
from utils.data_loader import load_matches, load_deliveries, load_batting_summary, load_bowling_summary
from utils.batting_analysis import get_filtered_batting_summary, get_highest_individual_innings
from utils.bowling_analysis import get_filtered_bowling_summary
from utils.team_analysis import get_team_standings, get_head_to_head, get_toss_impact_analysis
from utils.advanced_analytics import calculate_batting_efficiency, perform_toss_significance_test

class TestAnalysisModules(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.matches = load_matches()
        # Read a smaller slice of deliveries for speedy testing
        cls.deliv = load_deliveries().head(10000)
        cls.batting = load_batting_summary()
        cls.bowling = load_bowling_summary()

    def test_team_standings_calculation(self):
        """Test franchise standings generation and win % calculation."""
        standings = get_team_standings(self.matches)
        self.assertFalse(standings.empty)
        self.assertIn('win_pct', standings.columns)
        self.assertTrue((standings['win_pct'] >= 0).all())
        self.assertTrue((standings['win_pct'] <= 100).all())

    def test_head_to_head_calculation(self):
        """Test head to head rivalry metrics."""
        h2h = get_head_to_head(self.matches, 'Mumbai Indians', 'Chennai Super Kings')
        self.assertGreater(h2h['total_matches'], 20)
        self.assertEqual(h2h['total_matches'], h2h['team1_wins'] + h2h['team2_wins'] + h2h['ties_or_nr'])

    def test_toss_significance_test(self):
        """Verify chi-square toss hypothesis testing output structure."""
        res = perform_toss_significance_test(self.matches)
        self.assertIn('chi2_statistic', res)
        self.assertIn('p_value', res)
        self.assertIn('is_statistically_significant', res)
        self.assertGreaterEqual(res['p_value'], 0.0)
        self.assertLessEqual(res['p_value'], 1.0)

    def test_batting_efficiency_index(self):
        """Verify Batting Efficiency Rating bounds [0, 100]."""
        eff_df = calculate_batting_efficiency(self.batting)
        self.assertFalse(eff_df.empty)
        self.assertTrue((eff_df['batting_efficiency'] >= 0).all())
        self.assertTrue((eff_df['batting_efficiency'] <= 100).all())

if __name__ == '__main__':
    unittest.main()

