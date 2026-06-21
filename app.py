import os
from flask import Flask, redirect, url_for
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from config import Config
from models.database import db
from models.user import User
from auth import auth_bp, bcrypt
from admin import admin_bp
from teachers import teacher_bp
from students import student_bp
from api import api_bp
# Initialize Login Manager and CSRF Protection
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
csrf = CSRFProtect()
# Initialize Rate Limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"]
)
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))
def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extension objects
    config_class.init_app(app)
    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    limiter.init_app(app)
    
    # Exclude API endpoints from CSRF if token authentication or token-based headers are used,
    # but here we use session cookies + custom header csrf check 'X-CSRFToken' which is fully supported by flask-wtf!
    # Therefore, CSRF is active on everything, and JS fetches the csrf token and passes it via 'X-CSRFToken' header.
    
    # Register Blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(teacher_bp)
    app.register_blueprint(student_bp)
    app.register_blueprint(api_bp)
    
    # Initialize DB & Seed Default Admin Account if empty
    with app.app_context():
        db.create_all()
        
        # Check if database is empty of admin
        admin_exists = User.query.filter_by(role='admin').first()
        if not admin_exists:
            hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
            default_admin = User(
                email='admin@smart.com',
                password_hash=hashed_pw,
                role='admin'
            )
            db.session.add(default_admin)
            db.session.commit()
            print("==================================================")
            print("System Database initialized successfully.")
            print("Created default administrator account:")
            print("Email: admin@smart.com")
            print("Password: admin123")
            print("==================================================")
            
    return app
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
