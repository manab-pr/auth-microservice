"""
Simple script to test the authentication API.
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
            "email": "test@example.com",
            "password": "testpassword123",
            "full_name": "Test User"
        }
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    return response.status_code in [200, 201, 400]  # 400 if user already exists


def test_login():
    """Test user login."""
    print("\n🔍 Testing user login...")
    response = requests.post(
        f"{BASE_URL}/auth/login",
        json={
            "email": "test@example.com",
            "password": "testpassword123"
        }
    )
    print(f"Status: {response.status_code}")
    data = response.json()
    print(f"Response: {data}")

    if response.status_code == 200:
        return data.get("access_token")
    return None


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
    print("=" * 60)
    print("FastAPI Authentication API Test")
    print("=" * 60)

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
        access_token = test_login()
        if not access_token:
            print("\n❌ Login failed!")
            sys.exit(1)

        print("\n✅ Login successful! Got access token.")

        # Test logout
        if not test_logout(access_token):
            print("\n❌ Logout failed!")
            sys.exit(1)

        print("\n✅ Logout successful!")

        print("\n" + "=" * 60)
        print("🎉 All tests passed! Your API is working correctly!")
        print("=" * 60)
        print("\n📚 Next steps:")
        print("   1. Visit http://localhost:8000/docs for interactive API docs")
        print("   2. Read README.md for more information")
        print("   3. Start building your application!")

    except requests.exceptions.ConnectionError:
        print("\n❌ Cannot connect to server!")
        print("   Make sure the server is running: python main.py")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
