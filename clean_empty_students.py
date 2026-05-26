import pymysql

try:
    conn = pymysql.connect(user='root', password='Tanmay', host='localhost', database='face_recognition', port=3306, charset='utf8mb4')
    cursor = conn.cursor(pymysql.cursors.DictCursor)

    # Check current students
    cursor.execute('SELECT COUNT(*) as count FROM student')
    result = cursor.fetchone()
    print('Total students in database:', result['count'])

    # Check for students with empty Student_id
    cursor.execute("SELECT COUNT(*) as count FROM student WHERE Student_id IS NULL OR Student_id = ''")
    empty_result = cursor.fetchone()
    print('Students with empty Student_id:', empty_result['count'])

    if empty_result['count'] > 0:
        # Delete students with empty Student_id
        cursor.execute("DELETE FROM student WHERE Student_id IS NULL OR Student_id = ''")
        deleted_count = cursor.rowcount
        print('Deleted', deleted_count, 'students with empty Student_id')
        conn.commit()

    # Check remaining students
    cursor.execute('SELECT COUNT(*) as count FROM student')
    result = cursor.fetchone()
    print('Total students remaining:', result['count'])

    if result['count'] > 0:
        cursor.execute('SELECT Student_id, Name FROM student LIMIT 3')
        students = cursor.fetchall()
        print('Sample students:')
        for student in students:
            print('  ID:', student['Student_id'], ', Name:', student['Name'])

    conn.close()
except Exception as e:
    print('Error:', e)
