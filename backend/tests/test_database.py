import pytest
import os
import sys
import os
from datetime import datetime
from sqlalchemy import text

# Add the parent directory to the Python path to allow imports from the main application
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from app.database.base import get_db
from app.database.models import User

# Database session is now provided by conftest.py
class TestDatabaseConnection:
    """Test cases for database connection and setup"""
    
    def test_database_connection(self, db_session):
        """Test that database connection works"""
        result = db_session.execute(text("SELECT 1")).scalar()
        assert result == 1
    
    def test_tables_created(self, db_session):
        """Test that all tables are created"""
        # Check if tables exist by querying sqlite_master
        tables = db_session.execute(
            text("SELECT name FROM sqlite_master WHERE type='table'")
        ).fetchall()
        
        table_names = [table[0] for table in tables]
        
        # Check that our model tables exist
        assert "users" in table_names
        assert "appointments" in table_names
        assert "prescriptions" in table_names
        assert "reminders" in table_names
        assert "call_logs" in table_names
    
    def test_get_db_dependency(self):
        """Test the get_db dependency function"""
        db_gen = get_db()
        db = next(db_gen)
        
        # Should return a database session
        assert db is not None
        
        # Clean up
        try:
            next(db_gen)
        except StopIteration:
            pass  # Expected behavior

