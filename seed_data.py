import os
from app import create_app
from models.database import db
from models.user import User
from models.student import Student
from models.teacher import Teacher
from models.subject import Subject
from models.class_model import Class
from routes.auth import bcrypt
def seed_database():
    app = create_app()
    with app.app_context():
        print("Starting Database Seeding...")
        
        # 1. Clear database (Optional but helpful for clean seeding)
        # db.drop_all()
        # db.create_all()
        
        # Check if seed has already been run
        if Class.query.first():
            print("Database already contains data. Seeding aborted.")
            return
        # 2. Add Classes
        classes_data = [
            {"class_name": "TY CS", "department": "Computer Science"},
            {"class_name": "SY CS", "department": "Computer Science"},
            {"class_name": "FY BSc IT", "department": "Information Technology"}
        ]
        classes_map = {}
        for c_data in classes_data:
            c = Class(class_name=c_data["class_name"], department=c_data["department"])
            db.session.add(c)
            classes_map[c_data["class_name"]] = c
        
        # 3. Add Subjects
        subjects_data = [
            {"subject_name": "Computer Networks", "subject_code": "CS-301"},
            {"subject_name": "Software Engineering", "subject_code": "CS-302"},
            {"subject_name": "Database Management Systems", "subject_code": "CS-201"},
            {"subject_name": "Object Oriented Programming", "subject_code": "CS-202"},
            {"subject_name": "Web Development", "subject_code": "IT-101"}
        ]
        subjects_map = {}
        for s_data in subjects_data:
            s = Subject(subject_name=s_data["subject_name"], subject_code=s_data["subject_code"])
            db.session.add(s)
            subjects_map[s_data["subject_code"]] = s
            
        db.session.flush()
        # 4. Add Teacher
        teacher_email = "teacher@smart.com"
        if not User.query.filter_by(email=teacher_email).first():
            hashed_pw = bcrypt.generate_password_hash("teacher123").decode("utf-8")
            teacher_user = User(email=teacher_email, password_hash=hashed_pw, role="teacher")
            db.session.add(teacher_user)
            db.session.flush()
            
            teacher_profile = Teacher(
                user_id=teacher_user.id,
                teacher_id="TCH101",
                name="Dr. Sarah Jenkins",
                email=teacher_email
            )
            # Assign subjects to teacher
            teacher_profile.subjects.append(subjects_map["CS-301"])
            teacher_profile.subjects.append(subjects_map["CS-302"])
            teacher_profile.subjects.append(subjects_map["CS-201"])
            db.session.add(teacher_profile)
            print("Seeded Teacher: teacher@smart.com (password: teacher123)")
        # 5. Add Students
        students_data = [
            {
                "email": "student1@smart.com",
                "name": "Alice Smith",
                "class_name": "TY CS",
                "roll_no": "1",
                "gender": "Female",
                "subjects": ["CS-301", "CS-302"]
            },
            {
                "email": "student2@smart.com",
                "name": "Bob Jones",
                "class_name": "TY CS",
                "roll_no": "2",
                "gender": "Male",
                "subjects": ["CS-301", "CS-201"]
            },
            {
                "email": "student3@smart.com",
                "name": "Charlie Brown",
                "class_name": "SY CS",
                "roll_no": "1",
                "gender": "Male",
                "subjects": ["CS-201", "CS-202"]
            }
        ]
        
        for index, stu in enumerate(students_data):
            if not User.query.filter_by(email=stu["email"]).first():
                hashed_pw = bcrypt.generate_password_hash("student123").decode("utf-8")
                user = User(email=stu["email"], password_hash=hashed_pw, role="student")
                db.session.add(user)
                db.session.flush()
                
                student_profile = Student(
                    user_id=user.id,
                    student_id=f"STU202600{index+1}",
                    name=stu["name"],
                    class_name=stu["class_name"],
                    roll_no=stu["roll_no"],
                    gender=stu["gender"]
                )
                
                # Enroll in subjects
                for sub_code in stu["subjects"]:
                    student_profile.enrolled_subjects.append(subjects_map[sub_code])
                    
                db.session.add(student_profile)
                print(f"Seeded Student: {stu['email']} (password: student123)")
        db.session.commit()
        print("Database Seeding Completed Successfully!")
if __name__ == '__main__':
    seed_database()
