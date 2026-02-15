import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.filters import FilterEngine

def test_whitelist_keeps_messages():
    """Messages from whitelisted domains should not be archived"""
    filters = FilterEngine(config_file=None)  # Use defaults
    filters.config['whitelist'] = ['@safe.com']
    
    msg = {'from': 'newsletter@safe.com', 'subject': 'test', 'snippet': ''}
    should_archive, reason = filters.should_archive(msg)
    
    assert should_archive == False
    assert 'whitelisted' in reason

def test_blacklist_archives_messages():
    """Messages from blacklisted domains should be archived"""
    filters = FilterEngine(config_file=None)
    filters.config['blacklist'] = ['@spam.com']
    
    msg = {'from': 'ads@spam.com', 'subject': 'test', 'snippet': ''}
    should_archive, reason = filters.should_archive(msg)
    
    assert should_archive == True
    assert 'blacklisted' in reason

def test_newsletter_patterns():
    """Messages with newsletter keywords should be archived"""
    filters = FilterEngine(config_file=None)
    
    msg = {'from': 'someone@example.com', 'subject': 'Your weekly newsletter', 'snippet': ''}
    should_archive, reason = filters.should_archive(msg)
    
    assert should_archive == True
    assert 'newsletter' in reason

def test_stats_tracking():
    """Should count how many messages processed"""
    filters = FilterEngine(config_file=None)
    
    msg1 = {'from': 'keep@example.com', 'subject': 'hello', 'snippet': ''}
    msg2 = {'from': 'spam@spam.com', 'subject': 'unsubscribe', 'snippet': ''}
    
    filters.config['blacklist'] = ['@spam.com']
    filters.config['newsletter_patterns'] = ['unsubscribe']
    
    filters.should_archive(msg1)
    filters.should_archive(msg2)
    
    assert filters.stats['checked'] == 2
    assert filters.stats['archived'] == 1
    assert filters.stats['kept'] == 1