class TestDatabaseOperations:
    """Test cases for basic database operations"""
    
    def test_create_user_in_db(self, db_session):
        """Test creating a user in the database"""
        user = User(
            first_name="Test",
            last_name="User",
            email="test@example.com",
            password_hash="hashed_password",
            role="patient"
        )
        
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        assert user.user_id is not None
        assert user.created_at is not None
    
    def test_query_user_from_db(self, db_session):
        """Test querying a user from the database"""
        # Create user
        user = User(
            first_name="Query",
            last_name="Test",
            email="query@example.com",
            password_hash="hashed_password",
            role="doctor",
            specialty="Cardiology"
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Query user
        queried_user = db_session.query(User).filter(
            User.email == "query@example.com"
        ).first()
        
        assert queried_user is not None
        assert queried_user.first_name == "Query"
        assert queried_user.specialty == "Cardiology"
    
    def test_update_user_in_db(self, db_session):
        """Test updating a user in the database"""
        # Create user
        user = User(
            first_name="Update",
            last_name="Test",
            email="update@example.com",
            password_hash="hashed_password",
            role="patient"
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Update user
        user.phone_number = "1234567890"
        user.address = "123 Updated St"
        db_session.commit()
        
        # Verify update
        updated_user = db_session.query(User).filter(
            User.email == "update@example.com"
        ).first()
        
        assert updated_user.phone_number == "1234567890"
        assert updated_user.address == "123 Updated St"
    
    def test_delete_user_from_db(self, db_session):
        """Test deleting a user from the database"""
        # Create user
        user = User(
            first_name="Delete",
            last_name="Test",
            email="delete@example.com",
            password_hash="hashed_password",
            role="patient"
        )
        
        db_session.add(user)
        db_session.commit()
        user_id = user.user_id
        
        # Delete user
        db_session.delete(user)
        db_session.commit()
        
        # Verify deletion
        deleted_user = db_session.query(User).filter(
            User.user_id == user_id
        ).first()
        
        assert deleted_user is None

class TestDatabaseConstraints:
    """Test cases for database constraints and validation"""
    
    def test_unique_email_constraint(self, db_session):
        """Test that email uniqueness is enforced"""
        # Create first user
        user1 = User(
            first_name="First",
            last_name="User",
            email="same@example.com",
            password_hash="hashed_password",
            role="patient"
        )
        
        db_session.add(user1)
        db_session.commit()
        
        # Try to create second user with same email
        user2 = User(
            first_name="Second",
            last_name="User",
            email="same@example.com",
            password_hash="hashed_password",
            role="doctor"
        )
        
        db_session.add(user2)
        
        with pytest.raises(Exception):  # Should raise integrity error
            db_session.commit()
    
    def test_required_fields_constraint(self, db_session):
        """Test that required fields are enforced"""
        # Try to create user without required fields
        with pytest.raises(Exception):
            user = User(
                first_name="Test",
                # Missing last_name, email, password_hash, role
            )
            db_session.add(user)
            db_session.commit()
    
    def test_foreign_key_constraints(self, db_session):
        """Test foreign key constraints"""
        from models import Appointment
        from sqlalchemy import text
        
        # For SQLite, we need to enable foreign key constraints
        if 'sqlite' in str(db_session.bind.url):
            db_session.execute(text('PRAGMA foreign_keys = ON'))
        
        # Try to create appointment with non-existent user IDs
        appointment = Appointment(
            patient_id=999,  # Non-existent user
            doctor_id=888,   # Non-existent user
            appointment_date=datetime.now(),
            status="scheduled"
        )
        
        db_session.add(appointment)
        
        # The specific exception might vary by database, so we'll catch the general Exception
        with pytest.raises(Exception) as exc_info:
            db_session.commit()
        
        # For SQLite, we should see an IntegrityError for foreign key constraint violation
        # For other databases, we'll just verify that an exception was raised
        if 'sqlite' in str(db_session.bind.url):
            assert 'FOREIGN KEY constraint failed' in str(exc_info.value)

class TestDatabaseTransactions:
    """Test cases for database transactions"""
    
    def test_transaction_rollback(self, db_session):
        """Test transaction rollback on error"""
        # Create a user
        user = User(
            first_name="Transaction",
            last_name="Test",
            email="transaction@example.com",
            password_hash="hashed_password",
            role="patient"
        )
        
        db_session.add(user)
        
        try:
            # Try to create another user with same email (should fail)
            duplicate_user = User(
                first_name="Duplicate",
                last_name="User",
                email="transaction@example.com",
                password_hash="hashed_password",
                role="doctor"
            )
            db_session.add(duplicate_user)
            db_session.commit()
        except Exception:
            db_session.rollback()
        
        # Verify that no users were created due to rollback
        users = db_session.query(User).filter(
            User.email == "transaction@example.com"
        ).all()
        
        assert len(users) == 0
    
    def test_transaction_commit(self, db_session):
        """Test successful transaction commit"""
        # Create multiple users in one transaction
        users = [
            User(
                first_name=f"User{i}",
                last_name="Test",
                email=f"user{i}@example.com",
                password_hash="hashed_password",
                role="patient"
            )
            for i in range(3)
        ]
        
        for user in users:
            db_session.add(user)
        
        db_session.commit()
        
        # Verify all users were created
        created_users = db_session.query(User).filter(
            User.email.like("user%@example.com")
        ).all()
        
        assert len(created_users) == 3

class TestDatabasePerformance:
    """Test cases for database performance considerations"""
    
    def test_bulk_insert_performance(self, db_session):
        """Test bulk insert operations"""
        import time
        
        # Create many users
        users = [
            User(
                first_name=f"Bulk{i}",
                last_name="User",
                email=f"bulk{i}@example.com",
                password_hash="hashed_password",
                role="patient"
            )
            for i in range(100)
        ]
        
        start_time = time.time()
        
        # Bulk insert
        db_session.add_all(users)
        db_session.commit()
        
        end_time = time.time()
        
        # Verify all users were created
        bulk_users = db_session.query(User).filter(
            User.email.like("bulk%@example.com")
        ).all()
        
        assert len(bulk_users) == 100
        assert end_time - start_time < 5.0  # Should complete within 5 seconds
    
    def test_query_with_index(self, db_session):
        """Test querying with indexed fields"""
        # Create user
        user = User(
            first_name="Index",
            last_name="Test",
            email="index@example.com",
            password_hash="hashed_password",
            role="patient"
        )
        
        db_session.add(user)
        db_session.commit()
        
        # Query by email (indexed field)
        result = db_session.query(User).filter(
            User.email == "index@example.com"
        ).first()
        
        assert result is not None
        assert result.first_name == "Index"

if __name__ == "__main__":
    pytest.main([__file__])
