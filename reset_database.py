import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Tanmay',
    'port': 3306,
    'charset': 'utf8mb4'
}

def reset_database():
    try:
        # Connect without specifying database
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Drop the database if it exists
        cursor.execute("DROP DATABASE IF EXISTS face_recognition")
        print("Dropped existing face_recognition database")

        # Create new database
        cursor.execute("CREATE DATABASE face_recognition")
        print("Created new face_recognition database")

        # Switch to the new database
        cursor.execute("USE face_recognition")

        # Create regteach table with all required columns
        cursor.execute("""
            CREATE TABLE regteach (
                id INT AUTO_INCREMENT PRIMARY KEY,
                fname VARCHAR(50),
                lname VARCHAR(50),
                cnum VARCHAR(50),
                username VARCHAR(50) UNIQUE,
                email VARCHAR(100) UNIQUE,
                ss_que VARCHAR(50),
                s_ans VARCHAR(50),
                password VARCHAR(255),
                verified BOOLEAN DEFAULT FALSE,
                verification_token VARCHAR(255) DEFAULT NULL,
                role VARCHAR(20) DEFAULT 'user'
            )
        """)
        print("Created regteach table")

        # Create student table
        cursor.execute("""
            CREATE TABLE student (
                Student_id VARCHAR(50) PRIMARY KEY,
                Name VARCHAR(100),
                Roll_No VARCHAR(50),
                Department VARCHAR(50),
                Year VARCHAR(10),
                Semester VARCHAR(10),
                Division VARCHAR(10),
                Gender VARCHAR(10),
                DOB VARCHAR(20),
                Email VARCHAR(100),
                Phone VARCHAR(20),
                Address TEXT,
                Photo VARCHAR(255)
            )
        """)
        print("Created student table")

        # Create stdattendance table
        cursor.execute("""
            CREATE TABLE stdattendance (
                id INT AUTO_INCREMENT PRIMARY KEY,
                std_id VARCHAR(50),
                std_roll_no VARCHAR(50),
                std_name VARCHAR(100),
                std_date DATE,
                std_time TIME,
                std_attendance VARCHAR(20)
            )
        """)
        print("Created stdattendance table")

        # Insert a default admin user
        cursor.execute("""
            INSERT INTO regteach (username, email, password, verified, role)
            VALUES (%s, %s, %s, %s, %s)
        """, ('admin', 'admin078@gmail.com', 'admin123', True, 'admin'))
        print("Inserted default admin user")

        # Insert a default regular user
        cursor.execute("""
            INSERT INTO regteach (username, email, password, verified, role)
            VALUES (%s, %s, %s, %s, %s)
        """, ('user', 'user@example.com', 'pbkdf2_sha256$870000$qIcv0sWrMRjbrUEUOcn3j9$5EtR6HrgcXjQLRtpO+hhcQQB1WLznaQk2YlYRreYlRY=', True, 'user'))
        print("Inserted default regular user")

        conn.commit()
        conn.close()

        print("\nDatabase reset completed successfully!")
        print("Default users:")
        print("Admin: username='admin', password='admin123'")
        print("User: username='user', password='user123'")

    except Exception as e:
        print(f"Error resetting database: {e}")

if __name__ == "__main__":
    reset_database()
