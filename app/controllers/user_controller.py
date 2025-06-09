import os

from flask import Blueprint, render_template, redirect, url_for, request, flash, session, send_file
from flask_login import login_required

from app.models import db, User, Organization, HelpRequest, ActivityLog, Service, Course, Policy

user_bp = Blueprint('user', __name__)


@user_bp.route('/dashboard')
def dashboard():
    if not session.get('user_id'):
        flash('please log in first', 'danger')
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    user = User.query.get(user_id)

    # 获取搜索关键词
    search_keyword = request.args.get('search', '')

    # 获取可访问的组织（添加搜索过滤）
    query = Organization.query.filter_by(status='approved')

    # 如果有搜索关键词，添加过滤条件
    if search_keyword:
        query = query.filter(
            db.or_(
                Organization.full_name.like(f'%{search_keyword}%'),
                Organization.short_name.like(f'%{search_keyword}%')
            )
        )

    organizations = query.all()

    # 获取最近活动
    recent_activities = ActivityLog.query.filter_by(user_id=user_id).order_by(ActivityLog.login_time.desc()).limit(
        5).all()

    # 添加格式化时间字符串
    for activity in recent_activities:
        activity.login_time_str = activity.login_time.strftime('%Y-%m-%d %H:%M')
        if activity.logout_time:
            activity.logout_time_str = activity.logout_time.strftime('%Y-%m-%d %H:%M')

    return render_template('user/dashboard.html',
                           user=user,
                           organizations=organizations,
                           recent_activities=recent_activities,
                           search_keyword=search_keyword)


@user_bp.route('/help_center', methods=['GET'])
def help_center():
    if not session.get('user_id'):
        flash('please log in first', 'danger')
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')

    # 获取帮助请求
    pending_requests = HelpRequest.query.filter_by(user_id=user_id, is_answered=False).order_by(
        HelpRequest.submit_time.desc()).all()
    answered_requests = HelpRequest.query.filter_by(user_id=user_id, is_answered=True).order_by(
        HelpRequest.response_time.desc()).all()

    return render_template('user/help_center.html',
                           pending_requests=pending_requests,
                           answered_requests=answered_requests)


@user_bp.route('/submit_help_request', methods=['POST'])
def submit_help_request():
    if not session.get('user_id'):
        flash('please log in first', 'danger')
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    title = request.form.get('title')
    description = request.form.get('description')

    if not title or not description:
        flash('Title and description are required fields', 'danger')
        return redirect(url_for('user.help_center'))

    help_request = HelpRequest(
        user_id=user_id,
        title=title,
        description=description
    )
    db.session.add(help_request)
    db.session.commit()

    flash('The help request has been submitted', 'success')
    return redirect(url_for('user.help_center'))


@user_bp.route('/view_organization/<int:org_id>')
def view_organization(org_id):
    if not session.get('user_id'):
        flash('please log in first', 'danger')
        return redirect(url_for('auth.login'))

    organization = Organization.query.get_or_404(org_id)

    # 获取公开服务
    services = Service.query.filter_by(
        organization_id=org_id,
        is_configured=True,
        is_public=True
    ).all()

    # 获取部分课程
    courses = Course.query.filter_by(organization_id=org_id).limit(6).all()

    # 记录活动
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    log = ActivityLog.query.filter_by(
        user_id=user_id,
        logout_time=None
    ).order_by(ActivityLog.login_time.desc()).first()

    if log:
        log.service_accessed = f'view_organization: {organization.short_name}'
        log.provider_organization_id = org_id
        db.session.commit()

    return render_template('user/view_organization.html',
                           organization=organization,
                           services=services,
                           courses=courses,
                           user=user)

@user_bp.route('/policies')
def view_policies():
    """登录用户查看政策列表"""
    policies = Policy.query.all()
    return render_template('user/policy.html', policies=policies)


@user_bp.route('/view_policy_pdf/<int:policy_id>')
def view_policy_pdf(policy_id):
    """用户在线查看政策 PDF 文件"""
    policy = Policy.query.get_or_404(policy_id)

    if not policy.file_path:
        flash('There is no associated PDF file for this policy', 'warning')
        return redirect(url_for('user.view_policies'))

    try:

        # 获取项目根目录
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
        # 构建完整的文件路径
        full_path = os.path.join(root_dir, policy.file_path)
        # 检查文件是否存在
        if not os.path.exists(full_path):
            flash(f'The file cannot be found: {os.path.basename(policy.file_path)}', 'danger')
            return redirect(url_for('user.view_policies'))

        # 返回文件用于在浏览器中查看
        return send_file(
            full_path,
            mimetype='application/pdf'
        )

    except Exception as e:
        flash(f'Failed to view the file: {str(e)}', 'danger')
        return redirect(url_for('user.view_policies'))

