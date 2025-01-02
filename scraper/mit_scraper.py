"""
MIT-specific scraper implementation
"""
import json
import logging
import re
import time
from typing import Dict, List, Optional
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from .template_scraper import TemplateScraper

class MITScraper(TemplateScraper):
    def __init__(self):
        super().__init__(
            university_name="Massachusetts Institute of Technology",
            university_id="mit_001",
            rank=1
        )
        self.university['location'] = "Cambridge, Massachusetts"
        self.university['type'] = "Private"
        self.base_url = "https://oge.mit.edu"
        self.programs_url = "https://oge.mit.edu/graduate-admissions/programs/"
    
    # Data-related program detection keywords
    DATA_KEYWORDS = [
        'data', 'analytics', 'statistics', 'machine learning',
        'artificial intelligence', 'computational', 'information systems',
        'business analytics', 'data science', 'quantitative',
        'operations research', 'mathematical', 'computer science',
        'informatics', 'business intelligence', 'predictive analytics',
        'big data', 'data engineering', 'data mining', 'deep learning'
    ]
    
    # Data-related programs at MIT that should be included
    DATA_PROGRAMS = [
        'Operations Research Center',
        'Computational Science and Engineering',
        'Electrical Engineering and Computer Science',
        'Mathematics',
        'Business Analytics',
        'Data Science and Machine Learning',
        'Information Systems',
        'Statistics and Data Science',
        'Technology and Policy Program',
        'System Design and Management'
    ]
    
    def is_data_program(self, program_name: str) -> bool:
        """
        Check if a program is data-related based on its name
        """
        return any(keyword.lower() in program_name.lower() for keyword in self.DATA_KEYWORDS) or \
               any(program.lower() in program_name.lower() for program in self.DATA_PROGRAMS)
    
    def find_program_urls(self) -> List[Dict]:
        """Find all STEM master's program URLs"""
        print(f'<navigate_browser url="{self.base_url}"/>')
        self.wait_for_browser(30)  # Wait for page load
        
        # Execute JavaScript to analyze page structure and extract programs
        self.logger.info("Analyzing page structure and extracting programs...")
        try:
            print('''<run_javascript_browser>
            // Initialize programs array
            const programs = [];
            const figure = document.querySelector('figure');
            const table = figure ? figure.querySelector('table') : null;
            
            if (table) {
                const tbody = table.querySelector('tbody');
                
                const rows = tbody ? Array.from(tbody.querySelectorAll('tr')) : [];
                console.log(`Found ${rows.length} program rows`);
                
                // Define data program detection criteria
                const DATA_KEYWORDS = ['data', 'analytics', 'statistics', 'machine learning',
                    'artificial intelligence', 'computational', 'information systems',
                    'business analytics', 'data science', 'quantitative',
                    'operations research', 'mathematical', 'computer science',
                    'informatics', 'business intelligence', 'predictive analytics',
                    'big data', 'data engineering', 'data mining', 'deep learning'];
                
                const DATA_PROGRAMS = ['Operations Research Center',
                    'Computational Science and Engineering',
                    'Electrical Engineering and Computer Science',
                    'Mathematics', 'Business Analytics',
                    'Data Science and Machine Learning',
                    'Information Systems',
                    'Statistics and Data Science',
                    'Technology and Policy Program',
                    'System Design and Management'];
                
                console.log("=== Processing Programs ===");
                
                // Process each row with detailed logging
                rows.forEach((row, index) => {
                    const cells = row.querySelectorAll('td');
                    console.log(`\nProcessing Row ${index + 1}:`);
                    
                    
                    if (cells.length >= 2) {
                        const programCell = cells[0];
                        const deadlineCell = cells[1];
                        const programLink = programCell.querySelector('a');
                        
                        if (programLink) {
                            const title = programLink.textContent.trim();
                            const url = programLink.href;
                            const deadline = deadlineCell.textContent.trim();
                            
                            console.log(`Program Title: ${title}`);
                            console.log(`Program URL: ${url}`);
                            console.log(`Application Deadline: ${deadline}`);
                            
                            // Detailed STEM check logging
                            const matchingKeywords = DATA_KEYWORDS.filter(kw => 
                                title.toLowerCase().includes(kw.toLowerCase())
                            );
                            const matchingPrograms = DATA_PROGRAMS.filter(p => 
                                title.includes(p)
                            );
                            
                            const isDataProgram = matchingKeywords.length > 0 || matchingPrograms.length > 0;
                            
                            console.log("Data Program Analysis:", {
                                isDataProgram: isDataProgram,
                                matchingKeywords: matchingKeywords,
                                matchingPrograms: matchingPrograms
                            });
                            
                            if (isDataProgram) {
                                console.log(`Found data-related program: ${title}`);
                                try {
                                    // Extract department and degree type from title
                                    const departmentMatch = title.match(/^([^(]+?)(?:[ ]+\\(|$)/);
                                    const degreeMatch = title.match(/\\(([^)]+)\\)/);
                                    
                                    programs.push({
                                        title: title,
                                        url: url,
                                        application_deadline: deadline,
                                        is_stem: true,
                                        department: departmentMatch ? departmentMatch[1].trim() : title,
                                        degree_type: degreeMatch ? degreeMatch[1].trim() : 'Master\'s',
                                        program_id: `mit_${title.toLowerCase().replace(/[^a-z0-9]+/g, '_')}`,
                                        university_id: 'mit_001',
                                        university: 'Massachusetts Institute of Technology',
                                        university_url: 'https://www.mit.edu',
                                        university_location: 'Cambridge, MA',
                                        program_type: 'Graduate',
                                        last_updated: new Date().toISOString()
                                });
                            }
                        }
                    }
                });
                
            } else {
                console.error("No table found on the page");
            }
            
            // Output detailed results
            const results = {
                type: "program_results",
                timestamp: new Date().toISOString(),
                stats: {
                    total_rows_processed: rows.length,
                    total_programs_found: programs.length,
                    data_programs_found: programs.filter(p => p.is_data_program).length
                },
                data_keywords_used: DATA_KEYWORDS,
                data_programs_list: DATA_PROGRAMS,
                programs: programs
            };
            
            console.log("\n=== Extraction Summary ===");
            console.log(`Total rows processed: ${results.stats.total_rows_processed}`);
            console.log(`Total programs found: ${results.stats.total_programs_found}`);
            console.log(`Data-related programs found: ${results.stats.data_programs_found}`);
            
            console.log("\nMIT_SCRAPER_START");
            console.log(JSON.stringify(results, null, 2));
            console.log("MIT_SCRAPER_END");
            </run_javascript_browser>''')
            
            # Wait for JavaScript execution and get console output
            self.wait_for_browser(5)
            print('<get_browser_console/>')
            console_output = self.get_browser_console()
            
            if not console_output:
                return []
                
            # Find the JSON data between markers in console output
            start_marker = "MIT_SCRAPER_START"
            end_marker = "MIT_SCRAPER_END"
            start_idx = console_output.find(start_marker)
            end_idx = console_output.find(end_marker)
            
            if start_idx == -1 or end_idx == -1:
                return []
                
            json_text = console_output[start_idx + len(start_marker):end_idx].strip()
            
            if not json_text:
                return []
            
            try:
                result_data = json.loads(json_text)
                programs_data = result_data.get('programs', [])
                self.logger.info(f"Successfully parsed {len(programs_data)} programs")
            except json.JSONDecodeError as e:
                self.logger.error(f"Failed to parse JSON data: {e}")
                self.logger.debug(f"Raw JSON text: {json_text}")
                return []
            
            
            # Filter for STEM programs and add metadata
            stem_programs = []
            for program in programs_data:
                if self.is_data_program(program['title']):
                    self.logger.info(f"Found data-related program: {program['title']}")
                    program['department'] = program['title']
                    program['degree_type'] = 'MS'
                    program['is_data_program'] = True
                    stem_programs.append(program)
                else:
                    self.logger.debug(f"Skipping non-data-related program: {program['title']}")
            
            self.logger.info(f"Found {len(stem_programs)} STEM programs out of {len(programs_data)} total programs")
            return stem_programs
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON: {e}")
            self.logger.debug(f"Raw JSON text: {json_text}")
            print('<screenshot_browser>\nChecking page state after error\n</screenshot_browser>')
            return []
        except Exception as e:
            self.logger.error(f"Error processing programs: {str(e)}")
            print('<screenshot_browser>\nChecking page state after error\n</screenshot_browser>')
            return []
        
        # Get additional console output for debugging
        print('<get_browser_console/>')
        console_output = self.get_browser_console()
        self.logger.debug("Raw console output (length=%d):", len(console_output))
        self.logger.debug(repr(console_output))  # Use repr to show escape characters
    
    def extract_program_info(self, program_data: Dict) -> Dict:
        """Extract detailed program information"""
        print(f'<navigate_browser url="{program_data["url"]}"/>')
        
        # Wait for page load with content verification
        content_selectors = ['h1, h2, h3, h4', 'p', '.program-content, article']
        for selector in content_selectors:
            if self.wait_for_browser(10, check_interval=1, content_check=selector):
                break
        else:
            return self._create_minimal_program_info(program_data)
            
        print('''<run_javascript_browser>
        function extractProgramInfo() {
            const info = {
                program_info: {
                    title: document.querySelector('h1')?.textContent?.trim() || '',
                    description: Array.from(document.querySelectorAll('p'))
                        .slice(0, 3)
                        .map(p => p.textContent.trim())
                        .join(' '),
                    department: document.querySelector('.department-name')?.textContent?.trim() || '',
                    website: window.location.href
                },
                admission_requirements: [],
                financial_info: [],
                program_features: [],
                courses: []
            };
            
            // Extract section content
            function extractSectionContent(keyword) {
                const section = Array.from(document.querySelectorAll('h2, h3, h4'))
                    .find(h => h.textContent.toLowerCase().includes(keyword));
                if (!section) return [];
                
                const content = [];
                let current = section.nextElementSibling;
                while (current && !['H2', 'H3', 'H4'].includes(current.tagName)) {
                    if (current.tagName === 'P' || current.tagName === 'LI') {
                        content.push(current.textContent.trim());
                    }
                    current = current.nextElementSibling;
                }
                return content;
            }
            
            info.admission_requirements = extractSectionContent('admission');
            
            info.financial_info = extractSectionContent('financial');
            
            // Extract program features
            const featuresSection = Array.from(document.querySelectorAll('h2, h3, h4'))
                .find(h => h.textContent.toLowerCase().includes('program') || 
                          h.textContent.toLowerCase().includes('research') ||
                          h.textContent.toLowerCase().includes('specialization'));
                          
            if (featuresSection) {
                let current = featuresSection.nextElementSibling;
                while (current && !['H2', 'H3', 'H4'].includes(current.tagName)) {
                    if (current.tagName === 'P' || current.tagName === 'LI') {
                        const text = current.textContent.trim();
                        
                        // Check for duration
                        if (text.toLowerCase().includes('year') || text.toLowerCase().includes('semester')) {
                            info.program_features.duration = text;
                        }
                        // Check for format
                        if (text.toLowerCase().includes('online') || 
                            text.toLowerCase().includes('campus') || 
                            text.toLowerCase().includes('hybrid')) {
                            info.program_features.format = text;
                        }
                        // Check for specializations and research areas
                        if (text.toLowerCase().includes('specialization') || 
                            text.toLowerCase().includes('concentration')) {
                            info.program_features.specializations.push(text);
                        }
                        if (text.toLowerCase().includes('research')) {
                            info.program_features.research_areas.push(text);
                        }
                    }
                    current = current.nextElementSibling;
                }
            }
            
            // Extract course information
            const coursesSection = Array.from(document.querySelectorAll('h2, h3, h4'))
                .find(h => h.textContent.toLowerCase().includes('course') || 
                          h.textContent.toLowerCase().includes('curriculum'));
                          
            if (coursesSection) {
                let current = coursesSection.nextElementSibling;
                while (current && !['H2', 'H3', 'H4'].includes(current.tagName)) {
                    if (current.tagName === 'P' || current.tagName === 'LI') {
                        const text = current.textContent.trim();
                        
                        // Check for course codes (MIT format: XX.XXX)
                        const courseCodeMatch = text.match(/([0-9]{1,2}[.][0-9]{3})/g);
                        if (courseCodeMatch) {
                            info.courses.course_codes.push(...courseCodeMatch);
                        }

                        // Check for core courses
                        if (text.toLowerCase().includes('core') || 
                            text.toLowerCase().includes('required')) {
                            info.courses.core_courses.push(text);
                            
                            // Try to extract course description if available
                            const nextSibling = current.nextElementSibling;
                            if (nextSibling && nextSibling.tagName === 'P') {
                                info.courses.course_descriptions.push({
                                    course: text,
                                    description: nextSibling.textContent.trim()
                                });
                            }
                        }
                        
                        // Check for electives
                        if (text.toLowerCase().includes('elective')) {
                            info.courses.electives.push(text);
                        }
                        
                        // Check for prerequisites
                        if (text.toLowerCase().includes('prerequisite') || 
                            text.toLowerCase().includes('pre-requisite') ||
                            text.toLowerCase().includes('required background')) {
                            info.courses.prerequisites.push(text);
                        }
                        
                        // Check for total credits
                        if (text.toLowerCase().includes('credit')) {
                            const creditMatch = text.match(/([0-9]+)[ ]*credits?/i);
                            if (creditMatch) {
                                info.courses.total_credits = parseInt(creditMatch[1]);
                            }
                        }
                    }
                    current = current.nextElementSibling;
                }
            }
            
            return info;
        }
        
        // Execute extraction and log results
        const programInfo = extractProgramInfo();
        console.log("PROGRAM_INFO_START");
        console.log(JSON.stringify(programInfo, null, 2));
        console.log("PROGRAM_INFO_END");
        </run_javascript_browser>''')
        
        # Wait for JavaScript execution and get results
        self.wait_for_browser(5)
        console_output = self.get_browser_console()
        
        if not console_output:
            self.logger.error("Failed to get program information from console")
            return self._create_minimal_program_info(program_data)
            
        # Extract program information from console output
        start_marker = "PROGRAM_INFO_START"
        end_marker = "PROGRAM_INFO_END"
        start_idx = console_output.find(start_marker)
        end_idx = console_output.find(end_marker)
        
        if start_idx == -1 or end_idx == -1:
            self.logger.error("Could not find program info markers in console output")
            return self._create_minimal_program_info(program_data)
            
        try:
            json_text = console_output[start_idx + len(start_marker):end_idx].strip()
            extracted_info = json.loads(json_text)
            
            # Merge extracted info with basic program data
            result = {
                'university_info': {
                    'name': self.university['name'],
                    'rank': self.university['rank'],
                    'location': self.university['location'],
                    'type': self.university['type']
                },
                'program_info': {
                    **program_data,
                    **extracted_info['program_info']
                },
                'admission_requirements': extracted_info['admission_requirements'],
                'financial_info': extracted_info['financial_info'],
                'program_features': extracted_info['program_features'],
                'courses': extracted_info['courses']
            }
            
            self.logger.info(f"Successfully extracted program information for {program_data['title']}")
            return result
            
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse program information JSON: {e}")
            return self._create_minimal_program_info(program_data)
        except Exception as e:
            self.logger.error(f"Error processing program information: {e}")
            return self._create_minimal_program_info(program_data)
            
    def _create_minimal_program_info(self, program_data: Dict) -> Dict:
        """Create minimal program information when full extraction fails"""
        self.logger.warning(f"Creating minimal program info for {program_data['title']}")
        return {
            'university_info': {
                'name': self.university['name'],
                'rank': self.university['rank'],
                'location': self.university['location'],
                'type': self.university['type']
            },
            'program_info': {
                'program_id': program_data.get('program_id', f"mit_{int(time.time())}"),
                'university_id': 'mit_001',
                'department': program_data.get('department', ''),
                'degree_name': program_data.get('title', ''),
                'degree_type': program_data.get('degree_type', 'Master\'s'),
                'application_deadline': program_data.get('application_deadline', '')
            },
            'admission_requirements': {
                'gre_required': None,
                'english_requirements': None,
                'minimum_gpa': None,
                'other_requirements': []
            },
            'financial_info': {
                'tuition': None,
                'financial_aid': [],
                'scholarships': []
            },
            'program_features': {
                'duration': None,
                'format': None,
                'specializations': [],
                'research_areas': []
            },
            'courses': {
                'core_courses': [],
                'electives': [],
                'total_credits': None
            }
        }
        
        print('''<run_javascript_browser>
        function extractProgramInfo() {
            const content = document.querySelector('.entry-content, .program-content');
            if (!content) {
                return self._create_minimal_program_info(program_data);
            }
            
            // Helper function to find content in sections
            const findInSections = (keywords) => {
                const sections = Array.from(content.querySelectorAll('h2, h3, h4, p'));
                const matches = sections
                    .filter(el => keywords.some(kw => el.textContent.toLowerCase().includes(kw.toLowerCase())))
                    .map(el => el.textContent.trim());
                return matches.join(' ').trim();
            };
            
            const result = {
                program_info: {
                    title: document.querySelector('h1')?.textContent?.trim() || document.title,
                    description: Array.from(document.querySelectorAll('p')).slice(0, 3).map(p => p.textContent.trim()).join(' '),
                    department: document.querySelector('.department-name')?.textContent?.trim() || '',
                    website: window.location.href
                },
                admission_requirements: findInSections(['admission', 'requirements', 'GRE', 'TOEFL', 'IELTS', 'GPA']),
                financial_info: findInSections(['tuition', 'cost', 'fees', 'financial aid', 'funding', 'scholarship', 'fellowship'])
                },
                program_features: findInSections(['duration', 'format', 'specialization', 'concentration', 'track', 'research', 'focus'])
                },
                courses: findInSections(['course', 'curriculum', 'elective', 'credit', 'requirement'])
                }
            };
            
            console.log("START_PROGRAM_INFO");
            console.log(JSON.stringify(result, null, 2));
            console.log("END_PROGRAM_INFO");
            return result;
        }
        
        const result = extractProgramInfo();
        result;  // Return the result
        </run_javascript_browser>''')
        
        # Get console output with enhanced error handling and retries
        console_output = None
        max_attempts = 3
        for attempt in range(max_attempts):
            if attempt > 0:
                self.logger.info(f"Retrying program info extraction (attempt {attempt + 1}/{max_attempts})")
                # Clear console and re-run extraction on retry
                print('<run_javascript_browser>console.clear();</run_javascript_browser>')
                time.sleep(2)  # Add delay between retries
            
            # Wait for any pending operations with content verification
            if not self.wait_for_browser(5, check_interval=1, content_check='.entry-content'):
                self.logger.warning(f"Content verification failed on attempt {attempt + 1}")
                continue
            
            # Get console output
            print('<get_browser_console/>')
            console_output = self.get_browser_console()
            
            if not console_output:
                self.logger.warning(f"Empty console output on attempt {attempt + 1}")
                continue
                
            self.logger.debug(f"Attempt {attempt + 1} output length: {len(console_output)}")
            
            if "START_PROGRAM_INFO" in console_output:
                self.logger.info("Successfully captured program info")
                break
            
            # Check for specific error patterns
            if "error" in console_output.lower() or "exception" in console_output.lower():
                self.logger.error(f"Detected error in console output: {console_output[:200]}")
                print('<screenshot_browser>\nChecking page state after console error\n</screenshot_browser>')
            
            self.logger.warning(f"No program info markers (attempt {attempt + 1})")
            
        if not console_output:
            self.logger.error("No console output received for program info")
            print('<screenshot_browser>\nChecking page state after failed program info capture\n</screenshot_browser>')
            return self._create_minimal_program_info(program_data)
            
        self.logger.debug(f"Final program info console output: {repr(console_output)}")
        
        try:
            start_marker = "START_PROGRAM_INFO"
            end_marker = "END_PROGRAM_INFO"
            start_idx = console_output.find(start_marker)
            end_idx = console_output.find(end_marker)
            
            if start_idx == -1 or end_idx == -1:
                self.logger.error("Could not find program info markers in console output")
                print('<screenshot_browser>\nChecking program page state\n</screenshot_browser>')
                return self._create_minimal_program_info(program_data)
                
            json_str = console_output[start_idx + len(start_marker):end_idx].strip()
            program_info = json.loads(json_str)
            
            # Add university info
            program_info['university_info'] = {
                'name': self.university['name'],
                'rank': self.university['rank'],
                'location': self.university['location'],
                'type': self.university['type']
            }
            
            # Validate and standardize program info structure
            if not program_info.get('program_info', {}).get('program_id'):
                program_info['program_info']['program_id'] = program_data.get('program_id', f"mit_{int(time.time())}")
            
            # Ensure all required sections exist with proper structure
            required_sections = {
                'admission_requirements': {
                    'gre_required': None,
                    'english_requirements': None,
                    'minimum_gpa': None,
                    'other_requirements': []
                },
                'financial_info': {
                    'tuition': None,
                    'financial_aid': [],
                    'scholarships': []
                },
                'program_features': {
                    'duration': None,
                    'format': None,
                    'specializations': [],
                    'research_areas': []
                },
                'courses': {
                    'core_courses': [],
                    'electives': [],
                    'total_credits': None,
                    'course_codes': [],
                    'course_descriptions': [],
                    'prerequisites': []
                }
            }
            
            for section, default_structure in required_sections.items():
                if section not in program_info:
                    program_info[section] = default_structure
                else:
                    # Ensure all fields exist in each section
                    for field, default_value in default_structure.items():
                        if field not in program_info[section]:
                            program_info[section][field] = default_value
            
            return program_info
            
        except (json.JSONDecodeError, IndexError) as e:
            self.logger.error(f"Failed to parse program info: {e}")
            self.logger.debug(f"Console output: {console_output}")
            print('<screenshot_browser>\nChecking program page state after error\n</screenshot_browser>')
            return self._create_minimal_program_info(program_data)
        
