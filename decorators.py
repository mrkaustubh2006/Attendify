from functools import wraps
from flask import abort, flash, redirect, url_for
from flask_login import current_user
def role_required(*roles):
    """
    Decorator to restrict route access to specific user roles.
    Example: @role_required('admin', 'teacher')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                return redirect(url_for('auth.login'))
            if current_user.role not in roles:
                flash("You do not have permission to access this page.", "danger")
                # Redirect to appropriate page based on role
                if current_user.role == 'teacher':
                    return redirect(url_for('teacher.dashboard'))
                elif current_user.role == 'student':
                    return redirect(url_for('student.dashboard'))
                elif current_user.role == 'admin':
                    return redirect(url_for('admin.dashboard'))
                else:
                    abort(403)
            return f(*args, **kwargs)
        return decorated_function
    return decorator