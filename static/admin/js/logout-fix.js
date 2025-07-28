// Logout Fix for ACAT Admin
// This script detects when user clicks logout and handles the redirect properly

(function() {
    'use strict';
    
    // Function to handle logout redirect
    function handleLogout() {
        console.log('ACAT: Logout detected, redirecting to login...');
        // Clear any existing session data
        if (typeof(Storage) !== "undefined") {
            localStorage.clear();
            sessionStorage.clear();
        }
        
        // Redirect to login page
        window.location.href = '/admin/login/';
    }
    
    // Check if we're on a blank page after logout attempt
    function checkForBlankPage() {
        const body = document.body;
        const content = body.textContent || body.innerText || '';
        
        // If page is essentially empty or just whitespace
        if (content.trim().length < 50 && document.title === '') {
            console.log('ACAT: Blank page detected after logout, redirecting...');
            handleLogout();
            return true;
        }
        
        // Check for logout indicators in URL
        if (window.location.pathname.includes('/admin/logout/')) {
            console.log('ACAT: Logout URL detected, redirecting...');
            setTimeout(handleLogout, 100); // Small delay to ensure proper processing
            return true;
        }
        
        return false;
    }
    
    // Add click handler to logout links
    function addLogoutHandlers() {
        // Find all logout links/buttons
        const logoutLinks = document.querySelectorAll('a[href*="logout"], button[name*="logout"], input[value*="logout"]');
        
        logoutLinks.forEach(function(link) {
            link.addEventListener('click', function(e) {
                console.log('ACAT: Logout link clicked');
                // Allow the default action but set up a fallback
                setTimeout(function() {
                    // Check if we ended up on a blank page
                    if (checkForBlankPage()) {
                        return;
                    }
                    
                    // If still on admin and no clear success, try manual redirect
                    if (window.location.pathname.startsWith('/admin') && 
                        !window.location.pathname.includes('/login/')) {
                        console.log('ACAT: Logout may not have worked properly, forcing redirect...');
                        handleLogout();
                    }
                }, 1000);
            });
        });
    }
    
    // Monitor for navigation changes (SPA-like behavior)
    function setupNavigationMonitoring() {
        let lastUrl = location.href;
        new MutationObserver(() => {
            const url = location.href;
            if (url !== lastUrl) {
                lastUrl = url;
                checkForBlankPage();
                addLogoutHandlers(); // Re-add handlers for new content
            }
        }).observe(document, {subtree: true, childList: true});
    }
    
    // Initialize when DOM is ready
    function init() {
        console.log('ACAT: Logout fix script loaded');
        
        // Check immediately if we're already on a problematic page
        if (checkForBlankPage()) {
            return;
        }
        
        // Add handlers to existing logout elements
        addLogoutHandlers();
        
        // Set up monitoring for dynamic content
        setupNavigationMonitoring();
        
        // Fallback check every 2 seconds for blank pages
        setInterval(function() {
            if (document.body && checkForBlankPage()) {
                return;
            }
        }, 2000);
    }
    
    // Start when document is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
