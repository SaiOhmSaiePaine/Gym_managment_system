// Hide Settings Tab Script - Removes the non-functional Settings tab from admin dashboard
// Enhanced v1.0: Hide Settings tab that shows "Settings panel will be available soon"

(function() {
    'use strict';
    
    console.log('🔧 Hide Settings Tab - Loading...');
    
    let hideObserver = null;
    
    // Function to hide the settings tab
    function hideSettingsTab() {
        // Look for Settings tab by text content
        const settingsElements = document.querySelectorAll('*');
        let settingsTab = null;
        
        // Find the Settings tab by looking for text content
        for (const element of settingsElements) {
            if (element.textContent && element.textContent.trim() === 'Settings' && 
                element.closest('a, button, div[role="button"]')) {
                settingsTab = element.closest('a, button, div[role="button"]');
                break;
            }
        }
        
        // Also try to find by common Material-UI patterns
        if (!settingsTab) {
            const possibleSelectors = [
                'a[href*="settings"]',
                'button[aria-label*="settings" i]',
                '[data-testid*="settings"]',
                '.MuiListItem-root:has([data-testid*="SettingsIcon"])',
                '.MuiListItemButton-root:has(svg[data-testid*="Settings"])'
            ];
            
            for (const selector of possibleSelectors) {
                try {
                    settingsTab = document.querySelector(selector);
                    if (settingsTab) break;
                } catch (e) {
                    // Ignore selector errors
                }
            }
        }
        
        // If we found the settings tab, hide it
        if (settingsTab) {
            settingsTab.style.display = 'none';
            console.log('✅ Settings tab hidden successfully');
            return true;
        }
        
        // Alternative approach: hide by looking for the settings icon
        const settingsIcons = document.querySelectorAll('svg[data-testid*="Settings"], svg[data-testid="SettingsIcon"]');
        for (const icon of settingsIcons) {
            const tabElement = icon.closest('a, button, .MuiListItem-root, .MuiListItemButton-root');
            if (tabElement) {
                tabElement.style.display = 'none';
                console.log('✅ Settings tab hidden via icon detection');
                return true;
            }
        }
        
        return false;
    }
    
    // Function to add CSS rule to hide settings tab
    function addHideSettingsCss() {
        const style = document.createElement('style');
        style.id = 'hide-settings-tab-style';
        style.textContent = `
            /* Hide Settings tab in admin dashboard */
            a[href*="settings" i]:has(svg),
            button:has(svg[data-testid*="Settings"]),
            .MuiListItem-root:has(svg[data-testid*="Settings"]),
            .MuiListItemButton-root:has(svg[data-testid*="Settings"]) {
                display: none !important;
            }
            
            /* Hide any element containing "Settings" text in sidebar */
            nav a:has(*):has([aria-label*="settings" i]),
            nav button:has(*):has([aria-label*="settings" i]) {
                display: none !important;
            }
        `;
        
        document.head.appendChild(style);
        console.log('✅ Added CSS to hide Settings tab');
    }
    
    // Main function to hide settings tab
    function processSettingsTab() {
        const success = hideSettingsTab();
        
        if (!success) {
            // If direct hiding didn't work, add CSS rules
            addHideSettingsCss();
        }
    }
    
    // Set up observer for dynamic content
    function setupObserver() {
        if (hideObserver) {
            hideObserver.disconnect();
        }
        
        hideObserver = new MutationObserver(function(mutations) {
            let shouldCheck = false;
            mutations.forEach(mutation => {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    // Check if navigation or sidebar content was added
                    for (const node of mutation.addedNodes) {
                        if (node.nodeType === Node.ELEMENT_NODE && 
                            (node.tagName === 'NAV' || 
                             node.querySelector && (node.querySelector('nav') || 
                             node.classList && (node.classList.contains('MuiDrawer') || 
                             node.classList.contains('sidebar'))))) {
                            shouldCheck = true;
                            break;
                        }
                    }
                }
            });
            
            if (shouldCheck) {
                console.log('🔄 Navigation content changed, checking for Settings tab...');
                setTimeout(processSettingsTab, 100);
            }
        });
        
        // Observe the entire document body for changes
        hideObserver.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        console.log('✅ Observer set up for Settings tab removal');
    }
    
    // Initialize when DOM is ready
    function init() {
        console.log('🚀 Initializing Settings tab removal...');
        
        // Add CSS immediately
        addHideSettingsCss();
        
        // Try to hide immediately
        processSettingsTab();
        
        // Set up observer for dynamic content
        setupObserver();
        
        // Also try again after a short delay in case content loads later
        setTimeout(processSettingsTab, 1000);
        setTimeout(processSettingsTab, 3000);
    }
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
    console.log('✅ Hide Settings Tab script loaded');
})(); 