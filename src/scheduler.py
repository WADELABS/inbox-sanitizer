"""Run inbox cleaning on a schedule"""

import time
import schedule
from datetime import datetime

class SanitizerScheduler:
    """Runs the cleaning process at regular intervals"""
    
    def __init__(self, gmail_client, filter_engine):
        self.gmail = gmail_client
        self.filters = filter_engine
        self.runs_completed = 0
    
    def run_once(self, max_messages=100, dry_run=False):
        """
        Process one batch of messages.
        
        Args:
            max_messages: Maximum to check in this run
            dry_run: If True, only report what would be done
        
        Returns:
            dict: Stats from this run
        """
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Checking inbox...")
        
        # Get unread messages
        messages = self.gmail.list_messages(query='in:inbox', max_results=max_messages)
        
        if not messages:
            print("No messages found")
            return {'processed': 0, 'archived': 0}
        
        print(f"Found {len(messages)} messages in inbox")
        
        archived_count = 0
        for msg_data in messages:
            # Get full message details
            msg = self.gmail.get_message(msg_data['id'])
            if not msg:
                continue
            
            # Apply filters
            should_archive, reason = self.filters.should_archive(msg)
            
            if should_archive:
                archived_count += 1
                subject = msg.get('subject', 'No subject')[:40]
                if dry_run:
                    print(f"  Would archive: {subject} ({reason})")
                else:
                    self.gmail.archive_message(msg['id'])
                    print(f"  Archived: {subject} ({reason})")
        
        self.runs_completed += 1
        
        return {
            'processed': len(messages),
            'archived': archived_count,
            'kept': len(messages) - archived_count,
            'dry_run': dry_run
        }
    
    def run_forever(self, interval_minutes=60):
        """
        Run continuously at specified interval.
        
        Args:
            interval_minutes: How often to check inbox
        """
        print(f"Starting inbox sanitizer (checking every {interval_minutes} minutes)")
        print("Press Ctrl+C to stop")
        
        # Run once immediately
        self.run_once()
        
        # Schedule future runs
        schedule.every(interval_minutes).minutes.do(self.run_once)
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(10)
        except KeyboardInterrupt:
            print(f"\nStopped after {self.runs_completed} runs")
