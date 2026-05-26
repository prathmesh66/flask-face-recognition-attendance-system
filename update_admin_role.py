import pymysql

# Database configuration
DB_CONFIG = {
    'user': 'root',
    'password': 'Tanmay',
    'host': 'localhost',
    'database': 'face_recognition',
    'port': 3306,
    'charset': 'utf8mb4'
}

def update_admin_role():
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Update the role to 'admin' for the admin user
        # You can identify the admin user by email or username
        # For example, if the admin email is 'admin@example.com', use:
        # cursor.execute("UPDATE regteach SET role = 'admin' WHERE email = 'admin@example.com'")

        # Or if you want to update all users with role 'user' to 'admin', use:
        # cursor.execute("UPDATE regteach SET role = 'admin' WHERE role = 'user'")

        # For now, let's update a specific user by email
        admin_email = 'admin@example.com'  # Replace with the actual admin email
        cursor.execute("UPDATE regteach SET role = 'admin' WHERE email = %s", (admin_email,))

        conn.commit()
        print(f"Updated role to 'admin' for user with email: {admin_email}")

        # Verify the update
        cursor.execute("SELECT username, email, role FROM regteach WHERE email = %s", (admin_email,))
        user = cursor.fetchone()
        if user:
            print(f"User: {user[0]}, Email: {user[1]}, Role: {user[2]}")
        else:
            print("User not found")

        conn.close()

    except Exception as e:
        print(f"Error updating admin role: {e}")

if __name__ == '__main__':
    update_admin_role()
