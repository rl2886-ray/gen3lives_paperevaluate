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
        
        return program_urls
    
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
            'admission_requirements': {},
            'financial_info': {},
            'program_features': {},
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
            
            # Department information
            dept_elem = soup.find('div', {'class': 'department-name'})
            if dept_elem:
                program_info['department'] = dept_elem.text.strip()
            
            # Admission requirements
            admissions_section = soup.find('div', string=lambda text: text and 'Admission Requirements' in text)
            if admissions_section:
                requirements_list = admissions_section.find_next('ul')
                if requirements_list:
                    program_info['admission_requirements'] = {
                        'requirements_list': [li.text.strip() for li in requirements_list.find_all('li')]
                    }
            
            # Course information
            courses_section = soup.find('div', string=lambda text: text and 'Curriculum' in text)
            if courses_section:
                course_lists = courses_section.find_all('ul')
                for course_list in course_lists:
                    courses = [li.text.strip() for li in course_list.find_all('li')]
                    if courses:
                        program_info['courses']['core_courses'].extend(courses)
            
        except Exception as e:
            self.logger.error(f"Error extracting program info from {url}: {str(e)}")
            return None
        
        return program_info
