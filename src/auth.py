"""OAuth2 authentication for Gmail with token refresh and error handling"""

from typing import Optional, Dict, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import os.path
import pickle
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Gmail API scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.modify']
TOKEN_FILE = 'token.pickle'
CREDENTIALS_FILE = 'credentials.json'

def get_service(provider: str = 'gmail') -> Optional[Any]:
    """
    Authenticate and return Gmail service client.
    
    This function handles:
    - Loading existing credentials from token.pickle
    - Refreshing expired tokens automatically
    - Initiating new OAuth flow if needed
    - Saving credentials for future use
    
    Args:
        provider: Email provider (currently only 'gmail' supported)
    
    Returns:
        Authenticated Gmail API service client, or None if authentication fails
    
    Raises:
        FileNotFoundError: If credentials.json is missing
        ValueError: If token refresh fails and cannot be recovered
    
    Examples:
        >>> service = get_service()
        >>> if service:
        ...     profile = service.users().getProfile(userId='me').execute()
        ...     print(f"Connected as: {profile['emailAddress']}")
    """
    if provider != 'gmail':
        logger.warning(f"Provider '{provider}' not yet supported, defaulting to Gmail")
    
    return _get_gmail_service()

def _get_gmail_service() -> Optional[Any]:
    """
    Get authenticated Gmail service with automatic token refresh.
    
    Returns:
        Gmail API service client or None if authentication fails
    """
    creds = None
    
    # Load existing token if it exists
    if os.path.exists(TOKEN_FILE):
        try:
            with open(TOKEN_FILE, 'rb') as token:
                creds = pickle.load(token)
            logger.info("Loaded existing credentials from token.pickle")
        except Exception as e:
            logger.error(f"Failed to load token file: {e}")
            creds = None
    
    # Check if credentials are valid or can be refreshed
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Try to refresh the token
            try:
                logger.info("Refreshing expired access token...")
                creds.refresh(Request())
                logger.info("✓ Token refreshed successfully")
            except Exception as e:
                logger.error(f"✗ Token refresh failed: {e}")
                logger.info("Will initiate new OAuth flow")
                creds = None
        
        # If we still don't have valid creds, start new OAuth flow
        if not creds:
            if not os.path.exists(CREDENTIALS_FILE):
                raise FileNotFoundError(
                    f"Missing {CREDENTIALS_FILE}. "
                    f"Download OAuth2 credentials from Google Cloud Console:\n"
                    f"1. Go to https://console.cloud.google.com/\n"
                    f"2. Enable Gmail API\n"
                    f"3. Create OAuth2 credentials\n"
                    f"4. Download and save as {CREDENTIALS_FILE}"
                )
            
            try:
                logger.info("Starting OAuth2 authentication flow...")
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_FILE, SCOPES
                )
                creds = flow.run_local_server(port=0)
                logger.info("✓ Authentication successful")
            except Exception as e:
                logger.error(f"✗ OAuth flow failed: {e}")
                return None
        
        # Save credentials for future use
        try:
            with open(TOKEN_FILE, 'wb') as token:
                pickle.dump(creds, token)
            logger.info(f"Credentials saved to {TOKEN_FILE}")
        except Exception as e:
            logger.error(f"Warning: Could not save credentials: {e}")
    
    # Build and return the Gmail service
    try:
        service = build('gmail', 'v1', credentials=creds)
        logger.info("Gmail API service initialized")
        return service
    except Exception as e:
        logger.error(f"Failed to build Gmail service: {e}")
        return None

def test_connection(service: Any, provider: str = 'gmail') -> Dict[str, Any]:
    """
    Test email service connection and retrieve account information.
    
    Args:
        service: Authenticated email service client
        provider: Email provider type ('gmail')
    
    Returns:
        Dictionary containing connection status:
        - status: 'connected' or 'failed'
        - email: User's email address (if connected)
        - messages_total: Approximate message count (if connected)
        - error: Error message (if failed)
        - provider: Provider type
    
    Examples:
        >>> service = get_service()
        >>> result = test_connection(service)
        >>> if result['status'] == 'connected':
        ...     print(f"✓ Connected as {result['email']}")
        ...     print(f"  Total messages: {result['messages_total']}")
    """
    try:
        if provider == 'gmail':
            # Get user profile
            profile = service.users().getProfile(userId='me').execute()
            email_address = profile.get('emailAddress', 'unknown')
            
            # Get message count
            messages_response = service.users().messages().list(
                userId='me', maxResults=1
            ).execute()
            total_messages = messages_response.get('resultSizeEstimate', 0)
            
            logger.info(f"✓ Connection test successful: {email_address}")
            
            return {
                'status': 'connected',
                'email': email_address,
                'messages_total': total_messages,
                'provider': provider
            }
    except Exception as e:
        logger.error(f"✗ Connection test failed: {e}")
        return {
            'status': 'failed',
            'error': str(e),
            'provider': provider
        }

def revoke_credentials() -> bool:
    """
    Revoke stored credentials and delete token file.
    
    Useful for logging out or switching accounts.
    
    Returns:
        True if credentials were successfully removed
    """
    try:
        if os.path.exists(TOKEN_FILE):
            os.remove(TOKEN_FILE)
            logger.info(f"✓ Removed {TOKEN_FILE}")
            return True
        else:
            logger.info(f"{TOKEN_FILE} does not exist")
            return False
    except Exception as e:
        logger.error(f"✗ Failed to remove credentials: {e}")
        return False
