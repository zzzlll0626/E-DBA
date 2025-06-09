from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from app.models import db, Course, Organization, ActivityLog, User

course_bp = Blueprint('course', __name__)


@course_bp.route('/search')
def search_courses():
    keyword = request.args.get('keyword', '')
    org_id = request.args.get('org_id')  # 添加组织ID参数

    # 记录活动
    if session.get('user_id'):
        user_id = session.get('user_id')
        log = ActivityLog.query.filter_by(
            user_id=user_id,
            logout_time=None
        ).order_by(ActivityLog.login_time.desc()).first()

        if log:
            log.service_accessed = f'course_search: {keyword}'
            db.session.commit()

    query = Course.query

    # 如果指定了组织ID，只搜索该组织的课程
    if org_id:
        query = query.filter(Course.organization_id == org_id)

    # 应用关键词搜索条件
    if keyword:
        courses = query.filter(
            Course.title.like(f'%{keyword}%') |
            Course.description.like(f'%{keyword}%')
        ).all()
    else:
        if org_id:  # 如果有组织ID但没有关键词，显示该组织的所有课程
            courses = query.all()
        else:
            courses = []  # 如果既没有组织ID也没有关键词，则不显示任何课程

    # 获取组织信息
    org_ids = {course.organization_id for course in courses}
    organizations = {
        org.organization_id: org
        for org in Organization.query.filter(Organization.organization_id.in_(org_ids)).all()
    }

    # 添加组织信息到课程
    for course in courses:
        org = organizations.get(course.organization_id)
        if org:
            course.organization_name = org.short_name

    # 如果指定了组织ID，传递组织信息到模板
    organization = None
    if org_id:
        organization = Organization.query.get(org_id)

    return render_template('course/search_results.html',
                           courses=courses,
                           keyword=keyword,
                           org_id=org_id,
                           organization=organization)


@course_bp.route('/view/<int:course_id>')
def view_course(course_id):
    course = Course.query.get_or_404(course_id)
    organization = Organization.query.get(course.organization_id)

    # 记录活动
    if session.get('user_id'):
        user_id = session.get('user_id')
        org_id = session.get('organization_id')

        log = ActivityLog.query.filter_by(
            user_id=user_id,
            logout_time=None
        ).order_by(ActivityLog.login_time.desc()).first()

        if log:
            log.service_accessed = f'view_course: {course.title}'
            log.provider_organization_id = course.organization_id
            db.session.commit()

    return render_template('course/view.html', course=course, organization=organization)


@course_bp.route('/organization/<int:org_id>')
def organization_courses(org_id):
    organization = Organization.query.get_or_404(org_id)
    courses = Course.query.filter_by(organization_id=org_id).all()

    # 记录活动
    if session.get('user_id'):
        user_id = session.get('user_id')

        log = ActivityLog.query.filter_by(
            user_id=user_id,
            logout_time=None
        ).order_by(ActivityLog.login_time.desc()).first()

        if log:
            log.service_accessed = f'organization_courses: {organization.short_name}'
            log.provider_organization_id = org_id
            db.session.commit()

    return render_template('course/organization_courses.html', organization=organization, courses=courses)