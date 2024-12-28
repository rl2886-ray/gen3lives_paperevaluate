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
        self.base_url = "https://applygrad.stanford.edu/portal/programs"
    
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
        soup = self.make_request(base_url)
        if not soup:
            return []
        
        programs = []
        # Find program buttons
        program_buttons = soup.find_all('button', {'type': 'button'})
        
        for button in program_buttons:
            # Get program name from h2 inside button
            h2_elem = button.find('h2')
            if not h2_elem:
                continue
                
            program_name = h2_elem.text.strip()
            # Only include MS programs and check if it's a STEM program
            if '(MS)' in program_name and self.is_stem_program(program_name):
                # Get program details
                program_info = {
                    'name': program_name,
                    'url': base_url,  # Same page, we'll use button clicks
                    'deadline': None,  # Will be extracted after clicking
                    'button_id': button.get('devinid')  # Store button ID for clicking
                }
                programs.append(program_info)
                self.logger.info(f"Found STEM program: {program_name}")
        
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
