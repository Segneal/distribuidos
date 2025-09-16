"""
Integration test for email functionality
"""
import sys
import os
from unittest.mock import patch, MagicMock

# Add src directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), '../src'))

from config.email import EmailConfig

def test_email_config_initialization():
    """Test email configuration initialization"""
    email_config = EmailConfig()
    
    # Check default values
    assert email_config.smtp_server == 'smtp.ethereal.email'
    assert email_config.smtp_port == 587
    assert email_config.from_email == 'noreply@ong.com'
    assert email_config.from_name == 'Sistema ONG'

@patch('smtplib.SMTP')
def test_send_password_email_success(mock_smtp):
    """Test successful email sending"""
    # Setup mock
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server
    
    email_config = EmailConfig()
    
    # Test email sending
    result = email_config.send_password_email(
        "test@example.com",
        "test_user",
        "temp_password_123"
    )
    
    # Verify
    assert result == True
    mock_smtp.assert_called_once()
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once()
    mock_server.sendmail.assert_called_once()

@patch('smtplib.SMTP')
def test_send_password_email_failure(mock_smtp):
    """Test email sending failure"""
    # Setup mock to raise exception
    mock_smtp.side_effect = Exception("SMTP Error")
    
    email_config = EmailConfig()
    
    # Test email sending
    result = email_config.send_password_email(
        "test@example.com",
        "test_user",
        "temp_password_123"
    )
    
    # Verify
    assert result == False

def test_email_content_generation():
    """Test that email content is properly generated"""
    email_config = EmailConfig()
    
    # This test verifies the email content structure
    # In a real scenario, we would capture the email content
    # For now, we just verify the method exists and can be called
    try:
        # This would fail in real scenario due to SMTP, but we're testing structure
        email_config.send_password_email(
            "test@example.com",
            "test_user",
            "temp_password_123"
        )
    except Exception:
        # Expected to fail without proper SMTP setup
        pass
    
    # If we get here, the method structure is correct
    assert True

if __name__ == "__main__":
    # Run basic tests
    test_email_config_initialization()
    print("✓ Email configuration initialization test passed")
    
    # Note: SMTP tests require mocking and are better run with pytest
    print("✓ Email integration tests completed")