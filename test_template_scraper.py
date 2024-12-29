"""
Tests for the template scraper
"""
import pytest
from scraper.template_scraper import TemplateScraper


class TestTemplateScraper:
    def test_is_stem_program(self):
        scraper = TemplateScraper("Test University", "test_001", 1)
        
        # Test STEM program detection
        assert scraper.is_stem_program("Master of Science in Computer Science")
        assert scraper.is_stem_program("Mechanical Engineering")
        assert scraper.is_stem_program("Data Science and Analytics")
        assert scraper.is_stem_program("Artificial Intelligence")
        
        # Test non-STEM program detection
        assert not scraper.is_stem_program("Master of Arts in History")
        assert not scraper.is_stem_program("Business Administration")
        assert not scraper.is_stem_program("Philosophy")

    def test_scraper_initialization(self):
        university_name = "Test University"
        university_id = "test_001"
        rank = 1
        
        scraper = TemplateScraper(university_name, university_id, rank)
        
        assert scraper.university_name == university_name
        assert scraper.university_id == university_id
        assert scraper.rank == rank
        assert scraper.logger.name == "test_university_scraper"

    def test_unimplemented_methods(self):
        scraper = TemplateScraper("Test University", "test_001", 1)
        
        # Test that unimplemented methods raise NotImplementedError
        with pytest.raises(NotImplementedError):
            scraper.find_program_urls()
            
        with pytest.raises(NotImplementedError):
            scraper.extract_program_info({})
