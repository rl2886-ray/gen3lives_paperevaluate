import logging
import time
import json

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def verify_browser_state():
    """Verify browser state and readiness"""
    logger.info("Verifying browser state...")
    
    # First check if we can access the browser
    logger.debug("Checking initial browser access...")
    print('<view_browser reload_window="false"/>')
    print('<wait for="browser" seconds="2"/>')
    
    # Navigate to test page and verify browser is ready
    logger.debug("Navigating to test page...")
    print('<navigate_browser url="https://oge.mit.edu/programs/"/>')
    print('<wait for="browser" seconds="5"/>')
    
    # Check browser state
    logger.debug("Checking browser state...")
    print('''<run_javascript_browser>
    (() => {
        try {
            const state = {
                readyState: document.readyState,
                url: window.location.href,
                hasConsole: typeof console !== 'undefined',
                hasWindow: typeof window !== 'undefined',
                hasDocument: typeof document !== 'undefined',
                time: new Date().toISOString()
            };
            
            // Test console functionality
            console.log('BROWSER_STATE_START');
            console.log(JSON.stringify(state, null, 2));
            console.log('BROWSER_STATE_END');
            
            return {
                state: state,
                success: true,
                timestamp: Date.now()
            };
        } catch (error) {
            console.error('Error checking browser state:', error);
            return {
                error: error.toString(),
                success: false,
                timestamp: Date.now()
            };
        }
    })();
    </run_javascript_browser>''')
    print('<wait for="browser" seconds="3"/>')
    print('<get_browser_console/>')
    print('<wait for="browser" seconds="2"/>')
    print('<wait for="browser" seconds="2"/>')
    print('<get_browser_console/>')

def test_console_capture():
    """Minimal test case for console capture functionality"""
    logger.info("Starting console capture test...")
    
    # First verify browser state
    verify_browser_state()
    logger.debug("Browser verification complete, proceeding with console test...")
    
    # Initialize console capture
    print('''<run_javascript_browser>
    (() => {
        // Reset console state
        window.__devinConsole = {
            messages: [],
            initialized: false
        };
        
        // Store original methods
        const originalConsole = {
            log: console.log.bind(console),
            info: console.info.bind(console),
            warn: console.warn.bind(console),
            error: console.error.bind(console)
        };
        
        // Helper to stringify any type of argument
        function safeStringify(arg) {
            if (typeof arg === 'undefined') return 'undefined';
            if (arg === null) return 'null';
            if (typeof arg === 'object') {
                try {
                    return JSON.stringify(arg);
                } catch (e) {
                    return '[Object]';
                }
            }
            return String(arg);
        }
        
        // Create wrapper for each console method
        function wrapConsole(method) {
            return function() {
                const args = Array.from(arguments).map(safeStringify);
                const msg = args.join(' ');
                window.__devinConsole.messages.push(msg);
                originalConsole[method].apply(console, arguments);
            };
        }
        
        // Override console methods
        console.log = wrapConsole('log');
        console.info = wrapConsole('info');
        console.warn = wrapConsole('warn');
        console.error = wrapConsole('error');
        
        window.__devinConsole.initialized = true;
        console.log("Console override initialized");
        return window.__devinConsole;
    })();
    </run_javascript_browser>''')
    print('<wait for="browser" seconds="2"/>')
    
    # Test console capture with simple messages
    print('''<run_javascript_browser>
    (() => {
        console.log("TEST_MESSAGE_1");
        console.info("TEST_MESSAGE_2");
        console.warn("TEST_MESSAGE_3");
        console.error("TEST_MESSAGE_4");
        return window.__devinConsole;
    })();
    </run_javascript_browser>''')
    print('<wait for="browser" seconds="2"/>')
    
    # Get and verify console output
    logger.info("Getting console output...")
    print('<get_browser_console/>')
    print('<wait for="browser" seconds="1"/>')
    
    # Final verification with explicit console test
    logger.info("Performing final verification...")
    print('''<run_javascript_browser>
    (() => {
        try {
            const state = {
                consoleInitialized: window.__devinConsole?.initialized || false,
                messageCount: window.__devinConsole?.messages?.length || 0,
                messages: window.__devinConsole?.messages || [],
                timestamp: Date.now()
            };
            
            // Test if console is working
            console.log('FINAL_STATE_START');
            console.log(JSON.stringify(state, null, 2));
            console.log('FINAL_STATE_END');
            
            // Test each console method
            console.log('TEST_LOG_' + Date.now());
            console.info('TEST_INFO_' + Date.now());
            console.warn('TEST_WARN_' + Date.now());
            console.error('TEST_ERROR_' + Date.now());
            
            return {
                state: state,
                success: true,
                finalTest: true
            };
        } catch (error) {
            console.error('Error in final verification:', error);
            return {
                error: error.toString(),
                success: false,
                finalTest: true
            };
        }
    })();
    </run_javascript_browser>''')
    print('<get_browser_console/>')

if __name__ == '__main__':
    logger.info("=== Starting Console Capture Test ===")
    test_console_capture()
    logger.info("=== Test Complete ===")
