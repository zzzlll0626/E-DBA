# from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from app.models import db

class User(db.Model):
    __tablename__ = 'users'

    user_id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    # password_hash = db.Column(db.String(255), nullable=True)  # For admin users
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.organization_id'))
    access_level = db.Column(db.Integer, default=1)  # 1: public, 2: consumer, 3: provider
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    role = db.Column(db.String(50), default='user')  # user, T-Admin, E-Admin, Senior-E-Admin, O-Convener
    last_login = db.Column(db.DateTime, nullable=True)  # 新增字段，记录最后登录时间
    wildcard_source = db.Column(db.String(120), nullable=True)
    is_wildcard_user = db.Column(db.Boolean, default=False)  # 新增字段，标记是否通过通配符创建
    activity_logs = db.relationship('ActivityLog', backref='user', cascade='all, delete-orphan')
    # Relationships
    organization = db.relationship('Organization', backref='members')



    # def check_password(self, password):
    #     if self.password_hash:
    #         return check_password_hash(self.password_hash, password)
    #     return False

    @property
    def is_admin(self):
        return self.role in ['T-Admin', 'E-Admin', 'Senior-E-Admin']

    @property
    def is_convener(self):
        return self.role == 'O-Convener'