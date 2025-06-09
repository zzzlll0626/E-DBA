from datetime import datetime
from app.models import db

class Policy(db.Model):
    __tablename__ = 'policies'

    policy_id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=True)
    description = db.Column(db.Text)


class HelpRequest(db.Model):
    __tablename__ = 'help_requests'

    request_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    is_answered = db.Column(db.Boolean, default=False)
    is_read = db.Column(db.Boolean, default=False)
    response = db.Column(db.Text, nullable=True)
    submit_time = db.Column(db.DateTime, default=datetime.utcnow)
    response_time = db.Column(db.DateTime, nullable=True)

    # Relationships
    user = db.relationship('User', backref='help_requests')

    @property
    def user_email(self):
        return self.user.email if self.user else None

    @property
    def user_role(self):
        return self.user.role if self.user else None

    @property
    def organization_name(self):
        return self.user.organization.short_name if self.user and self.user.organization else None