"""
Unit Tests for Cricket Dataset Integrity and Cleaning
Tests dataset loading, column schemas, duplicate records, and data types.
"""

import os
import unittest
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')

class TestCricketData(unittest.TestCase):

    def setUp(self):
        self.matches_path = os.path.join(PROCESSED_DIR, 'matches_clean.csv')
        self.deliv_path = os.path.join(PROCESSED_DIR, 'deliveries_clean.csv')
        self.batting_path = os.path.join(PROCESSED_DIR, 'player_batting_summary.csv')
        self.bowling_path = os.path.join(PROCESSED_DIR, 'player_bowling_summary.csv')

    def test_files_exist(self):
        """Verify that all processed datasets exist on disk."""
        self.assertTrue(os.path.exists(self.matches_path), "matches_clean.csv missing")
        self.assertTrue(os.path.exists(self.deliv_path), "deliveries_clean.csv missing")
        self.assertTrue(os.path.exists(self.batting_path), "player_batting_summary.csv missing")
        self.assertTrue(os.path.exists(self.bowling_path), "player_bowling_summary.csv missing")

    def test_matches_data_integrity(self):
        """Verify matches schema and non-emptiness."""
        df = pd.read_csv(self.matches_path)
        self.assertGreater(len(df), 1000, "Matches dataset should contain >1000 records")
        required_cols = ['match_id', 'season', 'date', 'venue', 'team1', 'team2', 'toss_winner', 'winner', 'result']
        for col in required_cols:
            self.assertIn(col, df.columns, f"Missing required column in matches: {col}")
        
        # Check match_id uniqueness
        self.assertEqual(df['match_id'].nunique(), len(df), "Match IDs must be strictly unique")

    def test_deliveries_data_integrity(self):
        """Verify ball-by-ball delivery event schema and sample records."""
        # Read sample of deliveries
        df = pd.read_csv(self.deliv_path, nrows=5000)
        self.assertGreater(len(df), 1000)
        required_cols = ['match_id', 'innings', 'ball', 'batting_team', 'bowling_team', 'striker', 'bowler', 'runs_off_bat', 'extras', 'total_runs']
        for col in required_cols:
            self.assertIn(col, df.columns, f"Missing required column in deliveries: {col}")

    def test_batting_summary_calculations(self):
        """Verify that batting metrics conform to mathematical boundaries."""
        df = pd.read_csv(self.batting_path)
        self.assertGreater(len(df), 500)
        # Total runs >= 0
        self.assertTrue((df['total_runs'] >= 0).all())
        # Strike rate >= 0
        self.assertTrue((df['strike_rate'] >= 0).all())
        # Batting average >= 0
        self.assertTrue((df['batting_average'] >= 0).all())
        # Boundary percentage between 0 and 100
        self.assertTrue((df['boundary_percentage'].between(0, 100)).all())

    def test_bowling_summary_calculations(self):
        """Verify bowling metrics boundaries."""
        df = pd.read_csv(self.bowling_path)
        self.assertGreater(len(df), 400)
        # Economy rate >= 0
        self.assertTrue((df['economy_rate'] >= 0).all())
        # Wickets >= 0
        self.assertTrue((df['total_wickets'] >= 0).all())

if __name__ == '__main__':
    unittest.main()
