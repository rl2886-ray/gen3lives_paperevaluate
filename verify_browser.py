import time
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('browser_verification')

def verify_browser():
    """Verify basic browser functionality and JavaScript execution"""
    logger.info("Starting browser verification...")
    
    # Navigate to blank page
    print('<navigate_browser url="about:blank"/>')
    time.sleep(2)
    
    # Test basic DOM manipulation
    logger.info("Testing DOM manipulation...")
    print('<run_javascript_browser>document.body.innerHTML = "Browser Test Page";</run_javascript_browser>')
    time.sleep(1)
    
    # Take screenshot to verify page content
    print('<screenshot_browser>\nVerifying browser content\n</screenshot_browser>')
    
    # Test console functionality with state verification
    logger.info("Testing console functionality with state verification...")
    
    # Create a state object to store console messages
    state_setup = '''
    window.__testState = {
        messages: [],
        originalConsole: console.log
    };
    
    console.log = function() {
        window.__testState.messages.push(Array.from(arguments).join(' '));
        window.__testState.originalConsole.apply(console, arguments);
    };
    '''
    print(f'<run_javascript_browser>{state_setup}</run_javascript_browser>')
    time.sleep(1)
    
    # Log test messages
    test_message = f"Browser Test: {time.time()}"
    print(f'<run_javascript_browser>console.log("{test_message}");</run_javascript_browser>')
    time.sleep(1)
    
    # Get state and console output
    verify_state = '''
    (function() {
        const state = {
            hasMessages: window.__testState && window.__testState.messages.length > 0,
            messageCount: window.__testState ? window.__testState.messages.length : 0,
            lastMessage: window.__testState && window.__testState.messages.length > 0 
                ? window.__testState.messages[window.__testState.messages.length - 1] 
                : null
        };
        console.log("State verification:", JSON.stringify(state, null, 2));
        return state;
    })();
    '''
    print(f'<run_javascript_browser>{verify_state}</run_javascript_browser>')
    time.sleep(1)
    
    # Get console output
    logger.info("Getting console output...")
    print('<get_browser_console/>')
    time.sleep(1)
    
    # Restore original console
    restore_console = '''
    if (window.__testState && window.__testState.originalConsole) {
        console.log = window.__testState.originalConsole;
        delete window.__testState;
    }
    '''
    print(f'<run_javascript_browser>{restore_console}</run_javascript_browser>')

if __name__ == '__main__':
    verify_browser()
