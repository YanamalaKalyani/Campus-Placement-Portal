import mysql.connector
import os

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'campus_placement'
}

try:
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Create notification_status table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notification_status (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            notification_id INT NOT NULL,
            is_read BOOLEAN DEFAULT TRUE,
            read_at DATETIME,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (notification_id) REFERENCES notifications(id)
        );
    """)
    conn.commit()
    print("Table notification_status created successfully.")

    cursor.close()
    conn.close()

except Exception as e:
    print(f"Error: {e}")
