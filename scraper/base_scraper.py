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
        """Get browser console output using localStorage for persistence"""
        try:
            # Initialize console capture with localStorage
            print('''<run_javascript_browser>
            (() => {
                try {
                    // Initialize localStorage if needed
                    if (!localStorage.getItem('devinConsoleMessages')) {
                        localStorage.setItem('devinConsoleMessages', JSON.stringify([]));
                    }
                    
                    // Helper functions for localStorage
                    const consoleStorage = {
                        getMessages: () => {
                            try {
                                return JSON.parse(localStorage.getItem('devinConsoleMessages')) || [];
                            } catch (e) {
                                console.error('Error reading messages:', e);
                                return [];
                            }
                        },
                        addMessage: (msg) => {
                            try {
                                const messages = consoleStorage.getMessages();
                                messages.push(msg);
                                localStorage.setItem('devinConsoleMessages', JSON.stringify(messages));
                            } catch (e) {
                                console.error('Error adding message:', e);
                            }
                        },
                        clear: () => {
                            localStorage.setItem('devinConsoleMessages', JSON.stringify([]));
                        }
                    };
                    
                    // Store original methods
                    const originalConsole = {
                        log: console.log.bind(console),
                        info: console.info.bind(console),
                        warn: console.warn.bind(console),
                        error: console.error.bind(console)
                    };
                    
                    // Helper to stringify any type of argument
                    function safeStringify(arg) {
                        if (typeof arg === 'undefined') return 'undefined';
                        if (arg === null) return 'null';
                        if (typeof arg === 'object') {
                            try {
                                return JSON.stringify(arg);
                            } catch (e) {
                                return '[Object]';
                            }
                        }
                        return String(arg);
                    }
                    
                    // Create wrapper for each console method
                    function wrapConsole(method) {
                        return function() {
                            try {
                                const args = Array.from(arguments).map(safeStringify);
                                const msg = `${method}: ${args.join(' ')}`;
                                consoleStorage.addMessage(msg);
                                originalConsole[method].apply(console, arguments);
                            } catch (e) {
                                originalConsole.error('Error in console wrapper:', e);
                            }
                        };
                    }
                    
                    // Override console methods
                    console.log = wrapConsole('log');
                    console.info = wrapConsole('info');
                    console.warn = wrapConsole('warn');
                    console.error = wrapConsole('error');
                    
                    // Clear previous messages
                    consoleStorage.clear();
                    
                    // Verify console capture is working
                    const testMsg = "TEST_CONSOLE_CAPTURE_" + Date.now();
                    console.log(testMsg);
                    const messages = consoleStorage.getMessages();
                    const working = messages.some(msg => msg.includes(testMsg));
                    
                    console.log("DEVIN_CONSOLE_START");
                    console.log(JSON.stringify({
                        initialized: true,
                        working: working,
                        messages: messages
                    }));
                    console.log("DEVIN_CONSOLE_END");
                    
                    return true;
                } catch (e) {
                    console.error("ERROR: Failed to initialize console capture:", e);
                    return false;
                }
            })();
            </run_javascript_browser>''')
            
            # Wait for JavaScript execution
            print('<wait for="browser" seconds="2"/>')
            
            # Get console output
            print('<get_browser_console/>')
            raw_output = self.get_browser_console()
            
            try:
                self.logger.debug("Processing console output...")
                self.logger.debug(f"Raw output length: {len(raw_output)}")
                
                # Extract messages between markers
                start_marker = "DEVIN_CONSOLE_START"
                end_marker = "DEVIN_CONSOLE_END"
                start_idx = raw_output.find(start_marker)
                end_idx = raw_output.find(end_marker)
                
                if start_idx != -1 and end_idx != -1:
                    json_text = raw_output[start_idx + len(start_marker):end_idx].strip()
                    try:
                        console_data = json.loads(json_text)
                        self.logger.debug(f"Parsed console data: {console_data}")
                        
                        if isinstance(console_data, dict):
                            if not console_data.get('initialized', False):
                                self.logger.error("Console capture not initialized")
                            if not console_data.get('working', False):
                                self.logger.warning("Console capture reported as not working")
                            if 'messages' in console_data:
                                messages = console_data['messages']
                                self.logger.debug(f"Found {len(messages)} messages")
                                return '\n'.join(str(msg) for msg in messages)
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Failed to parse console JSON: {e}")
                
                # Fallback: try to find any console messages
                self.logger.debug("Falling back to line-by-line parsing...")
                messages = []
                for line in raw_output.split('\n'):
                    line = line.strip()
                    if any(line.startswith(prefix) for prefix in ('console.log:', 'console.info:', 'console.warn:', 'console.error:')):
                        msg = line.split(':', 1)[1].strip()
                        if msg:
                            messages.append(msg)
                            self.logger.debug(f"Found console message: {msg}")
                    elif line.startswith('Return value:'):
                        self.logger.debug("Skipping return value line")
                        continue
                    elif line and not line.startswith(('DEBUG:', 'INFO:', 'WARNING:', 'ERROR:')):
                        messages.append(line)
                        self.logger.debug(f"Found raw message: {line}")
                
                if messages:
                    self.logger.debug(f"Returning {len(messages)} messages")
                    return '\n'.join(messages)
                
                self.logger.warning("No console messages found in output")
                self.logger.debug(f"Raw console output: {raw_output}")
                return raw_output
            except Exception as e:
                self.logger.error(f"Error parsing console output: {e}")
                self.logger.debug(f"Raw console output: {raw_output}")
                return raw_output
                
        except Exception as e:
            self.logger.error(f"Error in get_browser_console: {str(e)}")
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
            
            # Reset console state
            print('''<run_javascript_browser>
            (() => {
                window.__devinConsole = {
                    messages: [],
                    initialized: false
                };
                return true;
            })();
            </run_javascript_browser>''')
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
        """Wait for browser readiness with enhanced state checking and content verification
        
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
                const contentSelector = '" + (content_check || "None") + "';
                if (contentSelector && contentSelector !== 'None') {
                    const elements = document.querySelectorAll(contentSelector);
                    if (elements.length === 0) {
                        state.errors.push('Required content not found: ' + contentSelector);
                    } else {
                        const visible = Array.from(elements).some(el => 
                            window.getComputedStyle(el).display !== 'none' &&
                            window.getComputedStyle(el).visibility !== 'hidden'
                        );
                        if (!visible) state.errors.push('Required content not visible: ' + contentSelector);
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
