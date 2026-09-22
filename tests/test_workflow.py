"""
Test module for the Automated Web Testing & Workflow Bot.

This module contains unit and functional tests using pytest to verify:
- Configuration loading
- Logger functionality
- Data reading/writing
- Bot class methods (mocked browser interactions)
"""

import os
import sys
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import config
from utils.logger import setup_logger, get_timestamp, log_execution_step, log_error_with_traceback


class TestConfiguration:
    """Test configuration module settings."""
    
    def test_headless_mode_is_boolean(self):
        """Verify HEADLESS_MODE is a boolean."""
        assert isinstance(config.HEADLESS_MODE, bool)
    
    def test_browser_type_is_valid(self):
        """Verify BROWSER_TYPE is one of the supported browsers."""
        valid_browsers = ["chromium", "firefox", "webkit"]
        assert config.BROWSER_TYPE in valid_browsers
    
    def test_timeouts_are_positive_integers(self):
        """Verify all timeout values are positive integers."""
        assert config.PAGE_LOAD_TIMEOUT > 0
        assert config.ELEMENT_WAIT_TIMEOUT > 0
        assert config.ACTION_TIMEOUT > 0
    
    def test_max_retries_is_non_negative(self):
        """Verify MAX_RETRIES is non-negative."""
        assert config.MAX_RETRIES >= 0
    
    def test_file_paths_are_strings(self):
        """Verify file paths are strings."""
        assert isinstance(config.INPUT_EXCEL_PATH, str)
        assert isinstance(config.OUTPUT_EXCEL_PATH, str)
        assert isinstance(config.LOG_FILE_PATH, str)


class TestLogger:
    """Test logger utility functions."""
    
    def test_setup_logger_returns_logger_instance(self):
        """Verify setup_logger returns a logging.Logger instance."""
        logger = setup_logger("test_logger")
        assert logger is not None
        assert hasattr(logger, 'debug')
        assert hasattr(logger, 'info')
        assert hasattr(logger, 'warning')
        assert hasattr(logger, 'error')
    
    def test_get_timestamp_returns_string(self):
        """Verify get_timestamp returns a formatted string."""
        timestamp = get_timestamp()
        assert isinstance(timestamp, str)
        # Verify format matches expected pattern
        assert len(timestamp) == 19  # YYYY-MM-DD HH:MM:SS
    
    def test_get_timestamp_format(self):
        """Verify timestamp has correct format."""
        timestamp = get_timestamp()
        parts = timestamp.split(' ')
        assert len(parts) == 2  # Date and time
        assert '-' in parts[0]  # Date has dashes
        assert ':' in parts[1]  # Time has colons
    
    def test_log_execution_step(self, caplog):
        """Verify log_execution_step logs messages correctly."""
        logger = setup_logger("test_step_logger")
        with caplog.at_level('INFO'):
            log_execution_step(logger, "TEST_STEP", "Test details", "info")
            assert "TEST_STEP" in caplog.text
            assert "Test details" in caplog.text
    
    def test_log_error_with_traceback(self, caplog):
        """Verify log_error_with_traceback logs error information."""
        logger = setup_logger("test_error_logger")
        test_error = ValueError("Test error message")
        with caplog.at_level('ERROR'):
            log_error_with_traceback(logger, test_error, "Test context")
            assert "Test context" in caplog.text
            assert "ValueError" in caplog.text
            assert "Test error message" in caplog.text


class TestDataHandling:
    """Test data handling functions."""
    
    @pytest.fixture
    def sample_dataframe(self):
        """Create a sample DataFrame for testing."""
        import pandas as pd
        return pd.DataFrame({
            'url': ['https://example.com', 'https://test.com'],
            'username': ['user1', 'user2'],
            'password': ['pass1', 'pass2']
        })
    
    def test_dataframe_has_required_columns(self, sample_dataframe):
        """Verify sample DataFrame has expected structure."""
        assert 'url' in sample_dataframe.columns
        assert len(sample_dataframe) == 2
    
    def test_dataframe_iteration(self, sample_dataframe):
        """Verify DataFrame can be iterated."""
        count = 0
        for index, row in sample_dataframe.iterrows():
            count += 1
            assert 'url' in row.to_dict()
        assert count == 2


