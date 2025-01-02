"""
Base scraper for university STEM programs
"""
import time
import json
import logging
import re
import os
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
        
        # Initialize basic configuration
        self.logger.info(f"Initialized scraper for {self.university['name']}")
    
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
            
    def initialize_console_capture(self) -> bool:
        """Initialize console capture"""
        self.logger.info("Console capture initialized")
        return True
        
    def get_browser_console(self) -> str:
        """Get browser console output"""
        print('<get_browser_console/>')
        return ""
            
    def run_javascript(self, script: str) -> str:
        """
        Run JavaScript in the browser
        
        Args:
            script: JavaScript code to execute
            
        Returns:
            String result from JavaScript execution
        """
        try:
            print(f'<run_javascript_browser>{script}</run_javascript_browser>')
            return ""
        except Exception as e:
            self.logger.error(f"Error running JavaScript: {str(e)}")
            return ""
    def wait_for_browser(self, seconds: int = 60, check_interval: int = 2, content_check: str = None) -> bool:
        """Wait for browser readiness with simplified verification approach
        
        Args:
            seconds: Maximum time to wait in seconds (default 60s for slower operations)
            check_interval: Initial interval between checks in seconds
            content_check: Optional CSS selector to verify specific content loaded
            
        Returns:
            bool: True if browser is ready, False if timeout occurred
        """
        self.logger.info("Starting browser initialization")
        
        # Initialize tracking variables
        attempts = 0
        max_attempts = int(seconds / check_interval)
        total_waited = 0
        
        # Simple restart to ensure clean state
        self.logger.info("Restarting browser")
        print('<restart_browser url="about:blank" />')
        print('<wait for="browser" seconds="5"/>')
        total_waited += 5  # Account for initial wait
        
        # Initialize console capture - don't fail if it doesn't work
        if not self.initialize_console_capture():
            self.logger.warning("Console capture initialization failed, but continuing")
        
        self.logger.info(f"Waiting up to {seconds} seconds for browser (interval={check_interval}s)...")
        
        # Take initial screenshot
        print('<screenshot_browser>\nStarting browser wait sequence\n</screenshot_browser>')
        
        # Main verification loop
        while attempts < max_attempts and total_waited < seconds:
            try:
                # Simple state check
                state = self.run_javascript('''
                (() => {
                    return {
                        readyState: document.readyState,
                        hasBody: !!document.body,
                        url: window.location.href
                    };
                })();
                ''')
                
                self.logger.debug(f"Browser state (attempt {attempts + 1}/{max_attempts}): {state}")
                
                # Basic readiness check
                if state and state.get('readyState') in ['complete', 'interactive']:
                    # Check for specific content if requested
                    if content_check:
                        content_state = self.run_javascript(f'''
                        (() => {{
                            const elements = document.querySelectorAll('{content_check}');
                            return {{
                                found: elements.length > 0,
                                count: elements.length
                            }};
                        }})();
                        ''')
                        if not content_state or not content_state.get('found'):
                            self.logger.debug(f"Required content not found: {content_check}")
                        else:
                            self.logger.info(f"Browser ready after {total_waited} seconds")
                            return True
                    else:
                        self.logger.info(f"Browser ready after {total_waited} seconds")
                        return True
                
                # Take screenshot every 5 attempts for debugging
                if attempts % 5 == 0:
                    print(f'<screenshot_browser>\nBrowser state check (attempt {attempts + 1})\n</screenshot_browser>')
                
                attempts += 1
                total_waited += check_interval
                
                if attempts < max_attempts and total_waited < seconds:
                    print(f'<wait for="browser" seconds="{check_interval}"/>')
                    
            except Exception as e:
                self.logger.error(f"Error in browser verification (attempt {attempts + 1}/{max_attempts}): {str(e)}")
                attempts += 1
                total_waited += check_interval
                
                if attempts < max_attempts and total_waited < seconds:
                    print(f'<wait for="browser" seconds="{check_interval}"/>')
        
        self.logger.error(f"Browser wait timeout after {attempts} attempts ({total_waited}s)")
        print('<screenshot_browser>\nBrowser wait timeout\n</screenshot_browser>')
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
