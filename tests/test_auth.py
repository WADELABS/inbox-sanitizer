"""Comprehensive tests for authentication module"""

import pytest
from unittest.mock import Mock, patch, MagicMock, mock_open
from src.auth import (
    get_service, 
    test_connection, 
    _get_gmail_service, 
    revoke_credentials,
    TOKEN_FILE,
    CREDENTIALS_FILE
)
import pickle

class TestGetService:
    """Tests for get_service() function"""
    
    def test_get_service_gmail_success(self):
        """Should successfully return Gmail service"""
        with patch('src.auth._get_gmail_service') as mock_gmail:
            mock_service = Mock()
            mock_gmail.return_value = mock_service
            
            service = get_service('gmail')
            
            assert service == mock_service
            mock_gmail.assert_called_once()
    
    def test_get_service_defaults_to_gmail(self):
        """Should default to Gmail if provider not specified"""
        with patch('src.auth._get_gmail_service') as mock_gmail:
            mock_gmail.return_value = Mock()
            
            service = get_service()
            
            mock_gmail.assert_called_once()
    
    def test_get_service_unsupported_provider_fallback(self):
        """Should fall back to Gmail for unsupported providers"""
        with patch('src.auth._get_gmail_service') as mock_gmail:
            mock_gmail.return_value = Mock()
            
            service = get_service('outlook')
            
            mock_gmail.assert_called_once()

