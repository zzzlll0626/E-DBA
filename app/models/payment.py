from datetime import datetime
from app.models import db

class Member(db.Model):
    __tablename__ = 'members'

    member_id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.organization_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    access_level = db.Column(db.Integer, nullable=False)  # 1, 2, 3
    quota = db.Column(db.Float, default=0)  # Thesis download quota in RMB
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    organization = db.relationship('Organization', backref='member_list')


class BankAccount(db.Model):
    __tablename__ = 'bank_accounts'

    account_id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.organization_id'), unique=True, nullable=False)
    bank_name = db.Column(db.String(100), nullable=False)
    account_name = db.Column(db.String(100), nullable=False)
    account_no = db.Column(db.String(100), nullable=False)
    # password_hash = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(255), nullable=True)  # 新增明文密码字段
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)
    is_system_account = db.Column(db.Boolean, default=False)
    # Relationships
    organization = db.relationship('Organization', backref='bank_account')

    def set_password(self, password):
        # self.password_hash = generate_password_hash(password)
        self.password = password  # 明文存储


class Payment(db.Model):
    __tablename__ = 'payments'

    payment_id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.user_id'), nullable=False)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.organization_id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_type = db.Column(db.String(50),
                             nullable=False)  # membership_fee, service_fee, thesis_download, identity_auth
    payment_method = db.Column(db.String(50), nullable=False)  # transfer, quota
    service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'), nullable=True)
    receiver_organization_id = db.Column(db.Integer, db.ForeignKey('organizations.organization_id'), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    # Relationships
    user = db.relationship('User', backref='payments')
    organization = db.relationship('Organization', foreign_keys=[organization_id], backref='payments_made')
    receiver_organization = db.relationship('Organization', foreign_keys=[receiver_organization_id],
                                            backref='payments_received')
    service = db.relationship('Service', backref='payments')


class Transaction(db.Model):
    __tablename__ = 'transactions'

    transaction_id = db.Column(db.Integer, primary_key=True)
    payment_id = db.Column(db.Integer, db.ForeignKey('payments.payment_id'), nullable=True)
    from_organization_id = db.Column(db.Integer, db.ForeignKey('organizations.organization_id'), nullable=False)
    to_organization_id = db.Column(db.Integer, db.ForeignKey('organizations.organization_id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, success, failed
    reason = db.Column(db.Text, nullable=True)  # For failed transactions
    transaction_time = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    payment = db.relationship('Payment', backref='transactions')
    from_organization = db.relationship('Organization', foreign_keys=[from_organization_id],
                                        backref='outgoing_transactions')
    to_organization = db.relationship('Organization', foreign_keys=[to_organization_id],
                                      backref='incoming_transactions')


class MembershipFee(db.Model):
    __tablename__ = 'membership_fees'

    fee_id = db.Column(db.Integer, primary_key=True)
    access_level = db.Column(db.Integer, nullable=False)  # 1, 2, 3
    fee_type = db.Column(db.String(20), nullable=False)  # flat_rate, per_person
    fee_amount = db.Column(db.Float, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

