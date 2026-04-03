import mysql.connector

try:
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="campus_placement"
    )
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT UPPER(TRIM(branch)) as branch, 
               COUNT(*) as total,
               SUM(CASE WHEN placement_status = 'placed' THEN 1 ELSE 0 END) as placed
        FROM students 
        WHERE branch IS NOT NULL AND branch != ''
        GROUP BY UPPER(TRIM(branch))
    """)
    branch_stats = cursor.fetchall()
    
    print("BRANCH STATS FROM DB:")
    for stat in branch_stats:
        print(stat)
    
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
