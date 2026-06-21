import os
import sys
def test_imports_and_db():
    print("Testing imports...")
    try:
        from app import create_app
        from models.database import db
        from models.user import User
        from models.student import Student
        from models.teacher import Teacher
        from models.subject import Subject
        from models.class_model import Class
        from models.attendance import Attendance
        from models.audit import AuditLog
        print("Imports successful!")
    except Exception as e:
        print(f"Import failed: {e}")
        sys.exit(1)
        
    print("Initializing Flask App context...")
    try:
        app = create_app()
        print("Application factory initialized successfully!")
    except Exception as e:
        print(f"App initialization failed: {e}")
        sys.exit(1)
        
    print("All checks passed successfully!")
if __name__ == '__main__':
    test_imports_and_db()