from functools import wraps
from flask import abort, request
from flask_login import current_user
from models.database import db
from models.audit import AuditLog
def role_required(*roles):
    """
    Decorator to restrict route access to specific roles.
    Example: @role_required('admin', 'teacher')
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                abort(401)  # Unauthorized
            if current_user.role not in roles:
                abort(403)  # Forbidden
            return f(*args, **kwargs)
        return decorated_function
    return decorator
def log_action(action, user_id=None):
    """
    Helper function to log system actions to the AuditLog database.
    """
    try:
        ip = request.remote_addr if request else '127.0.0.1'
        u_id = user_id or (current_user.id if current_user and current_user.is_authenticated else None)
        log_entry = AuditLog(
            user_id=u_id,
            action=action,
            ip_address=ip
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        print(f"Error writing audit log: {e}")
        # Make sure database issues in auditing don't crash main flows
        db.session.rollback()
