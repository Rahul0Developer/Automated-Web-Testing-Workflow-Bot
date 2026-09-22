"""
Configuration module for the Automated Web Testing & Workflow Bot.

This module manages all configurable parameters including:
- Browser settings (headless mode)
- Target URLs
- Timeout limits
- File paths
"""

# Browser Configuration
HEADLESS_MODE = True  # Set to False for debugging with visible browser
BROWSER_TYPE = "chromium"  # Options: chromium, firefox, webkit

# Timeout Configuration (in milliseconds)
PAGE_LOAD_TIMEOUT = 30000  # 30 seconds
ELEMENT_WAIT_TIMEOUT = 10000  # 10 seconds
ACTION_TIMEOUT = 5000  # 5 seconds

# Target Web Application Configuration
BASE_URL = "https://example.com"  # Replace with your target URL
LOGIN_URL = f"{BASE_URL}/login"

# File Paths
INPUT_EXCEL_PATH = "input_data.xlsx"
OUTPUT_EXCEL_PATH = "output_report.xlsx"
LOG_FILE_PATH = "logs/bot_execution.log"

# Retry Configuration
MAX_RETRIES = 2  # Number of retry attempts for failed actions
RETRY_DELAY = 1000  # Delay between retries in milliseconds

# Screenshot Settings
SAVE_SCREENSHOTS_ON_ERROR = True
SCREENSHOT_DIR = "screenshots"
