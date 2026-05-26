import pymysql

try:
    # Connect to MySQL Server (without selecting a database initially)
    conn = pymysql.connect(user='root', password='Tanmay', host='localhost', port=3306)
    cursor = conn.cursor()

    # Create Database
    cursor.execute("CREATE DATABASE IF NOT EXISTS face_recognition")
    cursor.execute("USE face_recognition")

    # Create regteach table (For Login/Register)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS regteach (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) UNIQUE,
        fname VARCHAR(50),
        lname VARCHAR(50),
        cnum VARCHAR(50),
        email VARCHAR(50) UNIQUE,
        ss_que VARCHAR(50),
        s_ans VARCHAR(50),
        pwd VARCHAR(50),
        role VARCHAR(20) DEFAULT 'user',
        verified BOOLEAN DEFAULT FALSE,
        verification_token VARCHAR(255) DEFAULT NULL
    )
    """)

    # Create student table (For Student Details)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS student (
        Student_ID VARCHAR(45) PRIMARY KEY,
        Name VARCHAR(50),
        Department VARCHAR(50),
        Course VARCHAR(50),
        Year VARCHAR(50),
        Semester VARCHAR(50),
        Division VARCHAR(50),
        Gender VARCHAR(50),
        DOB VARCHAR(50),
        Phone VARCHAR(50),
        Address VARCHAR(50),
        Roll_No VARCHAR(50),
        Email VARCHAR(50),
        Teacher_Name VARCHAR(50),
        Photo VARCHAR(50)
    )
    """)

    # Create stdattendance table (For Attendance Records)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS stdattendance (
        std_id VARCHAR(45) PRIMARY KEY,
        std_roll_no VARCHAR(50),
        std_name VARCHAR(50),
        std_time VARCHAR(50),
        std_date VARCHAR(50),
        std_attendance VARCHAR(50)
    )
    """)

    conn.commit()
    conn.close()
    print("Database 'face_recognition' and tables created successfully!")

except Exception as e:
    print(f"Error: {e}")
