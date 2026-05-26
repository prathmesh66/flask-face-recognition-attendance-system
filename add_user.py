import pymysql

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Tanmay',
    'database': 'face_recognition',
    'port': 3306,
    'charset': 'utf8mb4'
}

def add_user(username, email, password):
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Check if username already exists
        cursor.execute("SELECT id FROM regteach WHERE username = %s", (username,))
        if cursor.fetchone():
            print(f"Username '{username}' already exists!")
            conn.close()
            return False

        # Check if email already exists
        cursor.execute("SELECT id FROM regteach WHERE email = %s", (email,))
        if cursor.fetchone():
            print(f"Email '{email}' already exists!")
            conn.close()
            return False

        # Insert new user
        cursor.execute("""
            INSERT INTO regteach (username, email, pwd)
            VALUES (%s, %s, %s)
        """, (username, email, password))

        conn.commit()
        conn.close()

        print(f"User '{username}' with email '{email}' added successfully!")
        return True

    except Exception as e:
        print(f"Error adding user: {str(e)}")
        return False

if __name__ == "__main__":
    # Example usage
    username = input("Enter username: ")
    email = input("Enter email: ")
    password = input("Enter password: ")

    add_user(username, email, password)
