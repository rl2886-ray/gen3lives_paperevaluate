"""
Stanford-specific scraper implementation
"""
import json
import logging
from typing import Dict, List, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class StanfordScraper(BaseScraper):
    # Define STEM-related keywords for filtering programs
    STEM_KEYWORDS = {
        'engineering', 'computer', 'science', 'technology', 'mathematics', 
        'physics', 'chemistry', 'biology', 'systems', 'computation',
        'data', 'electrical', 'mechanical', 'materials', 'aerospace',
        'chemical', 'computational', 'nuclear', 'robotics', 'artificial intelligence'
    }
    
    def __init__(self, university_data: Dict):
        super().__init__(university_data)
        self.base_url = "https://applygrad.stanford.edu/portal/programs"
        # Initialize filter IDs - these will be updated when the page loads
        self.engineering_filter_id = None
        self.ms_filter_id = None
        self.expand_button_id = None
    
    def is_stem_program(self, program_name: str) -> bool:
        """
        Check if a program is STEM-related based on its name
        """
        return any(keyword.lower() in program_name.lower() for keyword in self.STEM_KEYWORDS)
    
    def find_program_urls(self, max_retries: int = 3, timeout: int = 15) -> List[Dict]:
        """
        Find URLs and basic info for STEM programs at Stanford
        
        Args:
            max_retries: Maximum number of attempts to load the page
            timeout: Maximum time in seconds to wait for page elements
            
        Returns:
            List[Dict]: List of dictionaries containing program URLs and basic information
            
        Raises:
            TimeoutError: If page fails to load within specified timeout
            RuntimeError: If required elements are not found
        """
        import time
        from datetime import datetime
        
        MAX_RETRIES = 5
        LOAD_TIMEOUT = 30  # Increased timeout for better reliability
        
        self.logger.info(f"[{datetime.now()}] Loading Stanford programs portal...")
        
        # Navigate to the programs portal with retries
        for attempt in range(MAX_RETRIES):
            try:
                self.logger.info(f"[{datetime.now()}] Attempt {attempt + 1} of {MAX_RETRIES}")
                print(f'<navigate_browser url="{self.base_url}"/>')
                
                # Take a screenshot to verify page state
                print('''<screenshot_browser>
                Checking the current state of the Stanford programs portal.
                Looking for:
                1. Filter checkboxes
                2. Program listings
                3. Overall page structure
                </screenshot_browser>''')
                
                # Wait for initial page load with verification
                for attempt in range(LOAD_TIMEOUT):
                    self.logger.info(f"[{datetime.now()}] Page load attempt {attempt + 1}/{LOAD_TIMEOUT}")
                    
                    # Check page state and find interactive elements
                    print('''<run_javascript_browser>
                    function findFilterByText(text) {
                        return Array.from(document.querySelectorAll('input[type="checkbox"]')).find(input => {
                            const label = input.parentElement?.textContent?.trim().toLowerCase();
                            return label && label.includes(text.toLowerCase());
                        });
                    }

                    function findButtonByText(text) {
                        return Array.from(document.querySelectorAll('button')).find(button => {
                            const buttonText = button.textContent?.trim().toLowerCase();
                            return buttonText && buttonText.includes(text.toLowerCase());
                        });
                    }

                    const state = {
                        readyState: document.readyState,
                        bodyLength: document.body.textContent.length,
                        pageTitle: document.title,
                        filters: {
                            all: Array.from(document.querySelectorAll('input[type="checkbox"]')).map(f => ({
                                id: f.getAttribute('devinid'),
                                label: f.parentElement?.textContent?.trim(),
                                checked: f.checked,
                                visible: f.offsetParent !== null
                            })),
                            engineering: findFilterByText('engineering'),
                            ms: findFilterByText('master of science')
                        },
                        buttons: {
                            all: Array.from(document.querySelectorAll('button')).map(b => ({
                                id: b.getAttribute('devinid'),
                                text: b.textContent?.trim(),
                                expanded: b.getAttribute('aria-expanded'),
                                visible: b.offsetParent !== null
                            })),
                            expand: findButtonByText('expand')
                        },
                        content: {
                            hasFilters: document.querySelectorAll('input[type="checkbox"]').length > 0,
                            hasPrograms: document.querySelectorAll('button[aria-expanded]').length > 0,
                            filterLabels: Array.from(document.querySelectorAll('input[type="checkbox"]')).map(f => 
                                f.parentElement?.textContent?.trim()).filter(Boolean)
                        }
                    };
                    
                    console.log("=== Detailed Page State ===");
                    console.log(JSON.stringify(state, null, 2));
                    
                    const isLoaded = state.readyState === 'complete' && 
                                   state.filters.all.length > 0 && 
                                   state.buttons.all.length > 0 &&
                                   state.filters.engineering &&
                                   state.filters.ms &&
                                   state.buttons.expand;
                    
                    if (isLoaded) {
                        console.log("PAGE_LOAD_COMPLETE");
                        if (state.filters.engineering) {
                            console.log(`FOUND_ENGINEERING_FILTER:${state.filters.engineering.getAttribute('devinid')}`);
                        }
                        if (state.filters.ms) {
                            console.log(`FOUND_MS_FILTER:${state.filters.ms.getAttribute('devinid')}`);
                        }
                        if (state.buttons.expand) {
                            console.log(`FOUND_EXPAND_BUTTON:${state.buttons.expand.getAttribute('devinid')}`);
                        }
                    }
                    </run_javascript_browser>''')
                    print('<get_browser_console/>')
                    console_output = self.get_browser_console()
                    
                    # Parse the console output for filter and button IDs
                    engineering_filter_id = None
                    ms_filter_id = None
                    expand_button_id = None
                    
                    for line in console_output.split('\n'):
                        if "FOUND_ENGINEERING_FILTER:" in line:
                            engineering_filter_id = line.split(':')[1].strip()
                        elif "FOUND_MS_FILTER:" in line:
                            ms_filter_id = line.split(':')[1].strip()
                        elif "FOUND_EXPAND_BUTTON:" in line:
                            expand_button_id = line.split(':')[1].strip()
                    
                    if "PAGE_LOAD_COMPLETE" in console_output:
                        self.logger.info(f"[{datetime.now()}] Page loaded successfully")
                        self.logger.info(f"Found filter IDs - Engineering: {engineering_filter_id}, MS: {ms_filter_id}, Expand: {expand_button_id}")
                        
                        # Store the IDs for later use
                        self.engineering_filter_id = engineering_filter_id
                        self.ms_filter_id = ms_filter_id
                        self.expand_button_id = expand_button_id
                        
                        # Take another screenshot to verify successful load
                        print('''<screenshot_browser>
                        Verifying successful page load.
                        Checking that filters and program listings are visible.
                        </screenshot_browser>''')
                        break
                    
                    if attempt < LOAD_TIMEOUT - 1:
                        self.logger.info(f"[{datetime.now()}] Page not ready, waiting...")
                        time.sleep(3)  # Further increased wait time between checks
                        # Log detailed page state for debugging
                        print('''<run_javascript_browser>
                        console.log("=== Detailed Page State ===");
                        console.log(JSON.stringify({
                            readyState: document.readyState,
                            bodyLength: document.body.textContent.length,
                            filterCount: document.querySelectorAll('input[type="checkbox"]').length,
                            buttonCount: document.querySelectorAll('button').length,
                            hasEngFilter: Boolean(state.filters.engineering),
                            hasMsFilter: Boolean(state.filters.ms),
                            hasExpandButton: Boolean(state.buttons.expand)
                        }, null, 2));
                        </run_javascript_browser>''')
                        print('<get_browser_console/>')
                else:
                    self.logger.error(f"[{datetime.now()}] Page failed to load properly")
                    print('''<screenshot_browser>
                    Capturing failed page load state.
                    Looking for any error messages or incomplete loading indicators.
                    </screenshot_browser>''')
                    raise TimeoutError("Page failed to load within timeout")
                
                # If we get here, page loaded successfully
                break
                
            except Exception as e:
                self.logger.error(f"[{datetime.now()}] Error loading page (attempt {attempt + 1}): {str(e)}")
                if attempt == MAX_RETRIES - 1:
                    raise
                time.sleep(5)  # Wait before retry
        
        # Filter for School of Engineering and MS degrees
        self.logger.info("Applying filters...")
        
        if not hasattr(self, 'engineering_filter_id') or not hasattr(self, 'ms_filter_id') or not hasattr(self, 'expand_button_id'):
            self.logger.error("Filter IDs not found during page load")
            raise ValueError("Required filter IDs not found")
        
        # Apply Engineering filter
        if self.engineering_filter_id:
            self.logger.info(f"Clicking Engineering filter (ID: {self.engineering_filter_id})")
            print(f'''<run_javascript_browser>
            const engFilter = document.querySelector('input[devinid="{self.engineering_filter_id}"]');
            console.log("=== Engineering Filter State ===");
            const engState = {
                "exists": Boolean(engFilter),
                "checked": engFilter ? engFilter.checked : false,
                "visible": engFilter ? engFilter.offsetParent !== null : false,
                "parent": engFilter ? engFilter.parentElement?.textContent?.trim() : null
            };
            console.log(JSON.stringify(engState, null, 2));
            </run_javascript_browser>''')
            print('<get_browser_console/>')
            print(f'<click_browser box="{self.engineering_filter_id}"/>')
            time.sleep(3)
        
        # Apply MS filter
        if self.ms_filter_id:
            self.logger.info(f"Clicking MS filter (ID: {self.ms_filter_id})")
            print(f'''<run_javascript_browser>
            const msFilter = document.querySelector('input[devinid="{self.ms_filter_id}"]');
            console.log("=== MS Filter State ===");
            const msState = {
                "exists": Boolean(msFilter),
                "checked": msFilter ? msFilter.checked : false,
                "visible": msFilter ? msFilter.offsetParent !== null : false,
                "parent": msFilter ? msFilter.parentElement?.textContent?.trim() : null
            };
            console.log(JSON.stringify(msState, null, 2));
            </run_javascript_browser>''')
            print('<get_browser_console/>')
            print(f'<click_browser box="{self.ms_filter_id}"/>')
            time.sleep(3)
        
        # Click expand button
        if self.expand_button_id:
            self.logger.info(f"Clicking expand button (ID: {self.expand_button_id})")
            print(f'''<run_javascript_browser>
            const expandBtn = document.querySelector('button[devinid="{self.expand_button_id}"]');
            console.log("=== Expand Button State ===");
            const btnState = {
                "exists": Boolean(expandBtn),
                "expanded": expandBtn ? expandBtn.getAttribute('aria-expanded') : null,
                "visible": expandBtn ? expandBtn.offsetParent !== null : false,
                "text": expandBtn ? expandBtn.textContent?.trim() : null
            };
            console.log(JSON.stringify(btnState, null, 2));
            </run_javascript_browser>''')
            print('<get_browser_console/>')
            print(f'<click_browser box="{self.expand_button_id}"/>')
            time.sleep(3)
        
        # Extract program information using JavaScript
        js_code = '''
            const programs = Array.from(document.querySelectorAll("button[aria-expanded=true]")).map(button => {
                const section = button.parentElement;
                const title = button.querySelector("h2")?.textContent;
                const school = section.querySelector("a[href*=engineering\\.stanford\\.edu]")?.textContent;
                const programUrl = section.querySelector("a[aria-label*=Program\\ Website]")?.href;
                const bulletinUrl = section.querySelector("a[href*=bulletin\\.stanford\\.edu]")?.href;
                const email = section.querySelector("a[href^=mailto]")?.textContent;
                
                // Get deadlines
                const deadlines = {};
                const deadlineRows = section.querySelectorAll("tbody tr");
                deadlineRows.forEach(row => {
                    const term = row.querySelector("th")?.textContent;
                    const deadline = row.querySelector("td")?.textContent;
                    if (term && deadline) {
                        deadlines[term] = deadline;
                    }
                });

                // Get testing requirements
                const testingSection = Array.from(section.querySelectorAll("h3")).find(h3 => 
                    h3.textContent.includes("Testing Requirements"))?.parentElement;
                const testingRows = testingSection?.querySelectorAll("tbody tr") || [];
                const testingReqs = {};
                testingRows.forEach(row => {
                    const cols = row.querySelectorAll("td");
                    if (cols.length >= 2) {
                        testingReqs["GRE General"] = cols[0].textContent.trim();
                        testingReqs["GRE Subject"] = cols[1].textContent.trim();
                    }
                });

                return {
                    title,
                    school,
                    programUrl,
                    bulletinUrl,
                    email,
                    deadlines,
                    testingReqs,
                    buttonId: button.getAttribute("devinid")
                };
            }).filter(program => program.title && program.school);
            console.log(JSON.stringify(programs, null, 2));
        '''
        print(f'<run_javascript_browser>{js_code}</run_javascript_browser>')
        print('<get_browser_console/>')
        
        # Parse the console output to get program data
        try:
            # Get console output and parse JSON
            print('<get_browser_console/>')
            console_output = self.get_browser_console()
            
            # Find the JSON string in console output
            programs = []
            for line in console_output.split('\n'):
                if line.strip().startswith('[') or line.strip().startswith('{'):
                    try:
                        data = json.loads(line.strip())
                        if isinstance(data, list):
                            programs = data
                            break
                    except json.JSONDecodeError:
                        continue
            
            # Take a screenshot for verification
            print('<screenshot_browser>\nVerifying extracted program data\n</screenshot_browser>')
            
            # Filter for STEM programs
            stem_programs = []
            for program in programs:
                if program.get('title') and self.is_stem_program(program['title']):
                    self.logger.info(f"Found STEM program: {program['title']}")
                    stem_programs.append(program)
            
            if not stem_programs:
                self.logger.warning("No STEM programs found. This might indicate a problem with the filtering or page structure.")
                print('<screenshot_browser>\nNo STEM programs found\n</screenshot_browser>')
            
            return stem_programs
            
        except Exception as e:
            self.logger.error(f"Error parsing program data: {str(e)}")
            return []
    
    def extract_program_info(self, program_data: Dict) -> Optional[Dict]:
        """Extract program information from Stanford program page after clicking the program button"""
        try:
            # Click the program button to expand details
            button_id = program_data.get('buttonId')
            if not button_id:
                self.logger.error("No button ID provided for program")
                return None
                
            # Click the button to expand program details
            print(f'<click_browser box="{button_id}"/>')
            
            # Initialize program info structure with nested dictionaries
            program_info = {
                'program_id': None,
                'university_id': 'stanford',
                'department': None,
                'degree_name': program_data.get('title'),
                'degree_type': 'MS',
                'duration': None,
                'credits_required': None,
                'admission_requirements': {
                    'gre_required': None,
                    'minimum_gpa': None,
                    'toefl_minimum': None,
                    'ielts_minimum': None,
                    'application_deadline': None
                },
                'financial_info': {
                    'tuition_per_credit': None,
                    'estimated_total_cost': None,
                    'financial_aid_available': False,
                    'assistantship_available': False
                },
                'program_features': {
                    'specializations': [],
                    'internship_opportunities': False,
                    'research_areas': [],
                    'faculty_count': None,
                    'student_faculty_ratio': None
                },
                'courses': {
                    'core_courses': [],
                    'elective_courses': [],
                    'course_descriptions': {},
                    'concentration_tracks': []
                }
            }
            
            # Get the expanded content
            print('<view_browser reload_window="False" />')
            page_content = self.get_browser_content()
            if not page_content:
                return None
                
            soup = BeautifulSoup(page_content, 'html.parser')
            
            # Extract department from school field
            program_info['department'] = program_data.get('school', '').replace('School of ', '')
            
            # Extract application deadlines
            deadlines = program_data.get('deadlines', {})
            if deadlines:
                # Get the earliest deadline
                earliest_deadline = min(deadlines.values(), default=None)
                program_info['admission_requirements']['application_deadline'] = earliest_deadline
            
            # Extract testing requirements
            testing_reqs = program_data.get('testingReqs', {})
            if testing_reqs:
                gre_general = testing_reqs.get('GRE General', '').lower()
                program_info['admission_requirements']['gre_required'] = 'required' in gre_general
            
            # Extract program URL and bulletin URL
            program_url = program_data.get('programUrl')
            bulletin_url = program_data.get('bulletinUrl')
            
            # Use JavaScript to extract course information from bulletin URL if available
            if bulletin_url:
                print(f'<navigate_browser url="{bulletin_url}"/>')
                print('''<run_javascript_browser>
                const courseInfo = {
                    core: [],
                    elective: [],
                    descriptions: {},
                    tracks: []
                };
                
                // Find course lists
                document.querySelectorAll('h3, h4').forEach(header => {
                    const text = header.textContent.toLowerCase();
                    if (text.includes('required') || text.includes('core')) {
                        const list = header.nextElementSibling;
                        if (list && (list.tagName === 'UL' || list.tagName === 'OL')) {
                            courseInfo.core = Array.from(list.querySelectorAll('li')).map(li => li.textContent.trim());
                        }
                    } else if (text.includes('elective')) {
                        const list = header.nextElementSibling;
                        if (list && (list.tagName === 'UL' || list.tagName === 'OL')) {
                            courseInfo.elective = Array.from(list.querySelectorAll('li')).map(li => li.textContent.trim());
                        }
                    } else if (text.includes('concentration') || text.includes('track')) {
                        const list = header.nextElementSibling;
                        if (list && (list.tagName === 'UL' || list.tagName === 'OL')) {
                            courseInfo.tracks = Array.from(list.querySelectorAll('li')).map(li => li.textContent.trim());
                        }
                    }
                });
                
                // Find course descriptions
                document.querySelectorAll('p').forEach(p => {
                    const text = p.textContent;
                    const match = text.match(/^([A-Z]+[ ]*[0-9]+[A-Z]*):\s*(.+)/);
                    if (match) {
                        courseInfo.descriptions[match[1]] = match[2];
                    }
                });
                
                console.log(JSON.stringify(courseInfo, null, 2));
                </run_javascript_browser>''')
                print('<get_browser_console/>')
                
                # Parse course information from console output
                console_output = self.get_browser_console()
                try:
                    course_data = json.loads(console_output.strip())
                    program_info['courses']['core_courses'] = course_data.get('core', [])
                    program_info['courses']['elective_courses'] = course_data.get('elective', [])
                    program_info['courses']['course_descriptions'] = course_data.get('descriptions', {})
                    program_info['courses']['concentration_tracks'] = course_data.get('tracks', [])
                except json.JSONDecodeError:
                    self.logger.error("Failed to parse course information from bulletin")
            
            # Generate program_id
            if program_info['degree_name']:
                program_info['program_id'] = f"stanford_{program_info['degree_name'].lower().replace(' ', '_').replace('(', '').replace(')', '')}"
            
            return program_info
            
        except Exception as e:
            self.logger.error(f"Error extracting program info: {str(e)}")
            return None
