from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required, current_user
from flask_bcrypt import Bcrypt
from models.database import db
from models.user import User
from models.student import Student
from models.teacher import Teacher
from models.subject import Subject
from models.class_model import Class
from models.attendance import Attendance
from models.audit import AuditLog
from middleware.auth import role_required, log_action
from services.report_service import export_attendance_to_excel, export_attendance_to_pdf
from sqlalchemy import func
from datetime import datetime, date
admin_bp = Blueprint('admin', __name__, url_prefix='/admin')
bcrypt = Bcrypt()
@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    # Gather analytics data
    total_students = Student.query.count()
    total_teachers = Teacher.query.count()
    total_subjects = Subject.query.count()
    total_classes = Class.query.count()
    
    # Calculate overall attendance rate
    total_attendance_records = Attendance.query.count()
    present_records = Attendance.query.filter_by(status='Present').count()
    attendance_rate = 0
    if total_attendance_records > 0:
        attendance_rate = round((present_records / total_attendance_records) * 100, 2)
        
    recent_logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).limit(10).all()
    
    return render_template(
        'admin/dashboard.html',
        total_students=total_students,
        total_teachers=total_teachers,
        total_subjects=total_subjects,
        total_classes=total_classes,
        attendance_rate=attendance_rate,
        recent_logs=recent_logs
    )
# --- Students CRUD ---
@admin_bp.route('/students')
@login_required
@role_required('admin')
def list_students():
    students = Student.query.all()
    subjects = Subject.query.all()
    classes = Class.query.all()
    return render_template('admin/students.html', students=students, subjects=subjects, classes=classes)
@admin_bp.route('/students/add', methods=['POST'])
@login_required
@role_required('admin')
def add_student():
    email = request.form.get('email').strip().lower()
    password = request.form.get('password')
    name = request.form.get('name').strip()
    student_id = request.form.get('student_id', '').strip().upper()
    class_name = request.form.get('class_name')
    roll_no = request.form.get('roll_no', '').strip()
    gender = request.form.get('gender')
    selected_subject_ids = request.form.getlist('subjects')
    
    if User.query.filter_by(email=email).first():
        flash('Email is already registered.', 'danger')
        return redirect(url_for('admin.list_students'))
        
    if student_id and Student.query.filter_by(student_id=student_id).first():
        flash('Student ID is already registered.', 'danger')
        return redirect(url_for('admin.list_students'))
        
    # 1. Auto-generate Student ID if empty
    if not student_id:
        import random
        from datetime import datetime
        while True:
            rand_num = random.randint(1000, 9999)
            student_id = f"STU{datetime.now().year}{rand_num}"
            if not Student.query.filter_by(student_id=student_id).first():
                break
                
    # 2. Auto-generate Roll Number if empty
    if not roll_no:
        students_in_class = Student.query.filter_by(class_name=class_name).all()
        max_roll = 0
        for s in students_in_class:
            try:
                r_num = int(s.roll_no)
                if r_num > max_roll:
                    max_roll = r_num
            except ValueError:
                pass
        roll_no = str(max_roll + 1)
        
    # Create User
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(email=email, password_hash=hashed_pw, role='student')
    db.session.add(user)
    db.session.flush()
    
    # Create Student
    student = Student(
        user_id=user.id,
        student_id=student_id,
        name=name,
        class_name=class_name,
        roll_no=roll_no,
        gender=gender
    )
    
    for sub_id in selected_subject_ids:
        subject = Subject.query.get(int(sub_id))
        if subject:
            student.enrolled_subjects.append(subject)
            
    db.session.add(student)
    db.session.commit()
    
    log_action(f"Added Student: {name} ({student_id})")
    flash(f'Student {name} added successfully! Generated ID: {student_id}, Roll No: {roll_no}', 'success')
    return redirect(url_for('admin.list_students'))
