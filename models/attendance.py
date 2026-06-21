from datetime import datetime, date
from database import db

class Attendance(db.Model):
    __tablename__ = 'attendance'
    
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('students.id', ondelete='CASCADE'), nullable=False)
    subject_id = db.Column(db.Integer, db.ForeignKey('subjects.id', ondelete='CASCADE'), nullable=False)
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id', ondelete='SET NULL'), nullable=True)
    
    date = db.Column(db.Date, default=date.today, nullable=False, index=True)
    time = db.Column(db.Time, default=lambda: datetime.now().time(), nullable=False)
    status = db.Column(db.String(20), default='Present', nullable=False)
    method = db.Column(db.String(20), default='QR', nullable=False)
    
    __table_args__ = (
        db.UniqueConstraint('student_id', 'subject_id', 'date', name='uq_student_subject_date'),
    )
    
    def __repr__(self):
        return f"<Attendance Student:{self.student_id} Subject:{self.subject_id} Date:{self.date} Status:{self.status}>"
