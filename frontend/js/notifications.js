/**
 * Notifications Module
 * Handles fetching, rendering, and interaction with the notification system.
 */

async function initNotifications() {
    const header = document.querySelector('.top-header');
    if (!header) return;

    // Add notification bell to header
    const userInfo = header.querySelector('.user-info');
    if (!userInfo) return;

    const bellContainer = document.createElement('div');
    bellContainer.className = 'notification-bell-container';
    bellContainer.innerHTML = `
        <button class="notification-bell" id="notificationBell">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
            </svg>
            <span class="notification-badge hidden" id="notificationBadge">0</span>
        </button>
        <div class="notification-dropdown hidden" id="notificationDropdown">
            <div class="dropdown-header">
                <h3>Notifications</h3>
                <button onclick="markAllAsRead()">Mark all as read</button>
            </div>
            <div class="dropdown-list" id="dropdownList">
                <div class="loading-state">Loading...</div>
            </div>
            <div class="dropdown-footer">
                <a href="notifications.html">See all notifications</a>
            </div>
        </div>
    `;

    header.insertBefore(bellContainer, userInfo);

    // Toggle dropdown
    const bellBtn = document.getElementById('notificationBell');
    const dropdown = document.getElementById('notificationDropdown');

    bellBtn.addEventListener('click', (e) => {
        e.stopPropagation();
        dropdown.classList.toggle('hidden');
        if (!dropdown.classList.contains('hidden')) {
            loadDropdownNotifications();
        }
    });

    document.addEventListener('click', () => {
        dropdown.classList.add('hidden');
    });

    dropdown.addEventListener('click', (e) => {
        e.stopPropagation();
    });

    // Initial load
    updateNotificationBadge();
}

async function updateNotificationBadge() {
    try {
        const response = await fetch('/api/student/notifications', { credentials: 'include' });
        if (!response.ok) return;

        const data = await response.json();
        const unreadCount = data.notifications.filter(n => !n.is_read).length;
        
        const badge = document.getElementById('notificationBadge');
        if (badge) {
            if (unreadCount > 0) {
                badge.textContent = unreadCount > 9 ? '9+' : unreadCount;
                badge.classList.remove('hidden');
            } else {
                badge.classList.add('hidden');
            }
        }
    } catch (error) {
        console.error('Error updating badge:', error);
    }
}

async function loadDropdownNotifications() {
    const list = document.getElementById('dropdownList');
    try {
        const response = await fetch('/api/student/notifications', { credentials: 'include' });
        if (!response.ok) throw new Error('Failed to fetch');

        const data = await response.json();
        renderDropdownList(data.notifications.slice(0, 5));
    } catch (error) {
        list.innerHTML = '<div class="empty-state">Failed to load notifications</div>';
    }
}

function renderDropdownList(notifications) {
    const list = document.getElementById('dropdownList');
    if (!notifications || notifications.length === 0) {
        list.innerHTML = '<div class="empty-state">No new notifications</div>';
        return;
    }

    list.innerHTML = notifications.map(notif => `
        <div class="dropdown-item ${notif.is_read ? 'read' : 'unread'}" onclick="markAsRead(${notif.id})">
            <div class="item-icon">
                <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"></path>
                    <path d="M13.73 21a2 2 0 0 1-3.46 0"></path>
                </svg>
            </div>
            <div class="item-content">
                <p class="item-title">${notif.title}</p>
                <p class="item-time">${formatTimeAgo(notif.created_at)}</p>
            </div>
            ${!notif.is_read ? '<span class="unread-dot"></span>' : ''}
        </div>
    `).join('');
}

async function markAsRead(id) {
    try {
        await fetch('/api/student/notifications/read', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ notification_id: id }),
            credentials: 'include'
        });
        updateNotificationBadge();
        loadDropdownNotifications();
    } catch (error) {
        console.error('Error marking as read:', error);
    }
}

async function markAllAsRead() {
    try {
        await fetch('/api/student/notifications/read', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({}),
            credentials: 'include'
        });
        updateNotificationBadge();
        loadDropdownNotifications();
    } catch (error) {
        console.error('Error marking all as read:', error);
    }
}

function formatTimeAgo(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    return `${days}d ago`;
}

// Auto-init for student role
if (window.location.pathname.includes('/student/')) {
    initNotifications();
}
