"""
Main automation controller for the Automated Web Testing & Workflow Bot.

This module contains the core bot logic using Playwright to:
- Read task queues from Excel files
- Navigate to web forms and input data
- Handle exceptions gracefully without crashing
- Write execution results back to Excel
"""

import asyncio
import os
from datetime import datetime
from typing import Dict, List, Optional, Any

import pandas as pd
from playwright.async_api import async_playwright, Page, Browser, BrowserContext, TimeoutError as PlaywrightTimeoutError

import config
from utils.logger import setup_logger, log_execution_step, log_error_with_traceback, get_timestamp


class WorkflowBot:
    """
    Main bot class for automating web workflows and testing.
    
    This class handles browser automation, data processing, and error management
    for batch processing of web tasks defined in Excel spreadsheets.
    """
    
    def __init__(self):
        """Initialize the bot with logger and configuration."""
        self.logger = setup_logger("workflow_bot")
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.results: List[Dict[str, Any]] = []
        
    async def initialize_browser(self) -> None:
        """
        Initialize the Playwright browser instance.
        
        Sets up the browser with configured settings (headless mode, timeouts).
        """
        log_execution_step(self.logger, "BROWSER_INIT", 
                          f"Initializing {config.BROWSER_TYPE} browser")
        
        try:
            playwright = await async_playwright().start()
            
            # Launch browser with configured settings
            self.browser = await playwright.chromium.launch(
                headless=config.HEADLESS_MODE,
                timeout=config.PAGE_LOAD_TIMEOUT
            )
            
            # Create browser context with default viewport
            self.context = await self.browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            
            # Set default timeout for all operations
            self.context.set_default_timeout(config.ELEMENT_WAIT_TIMEOUT)
            
            # Create page
            self.page = await self.context.new_page()
            
            log_execution_step(self.logger, "BROWSER_INIT", 
                              "Browser initialized successfully", level="info")
            
        except Exception as e:
            log_error_with_traceback(self.logger, e, "Failed to initialize browser")
            raise
    
    async def close_browser(self) -> None:
        """Close the browser and clean up resources."""
        try:
            if self.page:
                await self.page.close()
            if self.context:
                await self.context.close()
            if self.browser:
                await self.browser.close()
            log_execution_step(self.logger, "BROWSER_CLOSE", 
                              "Browser closed successfully")
        except Exception as e:
            log_error_with_traceback(self.logger, e, "Error closing browser")
    
    def read_input_data(self, file_path: str) -> pd.DataFrame:
        """
        Read task queue from Excel file.
        
        Args:
            file_path: Path to the input Excel file
            
        Returns:
            DataFrame containing the task queue
            
        Raises:
            FileNotFoundError: If the input file doesn't exist
            ValueError: If the file is empty or has no valid columns
        """
        log_execution_step(self.logger, "DATA_LOAD", 
                          f"Reading input data from {file_path}")
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Input file not found: {file_path}")
        
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            
            if df.empty:
                raise ValueError("Input Excel file is empty")
            
            log_execution_step(self.logger, "DATA_LOAD", 
                              f"Loaded {len(df)} rows from input file")
            return df
            
        except Exception as e:
            log_error_with_traceback(self.logger, e, "Failed to read input data")
            raise
    
    async def navigate_to_page(self, url: str) -> bool:
        """
        Navigate to a target URL with error handling.
        
        Args:
            url: Target URL to navigate to
            
        Returns:
            True if navigation successful, False otherwise
        """
        try:
            log_execution_step(self.logger, "NAVIGATION", f"Navigating to {url}")
            await self.page.goto(url, timeout=config.PAGE_LOAD_TIMEOUT, wait_until='networkidle')
            log_execution_step(self.logger, "NAVIGATION", "Navigation successful", level="info")
            return True
        except PlaywrightTimeoutError as e:
            log_error_with_traceback(self.logger, e, f"Navigation timeout to {url}")
            return False
        except Exception as e:
            log_error_with_traceback(self.logger, e, f"Navigation failed to {url}")
            return False
    
    async def fill_form_field(self, selector: str, value: str, 
                             field_name: str = "Field") -> bool:
        """
        Fill a form field with retry logic.
        
        Args:
            selector: CSS selector for the input field
            value: Value to enter
            field_name: Human-readable name for logging
            
        Returns:
            True if successful, False otherwise
        """
        for attempt in range(config.MAX_RETRIES + 1):
            try:
                await self.page.fill(selector, value, timeout=config.ACTION_TIMEOUT)
                log_execution_step(self.logger, "FORM_FILL", 
                                  f"{field_name} filled successfully", level="info")
                return True
            except PlaywrightTimeoutError as e:
                if attempt == config.MAX_RETRIES:
                    log_error_with_traceback(self.logger, e, 
                                            f"Failed to fill {field_name} after {config.MAX_RETRIES} retries")
                    return False
                log_execution_step(self.logger, "FORM_FILL", 
                                  f"Retry {attempt + 1} for {field_name}", level="warning")
                await asyncio.sleep(config.RETRY_DELAY / 1000)
            except Exception as e:
                log_error_with_traceback(self.logger, e, 
                                        f"Error filling {field_name}")
                return False
        return False
    
    async def click_element(self, selector: str, element_name: str = "Element") -> bool:
        """
        Click an element with retry logic.
        
        Args:
            selector: CSS selector for the element
            element_name: Human-readable name for logging
            
        Returns:
            True if successful, False otherwise
        """
        for attempt in range(config.MAX_RETRIES + 1):
            try:
                await self.page.click(selector, timeout=config.ACTION_TIMEOUT)
                log_execution_step(self.logger, "ELEMENT_CLICK", 
                                  f"{element_name} clicked successfully", level="info")
                return True
            except PlaywrightTimeoutError as e:
                if attempt == config.MAX_RETRIES:
                    log_error_with_traceback(self.logger, e, 
                                            f"Failed to click {element_name} after {config.MAX_RETRIES} retries")
                    return False
                log_execution_step(self.logger, "ELEMENT_CLICK", 
                                  f"Retry {attempt + 1} for {element_name}", level="warning")
                await asyncio.sleep(config.RETRY_DELAY / 1000)
            except Exception as e:
                log_error_with_traceback(self.logger, e, 
                                        f"Error clicking {element_name}")
                return False
        return False
    
    async def extract_text(self, selector: str, field_name: str = "Field") -> Optional[str]:
        """
        Extract text content from an element.
        
        Args:
            selector: CSS selector for the element
            field_name: Human-readable name for logging
            
        Returns:
            Extracted text or None if failed
        """
        try:
            text = await self.page.text_content(selector, timeout=config.ACTION_TIMEOUT)
            log_execution_step(self.logger, "TEXT_EXTRACT", 
                              f"{field_name} extracted successfully", level="info")
            return text
        except PlaywrightTimeoutError as e:
            log_error_with_traceback(self.logger, e, 
                                    f"Failed to extract {field_name}")
            return None
        except Exception as e:
            log_error_with_traceback(self.logger, e, 
                                    f"Error extracting {field_name}")
            return None
    
    async def take_screenshot(self, task_id: str) -> Optional[str]:
        """
        Take a screenshot on error for debugging.
        
        Args:
            task_id: Unique identifier for the task
            
        Returns:
            Screenshot file path or None if failed
        """
        if not config.SAVE_SCREENSHOTS_ON_ERROR:
            return None
        
        try:
            # Create screenshots directory if it doesn't exist
            if not os.path.exists(config.SCREENSHOT_DIR):
                os.makedirs(config.SCREENSHOT_DIR, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = os.path.join(
                config.SCREENSHOT_DIR, 
                f"error_task_{task_id}_{timestamp}.png"
            )
            
            await self.page.screenshot(path=screenshot_path)
            log_execution_step(self.logger, "SCREENSHOT", 
                              f"Screenshot saved: {screenshot_path}")
            return screenshot_path
            
        except Exception as e:
            log_error_with_traceback(self.logger, e, "Failed to take screenshot")
            return None
    
    async def execute_task(self, row_data: Dict[str, Any], 
                          row_index: int) -> Dict[str, Any]:
        """
        Execute a single task/row from the input data.
        
        Args:
            row_data: Dictionary containing row data from Excel
            row_index: Row index for tracking
            
        Returns:
            Dictionary with execution results
        """
        task_id = str(row_index)
        result = {
            'row_index': row_index,
            'status': 'Pending',
            'error_message': '',
            'timestamp': get_timestamp(),
            'screenshot_path': ''
        }
        
        try:
            log_execution_step(self.logger, "TASK_START", 
                              f"Executing task at row {row_index}")
            
            # Get target URL from row data (assumes 'url' column exists)
            target_url = row_data.get('url', config.BASE_URL)
            
            # Navigate to target page
            if not await self.navigate_to_page(target_url):
                result['status'] = 'Failed'
                result['error_message'] = 'Navigation failed'
                result['screenshot_path'] = await self.take_screenshot(task_id)
                return result
            
            # Process form fields dynamically based on available columns
            # Skip 'url', 'expected_result', and result columns
            skip_columns = ['url', 'expected_result', 'status', 'error_message', 
                           'timestamp', 'screenshot_path']
            
            for column, value in row_data.items():
                if column.lower() in skip_columns or pd.isna(value):
                    continue
                
                # Try to find and fill elements based on column name
                # This is a generic approach - customize selectors based on your target site
                selector = f"[name='{column}'], [id='{column}'], .{column}"
                
                if not await self.fill_form_field(selector, str(value), column):
                    # Try clicking if it's a button-like element
                    if 'button' in column.lower() or 'submit' in column.lower():
                        if not await self.click_element(selector, column):
                            result['status'] = 'Failed'
                            result['error_message'] = f'Failed to interact with {column}'
                            result['screenshot_path'] = await self.take_screenshot(task_id)
                            return result
                    else:
                        result['status'] = 'Failed'
                        result['error_message'] = f'Failed to fill {column}'
                        result['screenshot_path'] = await self.take_screenshot(task_id)
                        return result
            
            # Small delay to allow page processing
            await asyncio.sleep(1)
            
            result['status'] = 'Success'
            log_execution_step(self.logger, "TASK_COMPLETE", 
                              f"Task at row {row_index} completed successfully", level="info")
            
        except PlaywrightTimeoutError as e:
            result['status'] = 'Failed'
            result['error_message'] = f'Timeout: {str(e)}'
            result['screenshot_path'] = await self.take_screenshot(task_id)
            log_error_with_traceback(self.logger, e, 
                                    f"Task {row_index} failed with timeout")
            
        except Exception as e:
            result['status'] = 'Failed'
            result['error_message'] = str(e)
            result['screenshot_path'] = await self.take_screenshot(task_id)
            log_error_with_traceback(self.logger, e, 
                                    f"Task {row_index} failed with error")
        
        return result
    
    async def run_workflow(self, input_file: str = None, 
                          output_file: str = None) -> pd.DataFrame:
        """
        Run the complete workflow: read input, execute tasks, write output.
        
        Args:
            input_file: Path to input Excel file (default from config)
            output_file: Path to output Excel file (default from config)
            
        Returns:
            DataFrame with execution results
        """
        input_file = input_file or config.INPUT_EXCEL_PATH
        output_file = output_file or config.OUTPUT_EXCEL_PATH
        
        log_execution_step(self.logger, "WORKFLOW_START", 
                          f"Starting workflow with input: {input_file}")
        
        try:
            # Initialize browser
            await self.initialize_browser()
            
            # Read input data
            df = self.read_input_data(input_file)
            
            # Process each row
            for index, row in df.iterrows():
                row_data = row.to_dict()
                result = await self.execute_task(row_data, index)
                self.results.append(result)
                
                # Update DataFrame with result
                df.at[index, 'status'] = result['status']
                df.at[index, 'error_message'] = result['error_message']
                df.at[index, 'timestamp'] = result['timestamp']
                df.at[index, 'screenshot_path'] = result['screenshot_path']
                
                log_execution_step(self.logger, "PROGRESS", 
                                  f"Processed {index + 1}/{len(df)} rows")
            
            # Write results to output file
            df.to_excel(output_file, index=False, engine='openpyxl')
            log_execution_step(self.logger, "WORKFLOW_COMPLETE", 
                              f"Results written to {output_file}", level="info")
            
            # Summary statistics
            success_count = len([r for r in self.results if r['status'] == 'Success'])
            fail_count = len([r for r in self.results if r['status'] == 'Failed'])
            log_execution_step(self.logger, "SUMMARY", 
                              f"Total: {len(self.results)}, Success: {success_count}, Failed: {fail_count}")
            
            return df
            
        finally:
            # Always close browser
            await self.close_browser()


async def main():
    """Main entry point for running the bot."""
    bot = WorkflowBot()
    await bot.run_workflow()


if __name__ == "__main__":
    asyncio.run(main())
