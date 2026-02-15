"""Command line interface for inbox-sanitizer"""

import argparse
import sys
import os
from .auth import get_service
from .gmail_client import GmailClient
from .filters import FilterEngine
from .scheduler import SanitizerScheduler

def main():
    parser = argparse.ArgumentParser(
        description='Clean up your Gmail inbox automatically',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  inbox-sanitizer auth                    # Connect to Gmail
  inbox-sanitizer test-auth               # Test connection and show account info
  inbox-sanitizer check                    # See what would be archived
  inbox-sanitizer clean                     # Actually archive messages
  inbox-sanitizer clean --max 200           # Process up to 200 messages
  inbox-sanitizer daemon                     # Run every hour
  inbox-sanitizer daemon --interval 30       # Run every 30 minutes
        """
    )
    
    parser.add_argument('command', choices=['auth', 'test-auth', 'check', 'clean', 'daemon'],
                       help='What to do')
    parser.add_argument('--max', type=int, default=100,
                       help='Maximum messages to process')
    parser.add_argument('--interval', type=int, default=60,
                       help='Minutes between runs (for daemon)')
    parser.add_argument('--config', default='config/filters.yaml',
                       help='Path to filter config file')
    
    args = parser.parse_args()
    
    # Auth command is special - just sets up connection
    if args.command == 'auth':
        service = get_service()
        if service:
            print("Authentication successful!")
            print("You can now use other commands.")
        return
    
    if args.command == 'test-auth':
        # Test authentication and display connection info
        from .auth import test_connection
        print("\n🔐 Testing authentication...")
        service = get_service()
        if service:
            result = test_connection(service)
            if result['status'] == 'connected':
                print(f"✓ Successfully connected to Gmail")
                print(f"  Email: {result['email']}")
                print(f"  Total messages: {result['messages_total']}")
            else:
                print(f"✗ Connection test failed")
                print(f"  Error: {result['error']}")
                sys.exit(1)
        else:
            print("✗ Authentication failed. Run 'inbox-sanitizer auth' first.")
            sys.exit(1)
        return
    
    # For other commands, we need authenticated service
    service = get_service()
    if not service:
        print("Not authenticated. Run 'inbox-sanitizer auth' first.")
        sys.exit(1)
    
    # Initialize components
    gmail = GmailClient(service)
    filters = FilterEngine(args.config)
    scheduler = SanitizerScheduler(gmail, filters)
    
    if args.command == 'check':
        print("DRY RUN - no messages will be modified")
        results = scheduler.run_once(max_messages=args.max, dry_run=True)
        print(f"\nSummary: {results['archived']} of {results['processed']} would be archived")
    
    elif args.command == 'clean':
        results = scheduler.run_once(max_messages=args.max, dry_run=False)
        print(f"\nSummary: Archived {results['archived']} of {results['processed']} messages")
    
    elif args.command == 'daemon':
        scheduler.run_forever(interval_minutes=args.interval)

if __name__ == '__main__':
    main()