class TestGmailService:
    """Tests for _get_gmail_service() function"""
    
    def test_loads_existing_valid_token(self):
        """Should load and use existing valid credentials"""
        mock_creds = MagicMock()
        mock_creds.valid = True
        
        with patch('src.auth.os.path.exists', return_value=True):
            with patch('builtins.open', mock_open(read_data=b'pickled_data')):
                with patch('pickle.load', return_value=mock_creds):
                    with patch('src.auth.build') as mock_build:
                        mock_build.return_value = Mock()
                        
                        service = _get_gmail_service()
                        
                        assert service is not None
                        mock_build.assert_called_once_with('gmail', 'v1', credentials=mock_creds)
    
    def test_refreshes_expired_token_with_refresh_token(self):
        """Should refresh expired token if refresh_token exists"""
        mock_creds = MagicMock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = 'refresh_token_123'
        
        with patch('src.auth.os.path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                with patch('pickle.load', return_value=mock_creds):
                    with patch('pickle.dump'):
                        with patch('src.auth.build') as mock_build:
                            mock_build.return_value = Mock()
                            
                            service = _get_gmail_service()
                            
                            mock_creds.refresh.assert_called_once()
                            assert service is not None
    
    def test_refresh_failure_starts_new_oauth_flow(self):
        """Should start new OAuth flow if token refresh fails"""
        mock_creds = MagicMock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = 'refresh_token_123'
        mock_creds.refresh.side_effect = Exception("Refresh failed")
        
        mock_new_creds = MagicMock()
        mock_new_creds.valid = True
        
        with patch('src.auth.os.path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                with patch('pickle.load', return_value=mock_creds):
                    with patch('pickle.dump'):
                        with patch('src.auth.InstalledAppFlow.from_client_secrets_file') as mock_flow:
                            mock_flow_instance = Mock()
                            mock_flow_instance.run_local_server.return_value = mock_new_creds
                            mock_flow.return_value = mock_flow_instance
                            
                            with patch('src.auth.build') as mock_build:
                                mock_build.return_value = Mock()
                                
                                service = _get_gmail_service()
                                
                                mock_flow_instance.run_local_server.assert_called_once()
                                assert service is not None
    
    def test_missing_credentials_file_raises_error(self):
        """Should raise FileNotFoundError if credentials.json missing"""
        with patch('src.auth.os.path.exists') as mock_exists:
            # Token file doesn't exist, credentials file doesn't exist
            mock_exists.side_effect = lambda path: False
            
            with pytest.raises(FileNotFoundError, match="credentials.json"):
                _get_gmail_service()
    
    def test_no_token_starts_oauth_flow(self):
        """Should start OAuth flow if no token file exists"""
        mock_creds = MagicMock()
        mock_creds.valid = True
        
        with patch('src.auth.os.path.exists') as mock_exists:
            # Token doesn't exist, credentials exists
            mock_exists.side_effect = lambda path: path == CREDENTIALS_FILE
            
            with patch('src.auth.InstalledAppFlow.from_client_secrets_file') as mock_flow:
                mock_flow_instance = Mock()
                mock_flow_instance.run_local_server.return_value = mock_creds
                mock_flow.return_value = mock_flow_instance
                
                with patch('builtins.open', mock_open()):
                    with patch('pickle.dump'):
                        with patch('src.auth.build') as mock_build:
                            mock_build.return_value = Mock()
                            
                            service = _get_gmail_service()
                            
                            mock_flow_instance.run_local_server.assert_called_once_with(port=0)
                            assert service is not None
    
    def test_oauth_flow_failure_returns_none(self):
        """Should return None if OAuth flow fails"""
        with patch('src.auth.os.path.exists') as mock_exists:
            mock_exists.side_effect = lambda path: path == CREDENTIALS_FILE
            
            with patch('src.auth.InstalledAppFlow.from_client_secrets_file') as mock_flow:
                mock_flow.side_effect = Exception("OAuth failed")
                
                service = _get_gmail_service()
                
                assert service is None
    
    def test_saves_credentials_after_auth(self):
        """Should save credentials to token.pickle after successful auth"""
        mock_creds = MagicMock()
        mock_creds.valid = True
        
        with patch('src.auth.os.path.exists') as mock_exists:
            mock_exists.side_effect = lambda path: path == CREDENTIALS_FILE
            
            with patch('src.auth.InstalledAppFlow.from_client_secrets_file') as mock_flow:
                mock_flow_instance = Mock()
                mock_flow_instance.run_local_server.return_value = mock_creds
                mock_flow.return_value = mock_flow_instance
                
                m_open = mock_open()
                with patch('builtins.open', m_open):
                    with patch('pickle.dump') as mock_dump:
                        with patch('src.auth.build', return_value=Mock()):
                            service = _get_gmail_service()
                            
                            # Verify pickle.dump was called with credentials
                            mock_dump.assert_called_once()
                            call_args = mock_dump.call_args[0]
                            assert call_args[0] == mock_creds

class TestConnectionTesting:
    """Tests for test_connection() function"""
    
    def test_connection_success_returns_details(self):
        """Should return connection details on successful test"""
        mock_service = Mock()
        mock_service.users().getProfile().execute.return_value = {
            'emailAddress': 'test@example.com'
        }
        mock_service.users().messages().list().execute.return_value = {
            'resultSizeEstimate': 1337
        }
        
        result = test_connection(mock_service, 'gmail')
        
        assert result['status'] == 'connected'
        assert result['email'] == 'test@example.com'
        assert result['messages_total'] == 1337
        assert result['provider'] == 'gmail'
    
    def test_connection_failure_returns_error(self):
        """Should return error details on connection failure"""
        mock_service = Mock()
        mock_service.users().getProfile().execute.side_effect = Exception("API Error")
        
        result = test_connection(mock_service, 'gmail')
        
        assert result['status'] == 'failed'
        assert 'API Error' in result['error']
        assert result['provider'] == 'gmail'
    
    def test_connection_handles_missing_email(self):
        """Should handle missing email in profile response"""
        mock_service = Mock()
        mock_service.users().getProfile().execute.return_value = {}
        mock_service.users().messages().list().execute.return_value = {}
        
        result = test_connection(mock_service, 'gmail')
        
        assert result['status'] == 'connected'
        assert result['email'] == 'unknown'
        assert result['messages_total'] == 0

class TestCredentialRevocation:
    """Tests for revoke_credentials() function"""
    
    def test_revoke_removes_token_file(self):
        """Should remove token.pickle file"""
        with patch('src.auth.os.path.exists', return_value=True):
            with patch('src.auth.os.remove') as mock_remove:
                result = revoke_credentials()
                
                assert result is True
                mock_remove.assert_called_once_with(TOKEN_FILE)
    
    def test_revoke_when_no_token_file(self):
        """Should return False if no token file exists"""
        with patch('src.auth.os.path.exists', return_value=False):
            result = revoke_credentials()
            
            assert result is False
    
    def test_revoke_handles_removal_failure(self):
        """Should handle errors during file removal"""
        with patch('src.auth.os.path.exists', return_value=True):
            with patch('src.auth.os.remove', side_effect=OSError("Permission denied")):
                result = revoke_credentials()
                
                assert result is False

class TestIntegration:
    """Integration tests for auth module"""
    
    def test_full_auth_flow_with_valid_token(self):
        """Test complete flow with valid token"""
        mock_creds = MagicMock()
        mock_creds.valid = True
        mock_service = Mock()
        
        with patch('src.auth.os.path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                with patch('pickle.load', return_value=mock_creds):
                    with patch('src.auth.build', return_value=mock_service):
                        service = get_service('gmail')
                        
                        assert service == mock_service
    
    def test_full_flow_with_token_refresh(self):
        """Test complete flow with token refresh"""
        mock_creds = MagicMock()
        mock_creds.valid = False
        mock_creds.expired = True
        mock_creds.refresh_token = 'refresh'
        mock_service = Mock()
        
        with patch('src.auth.os.path.exists', return_value=True):
            with patch('builtins.open', mock_open()):
                with patch('pickle.load', return_value=mock_creds):
                    with patch('pickle.dump'):
                        with patch('src.auth.build', return_value=mock_service):
                            service = get_service('gmail')
                            
                            mock_creds.refresh.assert_called_once()
                            assert service == mock_service
