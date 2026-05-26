import pymysql

try:
    # Test database connection
    conn = pymysql.connect(
        user='root',
        password='Tanmay',
        host='localhost',
        database='face_recognition',
        port=3306,
        charset='utf8mb4'
    )
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Get column names
    cursor.execute("DESCRIBE student")
    columns = cursor.fetchall()
    print("Student table columns:")
    for col in columns:
        print(f"  {col['Field']}: {col['Type']}")

    # Test query
    cursor.execute("SELECT * FROM student")
    students = cursor.fetchall()
    print(f"\nStudents in database: {len(students)}")
    if students:
        print("First student data:")
        for key, value in students[0].items():
            print(f"  {key}: {value} (type: {type(value)})")

    conn.close()

except Exception as e:
    print(f"Database connection error: {e}")
    import traceback
    traceback.print_exc()
