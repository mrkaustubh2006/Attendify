from datetime import datetime
from models.database import db
from models.subject import teacher_subjects
class Teacher(db.Model):
    __tablename__ = 'teachers'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    teacher_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    attendance_records = db.relationship('Attendance', backref='teacher', cascade='all, delete-orphan')
    # Many-to-many: subjects taught by this teacher
    subjects = db.relationship('Subject', secondary=teacher_subjects, backref='teachers', lazy='dynamic')
    
    def __repr__(self):
        return f"<Teacher {self.name} ({self.teacher_id})>"