@admin_bp.route('/students/edit/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def edit_student(id):
    student = Student.query.get_or_404(id)
    user = student.user
    
    email = request.form.get('email').strip().lower()
    name = request.form.get('name').strip()
    student_id = request.form.get('student_id').strip().upper()
    class_name = request.form.get('class_name')
    roll_no = request.form.get('roll_no').strip()
    gender = request.form.get('gender')
    password = request.form.get('password')
    selected_subject_ids = request.form.getlist('subjects')
    
    # Check uniqueness
    existing_user = User.query.filter(User.email == email, User.id != user.id).first()
    if existing_user:
        flash('Email is already in use.', 'danger')
        return redirect(url_for('admin.list_students'))
        
    existing_student = Student.query.filter(Student.student_id == student_id, Student.id != id).first()
    if existing_student:
        flash('Student ID is already in use.', 'danger')
        return redirect(url_for('admin.list_students'))
        
    user.email = email
    if password:
        user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
    student.name = name
    student.student_id = student_id
    student.class_name = class_name
    student.roll_no = roll_no
    student.gender = gender
    
    # Update subjects
    student.enrolled_subjects = []
    for sub_id in selected_subject_ids:
        subject = Subject.query.get(int(sub_id))
        if subject:
            student.enrolled_subjects.append(subject)
            
    db.session.commit()
    log_action(f"Updated Student Profile: {name}")
    flash('Student details updated successfully.', 'success')
    return redirect(url_for('admin.list_students'))
@admin_bp.route('/students/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_student(id):
    student = Student.query.get_or_404(id)
    user = student.user
    name = student.name
    
    # Deleting User will cascade delete the Student record too
    db.session.delete(user)
    db.session.commit()
    
    log_action(f"Deleted Student: {name}")
    flash('Student deleted successfully.', 'success')
    return redirect(url_for('admin.list_students'))
# --- Teachers CRUD ---
@admin_bp.route('/teachers')
@login_required
@role_required('admin')
def list_teachers():
    teachers = Teacher.query.all()
    subjects = Subject.query.all()
    return render_template('admin/teachers.html', teachers=teachers, subjects=subjects)
@admin_bp.route('/teachers/add', methods=['POST'])
@login_required
@role_required('admin')
def add_teacher():
    email = request.form.get('email').strip().lower()
    password = request.form.get('password')
    name = request.form.get('name').strip()
    teacher_id = request.form.get('teacher_id').strip().upper()
    selected_subject_ids = request.form.getlist('subjects')
    
    if User.query.filter_by(email=email).first():
        flash('Email is already registered.', 'danger')
        return redirect(url_for('admin.list_teachers'))
        
    if Teacher.query.filter_by(teacher_id=teacher_id).first():
        flash('Teacher ID is already registered.', 'danger')
        return redirect(url_for('admin.list_teachers'))
        
    # Create User
    hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
    user = User(email=email, password_hash=hashed_pw, role='teacher')
    db.session.add(user)
    db.session.flush()
    
    # Create Teacher
    teacher = Teacher(
        user_id=user.id,
        teacher_id=teacher_id,
        name=name,
        email=email
    )
    
    for sub_id in selected_subject_ids:
        subject = Subject.query.get(int(sub_id))
        if subject:
            teacher.subjects.append(subject)
            
    db.session.add(teacher)
    db.session.commit()
    
    log_action(f"Added Teacher: {name} ({teacher_id})")
    flash(f'Teacher {name} added successfully!', 'success')
    return redirect(url_for('admin.list_teachers'))
@admin_bp.route('/teachers/edit/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def edit_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    user = teacher.user
    
    email = request.form.get('email').strip().lower()
    name = request.form.get('name').strip()
    teacher_id = request.form.get('teacher_id').strip().upper()
    password = request.form.get('password')
    selected_subject_ids = request.form.getlist('subjects')
    
    existing_user = User.query.filter(User.email == email, User.id != user.id).first()
    if existing_user:
        flash('Email is already in use.', 'danger')
        return redirect(url_for('admin.list_teachers'))
        
    existing_teacher = Teacher.query.filter(Teacher.teacher_id == teacher_id, Teacher.id != id).first()
    if existing_teacher:
        flash('Teacher ID is already in use.', 'danger')
        return redirect(url_for('admin.list_teachers'))
        
    user.email = email
    teacher.email = email
    if password:
        user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        
    teacher.name = name
    teacher.teacher_id = teacher_id
    
    # Update teacher subjects
    teacher.subjects = []
    for sub_id in selected_subject_ids:
        subject = Subject.query.get(int(sub_id))
        if subject:
            teacher.subjects.append(subject)
            
    db.session.commit()
    log_action(f"Updated Teacher Profile: {name}")
    flash('Teacher details updated successfully.', 'success')
    return redirect(url_for('admin.list_teachers'))
@admin_bp.route('/teachers/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_teacher(id):
    teacher = Teacher.query.get_or_404(id)
    user = teacher.user
    name = teacher.name
    
    db.session.delete(user)
    db.session.commit()
    
    log_action(f"Deleted Teacher: {name}")
    flash('Teacher deleted successfully.', 'success')
    return redirect(url_for('admin.list_teachers'))
# --- Subjects CRUD ---
@admin_bp.route('/subjects')
@login_required
@role_required('admin')
def list_subjects():
    subjects = Subject.query.all()
    return render_template('admin/subjects.html', subjects=subjects)
@admin_bp.route('/subjects/add', methods=['POST'])
@login_required
@role_required('admin')
def add_subject():
    name = request.form.get('subject_name').strip()
    code = request.form.get('subject_code').strip().upper()
    
    if Subject.query.filter_by(subject_code=code).first():
        flash('Subject code already exists.', 'danger')
        return redirect(url_for('admin.list_subjects'))
        
    subject = Subject(subject_name=name, subject_code=code)
    db.session.add(subject)
    db.session.commit()
    
    log_action(f"Added Subject: {name} ({code})")
    flash(f'Subject {name} added successfully!', 'success')
    return redirect(url_for('admin.list_subjects'))
@admin_bp.route('/subjects/edit/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def edit_subject(id):
    subject = Subject.query.get_or_404(id)
    name = request.form.get('subject_name').strip()
    code = request.form.get('subject_code').strip().upper()
    
    existing = Subject.query.filter(Subject.subject_code == code, Subject.id != id).first()
    if existing:
        flash('Subject code already exists.', 'danger')
        return redirect(url_for('admin.list_subjects'))
        
    subject.subject_name = name
    subject.subject_code = code
    db.session.commit()
    
    log_action(f"Updated Subject: {name}")
    flash('Subject updated successfully.', 'success')
    return redirect(url_for('admin.list_subjects'))
@admin_bp.route('/subjects/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_subject(id):
    subject = Subject.query.get_or_404(id)
    name = subject.subject_name
    db.session.delete(subject)
    db.session.commit()
    
    log_action(f"Deleted Subject: {name}")
    flash('Subject deleted successfully.', 'success')
    return redirect(url_for('admin.list_subjects'))
# --- Classes & Departments CRUD ---
@admin_bp.route('/classes')
@login_required
@role_required('admin')
def list_classes():
    classes = Class.query.all()
    return render_template('admin/classes.html', classes=classes)
@admin_bp.route('/classes/add', methods=['POST'])
@login_required
@role_required('admin')
def add_class():
    name = request.form.get('class_name').strip()
    department = request.form.get('department').strip()
    
    if Class.query.filter_by(class_name=name).first():
        flash('Class name already exists.', 'danger')
        return redirect(url_for('admin.list_classes'))
        
    c = Class(class_name=name, department=department)
    db.session.add(c)
    db.session.commit()
    
    log_action(f"Added Class: {name}")
    flash(f'Class {name} added successfully!', 'success')
    return redirect(url_for('admin.list_classes'))
@admin_bp.route('/classes/edit/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def edit_class(id):
    c = Class.query.get_or_404(id)
    name = request.form.get('class_name').strip()
    department = request.form.get('department').strip()
    
    existing = Class.query.filter(Class.class_name == name, Class.id != id).first()
    if existing:
        flash('Class name already exists.', 'danger')
        return redirect(url_for('admin.list_classes'))
        
    c.class_name = name
    c.department = department
    db.session.commit()
    
    log_action(f"Updated Class: {name}")
    flash('Class updated successfully.', 'success')
    return redirect(url_for('admin.list_classes'))
@admin_bp.route('/classes/delete/<int:id>', methods=['POST'])
@login_required
@role_required('admin')
def delete_class(id):
    c = Class.query.get_or_404(id)
    name = c.class_name
    db.session.delete(c)
    db.session.commit()
    
    log_action(f"Deleted Class: {name}")
    flash('Class deleted successfully.', 'success')
    return redirect(url_for('admin.list_classes'))
# --- Attendance Records View & Filter ---
@admin_bp.route('/attendance')
@login_required
@role_required('admin')
def view_attendance():
    subject_id = request.args.get('subject_id', type=int)
    class_name = request.args.get('class_name')
    date_str = request.args.get('date')
    
    query = Attendance.query.join(Student)
    
    if subject_id:
        query = query.filter(Attendance.subject_id == subject_id)
    if class_name:
        query = query.filter(Student.class_name == class_name)
    if date_str:
        try:
            filter_date = datetime.strptime(date_str, '%Y-%m-%d').date()
            query = query.filter(Attendance.date == filter_date)
        except ValueError:
            pass
            
    records = query.order_by(Attendance.date.desc(), Attendance.time.desc()).all()
    
    subjects = Subject.query.all()
    classes = Class.query.all()
    
    return render_template(
        'admin/attendance.html',
        records=records,
        subjects=subjects,
        classes=classes,
        selected_subject=subject_id,
        selected_class=class_name,
        selected_date=date_str
    )
# --- Report Exports ---
@admin_bp.route('/export/excel')
@login_required
@role_required('admin')
def export_excel():
    records = Attendance.query.order_by(Attendance.date.desc()).all()
    excel_stream = export_attendance_to_excel(records)
    log_action("Exported Attendance Report (Excel)")
    return send_file(
        excel_stream,
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        as_attachment=True,
        download_name=f"Attendance_Report_{date.today().strftime('%Y%m%d')}.xlsx"
    )
@admin_bp.route('/export/pdf')
@login_required
@role_required('admin')
def export_pdf():
    records = Attendance.query.order_by(Attendance.date.desc()).all()
    pdf_stream = export_attendance_to_pdf(records, "System Attendance Records")
    log_action("Exported Attendance Report (PDF)")
    return send_file(
        pdf_stream,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"Attendance_Report_{date.today().strftime('%Y%m%d')}.pdf"
    )
# --- Audit Logs ---
@admin_bp.route('/logs')
@login_required
@role_required('admin')
def view_logs():
    logs = AuditLog.query.order_by(AuditLog.timestamp.desc()).all()
    return render_template('admin/logs.html', logs=logs)