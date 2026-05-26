import pymysql

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Tanmay',
    'database': 'face_recognition',
    'port': 3306,
    'charset': 'utf8mb4'
}

def update_database_schema():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Get existing columns
        cursor.execute("DESCRIBE regteach")
        existing_columns = [col[0] for col in cursor.fetchall()]
        print(f"Existing columns: {existing_columns}")

        # Add verified column if missing
        if 'verified' not in existing_columns:
            print("Adding 'verified' column...")
            cursor.execute("ALTER TABLE regteach ADD COLUMN verified BOOLEAN DEFAULT FALSE AFTER password")

        # Add verification_token column if missing
        if 'verification_token' not in existing_columns:
            print("Adding 'verification_token' column...")
            cursor.execute("ALTER TABLE regteach ADD COLUMN verification_token VARCHAR(255) DEFAULT NULL AFTER verified")

        # Add role column if missing
        if 'role' not in existing_columns:
            print("Adding 'role' column...")
            cursor.execute("ALTER TABLE regteach ADD COLUMN role VARCHAR(20) DEFAULT 'user' AFTER verification_token")

        # Ensure 'id' is the primary key and auto-increment
        if 'id' not in existing_columns:
            print("Adding 'id' column...")
            cursor.execute("ALTER TABLE regteach ADD COLUMN id INT AUTO_INCREMENT PRIMARY KEY FIRST")

        # Add username column if missing (required by Flask app)
        if 'username' not in existing_columns:
            print("Adding 'username' column...")
            cursor.execute("ALTER TABLE regteach ADD COLUMN username VARCHAR(50) UNIQUE AFTER fname")

        conn.commit()
        print("Database schema updated successfully!")

        # Check the updated table structure
        cursor.execute("DESCRIBE regteach")
        columns = cursor.fetchall()
        print("\nUpdated regteach table structure:")
        for col in columns:
            print(f"Column: {col[0]}, Type: {col[1]}, Default: {col[4]}, Key: {col[3]}")

        conn.close()

    except Exception as e:
        print(f"Error updating database schema: {e}")

if __name__ == "__main__":
    update_database_schema()
