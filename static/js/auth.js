// Authentication helper functions
const Auth = {
    // Get the token from localStorage
    getToken: function() {
        return localStorage.getItem('access_token');
    },
    
    // Set the token in localStorage and cookie
    setToken: function(token) {
        localStorage.setItem('access_token', token);
        document.cookie = `access_token=${token}; path=/; max-age=1800`;
    },
    
    // Remove the token from localStorage and cookie
    removeToken: function() {
        localStorage.removeItem('access_token');
        document.cookie = 'access_token=; path=/; max-age=0';
    },
    
    // Check if the user is authenticated
    isAuthenticated: function() {
        return !!this.getToken();
    },
    
    // Add the token to the headers of a fetch request
    addTokenToHeaders: function(headers = {}) {
        const token = this.getToken();
        if (token) {
            return {
                ...headers,
                'Authorization': `Bearer ${token}`
            };
        }
        return headers;
    }
};

// Override fetch to automatically add the token to API requests
const originalFetch = window.fetch;
window.fetch = function(url, options = {}) {
    // Only add the token for API requests
    if (url.toString().includes('/api/')) {
        options.headers = Auth.addTokenToHeaders(options.headers || {});
    }
    return originalFetch(url, options);
};

// Check if we're on a protected page and redirect if not authenticated
(function() {
    const currentPath = window.location.pathname;
    const publicPaths = ['/', '/signup', '/login', '/create-test-user'];
    
    if (!Auth.isAuthenticated() && !publicPaths.includes(currentPath)) {
        window.location.href = '/';
    }
})(); 