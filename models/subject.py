from database import db

# Many-to-many association table: which subjects a teacher is teaching/managing
teacher_subjects = db.Table(
    'teacher_subjects',
    db.Column('teacher_id', db.Integer, db.ForeignKey('teachers.id', ondelete='CASCADE'), primary_key=True),
    db.Column('subject_id', db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), primary_key=True)
)

class Subject(db.Model):
    __tablename__ = 'subjects'
    
    id = db.Column(db.Integer, primary_key=True)
    subject_name = db.Column(db.String(100), nullable=False)
    subject_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    
    attendance_records = db.relationship('Attendance', backref='subject', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f"<Subject {self.subject_name} ({self.subject_code})>"
