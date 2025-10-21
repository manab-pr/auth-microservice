# FastAPI Authentication Service with Clean Architecture

A production-ready authentication service built with FastAPI following clean architecture principles, inspired by Go's clean architecture patterns.

## Architecture Overview

This project follows clean architecture with clear separation of concerns:

```
auth/
├── domain/              # Business logic layer (pure Python, no external dependencies)
│   ├── entities/       # Domain entities (User)
│   ├── ports/          # Interfaces/Protocols (repositories, stores)
│   ├── services/       # Domain services interfaces (PasswordHasher, TokenGenerator)
│   └── usecases/       # Business use cases (Login, Register, Logout)
├── infra/              # Infrastructure layer (external dependencies)
│   ├── mongodb/        # MongoDB implementations
│   ├── redis/          # Redis implementations
│   └── security/       # Security implementations (Bcrypt, JWT)
├── presentation/       # Presentation layer
│   └── http/          # HTTP/REST API
│       ├── schemas/    # Pydantic models (DTOs)
│       ├── handlers/   # Route handlers
│       └── dependencies.py  # FastAPI dependencies
└── container.py        # Dependency injection container
```

## Features

- ✅ User registration with email and password
- ✅ User login with JWT token generation
- ✅ User logout with token revocation (using Redis)
- ✅ Clean architecture with dependency inversion
- ✅ Type hints throughout
- ✅ Async/await with Motor (MongoDB) and Redis
- ✅ Password hashing with bcrypt
- ✅ JWT tokens with access and refresh tokens
- ✅ Token blacklisting/revocation

## Prerequisites

Before you start, you need to have these installed:

- **Python 3.9+** - Check with: `python --version` or `python3 --version`
- **MongoDB** - A NoSQL database
- **Redis** - An in-memory data store

### Installing MongoDB (macOS)

```bash
# Install using Homebrew
brew tap mongodb/brew
brew install mongodb-community

# Start MongoDB
brew services start mongodb-community

# Verify it's running
mongosh
```

### Installing Redis (macOS)

```bash
# Install using Homebrew
brew install redis

# Start Redis
brew services start redis

# Verify it's running
redis-cli ping
# Should respond with: PONG
```

## Installation & Setup

### 1. Create a virtual environment

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# OR
venv\Scripts\activate  # On Windows
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and update the values
# IMPORTANT: Change JWT_SECRET_KEY to a secure random string in production!
```

### 4. Run the application

```bash
# Make sure MongoDB and Redis are running first!

# Run the FastAPI server
python main.py

# Or use uvicorn directly for more control
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative docs (ReDoc)**: http://localhost:8000/redoc

## API Endpoints

### Health Check
```bash
GET /health
```

### Register a new user
```bash
POST /auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123",
  "full_name": "John Doe"
}
```

### Login
```bash
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword123"
}

# Response:
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "token_type": "bearer"
}
```

### Logout (requires authentication)
```bash
POST /auth/logout
Authorization: Bearer <your_access_token>

# Response:
{
  "message": "Successfully logged out"
}
```

## Testing the API

### Using curl

```bash
# 1. Register a user
curl -X POST "http://localhost:8000/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123",
    "full_name": "Test User"
  }'

# 2. Login
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Save the access_token from the response

# 3. Logout
curl -X POST "http://localhost:8000/auth/logout" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### Using Python requests

```python
import requests

BASE_URL = "http://localhost:8000"

# Register
response = requests.post(
    f"{BASE_URL}/auth/register",
    json={
        "email": "test@example.com",
        "password": "password123",
        "full_name": "Test User"
    }
)
print("Register:", response.json())

# Login
response = requests.post(
    f"{BASE_URL}/auth/login",
    json={
        "email": "test@example.com",
        "password": "password123"
    }
)
tokens = response.json()
print("Login:", tokens)

# Logout
response = requests.post(
    f"{BASE_URL}/auth/logout",
    headers={"Authorization": f"Bearer {tokens['access_token']}"}
)
print("Logout:", response.json())
```

## Project Structure Explained

### Domain Layer (Business Logic)
- **entities/**: Core business objects (User)
- **ports/**: Interfaces that define contracts (UserRepository, RevocationStore)
- **services/**: Domain service interfaces (PasswordHasher, TokenGenerator)
- **usecases/**: Business use cases containing application logic

### Infrastructure Layer (External Dependencies)
- **mongodb/**: MongoDB repository implementations
- **redis/**: Redis store implementations
- **security/**: Bcrypt and JWT implementations

### Presentation Layer (HTTP API)
- **schemas/**: Request/Response models (Pydantic)
- **handlers/**: Route handlers (controllers)
- **dependencies.py**: FastAPI dependency injection

### Dependency Injection
- **container.py**: Wires together all dependencies (similar to Go's wire)

## Clean Architecture Benefits

1. **Testability**: Business logic is independent of frameworks
2. **Flexibility**: Easy to swap implementations (e.g., MongoDB → PostgreSQL)
3. **Maintainability**: Clear separation of concerns
4. **Scalability**: Each layer can evolve independently

## Next Steps

1. Add unit tests for use cases
2. Add integration tests for repositories
3. Implement refresh token endpoint
4. Add email verification
5. Add password reset functionality
6. Add rate limiting
7. Add logging and monitoring

## Common Issues

### MongoDB Connection Error
```bash
# Make sure MongoDB is running
brew services start mongodb-community

# Check if it's running
mongosh
```

### Redis Connection Error
```bash
# Make sure Redis is running
brew services start redis

# Test connection
redis-cli ping
```

### Import Errors
```bash
# Make sure you're in the virtual environment
source venv/bin/activate

# Install dependencies again
pip install -r requirements.txt
```

## Learning Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [MongoDB Motor Documentation](https://motor.readthedocs.io/)
- [Clean Architecture Blog](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)

## License

MIT
