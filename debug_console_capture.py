"""
Debug script for console capture mechanism
"""
import logging
from scraper.base_scraper import BaseScraper
import time

def main():
    # Setup logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger('console_debug')
    
    # Create scraper instance
    scraper = BaseScraper({'name': 'Debug University', 'rank': 999})
    
    # Navigate to test page
    print('<navigate_browser url="https://oge.mit.edu/programs/"/>')
    print('<wait for="browser" seconds="2"/>')
    
    # Initialize console capture
    scraper.initialize_console_capture()
    print('<wait for="browser" seconds="2"/>')
    
    # Test console messages
    print('''<run_javascript_browser>
    (() => {
        // Log test messages
        console.log('DEBUG_MESSAGE_1');
        console.info('DEBUG_MESSAGE_2');
        console.warn('DEBUG_MESSAGE_3');
        
        // Log state
        console.log('Console State:', {
            initialized: window.__consoleInitialized,
            hasMessages: Array.isArray(window.__consoleMessages),
            messageCount: (window.__consoleMessages || []).length,
            messages: window.__consoleMessages
        });
        
        return true;
    })();
    </run_javascript_browser>''')
    print('<wait for="browser" seconds="2"/>')
    
    # Get and log console output
    console_output = scraper.get_browser_console()
    logger.info(f"Console output: {console_output}")
    
    # Verify console state
    print('''<run_javascript_browser>
    (() => {
        return {
            initialized: window.__consoleInitialized,
            hasMessages: Array.isArray(window.__consoleMessages),
            messageCount: (window.__consoleMessages || []).length
        };
    })();
    </run_javascript_browser>''')

if __name__ == '__main__':
    main()
