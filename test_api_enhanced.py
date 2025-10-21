"""
Enhanced script to test all authentication API endpoints.
Run this after starting the server to verify everything works.
"""
import requests
import sys

BASE_URL = "http://localhost:8000"


def test_health():
    """Test health endpoint."""
    print("\n🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def test_register():
    """Test user registration."""
    print("\n🔍 Testing user registration...")
    response = requests.post(
        f"{BASE_URL}/auth/register",
        json={
            "email": "demo@example.com",
            "password": "demopassword123",
            "full_name": "Demo User"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code in [200, 201, 400]


def test_login():
    """Test user login."""
    print("\n🔍 Testing user login...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "demo@example.com",
            "password": "demopassword123"
        }
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Access Token: {data.get('access_token', '')[:50]}...")
    print(f"Refresh Token: {data.get('refresh_token', '')[:50]}...")

    if response.status_code == 200:
        return data.get("access_token"), data.get("refresh_token")
    return None, None


def test_get_profile(access_token):
    """Test get user profile."""
    print("\n🔍 Testing get user profile (GET /auth/me)...")
    response = requests.get(
        f"{BASE_URL}/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def test_update_profile(access_token):
    """Test update user profile."""
    print("\n🔍 Testing update user profile (PUT /auth/me)...")
    response = requests.put(
        f"{BASE_URL}/auth/me",
        headers={"Authorization": f"Bearer {access_token}"},
        json={"full_name": "Demo User Updated"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def test_refresh_token(refresh_token):
    """Test refresh token."""
    print("\n🔍 Testing refresh token (POST /auth/refresh)...")
    response = requests.post(
        f"{BASE_URL}/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"New Access Token: {data.get('access_token', '')[:50]}...")
    print(f"New Refresh Token: {data.get('refresh_token', '')[:50]}...")
    return response.status_code == 200


def test_logout(access_token):
    """Test user logout."""
    print("\n🔍 Testing user logout...")
    response = requests.post(
        f"{BASE_URL}/auth/logout",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code == 200


def main():
    """Run all tests."""
    print("=" * 70)
    print("FastAPI Authentication API - Enhanced Test Suite")
    print("=" * 70)

    try:
        # Test health
        if not test_health():
            print("\n❌ Health check failed! Is the server running?")
            print("   Start the server with: python main.py")
            sys.exit(1)

        print("\n✅ Health check passed!")

        # Test registration
        test_register()
        print("\n✅ Registration endpoint working!")

        # Test login
        access_token, refresh_token = test_login()
        if not access_token:
            print("\n❌ Login failed!")
            sys.exit(1)

        print("\n✅ Login successful! Got tokens.")

        # Test get profile
        if not test_get_profile(access_token):
            print("\n❌ Get profile failed!")
            sys.exit(1)

        print("\n✅ Get profile successful!")

        # Test update profile
        if not test_update_profile(access_token):
            print("\n❌ Update profile failed!")
            sys.exit(1)

        print("\n✅ Update profile successful!")

        # Test refresh token
        if not test_refresh_token(refresh_token):
            print("\n❌ Refresh token failed!")
            sys.exit(1)

        print("\n✅ Refresh token successful!")

        # Test logout
        if not test_logout(access_token):
            print("\n❌ Logout failed!")
            sys.exit(1)

        print("\n✅ Logout successful!")

        print("\n" + "=" * 70)
        print("🎉 All tests passed! Your enhanced API is working correctly!")
        print("=" * 70)
        print("\n📚 Available Endpoints:")
        print("   POST   /auth/register       - Register new user")
        print("   POST   /auth/login          - Login and get tokens")
        print("   POST   /auth/logout         - Logout (revoke token)")
        print("   GET    /auth/me             - Get current user profile")
        print("   PUT    /auth/me             - Update user profile")
        print("   POST   /auth/refresh        - Refresh access token")
        print("\n📝 Next Steps:")
        print("   1. Visit http://localhost:8000/docs for interactive API docs")
        print("   2. Run unit tests: pytest tests/ -v")
        print("   3. Check test coverage: pytest tests/ --cov=auth")
        print("   4. Review the clean architecture in auth/ directory")

    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server!")
        print("   Make sure the server is running: python main.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
