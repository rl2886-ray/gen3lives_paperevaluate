#!/usr/bin/env python3
"""
Test script to verify MIT scraper implementation with a real program page
"""
import json
import logging
from scraper.mit_scraper import MITScraper

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('mit_scraper_test')

import json
import pytest
import logging
from scraper.mit_scraper import MITScraper

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def test_mit_scraper_initialization():
    """Test MIT scraper initialization"""
    scraper = MITScraper()
    assert scraper.university['name'] == "Massachusetts Institute of Technology"
    assert scraper.university['rank'] == 1
    assert scraper.university['location'] == "Cambridge, Massachusetts"
    assert scraper.university['type'] == "Private"
    assert scraper.base_url == "https://oge.mit.edu"
    assert scraper.programs_url == "https://oge.mit.edu/graduate-admissions/programs/"

def test_mit_program_list_page():
    """Test MIT program listing page navigation and content loading"""
    scraper = MITScraper()
    
    # Navigate to programs page
    print('<navigate_browser url="https://oge.mit.edu/graduate-admissions/programs/"/>')
    print('<wait for="browser" seconds="5"/>')
    
    # Verify page load
    state = scraper.run_javascript('''
        const state = {
            readyState: document.readyState,
            url: window.location.href,
            bodyLength: document.body.innerHTML.length,
            title: document.title
        };
        return state;
    ''')
    
    assert state and isinstance(state, dict)
    assert state.get('readyState') == 'complete'
    assert 'programs' in state.get('url', '').lower()
    assert state.get('bodyLength', 0) > 0

def test_program_data_extraction():
    """Test program data extraction for a specific MIT program"""
    scraper = MITScraper()
    
    # Navigate to programs page
    print('<navigate_browser url="https://oge.mit.edu/graduate-admissions/programs/"/>')
    print('<wait for="browser" seconds="5"/>')
    
    # Find EECS program
    print('''<run_javascript_browser>
        const eecs_link = Array.from(document.querySelectorAll("a")).find(a => 
            a.textContent.toLowerCase().includes("electrical engineering and computer science"));
        if (eecs_link) {
            console.log("EECS_LINK_START");
            console.log(JSON.stringify({
                title: eecs_link.textContent.trim(),
                url: eecs_link.href,
                application_deadline: eecs_link.closest("tr")?.querySelector("td:nth-child(2)")?.textContent.trim() || ""
            }));
            console.log("EECS_LINK_END");
        } else {
            console.error("EECS program link not found");
        }
    </run_javascript_browser>''')
    
    # Get console output and parse program data
    console_output = scraper.get_browser_console()
    start_idx = console_output.find("EECS_LINK_START")
    end_idx = console_output.find("EECS_LINK_END")
    
    assert start_idx != -1 and end_idx != -1, "Failed to find EECS program link"
    
    program_data = json.loads(console_output[start_idx + len("EECS_LINK_START"):end_idx].strip())
    
    # Extract program information
    result = scraper.extract_program_info(program_data)
    
    # Verify all required fields are present
    assert result is not None, "Program extraction returned None"
    assert isinstance(result, dict), "Program extraction did not return a dictionary"
    
    # Verify top-level structure
    required_sections = ['university_info', 'program_info', 'admission_requirements', 
                        'financial_info', 'program_features', 'courses']
    for section in required_sections:
        assert section in result, f"Missing required section: {section}"
        assert isinstance(result[section], dict), f"Section {section} is not a dictionary"
    
    # Verify university info
    uni_info = result['university_info']
    assert uni_info.get('name') == "Massachusetts Institute of Technology"
    assert uni_info.get('rank') == 1
    assert uni_info.get('location') == "Cambridge, Massachusetts"
    assert uni_info.get('type') == "Private"
    
    # Verify program info structure
    prog_info = result['program_info']
    required_prog_fields = ['title', 'department', 'degree_type', 'application_deadline']
    for field in required_prog_fields:
        assert field in prog_info, f"Missing program info field: {field}"
        assert prog_info[field] is not None, f"Program info field is None: {field}"
    
    # Verify admission requirements structure
    adm_req = result['admission_requirements']
    required_adm_fields = ['gre_required', 'english_requirements', 'minimum_gpa', 'other_requirements']
    for field in required_adm_fields:
        assert field in adm_req, f"Missing admission requirement field: {field}"
    assert isinstance(adm_req['other_requirements'], list), "other_requirements should be a list"
    
    # Verify financial info structure
    fin_info = result['financial_info']
    required_fin_fields = ['tuition', 'financial_aid', 'scholarships']
    for field in required_fin_fields:
        assert field in fin_info, f"Missing financial info field: {field}"
    assert isinstance(fin_info['financial_aid'], list), "financial_aid should be a list"
    assert isinstance(fin_info['scholarships'], list), "scholarships should be a list"
    
    # Verify program features structure
    features = result['program_features']
    required_feature_fields = ['duration', 'format', 'specializations', 'research_areas']
    for field in required_feature_fields:
        assert field in features, f"Missing program feature field: {field}"
    assert isinstance(features['specializations'], list), "specializations should be a list"
    assert isinstance(features['research_areas'], list), "research_areas should be a list"
    
    # Verify courses structure
    courses = result['courses']
    required_course_fields = ['core_courses', 'electives', 'total_credits']
    for field in required_course_fields:
        assert field in courses, f"Missing course field: {field}"
    assert isinstance(courses['core_courses'], list), "core_courses should be a list"
    assert isinstance(courses['electives'], list), "electives should be a list"

def test_stem_program_detection():
    """Test STEM program detection logic"""
    scraper = MITScraper()
    
    # Test known STEM programs
    assert scraper.is_stem_program("Electrical Engineering and Computer Science")
    assert scraper.is_stem_program("Mechanical Engineering")
    assert scraper.is_stem_program("Mathematics")
    assert scraper.is_stem_program("Physics")
    
    # Test non-STEM programs
    assert not scraper.is_stem_program("History")
    assert not scraper.is_stem_program("Philosophy")
    assert not scraper.is_stem_program("Economics")

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
