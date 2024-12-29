"""
Template scraper implementation that other university scrapers can inherit from
"""
import json
import logging
import re
from typing import Dict, List, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .base_scraper import BaseScraper

class TemplateScraper(BaseScraper):
    # Define STEM-related keywords for filtering programs
    STEM_KEYWORDS = {
        'computer', 'data', 'engineering', 'technology', 'science', 'mathematics',
        'physics', 'chemistry', 'biology', 'robotics', 'artificial intelligence',
        'machine learning', 'statistics', 'analytics', 'information systems',
        'computational', 'quantum', 'aerospace', 'mechanical', 'electrical',
        'chemical', 'materials', 'biomedical', 'biotechnology', 'industrial'
    }

    def __init__(self, university_name: str, university_id: str, rank: int):
        """Initialize the scraper with university information"""
        university_data = {
            'name': university_name,
            'rank': rank,
            'location': None,  # Will be set by specific scrapers
            'type': None,  # Will be set by specific scrapers
            'id': university_id
        }
        super().__init__(university_data)
        self.logger = logging.getLogger(f"{university_name.lower().replace(' ', '_')}_scraper")

    def is_stem_program(self, program_title: str) -> bool:
        """Check if a program is STEM-related based on its title"""
        return any(keyword.lower() in program_title.lower() for keyword in self.STEM_KEYWORDS)

    def find_program_urls(self) -> List[Dict]:
        """Find all STEM master's program URLs for the university
        
        Returns:
            List[Dict]: List of program information dictionaries containing:
                - url: Program page URL
                - title: Program title
                - department: Department name
                - degree_type: Type of degree (MS, MEng, etc.)
        """
        raise NotImplementedError("Subclasses must implement find_program_urls")

    def extract_program_info(self, program_data: Dict) -> Optional[Dict]:
        """Extract detailed information for a specific program
        
        Args:
            program_data: Dictionary containing basic program information from find_program_urls
        
        Returns:
            Dict: Program information following the defined structure:
                - university_info
                    - university_id
                    - name
                    - rank
                    - location
                    - type (public/private)
                - program_info
                    - program_id
                    - university_id
                    - department
                    - degree_name
                    - degree_type
                    - duration
                    - credits_required
                - admission_requirements
                    - gre_required
                    - minimum_gpa
                    - toefl_minimum
                    - ielts_minimum
                    - application_deadline
                - financial_info
                    - tuition_per_credit
                    - estimated_total_cost
                    - financial_aid_available
                    - assistantship_available
                - program_features
                    - specializations
                    - internship_opportunities
                    - research_areas
                    - faculty_count
                    - student_faculty_ratio
                - courses
                    - core_courses
                    - elective_courses
                    - course_descriptions
                    - concentration_tracks
        """
        raise NotImplementedError("Subclasses must implement extract_program_info")

    def scrape_programs(self) -> List[Dict]:
        """Main method to scrape all STEM master's programs
        
        Returns:
            List[Dict]: List of program information dictionaries
        """
        programs = []
        try:
            # Find all program URLs
            program_urls = self.find_program_urls()
            self.logger.info(f"Found {len(program_urls)} potential STEM programs")

            # Extract information for each program
            for program_data in program_urls:
                try:
                    if not self.is_stem_program(program_data['title']):
                        continue

                    program_info = self.extract_program_info(program_data)
                    if program_info:
                        programs.append(program_info)
                        self.logger.info(f"Successfully scraped program: {program_data['title']}")
                except Exception as e:
                    self.logger.error(f"Failed to scrape program {program_data['title']}: {str(e)}")
                    continue

            self.logger.info(f"Successfully scraped {len(programs)} STEM programs")
            return programs

        except Exception as e:
            self.logger.error(f"Failed to scrape programs: {str(e)}")
            return []
