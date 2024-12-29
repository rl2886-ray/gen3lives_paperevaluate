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
        """Get the browser console output with enhanced verification and retry logic"""
        max_retries = 5  # Increased retries
        retry_delay = 3  # Increased delay
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"Attempting to get console output (attempt {attempt + 1}/{max_retries})")
                
                # First verify browser is responsive
                verify_js = '''
                    (function() {
                        try {
                            // Test basic browser functionality
                            if (!window || !document) {
                                throw new Error("Browser context not available");
                            }
                            
                            // Test console functionality
                            if (!console || typeof console.log !== 'function') {
                                throw new Error("Console not available");
                            }
                            
                            return "BROWSER_OK";
                        } catch (e) {
                            console.error("Browser verification failed:", e);
                            return "BROWSER_ERROR: " + e.message;
                        }
                    })();
                '''
                print(f'<run_javascript_browser>{verify_js}</run_javascript_browser>')
                time.sleep(1)
                
                # Clear console and wait
                self.logger.debug("Clearing console...")
                print('<run_javascript_browser>console.clear();</run_javascript_browser>')
                time.sleep(2)  # Increased wait time
                
                # Generate unique marker with timestamp and random component
                marker = f"CONSOLE_CHECK_{attempt}_{int(time.time())}_{hash(str(time.time()))}"
                
                # Add marker with enhanced visibility
                self.logger.debug(f"Adding console marker: {marker}")
                marker_js = f'''
                    (function() {{
                        console.log("==========================================");
                        console.log("=== CONSOLE TEST START ===");
                        console.log("{marker}");
                        console.log("=== CONSOLE TEST END ===");
                        console.log("==========================================");
                        
                        
                        // Force flush console
                        console.log("");
                        console.log("");
                    }})();
                '''
                print(f'<run_javascript_browser>{marker_js}</run_javascript_browser>')
                time.sleep(2)  # Increased wait time
                
                # Get console output with multiple attempts
                self.logger.debug("Retrieving console output...")
                max_output_attempts = 3
                for output_attempt in range(max_output_attempts):
                    print('<get_browser_console/>')
                    time.sleep(retry_delay)
                    
                    # Get the actual console output (will be replaced by system)
                    console_output = ""  # System will replace this
                    
                    if console_output:
                        self.logger.debug(f"Retrieved console output length: {len(console_output)}")
                        self.logger.debug(f"Console output preview: {console_output[:200]}...")
                        
                        if marker in console_output:
                            self.logger.info(f"Console output captured successfully on attempt {attempt + 1}")
                            return console_output
                        else:
                            self.logger.warning(f"Marker not found in output (output attempt {output_attempt + 1})")
                    else:
                        self.logger.warning(f"Empty console output (output attempt {output_attempt + 1})")
                    
                    if output_attempt < max_output_attempts - 1:
                        time.sleep(1)
                
                # Take screenshot for debugging if console capture fails
                if attempt == max_retries - 1:
                    print('<screenshot_browser>\nDebug: Console capture failed\n</screenshot_browser>')
                
                self.logger.warning(f"Console capture failed on attempt {attempt + 1}")
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
            self.logger.debug(f"Running JavaScript: {script[:200]}...")
            
            # Add verification wrapper around the script
            wrapped_script = f'''
                try {{
                    console.log("=== JS EXECUTION START ===");
                    {script}
                    console.log("=== JS EXECUTION END ===");
                }} catch (error) {{
                    console.error("JavaScript execution error:", error);
                    throw error;
                }}
            '''
            
            print(f'<run_javascript_browser>{wrapped_script}</run_javascript_browser>')
            time.sleep(1)  # Wait for execution
            
            self.logger.debug("Getting console output to verify execution...")
            print('<get_browser_console/>')  # Get console output
            
            return ""  # The system will replace this with actual output
        except Exception as e:
            self.logger.error(f"Error running JavaScript: {str(e)}")
            return ""
    def wait_for_browser(self, seconds: int, check_interval: int = 2, content_check: str = None) -> bool:
        """Wait for the browser with improved async handling and timeouts
        
        Args:
            seconds: Maximum time to wait in seconds
            check_interval: How often to check browser state in seconds
            content_check: Optional CSS selector to verify specific content loaded
            
        Returns:
            bool: True if browser is ready, False if timeout occurred
        """
        total_waited = 0
        last_check_time = 0
        self.logger.info(f"Waiting up to {seconds} seconds for browser...")
        
        while total_waited < seconds:
            current_time = time.time()
            if current_time - last_check_time < check_interval:
                time.sleep(0.1)  # Prevent CPU spinning
                continue
                
            last_check_time = current_time
            
            # Check browser state with improved async handling and proper Promise resolution
            print(f'''<run_javascript_browser>
            (async () => {{
                try {{
                    // Check network idle state
                    const checkNetworkIdle = () => new Promise((resolve) => {{
                        if (window.performance && window.performance.getEntriesByType) {{
                            const resources = window.performance.getEntriesByType('resource');
                            const pendingResources = resources.filter(r => !r.responseEnd);
                            resolve(pendingResources.length === 0);
                        }} else {{
                            resolve(true);
                        }}
                    }});
                    
                    // Wait for network idle
                    const networkIdle = await checkNetworkIdle();
                    
                    // Verify console functionality
                    const verifyConsole = () => new Promise((resolve) => {{
                        const testMessage = 'CONSOLE_TEST_' + Date.now();
                        let originalLog = console.log;
                        let testPassed = false;
                        
                        console.log = (...args) => {{
                            originalLog.apply(console, args);
                            if (args[0] === testMessage) {{
                                testPassed = true;
                            }}
                        }};
                        
                        console.log(testMessage);
                        setTimeout(() => {{
                            console.log = originalLog;
                            resolve(testPassed);
                        }}, 100);
                    }});
                    
                    // Check console functionality
                    const consoleWorking = await verifyConsole();
                    
                    // Check page state
                    const state = {{
                        readyState: document.readyState,
                        url: window.location.href,
                        bodyLength: document.body.innerHTML.length,
                        title: document.title,
                        networkIdle: networkIdle,
                        hasError: !!document.querySelector('.error-message, .error'),
                        consoleWorking: consoleWorking,
                        contentCheck: null,
                        success: false,
                        errors: []
                    }};
                    
                    // Check for specific content if requested
                    const contentSelector = '{content_check}';
                    if (contentSelector && contentSelector !== 'None') {{
                        const elements = document.querySelectorAll(contentSelector);
                        state.contentCheck = {{
                            found: elements.length > 0,
                            count: elements.length,
                            visible: Array.from(elements).some(el => 
                                window.getComputedStyle(el).display !== 'none' &&
                                window.getComputedStyle(el).visibility !== 'hidden'
                            )
                        }};
                    }}
                    
                    // Determine if page is ready and collect any issues
                    if (state.readyState !== 'complete') state.errors.push('Document not complete');
                    if (state.bodyLength === 0) state.errors.push('Empty body');
                    if (!state.networkIdle) state.errors.push('Network not idle');
                    if (!state.consoleWorking) state.errors.push('Console not working');
                    if (state.contentCheck && (!state.contentCheck.found || !state.contentCheck.visible)) {{
                        state.errors.push('Required content not found/visible');
                    }}
                    
                    state.success = (
                        state.readyState === 'complete' &&
                        state.bodyLength > 0 &&
                        state.networkIdle &&
                        state.consoleWorking &&
                        (!state.contentCheck || 
                         (state.contentCheck.found && state.contentCheck.visible))
                    );
                    
                    console.log("BROWSER_CHECK_START");
                    console.log(JSON.stringify(state));
                    console.log("BROWSER_CHECK_END");
                    
                }} catch (error) {{
                    console.error("Browser check failed:", error);
                    console.log("BROWSER_CHECK_START");
                    console.log(JSON.stringify({{ success: false, error: error.message }}));
                    console.log("BROWSER_CHECK_END");
                }}
            }})();
            </run_javascript_browser>''')
            
            # Wait for check interval
            print(f'<wait for="browser" seconds="{check_interval}"/>')
            total_waited += check_interval
            
            # Get console output to verify state
            print('<get_browser_console/>')
            console_output = self.get_browser_console()
            
            if console_output:
                try:
                    # Look for JSON state object in console output with improved error handling
                    state_start = console_output.find('BROWSER_CHECK_START')
                    state_end = console_output.find('BROWSER_CHECK_END')
                    if state_start != -1 and state_end != -1:
                        state_json = console_output[state_start + len('BROWSER_CHECK_START'):state_end].strip()
                        try:
                            state_data = json.loads(state_json)
                            self.logger.debug(f"Browser state: {state_data}")
                        except json.JSONDecodeError as e:
                            self.logger.error(f"Failed to parse browser state JSON: {e}")
                            self.logger.debug(f"Raw JSON: {state_json}")
                            return False
                        
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
