# Automated Web Testing & Workflow Bot

A production-ready Python application for automating repetitive web workflows and functional testing. This bot reads input queues from Excel sheets, executes browser interactions using Playwright, handles exceptions gracefully, and writes execution results back to Excel reports.

## Features

- **Excel-Based Task Queue**: Read test cases and workflow parameters directly from Excel spreadsheets
- **Playwright Browser Automation**: Modern, reliable cross-browser automation (Chromium, Firefox, WebKit)
- **Graceful Exception Handling**: Failed tasks don't crash the entire run; errors are logged and flagged
- **Comprehensive Logging**: Timestamped execution logs with error traces and screenshots
- **Retry Logic**: Automatic retries for transient failures with configurable delay
- **Audit Trail**: Complete execution reports with success/failure status and timestamps
- **Headless Mode**: Run automation in background without visible browser UI

## Project Structure

```
├── config.py                 # Configuration settings
├── requirements.txt          # Python dependencies
├── core/
│   └── bot.py               # Main automation controller
├── utils/
│   └── logger.py            # Logging utility
├── tests/
│   └── test_workflow.py     # Unit and functional tests
├── logs/                     # Execution logs (auto-created)
├── screenshots/              # Error screenshots (auto-created)
├── input_data.xlsx          # Input task queue (create your own)
└── output_report.xlsx       # Execution results (auto-generated)
```

## Installation

### 1. Clone or Download the Repository

```bash
cd /path/to/project
```

### 2. Create Virtual Environment (Recommended)

```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Playwright Browsers

```bash
playwright install
```

This downloads the browser binaries (Chromium, Firefox, WebKit) needed for automation.

### 5. Install System Dependencies (Linux Only)

If running on a Linux server, you may need additional system packages:

```bash
# Ubuntu/Debian
sudo apt-get install -y libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 libasound2

# Or use Playwright's dependency installer
playwright install-deps
```

## Configuration

Edit `config.py` to customize the bot behavior:

```python
# Browser settings
HEADLESS_MODE = True          # Set to False for debugging
BROWSER_TYPE = "chromium"     # chromium, firefox, or webkit

# Timeouts (milliseconds)
PAGE_LOAD_TIMEOUT = 30000     # Page load timeout
ELEMENT_WAIT_TIMEOUT = 10000  # Element wait timeout
ACTION_TIMEOUT = 5000         # Action timeout

# File paths
INPUT_EXCEL_PATH = "input_data.xlsx"
OUTPUT_EXCEL_PATH = "output_report.xlsx"
LOG_FILE_PATH = "logs/bot_execution.log"

# Retry settings
MAX_RETRIES = 2               # Number of retry attempts
RETRY_DELAY = 1000            # Delay between retries (ms)

# Screenshot settings
SAVE_SCREENSHOTS_ON_ERROR = True
SCREENSHOT_DIR = "screenshots"
```

## Creating Input Excel File

Create an `input_data.xlsx` file with the following structure:

| url | username | password | email | other_field |
|-----|----------|----------|-------|-------------|
| https://example.com/login | user1 | pass123 | user1@test.com | value1 |
| https://example.com/register | user2 | pass456 | user2@test.com | value2 |

**Important**: 
- The `url` column is required and specifies the target page for each task
- Other columns should match the `name` or `id` attributes of form fields on your target website
- The bot will automatically skip columns named: `status`, `error_message`, `timestamp`, `screenshot_path`, `expected_result`

## Running the Bot

### Basic Execution

```bash
python core/bot.py
```

### Programmatic Usage

```python
import asyncio
from core.bot import WorkflowBot

async def main():
    bot = WorkflowBot()
    
    # Run with default config paths
    await bot.run_workflow()
    
    # Or specify custom paths
    await bot.run_workflow(
        input_file="custom_input.xlsx",
        output_file="custom_output.xlsx"
    )

asyncio.run(main())
```

### With Custom Configuration

```python
import config
from core.bot import WorkflowBot
import asyncio

# Override config values
config.HEADLESS_MODE = False  # Show browser for debugging
config.MAX_RETRIES = 3

async def main():
    bot = WorkflowBot()
    await bot.run_workflow()

