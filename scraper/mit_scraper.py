"""
MIT-specific scraper implementation
"""
from typing import Dict, List, Optional, Set
from urllib.parse import urljoin
from .base_scraper import BaseScraper

class MITScraper(BaseScraper):
    # Define STEM-related keywords for filtering programs
    STEM_KEYWORDS = {
        'engineering', 'computer', 'science', 'technology', 'mathematics', 
        'physics', 'chemistry', 'biology', 'systems', 'computation',
        'data', 'electrical', 'mechanical', 'materials', 'aerospace',
        'chemical', 'computational', 'nuclear', 'robotics', 'artificial intelligence'
    }
    
    def __init__(self, university_data: Dict):
        super().__init__(university_data)
        self.base_url = "https://oge.mit.edu/graduate-admissions/programs/"
    
    def is_stem_program(self, program_name: str) -> bool:
        """
        Check if a program is STEM-related based on its name
        """
        return any(keyword.lower() in program_name.lower() for keyword in self.STEM_KEYWORDS)
    
    def find_program_urls(self, base_url: str) -> List[Dict]:
        """
        Find URLs and basic info for STEM programs at MIT
        Returns a list of dictionaries containing program URLs and basic information
        """
        soup = self.make_request(base_url)
        if not soup:
            return []
        
        programs = []
        # Find the program table
        table = soup.find('table')
        if not table:
            self.logger.error("Could not find program table")
            return []
            
        # Process each row in the table
        for row in table.find_all('tr')[1:]:  # Skip header row
            cols = row.find_all('td')
            if len(cols) >= 2:
                program_link = cols[0].find('a')
                if program_link:
                    program_name = program_link.text.strip()
                    if self.is_stem_program(program_name):
                        program_info = {
                            'name': program_name,
                            'url': urljoin(base_url, program_link['href']),
                            'deadline': cols[1].text.strip() if len(cols) > 1 else None
                        }
                        programs.append(program_info)
                        self.logger.info(f"Found STEM program: {program_name}")
        
        return programs
    
    def extract_program_info(self, url: str) -> Optional[Dict]:
        """Extract program information from MIT program page"""
        soup = self.make_request(url)
        if not soup:
            return None
        
        program_info = {
            'program_id': None,
            'department': None,
            'degree_name': None,
            'degree_type': None,
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
        
        try:
            # Basic program information
            title_elem = soup.find('h1')
            if title_elem:
                program_info['degree_name'] = title_elem.text.strip()
                program_info['department'] = title_elem.text.strip()  # Use program name as department for now
            
            # Extract application info
            app_fee = soup.find(string=lambda x: x and 'Fee:' in x)
            if app_fee:
                program_info['admission_requirements']['application_fee'] = app_fee.find_next(string=True).strip()
            
            deadline = soup.find(string=lambda x: x and 'Deadline:' in x)
            if deadline:
                program_info['admission_requirements']['application_deadline'] = deadline.find_next(string=True).strip()
            
            # Find all expandable sections
            buttons = soup.find_all('button')
            for button in buttons:
                section_title = button.text.strip()
                section_content = button.find_next(string=True)
                
                if section_content:
                    # Degrees section
                    if 'Degrees' in section_title:
                        degrees = [d.strip() for d in section_content.split('*') if d.strip()]
                        if degrees:
                            program_info['degree_type'] = degrees[0]
                    
                    # Standardized Tests section
                    elif 'Standardized Tests' in section_title:
                        program_info['admission_requirements']['standardized_tests'] = [
                            test.strip() for test in section_content.split('\n') if test.strip()
                        ]
                    
                    # Areas of Research section
                    elif 'Areas of Research' in section_title:
                        program_info['program_features']['research_areas'] = [
                            area.strip() for area in section_content.split('\n') if area.strip()
                        ]
                    
                    # Financial Support section
                    elif 'Financial Support' in section_title:
                        program_info['financial_info']['financial_aid_available'] = True
                        if 'assistantship' in section_content.lower():
                            program_info['financial_info']['assistantship_available'] = True
                    
                    # Application Requirements section
                    elif 'Application Requirements' in section_title:
                        requirements_list = button.find_next('ul')
                        if requirements_list:
                            program_info['admission_requirements']['required_documents'] = [
                                req.text.strip() for req in requirements_list.find_all('li')
                            ]
                            # Check for English proficiency requirement
                            for req in program_info['admission_requirements']['required_documents']:
                                if 'english proficiency' in req.lower():
                                    program_info['admission_requirements']['english_proficiency'] = req
            
            # Generate program_id
            if program_info['degree_name']:
                program_info['program_id'] = f"mit_{program_info['degree_name'].lower().replace(' ', '_')}"
            
        except Exception as e:
            self.logger.error(f"Error extracting program info from {url}: {str(e)}")
            return None
        
        return program_info
