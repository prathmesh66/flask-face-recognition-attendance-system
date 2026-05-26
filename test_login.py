import requests

BASE_URL = 'http://127.0.0.1:5000'

# Test registration
def test_register():
    data = {
        'username': 'testuser',
        'email': 'test@example.com',
        'password': 'testpass123'
    }
    response = requests.post(f'{BASE_URL}/register', data=data)
    print(f'Register status: {response.status_code}')
    print(f'Register response: {response.text}')
    return response.status_code == 200

# Test login
def test_login():
    data = {
        'username': 'testuser',
        'password': 'testpass123'
    }
    session = requests.Session()
    response = session.post(f'{BASE_URL}/login', data=data)
    print(f'Login status: {response.status_code}')
    print(f'Login response: {response.text}')
    return response.status_code == 302  # Redirect to dashboard

if __name__ == '__main__':
    print("Testing registration...")
    if test_register():
        print("Registration successful, testing login...")
        test_login()
    else:
        print("Registration failed")
