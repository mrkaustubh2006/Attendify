from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from models.database import db
from models.student import Student
from models.subject import Subject
from models.attendance import Attendance
from middleware.auth import role_required, log_action
from datetime import datetime, date
api_bp = Blueprint('api', __name__, url_prefix='/api')
@api_bp.route('/attendance/mark', methods=['POST'])
@login_required
@role_required('teacher')
def mark_attendance():
    """
    Endpoint for marking attendance via scanned static QR code.
    Verifies token, prevents duplicates, and checks enrollment constraints.
    """
    teacher = current_user.teacher_profile
    data = request.get_json() or {}
    
    qr_token = data.get('qr_token')
    subject_id = data.get('subject_id')
    class_name = data.get('class_name')
    
    if not qr_token or not subject_id or not class_name:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
        
    # 1. Verify QR token exists
    student = Student.query.filter_by(qr_token=qr_token).first()
    if not student:
        return jsonify({'success': False, 'message': 'Invalid QR Code token'}), 404
        
    # 2. Check if student class matches the current session class
    if student.class_name != class_name:
        return jsonify({
            'success': False, 
            'message': f"Student belongs to class '{student.class_name}', but session is for '{class_name}'"
        }), 400
        
    # 3. Check if student is enrolled in the subject (Subject Cart constraint)
    subject = Subject.query.get(subject_id)
    if not subject:
        return jsonify({'success': False, 'message': 'Subject not found'}), 404
        
    if subject not in student.enrolled_subjects.all():
        return jsonify({
            'success': False,
            'message': f"Student is not enrolled in subject '{subject.subject_name}' ({subject.subject_code})"
        }), 400
        
    # 4. Check for duplicate attendance today
    today = date.today()
    existing = Attendance.query.filter_by(
        student_id=student.id,
        subject_id=subject.id,
        date=today
    ).first()
    
    if existing:
        return jsonify({
            'success': False,
            'message': f"Duplicate: Attendance already marked for {student.name} today at {existing.time.strftime('%H:%M:%S')}"
        }), 409
        
    # 5. Mark Attendance
    try:
        new_attendance = Attendance(
            student_id=student.id,
            subject_id=subject.id,
            teacher_id=teacher.id,
            date=today,
            status='Present',
            method='QR'
        )
        db.session.add(new_attendance)
        db.session.commit()
        
        # Log action
        log_action(f"Marked QR Attendance: {student.name} for {subject.subject_name}", current_user.id)
        
        return jsonify({
            'success': True,
            'message': f"Attendance marked for {student.name}",
            'student': {
                'name': student.name,
                'student_id': student.student_id,
                'roll_no': student.roll_no,
                'time': new_attendance.time.strftime('%H:%M:%S')
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'message': 'Database error occurred'}), 500
@api_bp.route('/attendance/session_history/<int:subject_id>/<string:class_name>', methods=['GET'])
@login_required
@role_required('teacher')
def get_session_history(subject_id, class_name):
    """
    Get all attendance records marked today for a specific class and subject.
    Allows real-time list updates in the teacher interface.
    """
    today = date.today()
    records = Attendance.query.join(Student).filter(
        Attendance.subject_id == subject_id,
        Student.class_name == class_name,
        Attendance.date == today
    ).order_by(Attendance.time.desc()).all()
    
    data = []
    for r in records:
        data.append({
            'student_id': r.student.student_id,
            'name': r.student.name,
            'roll_no': r.student.roll_no,
            'time': r.time.strftime('%H:%M:%S'),
            'status': r.status,
            'method': r.method
        })
        
    return jsonify({'success': True, 'records': data})
