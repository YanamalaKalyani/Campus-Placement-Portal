// Main JavaScript file
document.addEventListener('DOMContentLoaded', function() {
    // Check if user is already logged in on landing page
    const user = localStorage.getItem('user');
    if (user && window.location.pathname === '/index.html' || window.location.pathname === '/') {
        const userData = JSON.parse(user);
        const redirects = {
            admin: '/admin/dashboard.html',
            student: '/student/dashboard.html',
            company: '/company/dashboard.html'
        };
        // Optionally redirect logged in users
        // window.location.href = redirects[userData.role] || '/index.html';
    }
});
