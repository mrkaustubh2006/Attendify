from datetime import datetime
import secrets
from models.database import db
# Many-to-many association table: which subjects a student is enrolled in
student_subjects = db.Table(
    'student_subjects',
    db.Column('student_id', db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), primary_key=True)
)
class Student(db.Model):
    __tablename__ = 'students'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    student_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    class_name = db.Column(db.String(100), nullable=False)
    roll_no = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(20), nullable=True) # Male, Female, Other
    qr_token = db.Column(db.String(100), unique=True, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='student', cascade='all, delete-orphan')
    # Many-to-many: subjects this student is enrolled in
    enrolled_subjects = db.relationship('Subject', secondary=student_subjects, backref='enrolled_students', lazy='dynamic')
    
    def __init__(self, **kwargs):
        super(Student, self).__init__(**kwargs)
        if not self.qr_token:
            self.qr_token = secrets.token_hex(32)
            
    def generate_new_qr_token(self):
        self.qr_token = secrets.token_hex(32)
        return self.qr_token
    def __repr__(self):
        return f"<Student {self.name} ({self.student_id})>"