"""
Test script for Stanford scraper
"""
import logging
from scraper.stanford_scraper import StanfordScraper

def test_stanford_scraper():
    # Initialize scraper with university data
    university_data = {
        'name': 'Stanford University',
        'rank': 2,
        'location': 'Stanford, CA',
        'type': 'Private'
    }
    
    scraper = StanfordScraper(university_data)
    print(f"Testing Stanford scraper for {university_data['name']}")
    
    # Navigate to programs page
    print("Navigating to Stanford programs page...")
    command = '<navigate_browser url="https://applygrad.stanford.edu/portal/programs"/>'
    print(command)
    
    # Test program URL finding
    print("\nTesting program URL finding...")
    programs = scraper.find_program_urls("https://applygrad.stanford.edu/portal/programs")
    print(f"\nFound {len(programs)} STEM programs:")
    
    # Display found programs
    for program in programs:
        print(f"\nProgram: {program['name']}")
        print(f"URL: {program['url']}")
        print(f"Button ID: {program['button_id']}")
    
    # Test first program extraction if any programs found
    if programs:
        print("\nTesting program information extraction...")
        program_info = scraper.extract_program_info(programs[0])
        if program_info:
            print("\nExample program information:")
            for key, value in program_info.items():
                if isinstance(value, dict):
                    print(f"\n{key}:")
                    for k, v in value.items():
                        print(f"  {k}: {v}")
                else:
                    print(f"{key}: {value}")
        else:
            print("Failed to extract program information")
    else:
        print("No programs found to test")

if __name__ == '__main__':
    test_stanford_scraper()
