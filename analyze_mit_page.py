from scraper.mit_scraper import MITScraper
import logging

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='analyzing_mit_page.log'
)
logger = logging.getLogger('analyze_mit_page')

def analyze_page():
    """Analyze the MIT graduate programs page structure."""
    scraper = MITScraper()
    logger.info("Starting MIT page analysis")
    
    # Navigate to the page
    print('<navigate_browser url="https://oge.mit.edu/graduate-admissions/programs/"/>')
    print('<wait for="browser" seconds="45"/>')
    
    # Take a screenshot and view the page
    print('<screenshot_browser>Analyzing MIT programs page structure</screenshot_browser>')
    print('<view_browser />')
    
    # Run JavaScript to analyze page structure with better formatting
    print('''<run_javascript_browser>
    (function analyzePage() {
        function logSection(title, content) {
            console.log(`\n=== ${title} ===`);
            console.log(JSON.stringify(content, null, 2));
        }

        // Basic page info
        logSection("Page Info", {
            readyState: document.readyState,
            url: window.location.href,
            title: document.title
        });

        // Analyze page structure
        const structure = {
            tables: Array.from(document.querySelectorAll('table')).map(table => ({
                rows: table.rows.length,
                hasTbody: !!table.querySelector('tbody'),
                headers: Array.from(table.querySelectorAll('th')).map(th => th.textContent.trim()),
                firstRowCells: Array.from(table.rows[0]?.cells || []).map(cell => ({
                    text: cell.textContent.trim(),
                    hasLink: !!cell.querySelector('a')
                }))
            })),
            lists: Array.from(document.querySelectorAll('ul, ol')).map(list => ({
                type: list.tagName.toLowerCase(),
                items: Array.from(list.children).length,
                hasLinks: !!list.querySelector('a'),
                firstItem: list.firstElementChild?.textContent.trim()
            }))
        };

        logSection("Page Structure", structure);

        // Analyze program-related content
        const programContent = {
            programLinks: Array.from(document.querySelectorAll('a')).filter(a => 
                a.href.includes('/programs/') || 
                a.href.includes('/degrees/') ||
                /program|degree|master|phd/i.test(a.textContent)
            ).map(a => ({
                text: a.textContent.trim(),
                href: a.href,
                parent: a.parentElement.tagName,
                container: a.closest('table, ul, ol, div[class*="program"]')?.tagName || 'none'
            })),
            possibleContainers: Array.from(document.querySelectorAll('div[class*="program"], div[class*="degree"], section, article')).map(el => ({
                tag: el.tagName,
                class: el.className,
                childCount: el.children.length,
                hasLinks: !!el.querySelector('a'),
                text: el.textContent.slice(0, 100) + '...'
            }))
        };

        logSection("Program Content", programContent);

        // Check for dynamic content
        const dynamicIndicators = {
            hasReactRoot: !!document.querySelector('#root, [data-reactroot]'),
            hasAngular: !!document.querySelector('[ng-app], [ng-controller]'),
            hasVue: !!document.querySelector('[data-v-]'),
            hasAjaxElements: !!document.querySelector('[data-ajax], [data-remote]'),
            scripts: Array.from(document.scripts).map(s => s.src).filter(Boolean)
        };

        logSection("Dynamic Content Indicators", dynamicIndicators);

        // Look for iframes that might contain program information
        const iframes = Array.from(document.querySelectorAll('iframe')).map(iframe => ({
            src: iframe.src,
            id: iframe.id,
            name: iframe.name
        }));

        logSection("Iframes", iframes);
    })();
    </run_javascript_browser>''')
    
    # Get console output
    print('<get_browser_console/>')

if __name__ == '__main__':
    analyze_page()
