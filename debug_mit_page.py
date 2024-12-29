"""
Debug script to inspect MIT programs page structure
"""
from scraper.mit_scraper import MITScraper

def main():
    scraper = MITScraper()
    print('<navigate_browser url="https://oge.mit.edu/graduate-admissions/programs/"/>')
    print('<wait for="browser" seconds="30"/>')
    print('<view_browser />')
    print('<screenshot_browser>\nChecking page structure and content\n</screenshot_browser>')
    
    # Inspect page structure with enhanced debugging and dynamic content handling
    print('''<run_javascript_browser>
    async function waitForElement(selector, maxWait = 30000) {
        return new Promise((resolve, reject) => {
            if (document.querySelector(selector)) {
                return resolve(document.querySelector(selector));
            }
            
            const observer = new MutationObserver(() => {
                if (document.querySelector(selector)) {
                    observer.disconnect();
                    resolve(document.querySelector(selector));
                }
            });
            
            observer.observe(document.body, {
                childList: true,
                subtree: true
            });
            
            setTimeout(() => {
                observer.disconnect();
                reject('Timeout waiting for element');
            }, maxWait);
        });
    }
    
    async function analyzePageStructure() {
        console.log("=== Enhanced Page Structure Analysis ===");
        
        // 1. Document and Page State
        console.log("\n1. Document and Page State:");
        console.log("- Ready State:", document.readyState);
        console.log("- URL:", document.URL);
        console.log("- Has Body:", !!document.body);
        console.log("- Body Children:", document.body?.children.length);
        
        // Wait for potential dynamic content
        try {
            await waitForElement('table, .table, [role="table"], .wp-block-table');
            console.log("- Dynamic content loaded successfully");
        } catch (e) {
            console.log("- Warning: Timeout waiting for table elements");
        }
        
        // 2. Enhanced Table Analysis
        console.log("\n2. Enhanced Table Analysis:");
        const tableSelectors = [
            'table',
            '.table',
            '[role="table"]',
            '.wp-block-table',
            '.programs-table',
            '.degree-programs'
        ];
        
        const tables = Array.from(document.querySelectorAll(tableSelectors.join(', ')));
        console.log("- Tables found:", tables.length);
        tables.forEach((table, i) => {
            console.log(`\nTable ${i + 1}:`);
            console.log("- Tag:", table.tagName);
            console.log("- Class:", table.className);
            console.log("- Role:", table.getAttribute('role'));
            console.log("- Rows:", table.rows?.length || 'N/A');
            console.log("- Parent:", table.parentElement?.tagName);
            console.log("- Parent Class:", table.parentElement?.className);
            
            // Enhanced table content analysis
            if (table.rows?.length > 0) {
                console.log("- Header Row:", table.rows[0]?.textContent?.trim());
                console.log("- Sample Data Row:", table.rows[1]?.textContent?.trim());
            }
            
            // Check for program links within table
            const programLinks = Array.from(table.querySelectorAll('a')).filter(a => 
                a.href.toLowerCase().includes('program') || 
                a.textContent.toLowerCase().includes('program')
            );
            console.log("- Program Links in Table:", programLinks.length);
            
            console.log("- Full HTML Structure:");
            console.log(table.outerHTML);
        });
        
        // 3. Content Structure Analysis
        console.log("\n3. Content Structure Analysis:");
        const mainContent = document.querySelector('main, [role="main"], #main-content, .entry-content');
        console.log("- Main content found:", !!mainContent);
        if (mainContent) {
            const headings = Array.from(mainContent.querySelectorAll('h1, h2, h3, h4'));
            console.log("- Headings found:", headings.length);
            headings.forEach(h => console.log(`  ${h.tagName}: ${h.textContent.trim()}`));
        }
        
        // 4. Program Link Analysis
        console.log("\n4. Program Link Analysis:");
        const programLinks = Array.from(document.querySelectorAll('a')).filter(a => {
            const href = a.href.toLowerCase();
            const text = a.textContent.toLowerCase();
            return (href.includes('program') || href.includes('degree') || 
                    text.includes('program') || text.includes('degree') ||
                    text.includes('master') || text.includes('phd'));
        });
        console.log("- Program-related links found:", programLinks.length);
        programLinks.forEach((link, i) => {
            console.log(`\nProgram Link ${i + 1}:`);
            console.log("- Text:", link.textContent.trim());
            console.log("- URL:", link.href);
            console.log("- Parent:", link.parentElement.tagName);
            console.log("- Parent HTML:", link.parentElement.outerHTML);
        });
        
        // 5. Dynamic Content Analysis
        console.log("\n5. Dynamic Content Analysis:");
        console.log("- iframes:", document.querySelectorAll('iframe').length);
        console.log("- Script tags:", document.querySelectorAll('script').length);
        console.log("- Dynamic containers:", document.querySelectorAll('[id*="content"], [class*="content"]').length);
        console.log("- AJAX requests:", performance.getEntriesByType('resource').filter(r => r.initiatorType === 'xmlhttprequest').length);
        
        // 6. Page Content Sample
        console.log("\n6. Page Content Sample:");
        console.log("First 1000 characters of cleaned text:");
        console.log(document.body.textContent.replace(/\\s+/g, ' ').trim().slice(0, 1000));
    }
    
    analyzePageStructure().catch(console.error);
    </run_javascript_browser>''')
    print('<get_browser_console/>')
    print('<get_browser_console/>')

if __name__ == '__main__':
    main()
