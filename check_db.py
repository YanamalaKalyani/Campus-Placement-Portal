import mysql.connector

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'campus_placement'
}

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)

    # Check notifications table structure
    cursor.execute('DESCRIBE notifications')
    columns = cursor.fetchall()
    print('Notifications table structure:')
    for col in columns:
        print(f'  {col["Field"]}: {col["Type"]}')

    # Check existing notifications
    cursor.execute('SELECT id, title, target_role, user_id, created_at FROM notifications ORDER BY created_at DESC LIMIT 10')
    notifications = cursor.fetchall()
    print(f'\nExisting notifications ({len(notifications)}):')
    for notif in notifications:
        print(f'  ID: {notif["id"]}, Title: {notif["title"]}, Target: {notif["target_role"]}, User: {notif["user_id"]}, Date: {notif["created_at"]}')

    # Check users table
    cursor.execute("SELECT id, name, role FROM users WHERE role='student'")
    students = cursor.fetchall()
    print(f'\nStudents ({len(students)}):')
    for student in students:
        print(f'  ID: {student["id"]}, Name: {student["name"]}, Role: {student["role"]}')

    # Check if user_id 12 exists
    cursor.execute('SELECT id, name, role FROM users WHERE id=12')
    user12 = cursor.fetchone()
    print(f'\nUser ID 12: {user12}')

    # Check student enrollment
    cursor.execute('SELECT * FROM students')
    all_students = cursor.fetchall()
    print(f'\nAll students ({len(all_students)}):')
    for student in all_students:
        print(f'  ID: {student["id"]}, User ID: {student["user_id"]}, Name: {student["name"]}, Enrollment: {student["enrollment_number"]}')

    cursor.close()
    conn.close()

except Exception as e:
    print(f'Error: {e}')