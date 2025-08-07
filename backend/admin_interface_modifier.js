// Admin Interface Modifier - Replace Edit Buttons with Working Delete Buttons
// Enhanced v2.3: Prevents pen icon flash while keeping trash icons visible

(function() {
    'use strict';
    
    console.log('🔧 Admin Interface Modifier - Loading (v2.3)...');
    
    let usersData = [];
    let globalObserver = null;
    let processedButtons = new Set(); // Track processed buttons to avoid re-processing
    let hideStyle = null; // Track the hiding style element
    
    // Immediately hide edit buttons while keeping our delete buttons visible
    function addEditButtonHiding() {
        if (hideStyle) return; // Already added
        
        hideStyle = document.createElement('style');
        hideStyle.id = 'admin-modifier-hide-style';
        hideStyle.textContent = `
            /* Hide original edit buttons immediately */
            button[title*="edit" i]:not([data-delete-button="true"]), 
            button[aria-label*="edit" i]:not([data-delete-button="true"]),
            .MuiIconButton-root:has(svg[data-testid*="edit" i]):not([data-delete-button="true"]),
            button:has(svg[data-testid*="edit" i]):not([data-delete-button="true"]) {
                opacity: 0 !important;
                visibility: hidden !important;
                pointer-events: none !important;
                transition: none !important;
            }
            
            /* Ensure our delete buttons are always visible */
            button[data-delete-button="true"] {
                opacity: 1 !important;
                visibility: visible !important;
                pointer-events: auto !important;
            }
        `;
        document.head.appendChild(hideStyle);
        console.log('✅ Added CSS to hide edit buttons immediately');
    }
    
    // Remove the hiding style when needed
    function removeEditButtonHiding() {
        if (hideStyle) {
            hideStyle.remove();
            hideStyle = null;
            console.log('✅ Removed edit button hiding CSS');
        }
    }
    
    // Fetch users data from API
    async function fetchUsersData() {
        try {
            const response = await fetch('/api/admin/users');
            const data = await response.json();
            usersData = data.users || [];
            console.log(`✅ Fetched ${usersData.length} users from API`);
            return usersData;
        } catch (error) {
            console.error('❌ Failed to fetch users data:', error);
            return [];
        }
    }
    
    // Simplified check if we're on the user management page
    function isUserManagementPage() {
        // Look for user-related table content
        const tableRows = document.querySelectorAll('tr, .MuiTableRow-root, [role="row"]');
        
        // Check for email patterns (strong indicator of user management)
        for (const row of tableRows) {
            const text = row.textContent || row.innerText || '';
            if (text.match(/@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}/)) {
                console.log('🧭 User management page detected (email found)');
                return true;
            }
        }
        
        // Check for typical user management headers
        const headers = document.querySelectorAll('th, .MuiTableCell-head, [role="columnheader"]');
        let hasNameHeader = false;
        let hasEmailHeader = false;
        
        for (const header of headers) {
            const text = (header.textContent || header.innerText || '').toLowerCase();
            if (text.includes('name')) hasNameHeader = true;
            if (text.includes('email')) hasEmailHeader = true;
        }
        
        if (hasNameHeader && hasEmailHeader) {
            console.log('🧭 User management page detected (headers found)');
            return true;
        }
        
        return false;
    }
    
    // Find user ID by matching name or email
    function findUserIdByContent(rowText) {
        for (const user of usersData) {
            if (rowText.includes(user.name) || rowText.includes(user.email)) {
                console.log(`✅ Matched user: ${user.name} (${user.email}) -> ${user.id}`);
                return { id: user.id, name: user.name, email: user.email };
            }
        }
        return null;
    }
    
    // Delete user function
    async function deleteUser(userId, userName, userRow) {
        console.log(`🗑️ Attempting to delete user: ${userName} (${userId})`);
        
        try {
            const response = await fetch(`/api/admin/users/${userId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            if (response.ok) {
                const result = await response.json();
                console.log('✅ User deleted successfully:', result);
                alert(`✅ User "${userName}" deleted successfully!`);
                
                // Remove the row from the table
                if (userRow) {
                    userRow.remove();
                }
                
                // Refresh the users data
                await fetchUsersData();
            } else {
                const error = await response.json();
                console.error('❌ Delete failed:', error);
                alert(`❌ Failed to delete user: ${error.error || 'Unknown error'}`);
            }
        } catch (error) {
            console.error('❌ Delete request failed:', error);
            alert(`❌ Delete request failed: ${error.message}`);
        }
    }
    
    // Replace edit buttons with delete buttons
    function replaceEditButtons() {
        // Only process if we're on the user management page AND have user data
        if (!isUserManagementPage() || usersData.length === 0) {
            console.log('🔍 Not on user management page or no user data available');
            // Remove hiding CSS if not on user management page
            removeEditButtonHiding();
            return;
        }
        
        // Add CSS to hide edit buttons immediately
        addEditButtonHiding();
        
        console.log('🔧 Processing edit buttons on user management page...');
        
        // Look for all buttons that might be edit buttons
        const allButtons = document.querySelectorAll('button, .MuiIconButton-root, [role="button"]');
        let replacedCount = 0;
        
        allButtons.forEach((button, index) => {
            // Skip if already processed (use a more reliable check)
            const buttonId = `btn_${index}_${button.innerHTML?.substring(0, 20)}`;
            if (processedButtons.has(buttonId) || button.getAttribute('data-delete-button') === 'true') return;
            
            // Check if this looks like an edit button
            const buttonHtml = button.innerHTML.toLowerCase();
            const hasEditIcon = buttonHtml.includes('edit') || 
                               buttonHtml.includes('✏️') || 
                               buttonHtml.includes('pencil') ||
                               button.querySelector('svg[data-testid*="edit" i]') ||
                               button.title?.toLowerCase().includes('edit') ||
                               button.getAttribute('aria-label')?.toLowerCase().includes('edit');
            
            if (hasEditIcon) {
                console.log(`🔧 Processing edit button ${index + 1}`);
                
                // Find the parent row
                const userRow = button.closest('tr') || button.closest('.MuiTableRow-root') || button.closest('[role="row"]');
                
                if (userRow) {
                    const rowText = userRow.textContent || userRow.innerText || '';
                    console.log(`🔍 Row text: "${rowText}"`);
                    
                    // Find matching user data
                    const userData = findUserIdByContent(rowText);
                    
                    if (userData) {
                        // Create delete button
                        const deleteButton = document.createElement('button');
                        deleteButton.className = button.className;
                        deleteButton.setAttribute('data-delete-button', 'true'); // Mark as our button
                        deleteButton.style.cssText = `
                            background-color: transparent !important;
                            color: #6b7280 !important;
                            border: none !important;
                            padding: 8px !important;
                            border-radius: 4px !important;
                            cursor: pointer !important;
                            font-size: 18px !important;
                            transition: all 0.2s !important;
                            display: inline-flex !important;
                            align-items: center !important;
                            justify-content: center !important;
                            width: 40px !important;
                            height: 40px !important;
                            opacity: 1 !important;
                            visibility: visible !important;
                            pointer-events: auto !important;
                        `;
                        deleteButton.innerHTML = `
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" style="opacity: 1 !important; visibility: visible !important;">
                                <path d="M3 6h18v2H3V6zm2 3h14l-1 14H6L5 9zm5-6h4v1H10V3z"/>
                                <rect x="9" y="11" width="2" height="6"/>
                                <rect x="13" y="11" width="2" height="6"/>
                            </svg>
                        `;
                        deleteButton.title = 'Remove user';
                        
                        // Add hover effects
                        deleteButton.onmouseover = function() {
                            this.style.backgroundColor = '#f3f4f6 !important';
                            this.style.color = '#ef4444 !important';
                        };
                        deleteButton.onmouseout = function() {
                            this.style.backgroundColor = 'transparent !important';
                            this.style.color = '#6b7280 !important';
                        };
                        
                        // Add click handler
                        deleteButton.onclick = function(e) {
                            e.preventDefault();
                            e.stopPropagation();
                            
                            const confirmMessage = `Are you sure you want to remove "${userData.name}"?\n\nEmail: ${userData.email}\n\nThis will permanently delete the user and all their items.\n\nThis action cannot be undone.`;
                            
                            if (confirm(confirmMessage)) {
                                deleteUser(userData.id, userData.name, userRow);
                            }
                        };
                        
                        // Replace the button
                        button.parentNode.replaceChild(deleteButton, button);
                        processedButtons.add(buttonId);
                        replacedCount++;
                        
                        console.log(`✅ Replaced edit button with delete button for ${userData.name}`);
                    } else {
                        console.log(`❌ Could not find matching user data for row: "${rowText}"`);
                    }
                } else {
                    console.log(`❌ Could not find parent row for button ${index + 1}`);
                }
            }
        });
        
        if (replacedCount > 0) {
            console.log(`🔧 Replaced ${replacedCount} edit buttons with delete buttons`);
        } else {
            console.log('🔍 No edit buttons found to replace');
        }
    }
    
    // Initialize the modifier
    async function init() {
        console.log('🚀 Admin Interface Modifier - Initializing (v2.3)...');
        
        // Remove any existing CSS that might interfere
        const existingStyles = document.querySelectorAll('style[id="admin-modifier-hide-style"]');
        existingStyles.forEach(style => style.remove());
        
        // Wait for users data to load
        await fetchUsersData();
        
        // Immediately add hiding CSS if on user management page
        if (isUserManagementPage()) {
            addEditButtonHiding();
        }
        
        // Initial check and replacement with multiple attempts
        let attempts = 0;
        const maxAttempts = 3;
        
        function attemptReplacement() {
            attempts++;
            console.log(`🔄 Attempt ${attempts}/${maxAttempts} to replace buttons`);
            
            if (isUserManagementPage() && usersData.length > 0) {
                replaceEditButtons();
                console.log('✅ Button replacement completed');
            } else if (attempts < maxAttempts) {
                setTimeout(attemptReplacement, 200);
            } else {
                console.log('⚠️ Max attempts reached, setting up observer only');
            }
        }
        
        // Start initial attempts immediately
        setTimeout(attemptReplacement, 50);
        
        // Set up global observer for navigation changes
        if (globalObserver) {
            globalObserver.disconnect();
        }
        
        globalObserver = new MutationObserver(function(mutations) {
            let shouldCheck = false;
            mutations.forEach(mutation => {
                if (mutation.type === 'childList' && mutation.addedNodes.length > 0) {
                    // Check if significant content was added
                    for (const node of mutation.addedNodes) {
                        if (node.nodeType === Node.ELEMENT_NODE && 
                            (node.tagName === 'TABLE' || node.querySelector && node.querySelector('table') ||
                             node.classList && node.classList.contains('MuiTable-root') || 
                             (node.querySelector && node.querySelector('.MuiTable-root')) ||
                             node.tagName === 'TR' || (node.querySelector && node.querySelector('tr')) ||
                             node.tagName === 'BUTTON' || (node.querySelector && node.querySelector('button')))) {
                            shouldCheck = true;
                            break;
                        }
                    }
                }
            });
            
            if (shouldCheck) {
                console.log('🔄 Content changed, checking for user management page...');
                setTimeout(() => {
                    if (isUserManagementPage() && usersData.length > 0) {
                        console.log('🔄 Re-processing buttons after content change...');
                        processedButtons.clear(); // Clear processed buttons for re-processing
                        replaceEditButtons();
                    } else {
                        // Not on user management page, remove hiding CSS
                        removeEditButtonHiding();
                    }
                }, 100); // Faster response
            }
        });
        
        // Observe the entire document body for navigation changes
        globalObserver.observe(document.body, {
            childList: true,
            subtree: true
        });
        
        console.log('✅ Admin Interface Modifier - Active (v2.3) - Edit button hiding enabled');
    }
    
    // Start when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
    
})(); 