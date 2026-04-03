import requests

# Test login as admin
base_url = 'http://localhost:5000'

# Admin login
admin_data = {
    'role': 'admin',
    'email': 'admin@campus.edu',
    'password': 'admin123'
}

session = requests.Session()

try:
    # Login as admin
    login_response = session.post(f'{base_url}/api/login', json=admin_data)
    print(f'Admin login response: {login_response.status_code}')
    login_result = login_response.json()
    print(f'Admin login data: {login_result}')

    if login_response.status_code == 200:
        # Get admin notifications
        notif_response = session.get(f'{base_url}/api/admin/notifications')
        print(f'Admin notifications response: {notif_response.status_code}')
        if notif_response.status_code == 200:
            notif_result = notif_response.json()
            print(f'Admin notifications count: {len(notif_result.get("notifications", []))}')
        
        # Try student notifications with admin session (should fail)
        student_notif = session.get(f'{base_url}/api/student/notifications')
        print(f'Student notifications with admin session: {student_notif.status_code}')

except Exception as e:
    print(f'Error: {e}')