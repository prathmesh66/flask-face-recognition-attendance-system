import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Tanmay',
    'database': 'face_recognition',
    'port': 3306,
    'charset': 'utf8mb4'
}

try:
    conn = pymysql.connect(**DB_CONFIG)
    cursor = conn.cursor()

    # Check tables
    cursor.execute("SHOW TABLES")
    tables = cursor.fetchall()
    print("Tables in database:", tables)

    # Check regteach table structure
    print("\n=== REGTEACH TABLE STRUCTURE ===")
    cursor.execute("DESCRIBE regteach")
    columns = cursor.fetchall()
    for col in columns:
        print(f"Column: {col[0]}, Type: {col[1]}, Key: {col[3]}")

    # Check regteach table data
    cursor.execute("SELECT COUNT(*) FROM regteach")
    regteach_count = cursor.fetchone()[0]
    print(f"Users in regteach: {regteach_count}")

    if regteach_count > 0:
        cursor.execute("SELECT * FROM regteach LIMIT 5")
        users = cursor.fetchall()
        print("Sample users:", users)

    # Check student table
    cursor.execute("SELECT COUNT(*) FROM student")
    student_count = cursor.fetchone()[0]
    print(f"Students: {student_count}")

    # Check stdattendance table
    cursor.execute("SELECT COUNT(*) FROM stdattendance")
    attendance_count = cursor.fetchone()[0]
    print(f"Attendance records: {attendance_count}")

    conn.close()
    print("Database connection successful!")

except Exception as e:
    print(f"Database error: {e}")
