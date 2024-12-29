"""
Base scraper for university STEM programs
"""
import time
import json
import logging
import re
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pandas as pd

class BaseScraper:
    def __init__(self, university_data: Dict, delay: int = 2):
        """
        Initialize base scraper
        
        Args:
            university_data: Dictionary containing university information
            delay: Delay between requests in seconds
        """
        self.university = university_data
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f"scraping_{self.university['name'].replace(' ', '_').lower()}.log"),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(self.university['name'])
        
        # Initialize browser state
        self._last_console_output = ""
    
    def make_request(self, url: str) -> Optional[BeautifulSoup]:
        """
        Make a request to URL with rate limiting and error handling
        
        Args:
            url: URL to request
            
        Returns:
            BeautifulSoup object or None if request fails
        """
        try:
            time.sleep(self.delay)  # Rate limiting
            response = self.session.get(url, timeout=30)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            self.logger.error(f"Error fetching {url}: {str(e)}")
            return None
    
    def find_program_urls(self, base_url: str) -> List[str]:
        """
        Find URLs for STEM programs
        
        Args:
            base_url: Base URL of the university's graduate programs
            
        Returns:
            List of program URLs
        """
        raise NotImplementedError("Subclasses must implement find_program_urls")
    
    def extract_program_info(self, url: str) -> Optional[Dict]:
        """
        Extract program information from program page
        
        Args:
            url: URL of the program page
            
        Returns:
            Dictionary containing program information or None if extraction fails
        """
        raise NotImplementedError("Subclasses must implement extract_program_info")
    
    def scrape_programs(self, base_url: str) -> List[Dict]:
        """
        Scrape all STEM programs for the university
        
        Args:
            base_url: Base URL for graduate programs
            
        Returns:
            List of program information dictionaries
        """
        programs = []
        program_urls = self.find_program_urls(base_url)
        
        for url in program_urls:
            self.logger.info(f"Scraping program at {url}")
            program_info = self.extract_program_info(url)
            if program_info:
                program_info['university_id'] = self.university['rank']
                program_info['university_name'] = self.university['name']
                programs.append(program_info)
        
        return programs
    
    def save_programs(self, programs: List[Dict], output_file: str):
        """
        Save scraped program information to file
        
        Args:
            programs: List of program dictionaries
            output_file: Path to output file
        """
        df = pd.DataFrame(programs)
        df.to_csv(output_file, index=False)
        self.logger.info(f"Saved {len(programs)} programs to {output_file}")
        
    def click_browser(self, selector: str) -> None:
        """Click an element in the browser using devinid"""
        try:
            if selector.startswith('devinid='):
                self.logger.info(f"Clicking element with {selector}")
                command = f'<click_browser box="{selector.split("=")[1]}"/>'
                # Execute the command (this is a placeholder - the actual execution
                # will be handled by the system)
                print(command)
            else:
                self.logger.error(f"Invalid selector format: {selector}")
        except Exception as e:
            self.logger.error(f"Error clicking browser element: {str(e)}")
            
    def get_browser_content(self) -> Optional[BeautifulSoup]:
        """Get the current browser content as BeautifulSoup"""
        try:
            # Get the current browser content
            print('<view_browser reload_window="True"/>')
            # Wait for content to load
            time.sleep(2)
            # Take a screenshot for debugging
            print('<screenshot_browser>\nChecking page content after loading\n</screenshot_browser>')
            # Get the HTML content
            print('<run_javascript_browser>document.documentElement.outerHTML</run_javascript_browser>')
            # The actual HTML content will be provided by the system in response to the above command
            # For now, we'll log that we're waiting for content
            self.logger.info("Waiting for browser content...")
            # The system will replace this return with actual parsed content
            return BeautifulSoup("<html><body>Waiting for content...</body></html>", 'html.parser')
        except Exception as e:
            self.logger.error(f"Error getting browser content: {str(e)}")
            return None
            
    def get_browser_console(self) -> str:
        """Get the browser console output"""
        try:
            # Initialize console output storage if not exists
            if not hasattr(self, '_last_console_output'):
                self._last_console_output = ""
            
            # Get console output directly
            print('<get_browser_console/>')
            # The system will set self._last_console_output
            
            if not self._last_console_output:
                self.logger.warning("Retrieved empty console output")
                # Try one more time after a short wait
                print('<wait for="browser" seconds="1"/>')
                print('<get_browser_console/>')
                # The system will set self._last_console_output again
            
            if self._last_console_output:
                self.logger.info(f"Successfully retrieved console output ({len(self._last_console_output)} bytes)")
            else:
                self.logger.warning("Console output still empty after retry")
                
            return self._last_console_output
            
        except Exception as e:
            self.logger.error(f"Error getting console output: {str(e)}")
            return ""
            
    def run_javascript(self, script: str) -> str:
        """
        Run JavaScript in the browser and return the result
        
        Args:
            script: JavaScript code to execute
            
        Returns:
            String result from JavaScript execution
        """
        try:
            self.logger.debug(f"Running JavaScript: {script[:200]}...")
            
            # Clear existing console messages
            print('<run_javascript_browser>window.__consoleMessages = [];</run_javascript_browser>')
            print('<wait for="browser" seconds="1"/>')
            
            # Add verification wrapper around the script
            wrapped_script = f'''
                (() => {{
                    try {{
                        console.log("JS_RESULT_START");
                        const result = (() => {{ {script} }})();
                        console.log(JSON.stringify(result));
                        console.log("JS_RESULT_END");
                        return result;
                    }} catch (error) {{
                        console.error("JavaScript execution error:", error);
                        console.log("JS_RESULT_START");
                        console.log(JSON.stringify({{ error: error.message }}));
                        console.log("JS_RESULT_END");
                        throw error;
                    }}
                }})();
            '''
            
            print(f'<run_javascript_browser>{wrapped_script}</run_javascript_browser>')
            print('<wait for="browser" seconds="1"/>')
            
            # Get console output and parse result
            console_output = self.get_browser_console()
            if console_output:
                start_idx = console_output.find("JS_RESULT_START")
                end_idx = console_output.find("JS_RESULT_END")
                if start_idx != -1 and end_idx != -1:
                    result = console_output[start_idx + len("JS_RESULT_START"):end_idx].strip()
                    try:
                        return json.loads(result)
                    except json.JSONDecodeError:
                        return result
            
            return ""
        except Exception as e:
            self.logger.error(f"Error running JavaScript: {str(e)}")
            return ""
    def wait_for_browser(self, seconds: int = 30, check_interval: int = 2, content_check: str = None) -> bool:
        """Wait for the browser with simplified state checking and reliable console capture
        
        Args:
            seconds: Maximum time to wait in seconds
            check_interval: How often to check browser state in seconds
            content_check: Optional CSS selector to verify specific content loaded
            
        Returns:
            bool: True if browser is ready, False if timeout occurred
        """
        total_waited = 0
        self.logger.info(f"Waiting up to {seconds} seconds for browser...")
        
        while total_waited < seconds:
            # Clear console and wait briefly
            print('<run_javascript_browser>window.__consoleMessages = [];</run_javascript_browser>')
            print('<wait for="browser" seconds="1"/>')
            
            # Check basic page state
            print('''<run_javascript_browser>
            (() => {
                const state = {
                    readyState: document.readyState,
                    url: window.location.href,
                    bodyLength: document.body.innerHTML.length,
                    title: document.title,
                    hasError: !!document.querySelector('.error-message, .error'),
                    success: false,
                    errors: []
                };
                
                if (state.readyState !== 'complete') state.errors.push('Document not complete');
                if (state.bodyLength === 0) state.errors.push('Empty body');
                
                // Check for specific content if requested
                const contentSelector = '${content_check}';
                if (contentSelector && contentSelector !== 'None') {
                    const elements = document.querySelectorAll(contentSelector);
                    if (elements.length === 0) {
                        state.errors.push('Required content not found');
                    } else {
                        const visible = Array.from(elements).some(el => 
                            window.getComputedStyle(el).display !== 'none' &&
                            window.getComputedStyle(el).visibility !== 'hidden'
                        );
                        if (!visible) state.errors.push('Required content not visible');
                    }
                }
                
                state.success = (
                    state.readyState === 'complete' &&
                    state.bodyLength > 0 &&
                    state.errors.length === 0
                );
                
                console.log("BROWSER_STATE:" + JSON.stringify(state));
            })();
            </run_javascript_browser>''')
            
            # Get console output
            print('<wait for="browser" seconds="1"/>')
            console_output = self.get_browser_console()
            
            if console_output:
                try:
                    # Parse browser state
                    state_marker = "BROWSER_STATE:"
                    if state_marker in console_output:
                        state_json = console_output.split(state_marker)[1].split("\n")[0].strip()
                        state_data = json.loads(state_json)
                        
                        if state_data.get('success', False):
                            self.logger.info(f"Browser ready after {total_waited} seconds")
                            return True
                        else:
                            self.logger.debug(f"Browser not ready: {state_data.get('errors', [])}")
                    else: 
                        self.logger.warning("Could not find browser state in console output")
                except Exception as e:
                    self.logger.error(f"Error checking browser state: {str(e)}")
            
            # Take screenshot and wait
            if total_waited >= seconds / 2:
                print('<screenshot_browser>Checking page state during wait</screenshot_browser>')
            
            print(f'<wait for="browser" seconds="{check_interval}"/>')
            total_waited += check_interval
        
        self.logger.warning(f"Browser wait timeout after {seconds} seconds")
        return False
        
    def parse_console_json(self, console_output: str, start_marker: str = None, end_marker: str = None) -> List[Dict]:
        """
        Parse JSON data from browser console output with optional markers
        
        Args:
            console_output: Raw console output string
            start_marker: Optional marker indicating start of JSON data
            end_marker: Optional marker indicating end of JSON data
            
        Returns:
            List of dictionaries parsed from JSON in console output
        """
        try:
            if not console_output:
                self.logger.warning("Empty console output")
                return []
                
            # If markers are provided, extract content between them
            if start_marker and end_marker:
                start_idx = console_output.find(start_marker)
                end_idx = console_output.find(end_marker)
                
                if start_idx != -1 and end_idx != -1:
                    json_text = console_output[start_idx + len(start_marker):end_idx].strip()
                    try:
                        data = json.loads(json_text)
                        return data if isinstance(data, list) else [data]
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Failed to parse marked JSON: {e}")
                        self.logger.debug(f"JSON text: {json_text}")
                        
            # Fall back to finding any JSON-like strings
            json_matches = re.findall(r'\{[^{}]*\}|\[[^\[\]]*\]', console_output)
            
            for match in json_matches:
                try:
                    data = json.loads(match)
                    if isinstance(data, (list, dict)):
                        return data if isinstance(data, list) else [data]
                except json.JSONDecodeError:
                    continue
                    
            self.logger.warning("No valid JSON found in console output")
            self.logger.debug(f"Console output: {repr(console_output)}")
            return []
            
        except Exception as e:
            self.logger.error(f"Error parsing console JSON: {str(e)}")
            self.logger.debug(f"Console output: {repr(console_output)}")
            return []
