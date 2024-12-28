"""
Stanford-specific scraper implementation
"""
from typing import Dict, List, Optional
from urllib.parse import urljoin
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
        self.base_url = "https://exploredegrees.stanford.edu/graduatedegrees/"
    
    def is_stem_program(self, program_name: str) -> bool:
        """
        Check if a program is STEM-related based on its name
        """
        return any(keyword.lower() in program_name.lower() for keyword in self.STEM_KEYWORDS)
    
    def find_program_urls(self, base_url: str) -> List[Dict]:
        """
        Find URLs and basic info for STEM programs at Stanford
        Returns a list of dictionaries containing program URLs and basic information
        """
        # Wait for page to load
        import time
        time.sleep(5)  # Wait for dynamic content to load
        
        # Get page content using browser
        self.logger.info("Attempting to load Stanford programs page...")
        
        # Wait longer for initial page load
        time.sleep(10)
        
        # Get initial page state and inspect structure
        print('<run_javascript_browser>console.log("Page Title:", document.title); console.log("Body Classes:", document.body.className); const programLinks = Array.from(document.querySelectorAll("a")).filter(a => a.href.includes("/schoolofengineering/") || a.href.includes("/schoolofsciences/") || a.href.includes("ms-") || a.href.includes("master-of-science")); console.log("Potential Program Links:", programLinks.length); programLinks.forEach(a => console.log("Program Link:", a.href, "Text:", a.textContent.trim())); document.documentElement.innerHTML;</run_javascript_browser>')
        
        print('<get_browser_console/>')
        
        # Get page content
        soup = self.get_browser_content()
        if not soup:
            self.logger.error("Failed to get initial browser content")
            return []
            
        # Log page analysis
        self.logger.info("Page loaded. Analyzing structure...")
        print('<screenshot_browser>\nAnalyzing page structure after JavaScript inspection\n</screenshot_browser>')
        
        programs = []
        # Try multiple selectors for program elements
        selectors = [
            ('div', {'class': 'program-card'}),
            ('div', {'class': 'degree-program'}),
            ('div', {'role': 'listitem'}),
            ('div', {'class': 'program'}),
            ('tr', {'class': 'program-row'})
        ]
        
        program_elements = []
        for tag, attrs in selectors:
            self.logger.info(f"Trying selector: {tag} with attributes {attrs}")
            elements = soup.find_all(tag, attrs)
            if elements:
                self.logger.info(f"Found {len(elements)} elements with selector {tag}, {attrs}")
                program_elements.extend(elements)
                break
        
        if not program_elements:
            self.logger.warning("No program cards found, trying alternative selectors")
            # Try finding buttons directly
            program_elements = soup.find_all('button')
        
        for element in program_elements:
            # Try to find program name in different possible locations
            program_name = None
            
            # Try h2 first
            h2_elem = element.find('h2')
            if h2_elem:
                program_name = h2_elem.text.strip()
            
            # If no h2, try h3
            if not program_name:
                h3_elem = element.find('h3')
                if h3_elem:
                    program_name = h3_elem.text.strip()
            
            # If still no name, try direct text
            if not program_name:
                program_name = element.text.strip()
            
            if program_name:
                # Log all found programs for debugging
                self.logger.info(f"Found program: {program_name}")
                
                # Only include MS programs and check if it's a STEM program
                if ('MS' in program_name or 'Master of Science' in program_name) and self.is_stem_program(program_name):
                    # Get button ID - try different approaches
                    button_id = None
                    if element.name == 'button':
                        button_id = element.get('devinid')
                    else:
                        # Try to find a button within the element
                        button = element.find('button')
                        if button:
                            button_id = button.get('devinid')
                    
                    if button_id:
                        program_info = {
                            'name': program_name,
                            'url': base_url,  # Same page, we'll use button clicks
                            'button_id': button_id
                        }
                        programs.append(program_info)
                        self.logger.info(f"Found STEM program: {program_name} with button ID: {button_id}")
                    else:
                        self.logger.warning(f"Found STEM program but no button ID: {program_name}")
        
        if not programs:
            self.logger.warning("No STEM programs found. This might indicate a problem with the page structure or loading.")
            # Take a screenshot for debugging
            print('<screenshot_browser>\nChecking page structure for program elements\n</screenshot_browser>')
        
        return programs
    
    def extract_program_info(self, program_data: Dict) -> Optional[Dict]:
        """Extract program information from Stanford program page after clicking the program button"""
        try:
            # Click the program button to expand details
            button_id = program_data['button_id']
            if not button_id:
                self.logger.error("No button ID provided for program")
                return None
                
            # Click the button to expand program details
            self.click_browser(f"devinid={button_id}")
            
            # Initialize program info structure
            program_info = {
                'program_id': None,
                'department': None,
                'degree_name': program_data['name'],
                'degree_type': 'MS',
                'duration': None,
                'credits_required': None,
                'admission_requirements': {
                    'required_documents': [],
                    'standardized_tests': [],
                    'english_proficiency': None,
                    'minimum_gpa': None,
                    'application_deadline': None,
                    'application_fee': None
                },
                'financial_info': {
                    'tuition_per_credit': None,
                    'estimated_total_cost': None,
                    'financial_aid_available': False,
                    'assistantship_available': False
                },
                'program_features': {
                    'specializations': [],
                    'research_areas': [],
                    'faculty_count': None,
                    'student_faculty_ratio': None,
                    'internship_opportunities': False
                },
                'courses': {
                    'core_courses': [],
                    'elective_courses': [],
                    'concentration_tracks': []
                }
            }
            
            # Get the expanded content
            soup = self.get_browser_content()
            if not soup:
                return None
            
            # Extract department
            dept_link = soup.find('a', href=lambda x: x and 'stanford.edu' in x)
            if dept_link:
                program_info['department'] = dept_link.text.strip()
            
            # Extract application deadlines
            deadline_tables = soup.find_all('table')
            for table in deadline_tables:
                headers = table.find_all('th')
                if headers and 'Application Deadline' in [h.text.strip() for h in headers]:
                    rows = table.find_all('tr')[1:]  # Skip header row
                    for row in rows:
                        cols = row.find_all('td')
                        if cols:
                            deadline = cols[-1].text.strip()
                            program_info['admission_requirements']['application_deadline'] = deadline
                            break
            
            # Extract testing requirements
            test_table = soup.find('h3', string='Testing Requirements').find_next('table')
            if test_table:
                rows = test_table.find_all('tr')[1:]  # Skip header row
                for row in rows:
                    cols = row.find_all('td')
                    if cols:
                        gre_general = cols[0].text.strip()
                        gre_subject = cols[1].text.strip()
                        program_info['admission_requirements']['standardized_tests'] = [
                            f"GRE General: {gre_general}",
                            f"GRE Subject: {gre_subject}"
                        ]
            
            # Generate program_id
            if program_info['degree_name']:
                program_info['program_id'] = f"stanford_{program_info['degree_name'].lower().replace(' ', '_').replace('(', '').replace(')', '')}"
            
            return program_info
            
        except Exception as e:
            self.logger.error(f"Error extracting program info: {str(e)}")
            return None
