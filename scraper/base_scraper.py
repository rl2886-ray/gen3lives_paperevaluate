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
        
        # Initialize browser state
        self._console_initialized = False
        self._console_messages = []
        self._console_output_file = '/tmp/devin_console_output.txt'
        
        # Ensure console output file exists with proper permissions
        try:
            with open(self._console_output_file, 'w') as f:
                f.write('')  # Create empty file
            os.chmod(self._console_output_file, 0o666)  # Make file readable/writable by all
        except Exception as e:
            self.logger.error(f"Error initializing console output file: {str(e)}")
            
    def _read_console_output(self) -> str:
        """Helper method to safely read console output from file
        
        Returns:
            str: Console output content or empty string on error
        """
        try:
            if not os.path.exists(self._console_output_file):
                self.logger.warning("Console output file does not exist")
                with open(self._console_output_file, 'w') as f:
                    f.write('')  # Create empty file
                os.chmod(self._console_output_file, 0o666)
                return ""
                
            with open(self._console_output_file, 'r') as f:
                content = f.read()
                self.logger.debug(f"Read {len(content)} bytes from console output file")
                return content
                
        except Exception as e:
            self.logger.error(f"Error reading console output: {str(e)}")
            self.logger.exception("Full traceback:")
            return ""
    
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
        """Initialize the console capture mechanism with persistence and verification"""
        try:
            self.logger.debug("Starting console capture initialization...")
            self._console_initialized = False
            
            # First clear any existing state
            print('''<run_javascript_browser>
            delete window.__consoleInitialized;
            delete window.__consoleMessages;
            delete window.__originalConsole;
            console.log("Cleared existing console state");
            </run_javascript_browser>''')
            print('<wait for="browser" seconds="2"/>')
            
            # Initialize with persistence
            print('''<run_javascript_browser>
            (() => {
                // Always reinitialize to ensure clean state
                try {
                    delete window.__consoleInitialized;
                    delete window.__consoleMessages;
                    delete window.__originalConsole;
                } catch (e) {
                    console.error("Error cleaning up old console state:", e);
                }
                
                try {
                    // Initialize message storage with persistence
                    window.__consoleMessages = [];
                    window.__originalConsole = {
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
                                return String(arg);
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
                                window.__consoleMessages.push(msg);
                                window.__originalConsole[method].apply(console, arguments);
                            } catch (e) {
                                window.__originalConsole.error('Error in console wrapper:', e);
                            }
                        };
                    }
                    
                    // Override console methods with persistence and proper cleanup handling
                    ['log', 'info', 'warn', 'error'].forEach(method => {
                        const wrapper = wrapConsole(method);
                        wrapper.__wrapped = true;
                        wrapper.__original = console[method];
                        console[method] = wrapper;
                    });
                    
                    // Mark as initialized with persistence and verify state
                    const verifyState = () => {
                        if (!window.__consoleMessages || !Array.isArray(window.__consoleMessages)) {
                            throw new Error("Console messages array not properly initialized");
                        }
                        if (!window.__originalConsole || typeof window.__originalConsole !== 'object') {
                            throw new Error("Original console not properly saved");
                        }
                        if (!console.log.__wrapped || !console.info.__wrapped || 
                            !console.warn.__wrapped || !console.error.__wrapped) {
                            throw new Error("Console methods not properly wrapped");
                        }
                    };
                    
                    window.__consoleInitialized = true;
                    verifyState();
                    
                    // Add cleanup method
                    window.__cleanupConsole = () => {
                        try {
                            ['log', 'info', 'warn', 'error'].forEach(method => {
                                if (console[method].__original) {
                                    console[method] = console[method].__original;
                                }
                            });
                            delete window.__consoleMessages;
                            delete window.__originalConsole;
                            delete window.__consoleInitialized;
                            console.log("Console cleanup successful");
                            return true;
                        } catch (e) {
                            console.error("Console cleanup failed:", e);
                            return false;
                        }
                    };
                    
                    console.log("Console capture initialized successfully");
                    return true;
                } catch (e) {
                    console.error("ERROR: Failed to initialize console capture:", e);
                    return false;
                }
            })();
            </run_javascript_browser>''')
            print('<wait for="browser" seconds="2"/>')
            
            # Get initialization result and verify state
            print('<get_browser_console/>')
            console_output = ""
            try:
                with open('/tmp/devin_console_output.txt', 'r') as f:
                    console_output = f.read()
            except Exception as e:
                self.logger.error(f"Error reading console output: {str(e)}")
            self.logger.debug(f"Initialization console output: {console_output}")
            
            # Verify initialization state
            print('''<run_javascript_browser>
            (() => {
                const state = {
                    initialized: window.__consoleInitialized === true,
                    hasMessages: Array.isArray(window.__consoleMessages),
                    hasOriginalConsole: typeof window.__originalConsole === 'object',
                    consoleWrapped: console.log.toString().includes('wrapConsole'),
                    messageCount: window.__consoleMessages ? window.__consoleMessages.length : 0,
                    consoleLogType: typeof console.log
                };
                console.log("CONSOLE_STATE:" + JSON.stringify(state));
                return state;
            })();
            </run_javascript_browser>''')
            print('<wait for="browser" seconds="2"/>')
            
            # Get verification state
            print('<get_browser_console/>')
            verification_output = self._read_console_output()
            self.logger.debug(f"Verification state output: {verification_output}")
            
            try:
                # Parse verification state
                state_line = next(line for line in verification_output.split('\n') 
                                if line.startswith('CONSOLE_STATE:'))
                state_json = state_line.replace('CONSOLE_STATE:', '')
                state = json.loads(state_json)
                self.logger.debug(f"Console state verification: {state}")
                
                # Check if initialization was successful
                initialization_success = (
                    state.get('initialized', False) and
                    state.get('hasMessages', False) and
                    state.get('hasOriginalConsole', False) and
                    state.get('consoleWrapped', False) and
                    "Console capture initialized successfully" in console_output and
                    "ERROR: Failed to initialize console capture" not in console_output
                )
                
                if initialization_success:
                    self._console_initialized = True
                    self.logger.info("Console capture initialized successfully")
                else:
                    self.logger.error("Failed to initialize console capture")
                    self.logger.debug(f"State verification failed: {state}")
                
                return initialization_success
                
            except Exception as e: 
                self.logger.error(f"Error verifying console state: {str(e)}")
                return False
                
        except Exception as e:
            self.logger.error(f"Error in console capture initialization: {str(e)}")
            self.logger.exception("Full traceback:")
            return False
        
    def get_browser_console(self) -> str:
        """Get browser console output with enhanced error handling and verification"""
        try:
            self.logger.debug("Starting console capture...")
            
            # Initialize console capture if not already initialized
            if not self._console_initialized:
                if not self.initialize_console_capture():
                    self.logger.error("Failed to initialize console capture")
                    return ""
            
            # Get console messages
            print('<get_browser_console/>')
            console_output = self._read_console_output()
            self.logger.debug(f"Raw console output received (length: {len(console_output)})")
            
            if not console_output:
                self.logger.warning("Empty console output received")
                return ""
            
            # Process the captured output
            self.logger.debug("Processing console output...")
            messages = []
            
            # Parse each line
            for line in console_output.split('\n'):
                line = line.strip()
                if not line:
                    continue
                    
                # Skip system messages and debug info
                if line.startswith(('DEBUG:', 'INFO:', 'WARNING:', 'ERROR:', '<', 'Return value:')):
                    continue
                    
                # Extract message from console methods
                if any(line.startswith(prefix) for prefix in ('console.log:', 'console.info:', 'console.warn:', 'console.error:')):
                    msg = line.split(':', 1)[1].strip() if ':' in line else line
                    if msg:
                        messages.append(msg)
                        self.logger.debug(f"Found console message: {msg}")
                else:
                    messages.append(line)
                    self.logger.debug(f"Found raw message: {line}")
            
            if messages:
                self.logger.debug(f"Returning {len(messages)} messages")
                return '\n'.join(messages)
            
            self.logger.warning("No console messages found in output")
            return console_output
                
        except Exception as e:
            self.logger.error(f"Error in get_browser_console: {str(e)}")
            self.logger.exception("Full traceback:")
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
            
            # Clean up previous console state
            print('''<run_javascript_browser>
            (() => {
                try {
                    // Clean up if initialized
                    if (window.__cleanupConsole) {
                        window.__cleanupConsole();
                    }
                    // Reset messages array
                    window.__consoleMessages = [];
                    return true;
                } catch (e) {
                    console.error("Error cleaning up console:", e);
                    return false;
                }
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
