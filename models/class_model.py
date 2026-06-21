from database import db

class Class(db.Model):
    __tablename__ = 'classes'
    
    id = db.Column(db.Integer, primary_key=True)
    class_name = db.Column(db.String(100), unique=True, nullable=False, index=True)
    department = db.Column(db.String(100), nullable=False)
    
    def __repr__(self):
        return f"<Class {self.class_name} - {self.department}>"
