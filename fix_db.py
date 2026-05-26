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

    print("Checking current regteach table structure...")

    # Check current structure
    cursor.execute("DESCRIBE regteach")
    columns_data = cursor.fetchall()
    columns = [col[0].lower() for col in columns_data]
    print("Current columns:", columns)

    # Check for 'id' column
    if 'id' not in columns:
        print("\nAdding 'id' column as auto-increment primary key...")
        cursor.execute("ALTER TABLE regteach ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST")
        print("ID column added successfully!")
    else:
        print("ID column already exists.")

    # Check for 'username' column
    if 'username' not in columns:
        print("\nAdding 'username' column...")
        cursor.execute("ALTER TABLE regteach ADD COLUMN username VARCHAR(50) NOT NULL UNIQUE AFTER id")
        print("Username column added.")
    else:
        print("Username column already exists.")

    # Check for 'email' column
    if 'email' not in columns:
        print("\nAdding 'email' column...")
        cursor.execute("ALTER TABLE regteach ADD COLUMN email VARCHAR(100) NOT NULL UNIQUE AFTER username")
        print("Email column added.")
    else:
        print("Email column already exists.")
        # Ensure email column can hold long enough values and is unique
        cursor.execute("ALTER TABLE regteach MODIFY email VARCHAR(100) NOT NULL UNIQUE")
        print("Email column modified to ensure it is of type VARCHAR(100), NOT NULL and UNIQUE.")


    # Check for 'password' column, and handle 'pwd' to 'password' rename
    if 'password' not in columns:
        if 'pwd' in columns:
            print("\nRenaming 'pwd' column to 'password'...")
            cursor.execute("ALTER TABLE regteach CHANGE COLUMN pwd password VARCHAR(255) NOT NULL")
            print("Renamed 'pwd' to 'password'.")
        else:
            print("\nAdding 'password' column...")
            cursor.execute("ALTER TABLE regteach ADD COLUMN password VARCHAR(255) NOT NULL AFTER email")
            print("Password column added.")
    else:
        print("Password column already exists.")
        cursor.execute("ALTER TABLE regteach MODIFY password VARCHAR(255) NOT NULL")
        print("Password column modified to ensure it is of type VARCHAR(255) and NOT NULL.")


    conn.commit()

    print("\nVerifying final table structure...")
    cursor.execute("DESCRIBE regteach")
    final_columns = cursor.fetchall()
    print("Final columns:")
    for col in final_columns:
        print(f"  {col[0]}: {col[1]} (Null: {col[2]}, Key: {col[3]})")


    conn.close()
    print("\nDatabase schema for 'regteach' table is now consistent with app.py.")
    print("Please try running the application again.")

except pymysql.err.OperationalError as e:
    print(f"\nDatabase connection error: {e}")
    print("Please ensure your MySQL server is running and the credentials in DB_CONFIG are correct.")
except Exception as e:
    print(f"\nAn unexpected error occurred: {e}")