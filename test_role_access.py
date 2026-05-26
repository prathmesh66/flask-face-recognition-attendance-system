import requests
import pymysql
from werkzeug.security import generate_password_hash

BASE_URL = 'http://127.0.0.1:5000'

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Tanmay',
    'database': 'face_recognition',
    'port': 3306,
    'charset': 'utf8mb4'
}

def setup_test_users():
    """Create test users with different roles"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()

        # Create regular user
        cursor.execute("""
            INSERT INTO regteach (username, email, password, role, verified)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE password=%s, role=%s, verified=%s
        """, ('testuser', 'testuser@example.com', 'testpass123', 'user', True,
              'testpass123', 'user', True))

        # Create admin user
        cursor.execute("""
            INSERT INTO regteach (username, email, password, role, verified)
            VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE password=%s, role=%s, verified=%s
        """, ('testadmin', 'testadmin@example.com', 'adminpass123', 'admin', True,
              'adminpass123', 'admin', True))

        conn.commit()
        conn.close()
        print("Test users created successfully")
        return True
    except Exception as e:
        print(f"Error setting up test users: {e}")
        return False

def test_login(session, username, password):
    """Login and return session"""
    data = {
        'email': username,
        'password': password
    }
    response = session.post(f'{BASE_URL}/login', data=data, allow_redirects=False)
    return response.status_code == 302  # Should redirect to dashboard

def test_route_access(session, route, expected_status, description):
    """Test access to a specific route"""
    response = session.get(f'{BASE_URL}{route}', allow_redirects=False)
    status = response.status_code
    success = status == expected_status
    result = "PASS" if success else "FAIL"
    print(f"{result}: {description} - Status: {status} (expected: {expected_status})")
    return success

def test_role_based_access():
    """Test role-based access control for all routes"""
    print("\n=== ROLE-BASED ACCESS CONTROL TESTING ===\n")

    # Setup test users
    if not setup_test_users():
        print("Failed to setup test users")
        return

    # Define routes and their access requirements
    routes = {
        '/': {'description': 'Dashboard', 'user': 200, 'admin': 200},
        '/face_recognition': {'description': 'Face Recognition', 'user': 200, 'admin': 200},
        '/attendance': {'description': 'Attendance View', 'user': 200, 'admin': 200},
        '/student': {'description': 'Student Management', 'user': 302, 'admin': 200},  # 302 = redirect for access denied
        '/train': {'description': 'Model Training', 'user': 302, 'admin': 200},
        '/delete_user': {'description': 'Delete User', 'user': 302, 'admin': 200}
    }

    all_tests_passed = True

    # Test regular user access
    print("Testing Regular User Access:")
    print("-" * 40)
    user_session = requests.Session()
    if test_login(user_session, 'testuser', 'testpass123'):
        print("✓ Regular user login successful")
        for route, config in routes.items():
            success = test_route_access(user_session, route, config['user'], f"Regular user access to {config['description']}")
            if not success:
                all_tests_passed = False
    else:
        print("✗ Regular user login failed")
        all_tests_passed = False

    print("\n" + "="*50 + "\n")

    # Test admin user access
    print("Testing Admin User Access:")
    print("-" * 40)
    admin_session = requests.Session()
    if test_login(admin_session, 'testadmin', 'adminpass123'):
        print("✓ Admin user login successful")
        for route, config in routes.items():
            success = test_route_access(admin_session, route, config['admin'], f"Admin user access to {config['description']}")
            if not success:
                all_tests_passed = False
    else:
        print("✗ Admin user login failed")
        all_tests_passed = False

    print("\n" + "="*50)

    # Test unauthenticated access (should redirect to login)
    print("\nTesting Unauthenticated Access:")
    print("-" * 40)
    unauth_session = requests.Session()
    for route, config in routes.items():
        success = test_route_access(unauth_session, route, 302, f"Unauthenticated access to {config['description']}")
        if not success:
            all_tests_passed = False

    print("\n" + "="*50)
    if all_tests_passed:
        print("🎉 ALL TESTS PASSED! Role-based access control is working correctly.")
    else:
        print("❌ SOME TESTS FAILED! Please review the implementation.")

    return all_tests_passed

def cleanup_test_users():
    """Clean up test users"""
    try:
        conn = pymysql.connect(**DB_CONFIG)
        cursor = conn.cursor()
        cursor.execute("DELETE FROM regteach WHERE username IN ('testuser', 'testadmin')")
        conn.commit()
        conn.close()
        print("Test users cleaned up")
    except Exception as e:
        print(f"Error cleaning up test users: {e}")

if __name__ == '__main__':
    try:
        success = test_role_based_access()
        cleanup_test_users()
        exit(0 if success else 1)
    except Exception as e:
        print(f"Test execution failed: {e}")
        cleanup_test_users()
        exit(1)
