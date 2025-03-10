document.addEventListener('DOMContentLoaded', function() {
    // Keep utility functions for potential future use
    
    /**
     * Display an alert message to the user
     * @param {string} message - The message to display
     * @param {string} type - The alert type (success, danger, warning, info)
     */
    function showAlert(message, type) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.querySelector('.dashboard-container').prepend(alertDiv);

        // Auto-dismiss after 3 seconds
        setTimeout(() => {
            alertDiv.remove();
        }, 3000);
    }

    /**
     * Display empty state when no predictions exist
     */
    function showEmptyState() {
        const emptyState = `
            <div class="empty-history">
                <i class="fas fa-history"></i>
                <h4>No Predictions Yet</h4>
                <p>Your prediction history will appear here</p>
            </div>
        `;
        document.querySelector('.prediction-history').innerHTML = emptyState;
    }

    /**
     * Get a cookie value by name
     * @param {string} name - The name of the cookie
     * @returns {string|undefined} - The cookie value or undefined
     */
    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }
    
    // Check if prediction history is empty on page load
    if (document.querySelectorAll('.prediction-item').length === 0) {
        showEmptyState();
    }
}); 