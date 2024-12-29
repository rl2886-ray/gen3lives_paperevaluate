"""
Tests for the MIT scraper implementation
"""
import pytest
from scraper.mit_scraper import MITScraper
import logging
import json
import time

@pytest.fixture(autouse=True)
def setup_logging():
    """Setup logging for all tests"""
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

@pytest.fixture
def scraper(setup_logging):
    """Create a MITScraper instance for testing with browser verification"""
    scraper = MITScraper()
    
    # Initialize browser with robust verification
    test_url = "https://oge.mit.edu/programs/"
    print(f'<navigate_browser url="{test_url}"/>')
    print('<wait for="browser" seconds="5"/>')
    
    # Initialize console capture with robust verification
    scraper.initialize_console_capture()
    
    # Test message capture with verification
    print('''<run_javascript_browser>
    (() => {
        // Verify console state
        const state = {
            initialized: window.__consoleInitialized === true,
            hasMessages: Array.isArray(window.__consoleMessages),
            hasOriginalConsole: typeof window.__originalConsole === 'object',
            consoleWrapped: console.log.toString().includes('wrapConsole')
        };
        
        // Log test messages
        console.log("TEST: Console verification message 1");
        console.info("TEST: Console verification message 2");
        console.warn("TEST: Console verification message 3");
        
        // Return detailed state
        return {
            ...state,
            messageCount: window.__consoleMessages.length,
            messages: window.__consoleMessages
        };
    })();
    </run_javascript_browser>''')
    print('<wait for="browser" seconds="2"/>')
    
    # Check document readiness
    print('''<run_javascript_browser>
    (() => {
        const state = {
            ready: document.readyState === 'complete',
            url: window.location.href,
            title: document.title,
            content: document.body.textContent.length > 0
        };
        console.log("BROWSER_STATE:" + JSON.stringify(state));
        return state;
    })();
    </run_javascript_browser>''')
    print('<wait for="browser" seconds="2"/>')
    
    # Verify console functionality with retries
    marker = f"TEST_MARKER_{int(time.time())}"
    max_retries = 3
    console_output = ""
    
    for attempt in range(max_retries):
        print(f'<run_javascript_browser>console.log("{marker}");</run_javascript_browser>')
        print('<wait for="browser" seconds="2"/>')
        console_output = scraper.get_browser_console()
        
        if console_output and marker in console_output:
            break
            
        print(f"Attempt {attempt + 1} failed, retrying...")
        print('<wait for="browser" seconds="2"/>')
    
    # Take screenshot for debugging
    print('<screenshot_browser>\nVerifying browser initialization\n</screenshot_browser>')
    
    assert console_output and marker in console_output, f"Console not working properly after {max_retries} attempts"
    assert scraper.wait_for_browser(30, check_interval=2), "Browser failed to initialize"
    
    yield scraper
    
    # Cleanup with verification
    print('<run_javascript_browser>window.__consoleMessages = [];</run_javascript_browser>')
    print('<wait for="browser" seconds="2"/>')
    print('<run_javascript_browser>console.clear();</run_javascript_browser>')
    print('<screenshot_browser>\nVerifying cleanup\n</screenshot_browser>')

def test_find_program_urls(scraper):
    """Test finding program URLs"""
    programs = scraper.find_program_urls()
    assert len(programs) > 0, "Should find some STEM programs"
    
    # Test program URL structure
    program = programs[0]
    assert 'url' in program, "Program should have URL"
    assert 'title' in program, "Program should have title"
    assert 'department' in program, "Program should have department"
    assert 'degree_type' in program, "Program should have degree type"
    assert 'application_deadline' in program, "Program should have application deadline"

def test_minimal_program_info(scraper):
    """Test creation of minimal program info"""
    test_data = {
        'title': 'Test Program',
        'url': 'https://example.com',
        'department': 'Test Department',
        'degree_type': 'MS'
    }
    
    result = scraper._create_minimal_program_info(test_data)
    
    # Test basic structure
    required_sections = [
        'university_info',
        'program_info',
        'admission_requirements',
        'financial_info',
        'program_features',
        'courses'
    ]
    for section in required_sections:
        assert section in result, f"Missing section: {section}"
    
    # Test university info
    assert result['university_info']['name'] == "Massachusetts Institute of Technology"
    assert result['university_info']['rank'] == 1
    assert result['university_info']['location'] == "Cambridge, Massachusetts"
    assert result['university_info']['type'] == "Private"
    
    # Test program info structure
    program_info = result['program_info']
    assert program_info['program_id'].startswith('mit_')
    assert program_info['university_id'] == 'mit_001'
    assert program_info['department'] == test_data['department']
    assert program_info['degree_type'] == test_data['degree_type']
    
    # Test field types
    assert isinstance(result['admission_requirements']['other_requirements'], list)
    assert isinstance(result['financial_info']['financial_aid'], list)
    assert isinstance(result['program_features']['specializations'], list)
    assert isinstance(result['courses']['core_courses'], list)

def test_extract_program_info_success(scraper):
    """Test successful program info extraction with proper browser handling"""
    test_program = {
        'title': 'Electrical Engineering and Computer Science',
        'url': 'https://oge.mit.edu/programs/eecs/',
        'department': 'Electrical Engineering and Computer Science',
        'degree_type': 'MS'
    }
    
    # Navigate to program page
    print(f'<navigate_browser url="{test_program["url"]}"/>')
    
    # Wait for page to load and verify browser state
    assert scraper.wait_for_browser(30, check_interval=2), "Failed to load program page"
    
    # Take screenshot for debugging
    print('<screenshot_browser>\nVerifying program page content\n</screenshot_browser>')
    
    # Extract program info with proper browser state
    result = scraper.extract_program_info(test_program)
    
    # Test structure and types
    assert isinstance(result['admission_requirements']['gre_required'], (bool, type(None)))
    assert isinstance(result['admission_requirements']['minimum_gpa'], (float, type(None)))
    assert isinstance(result['financial_info']['financial_aid'], list)
    assert isinstance(result['program_features']['specializations'], list)
    assert isinstance(result['courses']['core_courses'], list)
    assert isinstance(result['courses']['total_credits'], (int, type(None)))
    
    # Test field values
    assert result['program_info']['department'] == test_program['department']
    assert result['program_info']['degree_type'] == test_program['degree_type']
    assert result['program_info']['program_id'].startswith('mit_')

def test_extract_program_info_error_handling(scraper):
    """Test error handling in program info extraction"""
    # Test with invalid URL
    test_program = {
        'title': 'Invalid Program',
        'url': 'https://invalid.url/',
        'department': 'Test Department',
        'degree_type': 'MS'
    }
    
    result = scraper.extract_program_info(test_program)
    assert result is not None, "Should return minimal info on error"
    assert 'university_info' in result
    assert 'program_info' in result
    assert result['program_info']['program_id'].startswith('mit_')
    
    # Test with missing fields
    incomplete_program = {
        'title': 'Incomplete Program'
    }
    result = scraper.extract_program_info(incomplete_program)
    assert result is not None, "Should handle missing fields"
    assert result['program_info']['degree_type'] == 'MS'  # Default value
    
    # Test data structure consistency
    required_sections = [
        'university_info',
        'program_info',
        'admission_requirements',
        'financial_info',
        'program_features',
        'courses'
    ]
    for section in required_sections:
        assert section in result, f"Missing section in error case: {section}"

if __name__ == "__main__":
    pytest.main([__file__])
