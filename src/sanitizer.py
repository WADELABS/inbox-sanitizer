"""
src/sanitizer.py
The First Real Script: Rule-based inbox sanitization.
"""

from typing import List, Dict

class InboxSanitizer:
    """
    Digital Secretary: Neutralizing noise and isolating signal.
    """
    def __init__(self, salience_keywords: List[str]):
        self.salience_keywords = [k.lower() for k in salience_keywords]
        self.blacklisted_domains = ["sales.com", "newsletter.info", "spam.net"]

    def sanitize(self, inbox: List[Dict[str, str]]) -> List[Dict[str, str]]:
        """
        Runs the sanitization gauntlet on a collection of messages.
        """
        signal = []
        for message in inbox:
            if self._is_signal(message):
                signal.append(message)
                
        return signal

    def _is_signal(self, message: Dict[str, str]) -> bool:
        sender = message.get("sender", "").lower()
        subject = message.get("subject", "").lower()
        body = message.get("body", "").lower()

        # Domain Check
        if any(domain in sender for domain in self.blacklisted_domains):
            return False

        # Keyword Salience (The Job Search Signal)
        context = subject + " " + body
        if any(keyword in context for keyword in self.salience_keywords):
            return True

        # Default to neutral/noise if no signal detected
        return False
