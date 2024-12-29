"""
Stanford-specific scraper implementation
"""
import json
import logging
import re
from typing import Dict, List, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

def parse_console_json(console_output: str) -> Optional[Dict]:
    """Parse JSON from console output"""
    try:
        # Find JSON-like strings in console output
        json_matches = re.findall(r'(\{.*\}|\[.*\])', console_output, re.DOTALL)
        if not json_matches:
            return None
        # Try to parse each match, return the last valid one
        for match in reversed(json_matches):
            try:
                return json.loads(match)
            except json.JSONDecodeError:
                continue
        return None
    except Exception:
        return None

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
        
        self.logger.info(f"[{datetime.now()}] Loading Stanford programs portal...")
        
        # Navigate to the programs portal
        print(f'<navigate_browser url="{self.base_url}"/>')
        time.sleep(5)  # Increased wait for initial page load
        
        # Take screenshot to verify initial page state
        print('''<screenshot_browser>
        Verifying initial page state before applying filters.
        Looking for:
        1. Filter checkboxes
        2. Program listings
        3. Overall page structure
        </screenshot_browser>''')
        
        # Debug page state
        print('''<run_javascript_browser>
        const pageState = {
            filters: Array.from(document.querySelectorAll('input[type="checkbox"]')).map(f => ({
                id: f.getAttribute('devinid'),
                label: f.parentElement?.textContent?.trim(),
                checked: f.checked
            })),
            buttons: Array.from(document.querySelectorAll('button')).map(b => ({
                id: b.getAttribute('devinid'),
                text: b.textContent?.trim(),
                expanded: b.getAttribute('aria-expanded')
            }))
        };
        console.log(JSON.stringify(pageState));
        </run_javascript_browser>''')
        
        # Get console output and parse JSON
        console_output = self.get_browser_console()
        state_data = parse_console_json(console_output)
        
        if state_data:
            self.logger.info(f"Found {len(state_data.get('filters', []))} filters and {len(state_data.get('buttons', []))} buttons")
            
            # Log filter details for debugging
            for f in state_data.get('filters', []):
                self.logger.debug(f"Filter: {f.get('label')} (id={f.get('id')}, checked={f.get('checked')})")
                
            # Log button details for debugging
            for b in state_data.get('buttons', []):
                self.logger.debug(f"Button: {b.get('text')} (id={b.get('id')}, expanded={b.get('expanded')})")
        else:
            self.logger.error("Failed to parse page state")
            self.logger.debug(f"Raw console output: {console_output}")
            
        # Take a screenshot to verify page state
        print('''<screenshot_browser>
        Checking page state after initial load.
        Looking for filter checkboxes and buttons.
        </screenshot_browser>''')
        
        # Click School of Engineering filter (devinid="49")
        self.logger.info("Clicking School of Engineering filter")
        print('<click_browser box="49"/>')
        time.sleep(3)
        
        # Verify Engineering filter applied
        print('''<screenshot_browser>
        Verifying Engineering filter applied.
        Checking if program list has updated.
        </screenshot_browser>''')
        
        # Click MS degree filter (devinid="57")
        self.logger.info("Clicking MS degree filter")
        print('<click_browser box="57"/>')
        time.sleep(3)
        
        # Verify MS filter applied
        print('''<screenshot_browser>
        Verifying MS filter applied.
        Checking if program list shows only MS programs.
        </screenshot_browser>''')
        
        # Click expand all button (devinid="68")
        self.logger.info("Clicking expand all button")
        print('<click_browser box="68"/>')
        time.sleep(5)  # Increased wait for expansion
        
        # Debug expanded state
        print('''<run_javascript_browser>
        const expandedState = {
            totalButtons: document.querySelectorAll('button').length,
            expandedButtons: document.querySelectorAll('button[aria-expanded="true"]').length,
            visibleH2s: document.querySelectorAll('h2').length,
            programButtons: Array.from(document.querySelectorAll('button')).filter(b => b.querySelector('h2')).length
        };
        console.log(JSON.stringify(expandedState));
        </run_javascript_browser>''')
        
        # Get console output and parse JSON
        console_output = self.get_browser_console()
        state_data = parse_console_json(console_output)
        
        if state_data:
            self.logger.info(
                f"Found {state_data.get('totalButtons', 0)} total buttons, "
                f"{state_data.get('expandedButtons', 0)} expanded, "
                f"{state_data.get('programButtons', 0)} program buttons"
            )
            
            if state_data.get('programButtons', 0) == 0:
                self.logger.warning("No program buttons found after expansion")
        else:
            self.logger.error("Failed to parse expanded state")
            self.logger.debug(f"Raw console output: {console_output}")
            
        # Take a screenshot to verify expanded state
        print('''<screenshot_browser>
        Checking expanded state after clicking expand all.
        Looking for expanded program buttons.
        </screenshot_browser>''')
        
        # Extract program information using JavaScript
        self.logger.info("Extracting program information")
        print('''<run_javascript_browser>
        const programs = Array.from(document.querySelectorAll('button')).map(button => {
            const h2 = button.querySelector('h2');
            if (!h2) return null;
            
            const title = h2.textContent.trim();
            if (!title.includes('(MS)')) return null;
            
            const section = button.parentElement;
            return {
                title,
                school: section.querySelector('a[href*="engineering.stanford.edu"]')?.textContent?.trim(),
                programUrl: section.querySelector('a[aria-label*="Program Website"]')?.href,
                bulletinUrl: section.querySelector('a[href*="bulletin.stanford.edu"]')?.href,
                email: section.querySelector('a[href^="mailto"]')?.textContent?.trim(),
                buttonId: button.getAttribute('devinid')
            };
        }).filter(p => p !== null);
        console.log(JSON.stringify(programs));
        </run_javascript_browser>''')
        
        # Get console output and parse JSON
        console_output = self.get_browser_console()
        programs = parse_console_json(console_output)
        
        if not programs:
            self.logger.warning("No MS programs found")
            self.logger.debug(f"Raw console output: {console_output}")
            return []
            
        self.logger.info(f"Found {len(programs)} MS programs")
        for program in programs:
            self.logger.info(f"Found program: {program.get('title', 'Unknown')}")
            self.logger.debug(f"Program details: {json.dumps(program, indent=2)}")
            
        return programs
            
        # Take a screenshot to verify program extraction
        print('''<screenshot_browser>
        Checking program extraction results.
        Looking for MS program buttons and their details.
        </screenshot_browser>''')
        
        print('<get_browser_console/>')
        console_output = self.get_browser_console()
        
        try:
            # Parse program data from console output
            result = json.loads(console_output)
            
            if result.get('type') == 'error':
                self.logger.error(f"Error extracting programs: {result.get('message')}")
                return []
                
            if result.get('type') != 'programs':
                self.logger.error(f"Unexpected result type: {result.get('type')}")
                return []
            
            programs = result.get('data', [])
            
            # Filter for STEM programs
            stem_programs = []
            for program in programs:
                if self.is_stem_program(program['title']):
                    self.logger.info(f"Found STEM program: {program['title']}")
                    stem_programs.append(program)
            
            if not stem_programs:
                self.logger.warning("No STEM programs found")
            else: 
                self.logger.info(f"Found {len(stem_programs)} STEM programs")
            
            return stem_programs
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing program data: {str(e)}")
            self.logger.error(f"Raw console output: {console_output}")
            return []
        except Exception as e:
            self.logger.error(f"Unexpected error: {str(e)}")
            return []
        
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
                    const match = text.match(/^([A-Z]+[ ]*[0-9]+[A-Z]*):[ ]*(.+)/);
                    if (match) {
                        courseInfo.descriptions[match[1]] = match[2];
                    }
                });
                
                console.log(JSON.stringify(courseInfo, null, 2));
                </run_javascript_browser>''')
                # Get console output and parse JSON
                console_output = self.get_browser_console()
                course_info = parse_console_json(console_output)
                
                if course_info:
                    program_info['courses']['core_courses'] = course_info.get('core', [])
                    program_info['courses']['elective_courses'] = course_info.get('elective', [])
                    program_info['courses']['course_descriptions'] = course_info.get('descriptions', {})
                    program_info['courses']['concentration_tracks'] = course_info.get('tracks', [])
                else:
                    self.logger.error("Failed to parse course information from bulletin")
            
            # Generate program_id
            if program_info['degree_name']:
                program_info['program_id'] = f"stanford_{program_info['degree_name'].lower().replace(' ', '_').replace('(', '').replace(')', '')}"
            
            return program_info
            
        except Exception as e:
            self.logger.error(f"Error extracting program info: {str(e)}")
            return None
