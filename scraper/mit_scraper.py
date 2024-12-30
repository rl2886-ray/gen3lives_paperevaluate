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
    
    # STEM program detection keywords
    STEM_KEYWORDS = [
        'engineering', 'computer', 'science', 'technology', 'mathematics', 
        'physics', 'chemistry', 'biology', 'systems', 'robotics', 
        'data', 'computation', 'artificial intelligence', 'machine learning', 
        'aerospace', 'mechanical', 'electrical', 'materials', 
        'biomedical', 'environmental', 'nuclear', 'brain', 'cognitive',
        'computational', 'oceanography', 'operations research',
        'analytics', 'informatics', 'biotechnology', 'bioinformatics',
        'quantum', 'nanotechnology', 'automation'
    ]
    
    # Programs that should be included even if they don't match keywords
    STEM_PROGRAMS = [
        'Aeronautics and Astronautics',
        'Biological Engineering',
        'Brain and Cognitive Sciences',
        'Chemical Engineering',
        'Chemistry',
        'Civil and Environmental Engineering',
        'Computational and Systems Biology',
        'Computational Science and Engineering',
        'Earth, Atmospheric, and Planetary Sciences',
        'Electrical Engineering and Computer Science',
        'Materials Science and Engineering',
        'Mathematics',
        'Mechanical Engineering',
        'Media Arts and Sciences',
        'MIT-WHOI Joint Program in Oceanography',
        'Nuclear Science and Engineering',
        'Operations Research Center',
        'Physics',
        'System Design and Management',
        'Technology and Policy Program'
    ]
    
    def is_stem_program(self, program_name: str) -> bool:
        """
        Check if a program is STEM-related based on its name
        """
        return any(keyword.lower() in program_name.lower() for keyword in self.STEM_KEYWORDS) or \
               any(program.lower() in program_name.lower() for program in self.STEM_PROGRAMS)
    
    def find_program_urls(self) -> List[Dict]:
        """Find all STEM master's program URLs"""
        self.logger.info("Finding MIT program URLs")
        
        # Navigate to programs page and wait for initial load
        print(f'<navigate_browser url="{self.base_url}"/>')
        self.wait_for_browser(60)  # Increased wait time for page load
        
        # Get page content to verify loading
        print('<view_browser reload_window="True" />')
        
        # Wait additional time for dynamic content
        self.wait_for_browser(10)
        
        # Debug page state and verify content
        print('<screenshot_browser>Checking page state after load</screenshot_browser>')
        print('<view_browser reload_window="True" />')  # Force reload to ensure fresh content
        
        # Debug page structure
        print('''<run_javascript_browser>
        // Force any pending console messages to flush
        console.clear();
        console.log("=== Page Analysis ===");
        console.log("URL:", window.location.href);
        console.log("Title:", document.title);
        console.log("Ready State:", document.readyState);
        console.log("Body Length:", document.body.innerHTML.length);
        
        const tables = document.getElementsByTagName('table');
        console.log("Tables found:", tables.length);
        
        if (tables.length > 0) {
            Array.from(tables).forEach((table, i) => {
                console.log(`\nTable ${i + 1}:`);
                console.log("Rows:", table.rows.length);
                console.log("Parent:", table.parentElement.tagName);
                if (table.rows.length > 0) {
                    console.log("First row cells:", table.rows[0].cells.length);
                    console.log("First row content:", Array.from(table.rows[0].cells).map(cell => cell.textContent.trim()));
                }
            });
        } else {
            console.log("\nNo tables found. Analyzing page structure:");
            console.log("Body content preview:", document.body.textContent.substring(0, 500));
        }
        </run_javascript_browser>''')
        # Get console output with improved handling
        console_output = self.get_browser_console()
        if console_output:
            self.logger.debug("Initial page analysis successful")
            self.logger.debug(f"Console output preview: {console_output[:500]}")
        else:
            self.logger.warning("Failed to get initial page analysis")
            print('<screenshot_browser>Checking page state after failed console capture</screenshot_browser>')
            
        print('<view_browser reload_window="True" />')
        
        # Clear console and prepare for program extraction
        print('<run_javascript_browser>console.clear();</run_javascript_browser>')
        self.wait_for_browser(2)
        
        # Execute JavaScript to analyze page structure and extract programs
        self.logger.info("Analyzing page structure and extracting programs...")
        try:
            # Get initial console state for debugging
            print('<get_browser_console/>')
            initial_console = self.get_browser_console()
            self.logger.debug(f"Initial console state: {repr(initial_console)}")
            
            print('''<run_javascript_browser>
            console.clear();
            console.log("=== Starting Program Extraction ===");
            
            // Initialize programs array and debug info
            const programs = [];
            console.log("Programs array initialized");
            
            // Find and verify the programs table
            console.log("Searching for programs table...");
            const figure = document.querySelector('figure');
            console.log("Figure element found:", !!figure);
            
            const table = figure ? figure.querySelector('table') : null;
            console.log("Table element found:", !!table);
            
            if (table) {
                console.log("=== Table Details ===");
                console.log("Parent element:", table.parentElement.tagName);
                console.log("Table HTML:", table.outerHTML.substring(0, 500) + "...");
                console.log("Total rows:", table.rows.length);
                console.log("Header cells:", Array.from(table.querySelector('thead tr').cells).map(cell => cell.textContent.trim()));
                
                // Get and verify tbody rows
                const tbody = table.querySelector('tbody');
                console.log("Tbody element found:", !!tbody);
                console.log("Tbody HTML preview:", tbody ? tbody.outerHTML.substring(0, 500) + "..." : "N/A");
                
                const rows = tbody ? Array.from(tbody.querySelectorAll('tr')) : [];
                console.log(`Found ${rows.length} program rows`);
                
                // Define STEM detection criteria
                const STEM_KEYWORDS = ['engineering', 'computer', 'science', 'technology', 'mathematics', 
                    'physics', 'chemistry', 'biology', 'systems', 'robotics', 'data', 'computation',
                    'artificial intelligence', 'machine learning', 'aerospace', 'mechanical', 'electrical',
                    'materials', 'biomedical', 'environmental', 'nuclear', 'brain', 'cognitive',
                    'computational', 'oceanography', 'operations research', 'analytics', 'informatics',
                    'biotechnology', 'bioinformatics', 'quantum', 'nanotechnology', 'automation'];
                
                const STEM_PROGRAMS = ['Aeronautics and Astronautics', 'Biological Engineering',
                    'Brain and Cognitive Sciences', 'Chemical Engineering', 'Chemistry',
                    'Civil and Environmental Engineering', 'Computational and Systems Biology',
                    'Computational Science and Engineering', 'Earth, Atmospheric, and Planetary Sciences',
                    'Electrical Engineering and Computer Science', 'Materials Science and Engineering',
                    'Mathematics', 'Mechanical Engineering', 'Media Arts and Sciences',
                    'MIT-WHOI Joint Program in Oceanography', 'Nuclear Science and Engineering',
                    'Operations Research Center', 'Physics', 'System Design and Management',
                    'Technology and Policy Program'];
                
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
                            const matchingKeywords = STEM_KEYWORDS.filter(kw => 
                                title.toLowerCase().includes(kw.toLowerCase())
                            );
                            const matchingPrograms = STEM_PROGRAMS.filter(p => 
                                title.includes(p)
                            );
                            
                            const isSTEM = matchingKeywords.length > 0 || matchingPrograms.length > 0;
                            
                            console.log("STEM Analysis:", {
                                isSTEM: isSTEM,
                                matchingKeywords: matchingKeywords,
                                matchingPrograms: matchingPrograms
                            });
                            
                            if (isSTEM) {
                                console.log(`Found STEM program: ${title}`);
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
                    stem_programs_found: programs.filter(p => p.is_stem).length
                },
                stem_keywords_used: STEM_KEYWORDS,
                stem_programs_list: STEM_PROGRAMS,
                programs: programs
            };
            
            console.log("\n=== Extraction Summary ===");
            console.log(`Total rows processed: ${results.stats.total_rows_processed}`);
            console.log(`Total programs found: ${results.stats.total_programs_found}`);
            console.log(`STEM programs found: ${results.stats.stem_programs_found}`);
            
            console.log("\nMIT_SCRAPER_START");
            console.log(JSON.stringify(results, null, 2));
            console.log("MIT_SCRAPER_END");
            </run_javascript_browser>''')
            
            # Wait for JavaScript execution and get console output with retries
            self.wait_for_browser(5)
            
            console_output = None
            for attempt in range(3):
                print('<get_browser_console/>')
                console_output = self.get_browser_console()
                self.logger.debug(f"Attempt {attempt + 1} console output length: {len(console_output) if console_output else 0}")
                self.logger.debug(f"Console output preview: {repr(console_output[:500] if console_output else '')}")
                
                if console_output and "MIT_SCRAPER_START" in console_output:
                    self.logger.info("Found scraper markers in console output")
                    break
                    
                self.logger.warning(f"No markers found in attempt {attempt + 1}, retrying...")
                self.wait_for_browser(2)
            
            if not console_output:
                self.logger.error("No console output received after all attempts")
                print('<screenshot_browser>\nChecking page state after failed console capture\n</screenshot_browser>')
                return []
                
            # Find the JSON data between markers in console output
            start_marker = "MIT_SCRAPER_START"
            end_marker = "MIT_SCRAPER_END"
            start_idx = console_output.find(start_marker)
            end_idx = console_output.find(end_marker)
            
            if start_idx == -1 or end_idx == -1:
                self.logger.error("Could not find scraper markers in console output")
                self.logger.debug("Console output:")
                self.logger.debug(repr(console_output))
                return []
                
            json_text = console_output[start_idx + len(start_marker):end_idx].strip()
            
            if not json_text:
                self.logger.error("Could not find JSON data in console output")
                self.logger.debug("Console output:")
                self.logger.debug(console_output)
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
                if self.is_stem_program(program['title']):
                    self.logger.info(f"Found STEM program: {program['title']}")
                    program['department'] = program['title']
                    program['degree_type'] = 'MS'
                    program['is_stem'] = True
                    stem_programs.append(program)
                else:
                    self.logger.debug(f"Skipping non-STEM program: {program['title']}")
            
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
        """Extract detailed program information with enhanced error handling"""
        self.logger.info(f"Extracting information for program: {program_data['title']}")
        
        # Navigate to program page with enhanced error handling
        print(f'<navigate_browser url="{program_data["url"]}"/>')
        
        # Wait for page load with improved content verification
        content_selectors = [
            '.entry-content',  # Main content container
            'h1, h2, h3, h4',  # Section headers
            'p',              # Paragraphs
            '.program-content, .department-content, article'  # Alternative content containers
        ]
        # Use first selector as primary, others as fallbacks
        for selector in content_selectors:
            if self.wait_for_browser(10, check_interval=1, content_check=selector):
                self.logger.info(f"Page loaded successfully with selector: {selector}")
                break
        else:
            self.logger.error(f"Failed to load program page or verify content: {program_data['url']}")
            print('<screenshot_browser>\nChecking failed program page load\n</screenshot_browser>')
            return self._create_minimal_program_info(program_data)
            
        # Additional verification after successful load
        print('''<run_javascript_browser>
        console.log("Starting program info extraction...");
        
        // Helper function to safely match numbers
        function matchNumber(text, pattern) {
            return text.match(new RegExp(pattern));
        }
        
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
                admission_requirements: {
                    gre_required: null,
                    english_requirements: null,
                    minimum_gpa: null,
                    other_requirements: []
                },
                financial_info: {
                    tuition: null,
                    financial_aid: [],
                    scholarships: []
                },
                program_features: {
                    duration: null,
                    format: null,
                    specializations: [],
                    research_areas: []
                },
                courses: {
                    core_courses: [],
                    electives: [],
                    total_credits: null
                }
            };
            
            // Extract admission requirements
            const admissionSection = Array.from(document.querySelectorAll('h2, h3, h4'))
                .find(h => h.textContent.toLowerCase().includes('admission') || 
                          h.textContent.toLowerCase().includes('requirements'));
                          
            if (admissionSection) {
                const requirements = [];
                let current = admissionSection.nextElementSibling;
                while (current && !['H2', 'H3', 'H4'].includes(current.tagName)) {
                    if (current.tagName === 'P' || current.tagName === 'LI') {
                        const text = current.textContent.trim();
                        requirements.push(text);
                        
                        // Check for specific requirements
                        if (text.toLowerCase().includes('gre')) {
                            info.admission_requirements.gre_required = !text.toLowerCase().includes('not required');
                        }
                        if (text.toLowerCase().includes('toefl') || text.toLowerCase().includes('ielts')) {
                            info.admission_requirements.english_requirements = text;
                        }
                        if (text.toLowerCase().includes('gpa')) {
                            const gpaMatch = text.match(/([0-9]+[.]?[0-9]*)/);
                            if (gpaMatch) {
                                info.admission_requirements.minimum_gpa = parseFloat(gpaMatch[1]);
                            }
                        }
                    }
                    current = current.nextElementSibling;
                }
                info.admission_requirements.other_requirements = requirements;
            }
            
            // Extract financial information
            const financialSection = Array.from(document.querySelectorAll('h2, h3, h4'))
                .find(h => h.textContent.toLowerCase().includes('financial') || 
                          h.textContent.toLowerCase().includes('tuition') ||
                          h.textContent.toLowerCase().includes('cost'));
                          
            if (financialSection) {
                const financialInfo = [];
                let current = financialSection.nextElementSibling;
                while (current && !['H2', 'H3', 'H4'].includes(current.tagName)) {
                    if (current.tagName === 'P' || current.tagName === 'LI') {
                        const text = current.textContent.trim();
                        financialInfo.push(text);
                        
                        // Check for tuition information
                        if (text.toLowerCase().includes('tuition')) {
                            const costMatch = text.match(/[$][0-9,]+/);
                            if (costMatch) {
                                info.financial_info.tuition = costMatch[0];
                            }
                        }
                        // Check for financial aid/scholarships
                        if (text.toLowerCase().includes('fellowship') || 
                            text.toLowerCase().includes('scholarship')) {
                            info.financial_info.scholarships.push(text);
                        }
                        if (text.toLowerCase().includes('financial aid') || 
                            text.toLowerCase().includes('funding')) {
                            info.financial_info.financial_aid.push(text);
                        }
                    }
                    current = current.nextElementSibling;
                }
            }
            
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
        
        # Clear console and prepare for program info extraction
        print('<run_javascript_browser>console.clear();</run_javascript_browser>')
        if not self.wait_for_browser(2):
            return self._create_minimal_program_info(program_data)
            
        # Extract program information using JavaScript with enhanced validation
        print('''<run_javascript_browser>
        console.log("Starting program info extraction with validation...");
        function extractProgramInfo() {
            // Verify page structure and content
            const contentValidation = {
                mainContent: document.querySelector('.entry-content'),
                alternativeContent: document.querySelector('.program-content'),
                headers: document.querySelectorAll('h1, h2, h3, h4'),
                paragraphs: document.querySelectorAll('p'),
                lists: document.querySelectorAll('ul, ol'),
                tables: document.querySelectorAll('table')
            };
            
            console.log("Content validation:", JSON.stringify(contentValidation, (key, value) => {
                if (value instanceof NodeList || value instanceof HTMLCollection) {
                    return Array.from(value).length;
                }
                return value ? true : false;
            }, 2));
            
            const content = contentValidation.mainContent || contentValidation.alternativeContent;
            if (!content) {
                console.error("Could not find main content container");
                return {
                    program_info: {
                        program_id: 'mit_' + Math.random().toString(36).substr(2, 9),
                        university_id: 'mit_001',
                        department: document.title.split('|')[0].trim(),
                        degree_name: document.title,
                        degree_type: 'MS',
                        application_deadline: ''
                    },
                    admission_requirements: {},
                    financial_info: {},
                    program_features: {},
                    courses: {}
                };
            }
            
            // Verify content structure
            if (contentValidation.headers.length < 2 || contentValidation.paragraphs.length < 3) {
                console.error("Page structure validation failed:", {
                    headers: contentValidation.headers.length,
                    paragraphs: contentValidation.paragraphs.length
                });
            }
            
            // Extract text content and sections
            const allText = content.textContent;
            const sections = Array.from(content.querySelectorAll('h2, h3, h4, p'));
            console.log(`Found ${sections.length} content sections`);
            
            // Enhanced helper function to find content in sections with validation
            const findInSections = (keywords, options = {}) => {
                const {
                    requireAll = false,  // Require all keywords to match
                    nearbyParagraphs = 2,  // Include nearby paragraphs for context
                    maxLength = 1000  // Maximum length of combined text
                } = options;
                
                const matches = sections
                    .filter(el => {
                        const text = el.textContent.toLowerCase();
                        return requireAll
                            ? keywords.every(kw => text.includes(kw.toLowerCase()))
                            : keywords.some(kw => text.includes(kw.toLowerCase()));
                    })
                    .map(el => {
                        // Get the element and its nearby paragraphs
                        const element = el;
                        const result = [element.textContent.trim()];
                        
                        // Add nearby paragraphs for context
                        let current = element;
                        for (let i = 0; i < nearbyParagraphs; i++) {
                            const next = current.nextElementSibling;
                            if (next && next.tagName === 'P') {
                                result.push(next.textContent.trim());
                            }
                            current = next;
                        }
                        
                        return result.join(' ');
                    });
                
                console.log(`Found ${matches.length} matches for keywords: ${keywords.join(', ')}`);
                
                // Combine and trim result
                let result = matches.join(' ').trim();
                if (result.length > maxLength) {
                    result = result.substring(0, maxLength) + '...';
                }
                
                return result;
            };
            
            // Helper function to split text into array and clean
            const splitAndClean = (text) => {
                if (!text) return [];
                return text.split(/[,;.]/)
                    .map(s => s.trim())
                    .filter(s => s.length > 0);
            };

            // Helper function to detect boolean requirements
            const detectRequirement = (text, keywords) => {
                if (!text) return null;
                const lowerText = text.toLowerCase();
                return keywords.some(kw => lowerText.includes(kw));
            };

            const result = {
                program_info: {
                    program_id: 'mit_' + document.title.toLowerCase().replace(/[^a-z0-9]+/g, '_'),
                    university_id: 'mit_001',
                    department: document.title.split('|')[0].trim(),
                    degree_name: document.title,
                    degree_type: 'MS',
                    application_deadline: findInSections(['deadline', 'application due', 'applications due'])
                },
                admission_requirements: {
                    gre_required: (() => {
                        const greText = findInSections(['GRE', 'Graduate Record Examination', 'test requirements', 'standardized test'], {
                            nearbyParagraphs: 2,
                            maxLength: 500
                        });
                        
                        // Check for explicit statements about GRE
                        if (/GRE.*(?:not|no longer|waived|optional)/i.test(greText)) {
                            return false;
                        }
                        if (/GRE.*(?:required|mandatory|must)/i.test(greText)) {
                            return true;
                        }
                        
                        // If no clear indication, return null
                        return null;
                    })(),
                    english_requirements: (() => {
                        const englishText = findInSections([
                            'TOEFL', 'IELTS', 'English proficiency', 
                            'language requirement', 'English language'
                        ], {
                            nearbyParagraphs: 2,
                            maxLength: 1000
                        });
                        
                        // Extract specific score requirements
                        const requirements = [];
                        
                        // Check for TOEFL scores
                        const toeflMatch = englishText.match(/TOEFL.*?([0-9]+)/i);
                        if (toeflMatch) {
                            requirements.push(`TOEFL: ${toeflMatch[1]}`);
                        }
                        
                        // Check for IELTS scores
                        const ieltsMatch = englishText.match(/IELTS.*?([0-9]+(?:[.][0-9]+)?)/i);
                        if (ieltsMatch) {
                            requirements.push(`IELTS: ${ieltsMatch[1]}`);
                        }
                        
                        return requirements.length > 0 ? requirements.join('; ') : englishText;
                    })(),
                    minimum_gpa: (() => {
                        const gpaText = findInSections([
                            'GPA', 'grade point average', 'academic performance',
                            'minimum grade', 'academic requirement'
                        ], {
                            nearbyParagraphs: 2,
                            maxLength: 300
                        });
                        
                        // Look for specific GPA patterns
                        const gpaPatterns = [
                            /minimum GPA.*?([0-9]+[.][0-9]+)/i,
                            /GPA.*?([0-9]+[.][0-9]+).*?minimum/i,
                            /([0-9]+[.][0-9]+).*?GPA/i,
                            /grade point average.*?([0-9]+[.][0-9]+)/i
                        ];
                        
                        for (const pattern of gpaPatterns) {
                            const match = gpaText.match(pattern);
                            if (match) {
                                const gpa = parseFloat(match[1]);
                                return gpa >= 2.0 && gpa <= 4.0 ? gpa : null;
                            }
                        }
                        
                        return null;
                    })(),
                    other_requirements: (() => {
                        const reqText = findInSections([
                            'application requirements',
                            'required documents',
                            'prerequisites',
                            'background requirements',
                            'admission criteria',
                            'application materials'
                        ], {
                            nearbyParagraphs: 3,
                            maxLength: 2000
                        });
                        
                        // Try to extract structured requirements
                        const requirements = new Set();
                        const listItems = content.querySelectorAll('ul li, ol li');
                        
                        listItems.forEach(item => {
                            const text = item.textContent.trim();
                            if (text.toLowerCase().includes('require') || 
                                text.toLowerCase().includes('submit') ||
                                text.toLowerCase().includes('application')) {
                                requirements.add(text);
                            }
                        });
                        
                        return Array.from(requirements).length > 0 ? 
                            Array.from(requirements) : 
                            splitAndClean(reqText);
                    })()
                },
                financial_info: {
                    tuition: (() => {
                        const tuitionText = findInSections([
                            'tuition', 'cost', 'fees', 'expenses',
                            'academic year', 'per semester'
                        ], {
                            nearbyParagraphs: 2,
                            maxLength: 500
                        });
                        
                        // Look for currency amounts
                        const amounts = tuitionText.match(/[$][0-9,]+(?:[.][0-9]{2})?/g);
                        if (amounts) {
                            return amounts.join('; ');
                        }
                        
                        // Fallback to the full text if no specific amounts found
                        return tuitionText;
                    })(),
                    financial_aid: (() => {
                        const aidText = findInSections([
                            'financial aid',
                            'funding',
                            'assistantship',
                            'financial support',
                            'funding opportunities'
                        ], {
                            nearbyParagraphs: 3,
                            maxLength: 2000
                        });
                        
                        // Try to extract structured financial aid information
                        const aid = new Set();
                        const listItems = content.querySelectorAll('ul li, ol li');
                        
                        listItems.forEach(item => {
                            const text = item.textContent.toLowerCase();
                            if (text.includes('financial') || 
                                text.includes('funding') || 
                                text.includes('assistantship')) {
                                aid.add(item.textContent.trim());
                            }
                        });
                        
                        return Array.from(aid).length > 0 ? 
                            Array.from(aid) : 
                            splitAndClean(aidText);
                    })(),
                    scholarships: (() => {
                        const scholarshipText = findInSections([
                            'scholarship',
                            'fellowship',
                            'grant',
                            'award',
                            'merit-based'
                        ], {
                            nearbyParagraphs: 3,
                            maxLength: 2000
                        });
                        
                        // Try to extract structured scholarship information
                        const scholarships = new Set();
                        const listItems = content.querySelectorAll('ul li, ol li');
                        
                        listItems.forEach(item => {
                            const text = item.textContent.toLowerCase();
                            if (text.includes('scholarship') || 
                                text.includes('fellowship') || 
                                text.includes('grant') ||
                                text.includes('award')) {
                                scholarships.add(item.textContent.trim());
                            }
                        });
                        
                        return Array.from(scholarships).length > 0 ? 
                            Array.from(scholarships) : 
                            splitAndClean(scholarshipText);
                    })()
                },
                program_features: {
                    duration: findInSections(['duration', 'length', 'time to degree', 'program length', 'completion time'], {
                        nearbyParagraphs: 1,
                        maxLength: 200
                    }),
                    format: findInSections(['format', 'delivery', 'online', 'campus', 'in-person', 'hybrid'], {
                        nearbyParagraphs: 1,
                        maxLength: 200
                    }),
                    specializations: (() => {
                        const specializationText = findInSections([
                            'specialization',
                            'concentration',
                            'track',
                            'focus area',
                            'emphasis',
                            'field of study'
                        ], {
                            nearbyParagraphs: 3,
                            maxLength: 2000
                        });
                        
                        // Try to extract structured specialization information
                        const specializations = [];
                        const listItems = content.querySelectorAll('ul li, ol li');
                        listItems.forEach(item => {
                            const text = item.textContent.toLowerCase();
                            if (text.includes('specialization') || 
                                text.includes('concentration') || 
                                text.includes('track')) {
                                specializations.push(item.textContent.trim());
                            }
                        });
                        
                        return specializations.length > 0 ? specializations : splitAndClean(specializationText);
                    })(),
                    research_areas: (() => {
                        const researchText = findInSections([
                            'research',
                            'research interests',
                            'research focus',
                            'research areas',
                            'research topics',
                            'research groups'
                        ], {
                            nearbyParagraphs: 3,
                            maxLength: 2000
                        });
                        
                        // Try to extract structured research information
                        const researchAreas = [];
                        const listItems = content.querySelectorAll('ul li, ol li');
                        listItems.forEach(item => {
                            const text = item.textContent.toLowerCase();
                            if (text.includes('research') || text.includes('laboratory') || text.includes('lab')) {
                                researchAreas.push(item.textContent.trim());
                            }
                        });
                        
                        return researchAreas.length > 0 ? researchAreas : splitAndClean(researchText);
                    })()
                },
                courses: {
                    core_courses: (() => {
                        const coreText = findInSections([
                            'core course',
                            'required course',
                            'curriculum',
                            'required subjects',
                            'degree requirements'
                        ], {
                            nearbyParagraphs: 3,
                            maxLength: 2000
                        });
                        
                        // Try to extract structured course information
                        const courses = [];
                        const listItems = content.querySelectorAll('ul li, ol li');
                        listItems.forEach(item => {
                            const text = item.textContent;
                            // Look for course codes (e.g., CS 101, EECS-101)
                            if (/[A-Z]{2,4}[-\x20]?[0-9]{3}/i.test(text)) {
                                courses.push(text.trim());
                            }
                        });
                        
                        return courses.length > 0 ? courses : splitAndClean(coreText);
                    })(),
                    electives: (() => {
                        const electiveText = findInSections([
                            'elective',
                            'optional course',
                            'optional subjects',
                            'choose from'
                        ], {
                            nearbyParagraphs: 3,
                            maxLength: 2000
                        });
                        
                        // Try to extract structured elective information
                        const electives = [];
                        const listItems = content.querySelectorAll('ul li, ol li');
                        listItems.forEach(item => {
                            const text = item.textContent.toLowerCase();
                            if ((text.includes('elective') || text.includes('optional')) &&
                                /[A-Z]{2,4}[-\x20]?[0-9]{3}/i.test(item.textContent)) {
                                electives.push(item.textContent.trim());
                            }
                        });
                        
                        return electives.length > 0 ? electives : splitAndClean(electiveText);
                    })(),
                    total_credits: (() => {
                        const creditText = findInSections(['credit', 'unit', 'credit hour', 'credit requirement'], {
                            nearbyParagraphs: 2,
                            maxLength: 500
                        });
                        // Look for numbers followed by "credits" or "units"
                        const creditMatch = creditText.match(/([0-9]+)(?:[ ]*(?:credit|unit|hour)s?)/i);
                        if (creditMatch) {
                            return parseInt(creditMatch[1]);
                        }
                        // Fallback to any number in the text
                        const numberMatch = creditText.match(/([0-9]+)/);
                        return numberMatch ? parseInt(numberMatch[1]) : null;
                    })()
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
        
