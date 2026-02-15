"""Filter rules to decide which emails to archive"""

import re
import yaml
import os
from datetime import datetime, timedelta

class FilterEngine:
    """Applies rules to decide if an email should be archived"""
    
    def __init__(self, config_file='config/filters.yaml'):
        self.config = self.load_config(config_file)
        self.stats = {'checked': 0, 'archived': 0, 'kept': 0}
    
    def load_config(self, config_file):
        """Load filter rules from YAML file"""
        default_config = {
            'whitelist': [],      # Always keep these domains
            'blacklist': [],      # Always archive these domains
            'newsletter_patterns': [
                'unsubscribe',
                'newsletter',
                'no-reply@',
                'noreply@',
                'weekly digest',
                'daily briefing'
            ],
            'max_age_days': 30,    # Archive after this many days
            'action': 'archive'     # or 'delete'
        }
        
        if config_file and os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    loaded = yaml.safe_load(f)
                    if loaded:
                        default_config.update(loaded)
            except Exception as e:
                print(f"Error loading config {config_file} from {os.getcwd()}: {e}")
        
        return default_config
    
    def should_archive(self, message):
        """
        Apply rules to determine if message should be archived.
        
        Returns:
            (bool, str): True if should archive, with reason
        """
        self.stats['checked'] += 1
        
        # Check whitelist first (these are never archived)
        from_addr = message.get('from', '').lower()
        for domain in self.config['whitelist']:
            if domain.lower() in from_addr:
                self.stats['kept'] += 1
                return False, f"whitelisted domain: {domain}"
        
        # Check blacklist
        for domain in self.config['blacklist']:
            if domain.lower() in from_addr:
                self.stats['archived'] += 1
                return True, f"blacklisted domain: {domain}"
        
        # Check newsletter patterns
        subject = message.get('subject', '').lower()
        snippet = message.get('snippet', '').lower()
        combined = subject + ' ' + snippet
        
        for pattern in self.config['newsletter_patterns']:
            if pattern.lower() in combined:
                self.stats['archived'] += 1
                return True, f"newsletter pattern: {pattern}"
        
        # Check age (if we have a date)
        if 'date' in message:
            try:
                # This is simplified - real date parsing is more complex
                msg_date = datetime.strptime(message['date'], '%a, %d %b %Y %H:%M:%S %z')
                age_days = (datetime.now().astimezone() - msg_date).days
                if age_days > self.config['max_age_days']:
                    self.stats['archived'] += 1
                    return True, f"older than {self.config['max_age_days']} days"
            except:
                pass  # If date parsing fails, skip age check
        
        self.stats['kept'] += 1
        return False, "no rules matched"
    
    def reset_stats(self):
        """Clear counters"""
        self.stats = {'checked': 0, 'archived': 0, 'kept': 0}
