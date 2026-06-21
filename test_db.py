import unittest
import os
import sys
from datetime import datetime, date
# Append current directory to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from app import create_app, bcrypt
from models.database import db
from models.user import User
from models.student import Student
from models.subject import Subject
from models.attendance import Attendance
from services.qr_service import QRService
from services.export_service import ExportService
from config import Config
class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
class SmartAttendanceTest(unittest.TestCase):
    def setUp(self):
        # Configure app for testing in memory using the TestConfig class
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        db.create_all()
        
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
        
    def test_password_hashing(self):
        """Test password encryption and verification"""
        password = "secure_password_123"
        hashed = bcrypt.generate_password_hash(password).decode('utf-8')
        
        self.assertNotEqual(password, hashed)
        self.assertTrue(bcrypt.check_password_hash(hashed, password))
        self.assertFalse(bcrypt.check_password_hash(hashed, "wrong_password"))
        
    def test_user_creation_and_roles(self):
        """Test database profiles and role mappings"""
        user = User(email="test@college.edu", password_hash="hashed", role="student")
        db.session.add(user)
        db.session.flush()
        
        student = Student(
            user_id=user.id,
            student_id="STU999",
            name="Alice Smith",
            class_name="SY BSc CS",
            roll_no="10"
        )
        db.session.add(student)
        db.session.commit()
        
        retrieved_student = Student.query.filter_by(student_id="STU999").first()
        self.assertIsNotNone(retrieved_student)
        self.assertEqual(retrieved_student.name, "Alice Smith")
        self.assertEqual(retrieved_student.user.email, "test@college.edu")
        self.assertIsNotNone(retrieved_student.qr_token)
        
    def test_qr_generation(self):
        """Test generating dynamic base64 QR codes"""
        token = "some_cryptographic_qr_token_string"
        qr_uri = QRService.generate_qr_base64(token)
        
        self.assertTrue(qr_uri.startswith("data:image/png;base64,"))
        
    def test_excel_export_format(self):
        """Test generating Excel reports does not raise exceptions"""
        records = [
            {
                'student_id': 'STU001',
                'name': 'John Doe',
                'class_name': 'FY BSc IT',
                'roll_no': '42',
                'subject_name': 'Mathematics',
                'subject_code': 'MATH101',
                'date': date.today(),
                'time': datetime.now().time(),
                'status': 'Present',
                'attendance_method': 'QR'
            }
        ]
        
        excel_stream = ExportService.export_to_excel(records, "Test Report")
        self.assertIsNotNone(excel_stream.getvalue())
if __name__ == '__main__':
    unittest.main()
