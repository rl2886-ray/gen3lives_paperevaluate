"""
Test script for Stanford program information extraction
"""
import logging
import unittest
from scraper.stanford_scraper import StanfordScraper

class TestStanfordProgram(unittest.TestCase):
    def setUp(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('scraping_stanford_university.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
        
        # Initialize scraper with university data
        self.university_data = {
            'name': 'Stanford University',
            'rank': 2,
            'location': 'Stanford, CA',
            'type': 'Private'
        }
        self.scraper = StanfordScraper(self.university_data)
        
    def test_program_data_structure(self):
        """Test that program information follows the required data structure"""
        MAX_RETRIES = 3
        TIMEOUT = 15
        
        def wait_for_browser(seconds: int):
            """Helper function to wait for browser with logging"""
            self.logger.info(f"Waiting for {seconds} seconds...")
            print(f'<wait for="browser" seconds="{seconds}"/>')

        self.logger.info("Starting program data structure test")
        
        try:
            # Navigate to programs page
            self.logger.info(f"Navigating to {self.scraper.base_url}")
            print(f'<navigate_browser url="{self.scraper.base_url}"/>')
            wait_for_browser(5)
            
            # Wait for page to load and find filters
            self.logger.info("Finding program URLs and filters")
            programs = self.scraper.find_program_urls(max_retries=MAX_RETRIES, timeout=TIMEOUT)
            
            if not programs:
                self.logger.error("No programs found after applying filters")
                raise RuntimeError("No programs found")
            
            # Verify filter IDs were found
            self.logger.info("Verifying filter IDs")
            self.assertIsNotNone(self.scraper.engineering_filter_id, "Engineering filter ID not found")
            self.assertIsNotNone(self.scraper.ms_filter_id, "MS filter ID not found")
            self.assertIsNotNone(self.scraper.expand_button_id, "Expand button ID not found")
            
            # Verify programs were found
            self.assertGreater(len(programs), 0, "No programs found")
        
            # Test first program's data structure
            self.logger.info("Testing first program's data structure")
            program = programs[0]
            self.logger.info(f"Extracting info for program: {program.get('title', 'Unknown')}")
            
            program_info = None
            for attempt in range(MAX_RETRIES):
                try: 
                    program_info = self.scraper.extract_program_info(program)
                    if program_info:
                        break
                    self.logger.warning(f"Attempt {attempt + 1}: Failed to extract program info")
                    wait_for_browser(3)
                except Exception as e:
                    self.logger.error(f"Attempt {attempt + 1}: Error extracting program info: {str(e)}")
                    if attempt == MAX_RETRIES - 1:
                        raise
                    wait_for_browser(3)
            
            if not program_info:
                raise RuntimeError("Failed to extract program information after all retries")
        
            # Verify all required fields are present
            self.logger.info("Verifying required fields")
            required_fields = {
                'program_id': str,
                'university_id': str,
                'department': str,
                'degree_name': str,
                'degree_type': str,
                'duration': (int, type(None)),
                'credits_required': (int, type(None)),
                'admission_requirements': dict,
                'financial_info': dict,
                'program_features': dict,
                'courses': dict
            }
            
            for field, expected_type in required_fields.items():
                self.assertIn(field, program_info, f"Missing field: {field}")
                if isinstance(expected_type, tuple):
                    self.assertIsInstance(program_info[field], expected_type, 
                        f"Field {field} has wrong type. Expected one of {expected_type}, got {type(program_info[field])}")
                else:
                    self.assertIsInstance(program_info[field], expected_type,
                        f"Field {field} has wrong type. Expected {expected_type}, got {type(program_info[field])}")
            
            # Verify sub-fields in admission_requirements
            admission_fields = {
                'gre_required': bool,
                'minimum_gpa': (float, type(None)),
                'toefl_minimum': (int, type(None)),
                'ielts_minimum': (float, type(None)),
                'application_deadline': str
            }
            
            for field, expected_type in admission_fields.items():
                self.assertIn(field, program_info['admission_requirements'], f"Missing admission field: {field}")
                if isinstance(expected_type, tuple):
                    self.assertIsInstance(program_info['admission_requirements'][field], expected_type,
                        f"Admission field {field} has wrong type")
                else:
                    self.assertIsInstance(program_info['admission_requirements'][field], expected_type,
                        f"Admission field {field} has wrong type")
            
            # Verify sub-fields in financial_info
            financial_fields = {
                'tuition_per_credit': (float, type(None)),
                'estimated_total_cost': (float, type(None)),
                'financial_aid_available': bool,
                'assistantship_available': bool
            }
            
            for field, expected_type in financial_fields.items():
                self.assertIn(field, program_info['financial_info'], f"Missing financial field: {field}")
                if isinstance(expected_type, tuple):
                    self.assertIsInstance(program_info['financial_info'][field], expected_type,
                        f"Financial field {field} has wrong type")
                else:
                    self.assertIsInstance(program_info['financial_info'][field], expected_type,
                        f"Financial field {field} has wrong type")
            
            # Verify sub-fields in program_features
            feature_fields = {
                'specializations': list,
                'internship_opportunities': bool,
                'research_areas': list,
                'faculty_count': (int, type(None)),
                'student_faculty_ratio': (float, type(None))
            }
            
            for field, expected_type in feature_fields.items():
                self.assertIn(field, program_info['program_features'], f"Missing feature field: {field}")
                if isinstance(expected_type, tuple):
                    self.assertIsInstance(program_info['program_features'][field], expected_type,
                        f"Feature field {field} has wrong type")
                else:
                    self.assertIsInstance(program_info['program_features'][field], expected_type,
                        f"Feature field {field} has wrong type")
            
            # Verify sub-fields in courses
            course_fields = {
                'core_courses': list,
                'elective_courses': list,
                'course_descriptions': dict,
                'concentration_tracks': list
            }
            
            for field, expected_type in course_fields.items():
                self.assertIn(field, program_info['courses'], f"Missing course field: {field}")
                self.assertIsInstance(program_info['courses'][field], expected_type,
                    f"Course field {field} has wrong type")

        except Exception as e:
            self.logger.error(f"Test failed: {str(e)}")
            print('''<screenshot_browser>
Capturing browser state after test failure.
Looking for any error messages or unexpected state.
</screenshot_browser>''')
            raise

if __name__ == '__main__':
    unittest.main()
