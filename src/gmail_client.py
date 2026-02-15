"""Wrapper for Gmail API operations"""

import base64
from email.message import EmailMessage
import time

class GmailClient:
    """Simple interface to Gmail"""
    
    def __init__(self, service):
        self.service = service
        self.user_id = 'me'
    
    def list_messages(self, query='', max_results=50):
        """
        Get messages matching a query.
        
        Args:
            query: Gmail search syntax (e.g., 'is:unread')
            max_results: Maximum number to return
        
        Returns:
            List of message objects with id, threadId, snippet
        """
        try:
            results = self.service.users().messages().list(
                userId=self.user_id,
                q=query,
                maxResults=max_results
            ).execute()
            
            return results.get('messages', [])
        except Exception as e:
            print(f"Error listing messages: {e}")
            return []
    
    def get_message(self, msg_id):
        """Get full message details including headers"""
        try:
            msg = self.service.users().messages().get(
                userId=self.user_id,
                id=msg_id,
                format='metadata',
                metadataHeaders=['From', 'Subject', 'Date']
            ).execute()
            
            # Extract headers
            headers = {}
            for header in msg['payload']['headers']:
                headers[header['name']] = header['value']
            
            return {
                'id': msg['id'],
                'threadId': msg['threadId'],
                'snippet': msg.get('snippet', ''),
                'from': headers.get('From', ''),
                'subject': headers.get('Subject', ''),
                'date': headers.get('Date', '')
            }
        except Exception as e:
            print(f"Error getting message {msg_id}: {e}")
            return None
    
    def archive_message(self, msg_id):
        """Remove message from inbox"""
        try:
            self.service.users().messages().modify(
                userId=self.user_id,
                id=msg_id,
                body={'removeLabelIds': ['INBOX']}
            ).execute()
            return True
        except Exception as e:
            print(f"Error archiving {msg_id}: {e}")
            return False
    
    def delete_message(self, msg_id):
        """Permanently delete message"""
        try:
            self.service.users().messages().delete(
                userId=self.user_id,
                id=msg_id
            ).execute()
            return True
        except Exception as e:
            print(f"Error deleting {msg_id}: {e}")
            return False