asyncio.run(main())
```

## Output

After execution, the bot generates:

### 1. Output Excel Report (`output_report.xlsx`)

Contains all input data plus additional columns:
- `status`: Success or Failed
- `error_message`: Error details if failed
- `timestamp`: Execution timestamp
- `screenshot_path`: Path to screenshot if error occurred

### 2. Execution Log (`logs/bot_execution.log`)

Detailed log file with:
- Timestamps for all operations
- Navigation events
- Form interactions
- Errors and exceptions
- Summary statistics

### 3. Screenshots (`screenshots/`)

PNG screenshots captured when tasks fail (if enabled in config).

## Running Tests

```bash
# Install pytest-asyncio for async tests
pip install pytest-asyncio

# Run all tests
pytest tests/test_workflow.py -v

# Run specific test class
pytest tests/test_workflow.py::TestConfiguration -v

# Run with coverage
pytest tests/test_workflow.py --cov=core --cov=utils --cov=config
```

## Docker Deployment

For production deployment, create a `Dockerfile`:

```dockerfile
FROM mcr.microsoft.com/playwright/python:v1.40.0-jammy

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

# Install any additional system dependencies if needed
RUN playwright install-deps

CMD ["python", "core/bot.py"]
```

Build and run:

```bash
docker build -t workflow-bot .
docker run -v $(pwd)/input_data.xlsx:/app/input_data.xlsx workflow-bot
```

## CI/CD Integration

### GitHub Actions Example

Create `.github/workflows/automation.yml`:

```yaml
name: Web Automation

on:
  schedule:
    - cron: '0 2 * * *'  # Run daily at 2 AM
  workflow_dispatch:

jobs:
  automate:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        playwright install
    
    - name: Run automation
      run: python core/bot.py
    
    - name: Upload results
      uses: actions/upload-artifact@v3
      with:
        name: automation-results
        path: |
          output_report.xlsx
          logs/
          screenshots/
```

## Customization Guide

### Adding Custom Selectors

Modify the `execute_task` method in `core/bot.py` to use site-specific selectors:

```python
# Instead of generic selector
selector = f"[name='{column}'], [id='{column}'], .{column}"

# Use specific selectors for your site
selectors = {
    'username': '#login-username',
    'password': '#login-password',
    'submit_button': '.btn-submit'
}
selector = selectors.get(column, f"[name='{column}']")
```

### Adding Authentication

Add login logic before processing tasks:

```python
async def login(self, username: str, password: str) -> bool:
    await self.navigate_to_page(config.LOGIN_URL)
    await self.fill_form_field('#username', username)
    await self.fill_form_field('#password', password)
    return await self.click_element('#login-btn')
```

### Adding Data Extraction

Use the `extract_text` method to scrape data:

```python
result_text = await self.extract_text('.result-class', 'Result')
row_data['extracted_value'] = result_text
```

## Troubleshooting

### Common Issues

1. **"Browser doesn't exist" error**
   ```bash
   playwright install
   ```

2. **Timeout errors**
   - Increase timeout values in `config.py`
   - Check network connectivity
   - Verify target URL is accessible

3. **Element not found errors**
   - Inspect the webpage to verify selectors
   - Run with `HEADLESS_MODE = False` to debug visually
   - Check if elements are inside iframes

4. **Excel file locked**
   - Close the Excel file before running the bot
   - Ensure no other process is accessing it

### Debug Mode

For debugging, modify `config.py`:

```python
HEADLESS_MODE = False  # Show browser window
SAVE_SCREENSHOTS_ON_ERROR = True
```

Then run the bot and watch the browser interactions in real-time.

## Best Practices

1. **Version Control**: Keep input Excel files out of version control if they contain sensitive data
2. **Secrets Management**: Use environment variables for credentials instead of Excel files
3. **Rate Limiting**: Add delays between requests to avoid overwhelming target servers
4. **Error Monitoring**: Review logs regularly to identify recurring issues
5. **Regular Updates**: Keep Playwright and dependencies updated for security patches

## License

MIT License - See LICENSE file for details.

## Support

For issues and feature requests, please open an issue on the project repository.
