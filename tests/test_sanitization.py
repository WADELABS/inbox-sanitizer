"""
tests/test_sanitization.py
Verification of the 'First Real Script' logic.
"""

import unittest
import sys
import os

# Path injection for IDE
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.sanitizer import InboxSanitizer

class TestSanitizer(unittest.TestCase):
    def setUp(self):
        self.sanitizer = InboxSanitizer(salience_keywords=["Interview", "Job", "Recruiter"])

    def test_signal_detection(self):
        """Test that important emails are preserved."""
        inbox = [
            {"sender": "recruiter@tech.com", "subject": "Interview Request", "body": "Are you available?"},
            {"sender": "no-reply@sales.com", "subject": "50% OFF EVERYTHING", "body": "Buy now!"}
        ]
        
        signal = self.sanitizer.sanitize(inbox)
        self.assertEqual(len(signal), 1)
        self.assertEqual(signal[0]["subject"], "Interview Request")

    def test_noise_neutralization(self):
        """Test that spam domains are blocked."""
        inbox = [
            {"sender": "news@spam.net", "subject": "Check this out", "body": "You won a prize!"}
        ]
        
        signal = self.sanitizer.sanitize(inbox)
        self.assertEqual(len(signal), 0)

if __name__ == "__main__":
    unittest.main()
