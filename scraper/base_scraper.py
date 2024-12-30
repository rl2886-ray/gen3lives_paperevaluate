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
            
    def _get_console_messages(self) -> List[Dict]:
        """Get console messages directly from browser memory
        
        Returns:
            List of message dictionaries with timestamp, method, and message content
        """
        try:
            result = self.run_javascript('''
            (() => {
                if (!window.__consoleMessages || !Array.isArray(window.__consoleMessages)) {
                    return [];
                }
                return window.__consoleMessages;
            })();
            ''')
            
            if isinstance(result, list):
                self.logger.debug(f"Retrieved {len(result)} messages from browser memory")
                return result
            
            self.logger.warning("Invalid console messages format")
            return []
            
            
        except Exception as e:
            self.logger.error(f"Error getting console messages: {str(e)}")
            return []
    
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
        """Initialize console capture with proper method wrapping and verification"""
        try:
            self.logger.debug("Initializing console capture...")
            
            # First verify browser is in a good state
            verify_state = self.run_javascript('''
            (() => {
                console.log("=== Pre-initialization Check ===");
                const state = {
                    ready: document.readyState === 'complete',
                    url: window.location.href,
                    console: {
                        log: typeof console.log === 'function',
                        info: typeof console.info === 'function',
                        warn: typeof console.warn === 'function',
                        error: typeof console.error === 'function'
                    }
                };
                console.log("Browser state:", JSON.stringify(state, null, 2));
                return state;
            })();
            ''')
            
            if not isinstance(verify_state, dict) or not verify_state.get('ready'):
                self.logger.error("Browser not ready for console capture")
                return False
                
            # Clear any existing console state
            cleanup_result = self.run_javascript('''
            (() => {
                try {
                    console.log("=== Cleaning Existing State ===");
                    
                    // Restore original console methods if they exist
                    ['log', 'info', 'warn', 'error'].forEach(method => {
                        if (console[method].__original) {
                            console[method] = console[method].__original;
                            console.log(`Restored original ${method}`);
                        }
                    });
                    
                    // Clean up global state
                    ['__consoleMessages', '__originalConsole', '__consoleInitialized'].forEach(prop => {
                        if (window[prop]) {
                            delete window[prop];
                            console.log(`Cleaned up ${prop}`);
                        }
                    });
                    
                    return { success: true };
                } catch (e) {
                    console.error("Cleanup failed:", e);
                    return { success: false, error: e.message };
                }
            })();
            ''')
            
            if not isinstance(cleanup_result, dict) or not cleanup_result.get('success'):
                self.logger.error("Failed to clean up existing console state")
                return False
            
            # Initialize with proper wrapper properties
            init_result = self.run_javascript('''
                (function() {
                    var global = (typeof window !== 'undefined') ? window : this;
                    
                    try {
                        // Reset state in global scope
                        global.__consoleMessages = [];
                        global.__consoleInitialized = false;
                        global.__originalConsole = {};
                        
                        // Store original methods and create wrappers
                        var methods = ['log', 'info', 'warn', 'error'];
                        for (var i = 0; i < methods.length; i++) {
                            var method = methods[i];
                            
                            
                            // Save original method with proper binding
                            global.__originalConsole[method] = console[method].bind(console);
                            
                            // Create wrapper function with proper closure
                            var wrapper = (function(methodName) {
                                return function() {
                                    var args = Array.prototype.slice.call(arguments);
                                    global.__consoleMessages.push({
                                        timestamp: new Date().toISOString(),
                                        method: methodName,
                                        message: args.map(function(arg) {
                                            return (typeof arg === 'object') ? JSON.stringify(arg) : String(arg);
                                        }).join(' ')
                                    });
                                    return global.__originalConsole[methodName].apply(console, args);
                                };
                            })(method);
                            
                            // Add wrapper properties
                            wrapper.__wrapped = true;
                            wrapper.__original = global.__originalConsole[method];
                            
                            // Override console method
                            console[method] = wrapper;
                        }
                        
                        global.__consoleInitialized = true;
                        console.log("Console capture initialized");
                        return { success: true };
                    } catch (e) {
                        console.error("Console initialization failed:", e);
                        return { success: false, error: e.message, stack: e.stack };
                    }
                }).call((typeof window !== 'undefined') ? window : this);
            ''')
            
            if not isinstance(init_result, dict) or not init_result.get('success'):
                self.logger.error("Failed to initialize console capture")
                return False
            
            # Verify initialization with detailed checks
            verify_result = self.run_javascript('''
                try {
                    if (!window.__consoleInitialized) {
                        return { success: false, error: "Console not initialized" };
                    }
                    
                    // Verify wrapper properties
                    const state = {
                        initialized: window.__consoleInitialized === true,
                        hasMessages: Array.isArray(window.__consoleMessages),
                        hasOriginalConsole: typeof window.__originalConsole === 'object',
                        wrappedMethods: {}
                    };
                    
                    ['log', 'info', 'warn', 'error'].forEach(method => {
                        state.wrappedMethods[method] = {
                            wrapped: console[method].__wrapped === true,
                            hasOriginal: console[method].__original !== undefined,
                            type: typeof console[method]
                        };
                    });
                    
                    // Test message capture
                    console.log("VERIFY: Test message");
                    
                    return {
                        success: true,
                        state: state,
                        messageCount: window.__consoleMessages.length
                    };
                } catch (e) {
                    return { success: false, error: e.message };
                }
            ''')
            
            if isinstance(verify_result, dict) and verify_result.get('success'):
                state = verify_result.get('state', {})
                if (state.get('initialized') and 
                    state.get('hasMessages') and 
                    state.get('hasOriginalConsole') and 
                    all(m.get('wrapped') and m.get('hasOriginal') 
                        for m in state.get('wrappedMethods', {}).values())):
                    self._console_initialized = True
                    self.logger.info("Console capture initialized successfully")
                    return True
            
            self.logger.error(f"Console initialization verification failed: {verify_result}")
            return False
            
        except Exception as e:
            self.logger.error(f"Error in console initialization: {str(e)}")
            return False
        
    def get_browser_console(self) -> str:
        """Get browser console output with direct implementation"""
        try:
            # Initialize if needed
            if not self._console_initialized and not self.initialize_console_capture():
                return ""
            
            # Get messages directly
            result = self.run_javascript('''
            (() => {
                try {
                    if (!window.__consoleInitialized || !window.__consoleMessages) {
                        console.error("Console capture not properly initialized");
                        return "";
                    }
                    const messages = window.__consoleMessages
                        .map(msg => `[${msg.timestamp}] ${msg.method}: ${msg.message}`)
                        .join("\\n");
                    // Clear messages after reading
                    window.__consoleMessages = [];
                    return messages;
                } catch (e) {
                    console.error("Error getting console messages:", e);
                    return "";
                }
            })();
            ''')
            
            return result if isinstance(result, str) else ""
            
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
            
            # Execute script with result logging
            wrapped_script = f'''
            (function() {{
                var global = (typeof window !== 'undefined') ? window : this;
                var result;
                
                try {{
                    // Clear any existing results
                    if ('__lastJsResult' in global) {{
                        delete global.__lastJsResult;
                    }}
                    
                    // Execute the script in the global scope
                    result = (function() {{
                        'use strict';
                        return eval('(' + function() {{ {script} }}.toString() + ')()');
                    }}).call(global);
                    
                    // Store the result
                    global.__lastJsResult = result;
                    
                    // Log the result for parsing
                    global.console.log("JS_RESULT_START");
                    global.console.log(JSON.stringify(result, null, 2));
                    global.console.log("JS_RESULT_END");
                    
                    return result;
                }} catch (error) {{
                    global.console.error("JavaScript execution error:", error);
                    var errorResult = {{ 
                        error: error.message,
                        stack: error.stack,
                        type: error.name
                    }};
                    global.console.log("JS_RESULT_START");
                    global.console.log(JSON.stringify(errorResult));
                    global.console.log("JS_RESULT_END");
                    return errorResult;
                }}
            }}).call((typeof window !== 'undefined') ? window : this);
            '''
            
            # Clear console before execution
            print('''<run_javascript_browser>
            console.clear();
            </run_javascript_browser>''')
            print('<wait for="browser" seconds="1"/>')
            
            # Execute the wrapped script
            print(f'''<run_javascript_browser>{wrapped_script}</run_javascript_browser>''')
            print('<wait for="browser" seconds="1"/>')
            print('<get_browser_console/>')
            
            # Parse result from console output
            console_output = self.get_browser_console()
            self.logger.debug(f"Console output: {console_output}")
            
            # Extract result between markers
            start_marker = "JS_RESULT_START"
            end_marker = "JS_RESULT_END"
            
            if start_marker in console_output and end_marker in console_output:
                result_lines = console_output.split(start_marker)[1].split(end_marker)[0].strip().split('\n')
                result_json = '\n'.join(line.strip() for line in result_lines)
                try:
                    return json.loads(result_json)
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to parse JSON result: {e}")
                    return result_json
            
            self.logger.error("No result markers found in console output")
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
