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
        """Get the browser console output with retries and verification"""
        max_retries = 3
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                # Clear console before attempting to get output
                print('<run_javascript_browser>console.clear();</run_javascript_browser>')
                time.sleep(1)  # Wait for console to clear
                
                # Add a marker to verify console access
                marker = f"CONSOLE_CHECK_{attempt}_{int(time.time())}"
                print(f'<run_javascript_browser>console.log("{marker}");</run_javascript_browser>')
                time.sleep(1)  # Wait for log
                
                # Get console output
                print('<get_browser_console/>')
                time.sleep(retry_delay)  # Wait for output capture
                
                # The actual console output will be provided by the system
                # This is just a placeholder that will be replaced
                console_output = "Result will be provided by the system"
                
                if console_output and marker in console_output:
                    self.logger.info(f"Console output captured successfully on attempt {attempt + 1}")
                    return console_output
                
                self.logger.warning(f"Console marker not found in output (attempt {attempt + 1})")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    
            except Exception as e:
                self.logger.error(f"Error getting console output (attempt {attempt + 1}): {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
        
        self.logger.error("Failed to get console output after all retries")
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
            self.logger.info("Running JavaScript in browser")
            print(f'<run_javascript_browser>{script}</run_javascript_browser>')
            # The actual result will be provided by the system
            return "Result will be provided by the system"
        except Exception as e:
            self.logger.error(f"Error running JavaScript: {str(e)}")
            return ""
    def wait_for_browser(self, seconds: int, check_interval: int = 2, content_check: str = None) -> bool:
        """Wait for the browser with enhanced state verification
        
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
            # Check browser state with enhanced verification
            print('''<run_javascript_browser>
            function checkNetworkIdle() {
                return new Promise((resolve) => {
                    if (window.performance && window.performance.getEntriesByType) {
                        const resources = window.performance.getEntriesByType('resource');
                        const pendingResources = resources.filter(r => !r.responseEnd);
                        resolve(pendingResources.length === 0);
                    } else {
                        resolve(true);  // Can't check network, assume idle
                    }
                });
            }
            
            async function checkBrowserState() {
                const networkIdle = await checkNetworkIdle();
                const state = {
                    readyState: document.readyState,
                    url: window.location.href,
                    bodyLength: document.body.innerHTML.length,
                    title: document.title,
                    networkIdle: networkIdle,
                    hasError: !!document.querySelector('.error-message, .error'),
                    contentCheck: null
                };
                
                if ('CONTENT_CHECK') {
                    const element = document.querySelector('CONTENT_CHECK');
                    state.contentCheck = {
                        found: !!element,
                        visible: element ? window.getComputedStyle(element).display !== 'none' : false,
                        text: element ? element.textContent : null
                    };
                }
                
                console.log("Browser State Check:", JSON.stringify(state));
            }
            
            checkBrowserState();
            </run_javascript_browser>'''.replace('CONTENT_CHECK', content_check if content_check else 'body'))
            
            # Wait for check interval
            print(f'<wait for="browser" seconds="{check_interval}"/>')
            total_waited += check_interval
            
            # Get console output to verify state
            print('<get_browser_console/>')
            console_output = self.get_browser_console()
            
            if console_output:
                try:
                    # Look for JSON state object in console output
                    state_start = console_output.find('"Browser State Check":')
                    if state_start != -1:
                        state_json = console_output[state_start:].split('\n')[0]
                        state_data = json.loads(state_json.replace('"Browser State Check":', '').strip())
                        
                        # Check for error conditions
                        if state_data.get('hasError'):
                            self.logger.error("Page error detected")
                            return False
                            
                        # Verify all conditions are met
                        conditions_met = (
                            state_data.get('readyState') == 'complete' and
                            state_data.get('bodyLength', 0) > 0 and
                            state_data.get('networkIdle', True) and
                            (not content_check or 
                             (state_data.get('contentCheck', {}).get('found') and 
                              state_data.get('contentCheck', {}).get('visible')))
                        )
                        
                        if conditions_met:
                            self.logger.info(f"Browser ready after {total_waited} seconds")
                            return True
                        else:
                            self.logger.debug(f"Still waiting: {state_data}")
                except Exception as e:
                    self.logger.error(f"Error parsing browser state: {str(e)}")
            
            # Take screenshot if having issues
            if total_waited >= seconds / 2:
                print('<screenshot_browser>\nChecking page state during wait\n</screenshot_browser>')
            
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
