from datetime import datetime
from app.models import db

# 服务-组织访问权限中间表
service_access = db.Table('service_access',
                          db.Column('service_id', db.Integer, db.ForeignKey('services.service_id'), primary_key=True),
                          db.Column('organization_id', db.Integer, db.ForeignKey('organizations.organization_id'),
                                    primary_key=True)
                          )

class Organization(db.Model):
    __tablename__ = 'organizations'

    organization_id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(200), nullable=False)
    short_name = db.Column(db.String(50), nullable=False)
    registration_email = db.Column(db.String(120), unique=True, nullable=False)
    proof_document = db.Column(db.String(255), nullable=True)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_by_e_admin = db.Column(db.Boolean, default=False)
    approved_by_e_admin_time = db.Column(db.DateTime)
    approved_by_senior_e_admin = db.Column(db.Boolean, default=False)
    approved_by_senior_e_admin_time = db.Column(db.DateTime)

    @property
    def is_fully_approved(self):
        return self.status == 'approved' and self.approved_by_e_admin and self.approved_by_senior_e_admin