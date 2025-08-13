# Healthcare AI - Test Suite Documentation

## Overview
This comprehensive test suite covers all aspects of the Healthcare AI backend application, ensuring reliability and maintainability for your hackathon project.

## Test Structure

### 📁 Test Files
- **`test_main.py`** - FastAPI app, startup events, route configuration
- **`test_auth_routes.py`** - Authentication endpoints, login/registration workflows
- **`test_models.py`** - SQLAlchemy models, relationships, database operations
- **`test_utils_auth.py`** - Password hashing, JWT tokens, security functions
- **`test_database.py`** - Database connections, constraints, transactions
- **`test_integration.py`** - End-to-end workflows, system integration
- **`conftest.py`** - Shared fixtures and test configuration
- **`pytest.ini`** - Pytest configuration and markers

### 🏷️ Test Categories
- **Unit Tests** (`@pytest.mark.unit`) - Individual function/class testing
- **Integration Tests** (`@pytest.mark.integration`) - End-to-end workflows
- **Auth Tests** (`@pytest.mark.auth`) - Authentication-related functionality
- **Database Tests** (`@pytest.mark.database`) - Database operations
- **Slow Tests** (`@pytest.mark.slow`) - Performance/load testing

## 🚀 Running Tests

### Quick Start
```bash
# Install test dependencies
pip install -r requirements.txt

# Run all tests
python run_tests.py

# Run specific test suite
python run_tests.py --suite unit
python run_tests.py --suite integration
python run_tests.py --suite auth

# Run with coverage
python run_tests.py --coverage

# Run specific test file
python run_tests.py --file test_auth_routes.py
```

### Direct Pytest Commands
```bash
# All tests
pytest

# Specific markers
pytest -m "unit"
pytest -m "auth"
pytest -m "not slow"

# Specific file
pytest test_models.py

# Verbose output
pytest -v

# With coverage
pytest --cov=. --cov-report=html
```

## 📊 Test Coverage

### Main Application (`test_main.py`)
- Root endpoint functionality
- FastAPI app configuration
- Startup event (admin user creation)
- Route inclusion and OpenAPI schema

### Authentication (`test_auth_routes.py`)
- User registration (patient/doctor/admin)
- Login with role validation
- JWT token generation and validation
- Token refresh workflow
- OAuth2 token endpoint
- Protected route access
- Admin token requirements for doctor registration

### Models (`test_models.py`)
- User model (patient/doctor/admin roles)
- Appointment model and relationships
- Prescription model and doctor-patient links
- Reminder model for medication/appointments
- CallLog model for patient interactions
- Complex relationship testing
- Database constraints and validation

### Authentication Utils (`test_utils_auth.py`)
- Password hashing with bcrypt
- Password verification
- JWT token creation (access/refresh)
- Token decoding and validation
- Token expiration handling
- Security configuration testing

### Database (`test_database.py`)
- Database connection and setup
- Table creation and schema
- CRUD operations
- Unique constraints (email)
- Foreign key constraints
- Transaction handling and rollback
- Bulk operations performance

### Integration (`test_integration.py`)
- Complete user registration → login → access workflow
- Patient care workflow (appointment → prescription → reminder)
- Multi-patient doctor management
- Token refresh and OAuth2 workflows
- Error handling across system
- Concurrent user operations

## 🛠️ Test Configuration

### Environment Variables
Tests automatically set up isolated environment variables:
```python
SECRET_KEY = "test-secret-key-for-testing-only"
ADMIN_TOKEN = "test-admin-token"
ACCESS_TOKEN_EXPIRE_MINUTES = "30"
REFRESH_TOKEN_EXPIRE_MINUTES = "43200"
```

### Test Database
- Uses SQLite in-memory database for isolation
- Each test gets fresh database instance
- Automatic cleanup after each test

### Fixtures Available
- `test_client` - FastAPI test client
- `db_session` - Database session
- `sample_users` - Pre-created patient/doctor/admin users
- `auth_headers` - Authentication headers for each role
- `sample_healthcare_data` - Complete healthcare data set

## Key Test Scenarios

### Authentication Security
- Password hashing verification
- JWT token tampering protection
- Role-based access control
- Admin token validation
- Token expiration handling

### Healthcare Workflows
- Patient registration and profile management
- Doctor-patient appointment scheduling
- Prescription management and tracking
- Medication reminders
- Patient call logging and follow-ups

### Data Integrity
- Email uniqueness enforcement
- Foreign key relationship validation
- Required field validation
- Database transaction consistency

### Error Handling
- Invalid authentication attempts
- Malformed request data
- Permission violations
- Database constraint violations

## Performance Testing
- Concurrent user registration
- Bulk data operations
- Database query optimization
- Token generation performance

## Customization

### Adding New Tests
1. Create test file following naming convention (`test_*.py`)
2. Use appropriate markers (`@pytest.mark.unit`, etc.)
3. Leverage existing fixtures from `conftest.py`
4. Follow AAA pattern (Arrange, Act, Assert)

### Test Data Management
- Use fixtures for reusable test data
- Keep tests isolated and independent
- Clean up resources after each test

## Best Practices Implemented
- **Isolation** - Each test runs independently
- **Reusability** - Shared fixtures and utilities
- **Coverage** - Comprehensive test scenarios
- **Performance** - Efficient test execution
- **Maintainability** - Clear test structure and documentation
- **Security** - Authentication and authorization testing
- **Real-world scenarios** - Integration testing

## Troubleshooting

### Common Issues
1. **Import Errors** - Ensure all dependencies installed: `pip install -r requirements.txt`
2. **Database Errors** - Tests use isolated SQLite, no PostgreSQL needed
3. **Token Errors** - Test environment variables are set automatically
4. **Slow Tests** - Use `pytest -m "not slow"` to skip performance tests

### Debug Mode
```bash
# Run with maximum verbosity
pytest -vvv --tb=long

# Run single test with debugging
pytest test_auth_routes.py::TestUserLogin::test_login_patient_success -vvv
```

This test suite ensures your Healthcare AI application is robust, secure, and ready for production deployment!