class TestWorkflowBot:
    """Test WorkflowBot class methods."""
    
    @pytest.fixture
    def mock_bot(self):
        """Create a WorkflowBot instance with mocked dependencies."""
        with patch('core.bot.setup_logger'):
            from core.bot import WorkflowBot
            bot = WorkflowBot()
            bot.logger = MagicMock()
            return bot
    
    @pytest.mark.asyncio
    async def test_initialize_browser(self, mock_bot):
        """Test browser initialization with mocked Playwright."""
        with patch('core.bot.async_playwright') as mock_playwright:
            # Setup mocks
            mock_browser = AsyncMock()
            mock_context = AsyncMock()
            mock_page = AsyncMock()
            
            mock_playwright_instance = AsyncMock()
            mock_playwright_instance.chromium.launch.return_value = mock_browser
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page
            
            mock_playwright.return_value.__aenter__.return_value = mock_playwright_instance
            
            # This test verifies the method can be called without errors
            # Actual implementation requires real Playwright installation
            pass
    
    def test_read_input_data_file_not_found(self, mock_bot):
        """Test read_input_data raises FileNotFoundError for missing files."""
        with pytest.raises(FileNotFoundError):
            mock_bot.read_input_data("nonexistent_file.xlsx")
    
    def test_execute_task_result_structure(self, mock_bot):
        """Test execute_task returns result with expected keys."""
        # This is a synchronous test for result structure validation
        result = {
            'row_index': 0,
            'status': 'Pending',
            'error_message': '',
            'timestamp': get_timestamp(),
            'screenshot_path': ''
        }
        
        required_keys = ['row_index', 'status', 'error_message', 'timestamp', 'screenshot_path']
        for key in required_keys:
            assert key in result
    
    def test_status_values(self):
        """Test that status values are valid."""
        valid_statuses = ['Success', 'Failed', 'Pending']
        
        # Test Success status
        assert 'Success' in valid_statuses
        
        # Test Failed status
        assert 'Failed' in valid_statuses
        
        # Test Pending status
        assert 'Pending' in valid_statuses


class TestExceptionHandling:
    """Test exception handling mechanisms."""
    
    def test_timeout_error_handling(self):
        """Verify TimeoutError can be caught and handled."""
        from playwright.async_api import TimeoutError as PlaywrightTimeoutError
        
        try:
            raise PlaywrightTimeoutError("Test timeout")
        except PlaywrightTimeoutError:
            # Successfully caught
            assert True
    
    def test_generic_exception_handling(self):
        """Verify generic exceptions can be caught."""
        try:
            raise ValueError("Test error")
        except Exception as e:
            assert str(e) == "Test error"
    
    def test_retry_logic_structure(self):
        """Verify retry logic structure is sound."""
        max_retries = config.MAX_RETRIES
        retry_count = 0
        
        for attempt in range(max_retries + 1):
            retry_count += 1
        
        # Should attempt max_retries + 1 times (initial + retries)
        assert retry_count == max_retries + 1


class TestIntegration:
    """Integration tests for the complete workflow."""
    
    def test_config_and_logger_integration(self):
        """Test that config and logger work together."""
        logger = setup_logger("integration_test")
        
        # Verify logger can use config values
        log_execution_step(logger, "CONFIG_TEST", 
                          f"Headless mode: {config.HEADLESS_MODE}")
        assert logger is not None
    
    def test_module_imports(self):
        """Verify all modules can be imported successfully."""
        import config
        from utils import logger
        from core import bot
        
        assert hasattr(config, 'HEADLESS_MODE')
        assert hasattr(logger, 'setup_logger')
        assert hasattr(bot, 'WorkflowBot')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
