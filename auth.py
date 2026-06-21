from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from models.database import db
from models.user import User
from models.student import Student
from models.subject import Subject
from models.class_model import Class
from middleware.auth import log_action
import random
from datetime import datetime
auth_bp = Blueprint('auth', __name__)
bcrypt = Bcrypt()
@auth_bp.route('/')
def index():
    if current_user.is_authenticated:
        if current_user.role == 'admin':
            return redirect(url_for('admin.dashboard'))
        elif current_user.role == 'teacher':
            return redirect(url_for('teacher.dashboard'))
        elif current_user.role == 'student':
            return redirect(url_for('student.dashboard'))
    return redirect(url_for('auth.login'))
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
        
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        
        user = User.query.filter_by(email=email).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            log_action("User Logged In", user.id)
            flash('Logged in successfully!', 'success')
            
            if user.role == 'admin':
                return redirect(url_for('admin.dashboard'))
            elif user.role == 'teacher':
                return redirect(url_for('teacher.dashboard'))
            elif user.role == 'student':
                return redirect(url_for('student.dashboard'))
        else:
            flash('Invalid email or password.', 'danger')
            
    return render_template('auth/login.html')
@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('auth.index'))
        
    subjects = Subject.query.all()
    classes = Class.query.all()
    
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        name = request.form.get('name').strip()
        class_name = request.form.get('class_name')
        gender = request.form.get('gender')
        selected_subject_ids = request.form.getlist('subjects')
        
        # Validation
        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return render_template('auth/register.html', subjects=subjects, classes=classes)
            
        if not selected_subject_ids:
            flash('Adding subjects is mandatory during registration.', 'danger')
            return render_template('auth/register.html', subjects=subjects, classes=classes)
            
        # 1. Auto-generate Student ID
        while True:
            rand_num = random.randint(1000, 9999)
            student_id = f"STU{datetime.now().year}{rand_num}"
            if not Student.query.filter_by(student_id=student_id).first():
                break
                
        # 2. Auto-generate Roll Number (increment within class)
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
        
        # Create user
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(email=email, password_hash=hashed_pw, role='student')
        db.session.add(new_user)
        db.session.flush() # Populate new_user.id
        
        # Create student profile
        new_student = Student(
            user_id=new_user.id,
            student_id=student_id,
            name=name,
            class_name=class_name,
            roll_no=roll_no,
            gender=gender
        )
        
        # Add selected subjects to student
        for sub_id in selected_subject_ids:
            subject = Subject.query.get(int(sub_id))
            if subject:
                new_student.enrolled_subjects.append(subject)
                
        db.session.add(new_student)
        db.session.commit()
        
        log_action("Student Registered", new_user.id)
        flash(f'Registration successful! Your generated ID is: {student_id} and Roll No is: {roll_no}. Please login.', 'success')
        return redirect(url_for('auth.login'))
        
    return render_template('auth/register.html', subjects=subjects, classes=classes)
@auth_bp.route('/logout')
@login_required
def logout():
    log_action("User Logged Out")
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('auth.login'))