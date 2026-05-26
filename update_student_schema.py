import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Tanmay',
    'database': 'face_recognition',
    'port': 3306,
    'charset': 'utf8mb4'
}

def update_student_schema():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Get existing student table columns
        cursor.execute("DESCRIBE student")
        student_columns = [col[0] for col in cursor.fetchall()]
        print(f"Existing student columns: {student_columns}")

        # Add Course column if missing
        if 'Course' not in student_columns:
            print("Adding 'Course' column to student table...")
            cursor.execute("ALTER TABLE student ADD COLUMN Course VARCHAR(50) DEFAULT NULL AFTER Department")

        # Add Teacher_Name column if missing
        if 'Teacher_Name' not in student_columns:
            print("Adding 'Teacher_Name' column to student table...")
            cursor.execute("ALTER TABLE student ADD COLUMN Teacher_Name VARCHAR(100) DEFAULT NULL AFTER Email")

        # Add PhotoSample column if missing
        if 'PhotoSample' not in student_columns:
            print("Adding 'PhotoSample' column to student table...")
            cursor.execute("ALTER TABLE student ADD COLUMN PhotoSample VARCHAR(10) DEFAULT 'No' AFTER Teacher_Name")

        conn.commit()
        print("Student table schema updated successfully!")

        # Check the updated student table structure
        cursor.execute("DESCRIBE student")
        columns = cursor.fetchall()
        print("\nUpdated student table structure:")
        for col in columns:
            print(f"Column: {col[0]}, Type: {col[1]}, Default: {col[4]}, Key: {col[3]}")

        conn.close()

    except Exception as e:
        print(f"Error updating student table schema: {e}")

if __name__ == "__main__":
    update_student_schema()
