from datetime import datetime
from app.models import db
from .organization import service_access

service_view_access = db.Table('service_view_access',
                          db.Column('service_id', db.Integer, db.ForeignKey('services.service_id'), primary_key=True),
                          db.Column('organization_id', db.Integer, db.ForeignKey('organizations.organization_id'),
                                    primary_key=True)
                          )

service_download_access = db.Table('service_download_access',
                          db.Column('service_id', db.Integer, db.ForeignKey('services.service_id'), primary_key=True),
                          db.Column('organization_id', db.Integer, db.ForeignKey('organizations.organization_id'),
                                    primary_key=True)
                          )

class Service(db.Model):
    __tablename__ = 'services'

    service_id = db.Column(db.Integer, primary_key=True)
    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.organization_id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    type = db.Column(db.String(50), nullable=False)  # course_info, student_identity, thesis_sharing
    description = db.Column(db.Text)
    price = db.Column(db.Float, default=0)  # 这里保存的是论文下载的价格，而不是服务访问的价格
    is_configured = db.Column(db.Boolean, default=False)
    is_public = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    access_organizations = db.relationship(
        'Organization',
        secondary=service_access,
        backref=db.backref('accessible_services', lazy='dynamic')
    )

    view_organizations = db.relationship(
        'Organization',
        secondary=service_view_access,
        backref=db.backref('viewable_services', lazy='dynamic')
    )

    download_organizations = db.relationship(
        'Organization',
        secondary=service_download_access,
        backref=db.backref('downloadable_services', lazy='dynamic')
    )


# 修改 service.py 模型
class APIConfig(db.Model):
    __tablename__ = 'api_configs'

    config_id = db.Column(db.Integer, primary_key=True)
    service_id = db.Column(db.Integer, db.ForeignKey('services.service_id'), nullable=False)
    config_name = db.Column(db.String(100), nullable=False)  # 新增配置名称字段
    base_url = db.Column(db.String(255), nullable=False)
    path = db.Column(db.String(255), nullable=False)
    method = db.Column(db.String(10), nullable=False)
    input = db.Column(db.JSON, default={})
    output = db.Column(db.JSON, default={})
    is_active = db.Column(db.Boolean, default=True)  # 标记是否激活
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, onupdate=datetime.utcnow)

    # 服务关联
    service = db.relationship('Service', backref=db.backref('api_configs', lazy='dynamic'))