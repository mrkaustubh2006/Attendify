from datetime import datetime
from flask_login import UserMixin
from database import db

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    student_profile = db.relationship('Student', backref='user', uselist=False, cascade='all, delete-orphan')
    teacher_profile = db.relationship('Teacher', backref='user', uselist=False, cascade='all, delete-orphan')
    audit_logs = db.relationship('AuditLog', backref='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
