from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user
from models.database import db
from models.student import Student
from models.subject import Subject
from models.attendance import Attendance
from middleware.auth import role_required, log_action
from services.qr_service import generate_qr_base64
from sqlalchemy import func
student_bp = Blueprint('student', __name__, url_prefix='/student')
@student_bp.route('/dashboard')
@login_required
@role_required('student')
def dashboard():
    student = current_user.student_profile
    enrolled_subjects = student.enrolled_subjects.all()
    
    # Generate static QR base64 code for scanner
    qr_code_base64 = generate_qr_base64(student.qr_token)
    
    # Calculate subject-wise attendance statistics
    subject_stats = []
    total_attended = 0
    total_conducted_all = 0
    
    for subject in enrolled_subjects:
        # Total classes conducted for this class and subject (based on attendance table dates)
        total_conducted = db.session.query(func.count(func.distinct(Attendance.date)))\
            .join(Student)\
            .filter(Student.class_name == student.class_name, Attendance.subject_id == subject.id)\
            .scalar() or 0
            
        # Total classes this student attended
        attended = Attendance.query.filter_by(student_id=student.id, subject_id=subject.id, status='Present').count()
        
        percentage = 100.0
        if total_conducted > 0:
            percentage = round((attended / total_conducted) * 100, 2)
            
        subject_stats.append({
            'subject_name': subject.subject_name,
            'subject_code': subject.subject_code,
            'attended': attended,
            'total_conducted': total_conducted,
            'percentage': percentage
        })
        
        total_attended += attended
        total_conducted_all += total_conducted
        
    overall_percentage = 100.0
    if total_conducted_all > 0:
        overall_percentage = round((total_attended / total_conducted_all) * 100, 2)
        
    # Get attendance history
    history_records = Attendance.query.filter_by(student_id=student.id).order_by(
        Attendance.date.desc(), Attendance.time.desc()
    ).all()
    
    return render_template(
        'student/dashboard.html',
        student=student,
        qr_code_base64=qr_code_base64,
        subject_stats=subject_stats,
        overall_percentage=overall_percentage,
        history_records=history_records
    )