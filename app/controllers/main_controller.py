from flask import Blueprint, render_template, redirect, url_for, request, flash, session, send_file
from app.models import db, Organization, Policy

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    # 不再传递组织数据到模板
    return render_template('index.html')


@main_bp.route('/about')
def about():
    return render_template('about.html')


@main_bp.route('/policy')
def policy():
    # 获取所有政策
    policies = Policy.query.all()

    return render_template('user/policy.html', policies=policies)


@main_bp.route('/download_policy/<int:policy_id>')
def download_policy(policy_id):
    policy = Policy.query.get_or_404(policy_id)

    try:
        return send_file(policy.file_path, as_attachment=True)
    except Exception as e:
        flash(f'download failed: {str(e)}', 'danger')
        return redirect(url_for('main.policy'))