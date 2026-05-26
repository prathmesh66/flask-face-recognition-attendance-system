import pymysql
import json
from datetime import datetime

def get_students():
    try:
        conn = pymysql.connect(
            user='root',
            password='Tanmay',
            host='localhost',
            database='face_recognition',
            port=3306,
            charset='utf8mb4'
        )
        cursor = conn.cursor(pymysql.cursors.DictCursor)
        cursor.execute("SELECT * FROM student")
        students = cursor.fetchall()
        conn.close()

        # Convert non-serializable objects to strings
        for student in students:
            for key, value in student.items():
                if isinstance(value, (datetime.date, datetime.datetime)):
                    student[key] = value.isoformat()

        return {"students": students}
    except Exception as e:
        return {"error": str(e)}

# Test the function
result = get_students()
print("Result:", json.dumps(result, indent=2))
