from scraper.mit_scraper import MITScraper

def test_mit_scraper():
    # Test data for MIT
    mit_data = {
        'rank': 1,
        'name': 'Massachusetts Institute of Technology',
        'location': 'Cambridge, MA',
        'type': 'Private'
    }
    
    # Initialize scraper
    scraper = MITScraper(mit_data)
    
    # Test program URL finding
    print("Testing program URL finding...")
    programs = scraper.find_program_urls(scraper.base_url)
    print(f"\nFound {len(programs)} STEM programs:")
    
    # Display found programs
    for program in programs:
        print(f"\nProgram: {program['name']}")
        print(f"URL: {program['url']}")
        print(f"Application Deadline: {program['deadline']}")
    
    # Test first program extraction if any programs found
    if programs:
        print("\nTesting program information extraction...")
        program_info = scraper.extract_program_info(programs[0]['url'])
        if program_info:
            print("\nExample program information:")
            for key, value in program_info.items():
                print(f"{key}: {value}")
        else:
            print("Failed to extract program information")

if __name__ == "__main__":
    test_mit_scraper()
