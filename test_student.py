import requests

# Test student login and notifications
base_url = 'http://localhost:5000'

# Student login data
student_data = {
    'role': 'student',
    'enrollment_number': '12302040701139',  # priti bhadja
    'password': 'admin123'  # Try this
}

session = requests.Session()

try:
    # Login as student
    login_response = session.post(f'{base_url}/api/login', json=student_data)
    print(f'Login response: {login_response.status_code}')
    login_result = login_response.json()
    print(f'Login result: {login_result}')

    if login_response.status_code == 200:
        # Get notifications
        notif_response = session.get(f'{base_url}/api/student/notifications')
        print(f'Notifications response: {notif_response.status_code}')
        if notif_response.status_code == 200:
            notif_result = notif_response.json()
            notifications = notif_result.get('notifications', [])
            print(f'Found {len(notifications)} notifications:')
            for notif in notifications:
                print(f'  - {notif["title"]}: {notif["message"][:50]}...')
        else:
            print(f'Notifications error: {notif_response.text}')
    else:
        print('Login failed')

except Exception as e:
    print(f'Error: {e}')