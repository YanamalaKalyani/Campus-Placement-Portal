// API Base URL
const API_URL = '/api';

// Show alert message
function showAlert(message, type = 'error') {
    const container = document.getElementById('alertContainer');
    if (!container) return;
    
    container.innerHTML = `
        <div class="alert alert-${type}">
            ${message}
        </div>
    `;
    
    setTimeout(() => {
        container.innerHTML = '';
    }, 5000);
}

// Login form handler
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const btn = document.getElementById('loginBtn');
        const btnText = document.getElementById('loginBtnText');
        const spinner = document.getElementById('loginSpinner');
        
        // Show loading state
        btn.disabled = true;
        btnText.textContent = 'Signing in...';
        spinner.classList.remove('hidden');
        
        const formData = new FormData(loginForm);
        const role = formData.get('role');
        const identifier = formData.get('identifier');

        const data = {
            role,
            password: formData.get('password')
        };

        if (role === 'student') {
            data.enrollment_number = identifier;
        } else {
            data.email = identifier;
        }

        try {
            const response = await fetch(`${API_URL}/login`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data),
                credentials: 'include'
            });
            
            const result = await response.json();
            
            if (response.ok) {
                // Store user data
                localStorage.setItem('user', JSON.stringify(result.user));
                
                // Redirect based on role
                const redirects = {
                    admin: 'admin/dashboard.html',
                    student: 'student/dashboard.html',
                    company: 'company/dashboard.html'
                };
                
                window.location.href = redirects[data.role] || 'index.html';
            } else {
                showAlert(result.error || 'Login failed');
            }
        } catch (error) {
            showAlert('Network error. Please try again.');
            console.error('Login error:', error);
        } finally {
            btn.disabled = false;
            btnText.textContent = 'Sign In';
            spinner.classList.add('hidden');
        }
    });
}

// Register form handler
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const btn = document.getElementById('registerBtn');
        const btnText = document.getElementById('registerBtnText');
        const spinner = document.getElementById('registerSpinner');
        
        const formData = new FormData(registerForm);
        
        // Validate passwords match
        if (formData.get('password') !== formData.get('confirmPassword')) {
            showAlert('Passwords do not match');
            return;
        }
        
        // Show loading state
        btn.disabled = true;
        btnText.textContent = 'Creating account...';
        spinner.classList.remove('hidden');
        
        const data = {
            name: formData.get('name'),
            email: formData.get('email'),
            password: formData.get('password'),
            role: formData.get('role')
        };

        // Prevent admin registration through public form
        if (data.role === 'admin') {
            showAlert('Admin registration is not allowed. Use admin login only.');
            return;
        }

        if (data.role === 'student') {
            data.enrollment_number = formData.get('enrollment_number');
            data.branch = formData.get('branch');
            data.cgpa = parseFloat(formData.get('cgpa')) || 0;
            data.phone = formData.get('phone');
        }

        if (data.role === 'company') {
            data.website = formData.get('website');
        }
        
        try {
            const response = await fetch(`${API_URL}/register`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(data),
                credentials: 'include'
            });
            
            const result = await response.json();
            
            if (response.ok) {
                showAlert('Registration successful! Redirecting to login...', 'success');
                setTimeout(() => {
                    window.location.href = `login.html?role=${data.role}`;
                }, 2000);
            } else {
                showAlert(result.error || 'Registration failed');
            }
        } catch (error) {
            showAlert('Network error. Please try again.');
            console.error('Registration error:', error);
        } finally {
            btn.disabled = false;
            btnText.textContent = 'Create Account';
            spinner.classList.add('hidden');
        }
    });
}

// Logout function
async function logout() {
    try {
        await fetch(`${API_URL}/logout`, {
            method: 'POST',
            credentials: 'include'
        });
    } catch (error) {
        console.error('Logout error:', error);
    } finally {
        localStorage.removeItem('user');
        window.location.href = '/index.html';
    }
}

// Check authentication
async function checkAuth(requiredRole = null) {
    try {
        const response = await fetch(`${API_URL}/session`, {
            credentials: 'include'
        });
        
        const result = await response.json();
        
        if (!result.authenticated) {
            window.location.href = '/index.html';
            return null;
        }
        
        if (requiredRole && result.user.role !== requiredRole) {
            window.location.href = '/index.html';
            return null;
        }
        
        return result.user;
    } catch (error) {
        console.error('Auth check error:', error);
        window.location.href = '/index.html';
        return null;
    }
}

// Get current user from localStorage (fallback)
function getCurrentUser() {
    const userData = localStorage.getItem('user');
    return userData ? JSON.parse(userData) : null;
}

// Format currency
function formatCurrency(amount) {
    if (amount >= 100000) {
        return `₹${(amount / 100000).toFixed(1)}L`;
    }
    return `₹${amount.toLocaleString('en-IN')}`;
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        day: '2-digit',
        month: 'short',
        year: 'numeric'
    });
}
