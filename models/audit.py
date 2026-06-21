from datetime import datetime
from database import db

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='SET NULL'), nullable=True)
    action = db.Column(db.String(255), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    ip_address = db.Column(db.String(45), nullable=True)
    
    def __repr__(self):
        return f"<AuditLog User:{self.user_id} Action:{self.action} Timestamp:{self.timestamp}>"
