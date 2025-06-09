from datetime import datetime
from app.models import db

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'

    log_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id',ondelete='CASCADE'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.organization_id'), nullable=True)
    login_time = db.Column(db.DateTime, default=datetime.utcnow)
    logout_time = db.Column(db.DateTime, nullable=True)
    service_accessed = db.Column(db.String(100), nullable=True)
    provider_organization_id = db.Column(db.Integer, db.ForeignKey('organizations.organization_id'), nullable=True)
    details = db.Column(db.Text, nullable=True)

    # Relationships
    organization = db.relationship('Organization', foreign_keys=[organization_id], backref='user_activities')
    provider_organization = db.relationship('Organization', foreign_keys=[provider_organization_id],
                                            backref='service_activities')

    @property
    def user_email(self):
        return self.user.email if self.user else None

    @property
    def provider_organization_name(self):
        return self.provider_organization.short_name if self.provider_organization else None