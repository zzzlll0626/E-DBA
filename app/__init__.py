# app/__init__.py
from datetime import timedelta

from flask import Flask, session, request
import os
from dotenv import load_dotenv
from flask_login import current_user

# 加载环境变量
load_dotenv()

# 初始化数据库
from app.models import db


def create_app():
    app = Flask(__name__)

    # 配置
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev_key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'mysql://username:password@localhost/edba')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)),'uploads')
    app.config['SESSION_COOKIE_SECURE'] = True  # 仅通过HTTPS发送cookie
    app.config['SESSION_COOKIE_HTTPONLY'] = True  # 防止JavaScript访问会话cookie
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=30)  # 会话有效期
    # 初始化插件
    db.init_app(app)

    # 导入模型
    from app.models.user import User
    from app.models.organization import Organization
    from app.models.service import Service

    # 注册蓝图
    from app.controllers.auth_controller import auth_bp
    from app.controllers.admin_controller import admin_bp
    from app.controllers.organization_controller import org_bp
    from app.controllers.provider_controller import provider_bp
    from app.controllers.course_controller import course_bp
    from app.controllers.user_controller import user_bp
    from app.controllers.payment_controller import payment_bp
    from app.controllers.main_controller import main_bp
    from app.controllers.helper_controller import helper_bp
    from app.controllers.consumer_controller import consumer_bp

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(org_bp, url_prefix='/organization')
    app.register_blueprint(provider_bp, url_prefix='/provider')
    app.register_blueprint(course_bp, url_prefix='/course')
    app.register_blueprint(user_bp, url_prefix='/user')
    app.register_blueprint(payment_bp, url_prefix='/payment')
    app.register_blueprint(main_bp)
    app.register_blueprint(helper_bp, url_prefix='/helper')
    app.register_blueprint(consumer_bp, url_prefix='/consumer')

    # 创建上传目录
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    config_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'config')
    os.makedirs(config_dir, exist_ok=True)

    #检查银行接口配置文件是否存在
    bank_config_path = os.path.join(config_dir,'BankInterfaceInfo')
    if not os.path.exists(bank_config_path):
        print(f"警告: 银行接口配置文件不存在，预期路径: {bank_config_path}")
        print("请确保在此路径下创建配置文件，否则银行相关功能将无法使用")
    # 自定义过滤器
    @app.template_filter('nl2br')
    def nl2br_filter(s):
        if s:
            return s.replace('\n', '<br>')
        return s

    @app.template_filter('tojson')
    def tojson_filter(obj):
        import json
        return json.dumps(obj)

    # 上下文处理器
    # 上下文处理器
    @app.context_processor
    def utility_processor():
        # 获取未读消息数量
        def get_unread_messages_count():
            try:
                # 检查用户是否已登录
                if not current_user.is_authenticated:
                    return 0

                # 使用 current_user 而不是 session 来获取用户 ID
                user_id = current_user.id if hasattr(current_user, 'id') else current_user.user_id

                # 如果无法获取有效的用户 ID，返回 0
                if not user_id:
                    return 0

                from app.models.policy import HelpRequest
                count = HelpRequest.query.filter_by(user_id=user_id, is_answered=True, is_read=False).count()
                return count
            except Exception:
                # 捕获所有可能的异常，确保页面仍能正常显示
                return 0

        return dict(get_unread_messages_count=get_unread_messages_count)

        @app.before_request
        def clear_session_for_auth_pages():
            # 如果访问的是登录或注册页面，且用户已登录，则清除会话
            if request.endpoint in ['auth.login', 'auth.register'] and session.get('user_id'):
                session.clear()
    return app