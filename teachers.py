from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from models.database import db
from models.teacher import Teacher
from models.subject import Subject
from models.class_model import Class
from models.attendance import Attendance
from models.student import Student
from middleware.auth import role_required, log_action
from services.report_service import export_attendance_to_excel, export_attendance_to_pdf
from datetime import datetime, date
teacher_bp = Blueprint('teacher', __name__, url_prefix='/teacher')
@teacher_bp.route('/dashboard', methods=['GET', 'POST'])
@login_required
@role_required('teacher')
def dashboard():
    teacher = current_user.teacher_profile
    all_subjects = Subject.query.all()
    classes = Class.query.all()
    
    # Handle Teacher Subject Management: Add/Remove subjects from their taught list
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'manage_subjects':
            selected_subject_ids = request.form.getlist('subjects')
            teacher.subjects = []
            for sub_id in selected_subject_ids:
                subject = Subject.query.get(int(sub_id))
                if subject:
                    teacher.subjects.append(subject)
            db.session.commit()
            log_action("Teacher updated their subject portfolio")
            flash('Your subject portfolio was updated successfully.', 'success')
            return redirect(url_for('teacher.dashboard'))
            
    # Calculate today's stats for this teacher
    today_records = Attendance.query.filter_by(teacher_id=teacher.id, date=date.today()).all()
    today_count = len(today_records)
    
    # Get subjects taught by this teacher
    taught_subjects = teacher.subjects.all()
    
    return render_template(
        'teacher/dashboard.html',
        teacher=teacher,
        all_subjects=all_subjects,
        taught_subjects=taught_subjects,
        classes=classes,
        today_count=today_count
    )
@teacher_bp.route('/session', methods=['GET'])
@login_required
@role_required('teacher')
def session_setup():
    # Helper redirection to dashboard
    return redirect(url_for('teacher.dashboard'))
@teacher_bp.route('/session/<int:subject_id>/<string:class_name>')
@login_required
@role_required('teacher')
def active_session(subject_id, class_name):
    teacher = current_user.teacher_profile
    subject = Subject.query.get_or_404(subject_id)
    
    # Check if student enrollment count for this class and subject exists
    total_students = Student.query.filter_by(class_name=class_name).filter(
        Student.enrolled_subjects.any(id=subject_id)
    ).count()
    
    return render_template(
        'teacher/session.html',
        subject=subject,
        class_name=class_name,
        teacher=teacher,
        total_students=total_students
    )
@teacher_bp.route('/history')
@login_required
@role_required('teacher')
def history():
    teacher = current_user.teacher_profile
    records = Attendance.query.filter_by(teacher_id=teacher.id).order_by(
        Attendance.date.desc(), Attendance.time.desc()
    ).all()
    return render_template('teacher/history.html', records=records)
@teacher_bp.route('/export/excel')
@login_required
@role_required('teacher')
def export_excel():
    teacher = current_user.teacher_profile
    records = Attendance.query.filter_by(teacher_id=teacher.id).order_by(Attendance.date.desc()).all()
    excel_stream = export_attendance_to_excel(records)
    log_action("Teacher Exported Attendance Report (Excel)")
    return send_file(
        excel_stream,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=f"Teacher_Report_{date.today().strftime('%Y%m%d')}.xlsx"
    )
@teacher_bp.route('/export/pdf')
@login_required
@role_required('teacher')
def export_pdf():
    teacher = current_user.teacher_profile
    records = Attendance.query.filter_by(teacher_id=teacher.id).order_by(Attendance.date.desc()).all()
    pdf_stream = export_attendance_to_pdf(records, f"Attendance Report - {teacher.name}")
    log_action("Teacher Exported Attendance Report (PDF)")
    return send_file(
        pdf_stream,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"Teacher_Report_{date.today().strftime('%Y%m%d')}.pdf"
    )