from flask import Blueprint, render_template, redirect, url_for, request, flash, session, send_from_directory, send_file
from app.models import db, User, Organization, HelpRequest, Policy, ActivityLog, MembershipFee, BankAccount
from werkzeug.utils import secure_filename
import os
import datetime

admin_bp = Blueprint('admin', __name__)


# T-Admin 相关路由
@admin_bp.route('/tadmin/dashboard')
def tadmin_dashboard():
    if session.get('user_role') != 'T-Admin':
        flash('No access right', 'danger')
        return redirect(url_for('main.index'))

    # 获取帮助请求
    unanswered_requests = HelpRequest.query.filter_by(is_answered=False).all()
    answered_requests = HelpRequest.query.filter_by(is_answered=True).order_by(HelpRequest.response_time.desc()).limit(
        10).all()

    # 添加格式化时间字符串
    for request in unanswered_requests:
        request.submit_time_str = request.submit_time.strftime('%Y-%m-%d %H:%M')

    for request in answered_requests:
        request.response_time_str = request.response_time.strftime('%Y-%m-%d %H:%M')

    return render_template('admin/tadmin_dashboard.html',
                           unanswered_requests=unanswered_requests,
                           answered_requests=answered_requests)


@admin_bp.route('/tadmin/answer_help/<int:request_id>', methods=['GET', 'POST'])
def answer_help_request(request_id):
    if session.get('user_role') != 'T-Admin':
        flash('No access right', 'danger')
        return redirect(url_for('main.index'))

    help_request = HelpRequest.query.get_or_404(request_id)

    if request.method == 'POST':
        answer = request.form.get('answer')
        send_email = request.form.get('send_email') == 'on'

        if not answer:
            flash('Please provide an answer', 'danger')
            return redirect(url_for('admin.answer_help_request', request_id=request_id))

        help_request.response = answer
        help_request.is_answered = True
        help_request.response_time = datetime.datetime.utcnow()
        db.session.commit()

        flash('Answer submitted', 'success')
        return redirect(url_for('admin.tadmin_dashboard'))

    return render_template('admin/answer_help.html', request=help_request)


@admin_bp.route('/tadmin/setup_eadmin', methods=['POST'])
def setup_eadmin():
    if session.get('user_role') != 'T-Admin':
        flash('No access right', 'danger')
        return redirect(url_for('main.index'))

    email = request.form.get('email')
    password = request.form.get('password')

    if User.query.filter_by(email=email).first():
        flash('This email address is already in use', 'danger')
        return redirect(url_for('admin.tadmin_dashboard'))

    user = User(email=email, role='E-Admin')
    # user.set_password(password)
    db.session.add(user)
    db.session.commit()

    flash(f'E-Admin {email} Create Success', 'success')
    return redirect(url_for('admin.tadmin_dashboard'))


@admin_bp.route('/tadmin/setup_senior_eadmin', methods=['POST'])
def setup_senior_eadmin():
    if session.get('user_role') != 'T-Admin':
        flash('No access right', 'danger')
        return redirect(url_for('main.index'))

    email = request.form.get('email')
    password = request.form.get('password')

    if User.query.filter_by(email=email).first():
        flash('This email address is already in use', 'danger')
        return redirect(url_for('admin.tadmin_dashboard'))

    user = User(email=email, role='Senior-E-Admin')
    # user.set_password(password)
    db.session.add(user)
    db.session.commit()

    flash(f'Senior E-Admin {email} Create success', 'success')
    return redirect(url_for('admin.tadmin_dashboard'))


# E-Admin 相关路由
@admin_bp.route('/eadmin/dashboard')
def eadmin_dashboard():
    if session.get('user_role') != 'E-Admin':
        flash('No access right', 'danger')
        return redirect(url_for('main.index'))

    # 获取待处理的申请
    applications = Organization.query.filter_by(status='pending', approved_by_e_admin=False).all()

    return render_template('admin/eadmin_dashboard.html', applications=applications)


@admin_bp.route('/eadmin/review/<int:app_id>', methods=['GET', 'POST'])
def review_application(app_id):
    if session.get('user_role') not in ['E-Admin', 'Senior-E-Admin']:
        flash('No access right', 'danger')
        return redirect(url_for('main.index'))

    application = Organization.query.get_or_404(app_id)

    if request.method == 'POST':
        status = request.form.get('status')
        reject_reason = request.form.get('reject_reason')

        if session.get('user_role') == 'E-Admin' and not application.approved_by_e_admin:
            if status == 'approve':
                application.approved_by_e_admin = True
                application.approved_by_e_admin_time = datetime.datetime.utcnow()
                db.session.commit()

                # TODO: 通知Senior E-Admin
                flash('The application has been approved and is awaiting review by Senior E-Admin', 'success')
            else:
                application.status = 'rejected'
                db.session.commit()

                # TODO: 发送拒绝邮件
                # send_email(application.registration_email, '组织注册申请被拒绝', f'拒绝原因：{reject_reason}')

                flash('Application rejected', 'success')

            return redirect(url_for('admin.eadmin_dashboard'))

        elif session.get(
                'user_role') == 'Senior-E-Admin' and application.approved_by_e_admin and not application.approved_by_senior_e_admin:
            if status == 'approve':
                application.approved_by_senior_e_admin = True
                application.approved_by_senior_e_admin_time = datetime.datetime.utcnow()
                application.status = 'approved'

                # 创建O-Convener用户
                user = User(
                    email=application.registration_email,
                    role='O-Convener',
                    organization_id=application.organization_id,
                    access_level=3  # 私有数据提供者
                )
                db.session.add(user)
                db.session.commit()

                # TODO: 发送通知邮件
                flash('The application has been finally approved and the organization has been created', 'success')
            else:
                application.status = 'rejected'
                db.session.commit()

                # TODO: 发送拒绝邮件
                flash('Application rejected', 'success')

            return redirect(url_for('admin.senior_eadmin_dashboard'))

    return render_template('admin/review_application.html', application=application)


@admin_bp.route('/eadmin/setup_bank_account', methods=['GET', 'POST'])
def setup_bank_account():
    if session.get('user_role') != 'E-Admin':
        flash('No access right', 'danger')
        return redirect(url_for('main.index'))

    # 获取或创建系统组织
    system_org = Organization.query.filter_by(short_name='SYSTEM').first()
    if not system_org:
        try:
            # 创建系统组织
            system_org = Organization(
                full_name='System Organization',
                short_name='SYSTEM',
                registration_email='system@edba.example.com',
                status='approved',
                approved_by_e_admin=True,
                approved_by_senior_e_admin=True
            )
            db.session.add(system_org)
            db.session.commit()

            # 组织创建后获取其ID
            system_org = Organization.query.filter_by(short_name='SYSTEM').first()
        except Exception as e:
            flash(f'Error creating system organization: {str(e)}', 'danger')
            return render_template('admin/setup_bank_account.html', current_account=None)

    # 获取当前系统银行账户
    current_account = BankAccount.query.filter_by(organization_id=system_org.organization_id).first()

    if request.method == 'POST':
        bank_name = request.form.get('bank_name')
        account_name = request.form.get('account_name')
        account_no = request.form.get('account_number')
        password = request.form.get('password')

        # 验证银行账户有效性
        from app.utils.bank_utils import check_bank_balance

        # 如果不是在更新模式下或者提供了新密码，则验证账户
        if not current_account or password:
            try:
                # 验证银行账户
                result = check_bank_balance(bank_name, account_name, account_no, password)

                if result['status'] != 'success':
                    flash(f'Bank account verification failed: {result.get("message", "Unknown Error")}', 'danger')
                    return render_template('admin/setup_bank_account.html', current_account=current_account)

                # 显示成功信息和余额
                flash(f'Bank account verification successful, current balance: {result.get("balance", "Unknown")}', 'success')
            except Exception as e:
                flash(f'Error connecting to bank interface: {str(e)}', 'danger')
                return render_template('admin/setup_bank_account.html', current_account=current_account)

        try:
            if current_account:
                # 更新现有账户
                current_account.bank_name = bank_name
                current_account.account_name = account_name
                current_account.account_no = account_no

                # 只有在提供密码时才更新密码
                # if password:
                #     current_account.set_password(password)

                # 更新时间戳
                current_account.updated_at = datetime.datetime.utcnow()
                db.session.commit()

                # 记录日志
                log = ActivityLog(
                    user_id=session.get('user_id'),
                    service_accessed='bank_account_update',
                    organization_id=system_org.organization_id
                )
                db.session.add(log)
                db.session.commit()

                flash('System bank account updated successfully', 'success')
            else:
                # 创建新账户
                new_account = BankAccount(
                    bank_name=bank_name,
                    account_name=account_name,
                    account_no=account_no,
                    organization_id=system_org.organization_id,  # 使用系统组织ID
                    is_system_account=True
                )
                # new_account.set_password(password)

                db.session.add(new_account)

                # 记录日志
                log = ActivityLog(
                    user_id=session.get('user_id'),
                    service_accessed='bank_account_setup',
                    organization_id=system_org.organization_id
                )
                db.session.add(log)
                db.session.commit()

                flash('System bank account has been successfully set up', 'success')

            return redirect(url_for('admin.eadmin_dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f'Error setting up bank account: {str(e)}', 'danger')

    return render_template('admin/setup_bank_account.html', current_account=current_account)

@admin_bp.route('/view_proof_document/<int:organization_id>')
def view_proof_document(organization_id):
    """在线查看组织证明文档"""
    organization = Organization.query.get_or_404(organization_id)

    if not organization.proof_document:
        flash('There is no supporting documentation associated with this organization', 'warning')
        if session.get('user_role') == 'E-Admin':
            return redirect(url_for('admin.eadmin_dashboard'))
        else:
            return redirect(url_for('admin.senior_eadmin_dashboard'))

    try:
        # 获取项目根目录
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

        # 构建完整的文件路径
        full_path = os.path.join(root_dir, organization.proof_document)

        # 检查文件是否存在
        if not os.path.exists(full_path):
            flash(f'File not found: {os.path.basename(organization.proof_document)}', 'danger')
            if session.get('user_role') == 'E-Admin':
                return redirect(url_for('admin.eadmin_dashboard'))
            else:
                return redirect(url_for('admin.senior_eadmin_dashboard'))

        # 返回文件用于在浏览器中查看
        return send_file(
            full_path,
            mimetype='application/pdf'
        )

    except Exception as e:
        flash(f'Failed to view file: {str(e)}', 'danger')
        if session.get('user_role') == 'E-Admin':
            return redirect(url_for('admin.eadmin_dashboard'))
        else:
            return redirect(url_for('admin.senior_eadmin_dashboard'))


@admin_bp.route('/admin/manage_policies', methods=['GET', 'POST'])
def manage_policies():
    if session.get('user_role') not in ['E-Admin', 'Senior-E-Admin']:
        flash('No access right', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            title = request.form.get('title')
            description = request.form.get('description')
            if 'policy_file' not in request.files:
                flash('Please upload the policy file', 'danger')
                return redirect(url_for('admin.manage_policies'))

            policy_file = request.files['policy_file']
            if policy_file.filename == '':
                flash('No file selected', 'danger')
                return redirect(url_for('admin.manage_policies'))

            # 获取项目根目录（假设admin_controller.py在app目录下）
            root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

            # 创建上传目录（相对于项目根目录）
            upload_folder = os.path.join(root_dir, 'uploads', 'policies')
            os.makedirs(upload_folder, exist_ok=True)

            # 安全处理文件名
            filename = secure_filename(policy_file.filename)

            # 构建完整的文件路径
            file_path = os.path.join(upload_folder, filename)

            # 保存文件
            try:
                policy_file.save(file_path)
            except Exception as e:
                flash(f'Failed to save file: {str(e)}', 'danger')
                return redirect(url_for('admin.manage_policies'))

            # 在数据库中存储相对路径（相对于项目根目录）
            db_file_path = os.path.join('uploads', 'policies', filename)

            # 标准化路径分隔符（统一使用正斜杠，避免在不同操作系统间的问题）
            db_file_path = db_file_path.replace('\\', '/')

            policy = Policy(
                title=title,
                description=description,  # 添加描述字段
                file_path=db_file_path
            )
            db.session.add(policy)
            db.session.commit()

            flash('Policy added successfully', 'success')

        elif action == 'update':
            policy_id = request.form.get('policy_id')
            title = request.form.get('title')
            description = request.form.get('description')

            policy = Policy.query.get_or_404(policy_id)
            policy.title = title
            policy.description = description
            policy.updated_at = datetime.datetime.utcnow()

            if 'policy_file' in request.files and request.files['policy_file'].filename != '':
                policy_file = request.files['policy_file']

                # 获取项目根目录
                root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

                # 创建上传目录
                upload_folder = os.path.join(root_dir, 'uploads', 'policies')
                os.makedirs(upload_folder, exist_ok=True)

                # 如果之前有文件，尝试删除
                if policy.file_path:
                    old_file_path = os.path.join(root_dir, policy.file_path.replace('/', os.path.sep))
                    if os.path.exists(old_file_path):
                        try:
                            os.remove(old_file_path)
                        except Exception:
                            # 如果删除失败，继续执行
                            pass

                # 安全处理文件名
                filename = secure_filename(policy_file.filename)

                # 构建完整的文件路径
                file_path = os.path.join(upload_folder, filename)

                # 保存文件
                try:
                    policy_file.save(file_path)
                except Exception as e:
                    flash(f'Failed to save file: {str(e)}', 'danger')
                    return redirect(url_for('admin.manage_policies'))

                # 在数据库中存储相对路径
                db_file_path = os.path.join('uploads', 'policies', filename).replace('\\', '/')
                policy.file_path = db_file_path

            db.session.commit()
            flash('Policy updated successfully', 'success')

        elif action == 'delete':
            policy_id = request.form.get('policy_id')
            policy = Policy.query.get_or_404(policy_id)

            # 删除文件
            if policy.file_path:
                root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
                file_path = os.path.join(root_dir, policy.file_path.replace('/', os.path.sep))
                if os.path.exists(file_path):
                    try:
                        os.remove(file_path)
                    except Exception:
                        # 如果删除失败，继续执行
                        pass

            db.session.delete(policy)
            db.session.commit()
            flash('Policy deleted successfully', 'success')

    policies = Policy.query.all()
    return render_template('admin/policies.html', policies=policies)


@admin_bp.route('/view_policy_pdf/<int:policy_id>')
def view_policy_pdf(policy_id):
    """在线查看政策 PDF 文件"""
    policy = Policy.query.get_or_404(policy_id)

    if not policy.file_path:
        flash('This policy has no associated PDF file', 'warning')
        return redirect(url_for('admin.manage_policies'))

    try:
        # 获取项目根目录
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

        # 构建完整的文件路径
        full_path = os.path.join(root_dir, policy.file_path)

        # 检查文件是否存在
        if not os.path.exists(full_path):
            flash(f'File not found: {os.path.basename(policy.file_path)}', 'danger')
            return redirect(url_for('admin.manage_policies'))

        # 返回文件用于在浏览器中查看（不作为附件下载）
        return send_file(
            full_path,
            mimetype='application/pdf'
        )

    except Exception as e:
        flash(f'Failed to view file: {str(e)}', 'danger')
        return redirect(url_for('admin.manage_policies'))


@admin_bp.route('/download_policy/<int:policy_id>')
def download_policy(policy_id):
    policy = Policy.query.get_or_404(policy_id)

    if not policy.file_path:
        flash('This policy has no associated PDF file', 'warning')
        return redirect(url_for('admin.manage_policies'))

    try:
        # 获取项目根目录
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))

        # 构建完整的文件路径
        full_path = os.path.join(root_dir, policy.file_path)

        # 检查文件是否存在
        if not os.path.exists(full_path):
            flash(f'File not found: {os.path.basename(policy.file_path)}', 'danger')
            return redirect(url_for('admin.manage_policies'))

        # 使用 send_file 代替 send_from_directory
        return send_file(
            full_path,
            as_attachment=True,
            download_name=os.path.basename(policy.file_path)
        )

    except Exception as e:
        flash(f'Download failed: {str(e)}', 'danger')
        return redirect(url_for('admin.manage_policies'))

@admin_bp.route('/admin/manage_membership_fees', methods=['GET', 'POST'])
def manage_membership_fees():
    # 权限检查
    if not session.get('user_id') or session.get('user_role') not in ['E-Admin', 'Senior-E-Admin']:
        flash('No access right', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        try:
            # 处理表单提交
            # 级别1支持flat_rate和per_person
            fee_type_1 = request.form.get('fee_type_1')
            fee_amount_1 = float(request.form.get('fee_amount_1', 0))

            if fee_type_1 in ['flat_rate', 'per_person']:
                fee_setting_1 = MembershipFee.query.filter_by(access_level=1).first()

                if fee_setting_1:
                    fee_setting_1.fee_type = fee_type_1
                    fee_setting_1.fee_amount = fee_amount_1
                else:
                    fee_setting_1 = MembershipFee(
                        access_level=1,
                        fee_type=fee_type_1,
                        fee_amount=fee_amount_1
                    )
                    db.session.add(fee_setting_1)

            # 级别2只支持per_person和free
            fee_type_2 = request.form.get('fee_type_2')
            fee_amount_2 = float(request.form.get('fee_amount_2', 0))

            if fee_type_2 == 'free':
                fee_amount_2 = 0

            fee_setting_2 = MembershipFee.query.filter_by(access_level=2).first()

            if fee_setting_2:
                fee_setting_2.fee_type = fee_type_2
                fee_setting_2.fee_amount = fee_amount_2
            else:
                fee_setting_2 = MembershipFee(
                    access_level=2,
                    fee_type=fee_type_2,
                    fee_amount=fee_amount_2
                )
                db.session.add(fee_setting_2)

            # 级别3只支持per_person和free
            fee_type_3 = request.form.get('fee_type_3')
            fee_amount_3 = float(request.form.get('fee_amount_3', 0))

            if fee_type_3 == 'free':
                fee_amount_3 = 0

            fee_setting_3 = MembershipFee.query.filter_by(access_level=3).first()

            if fee_setting_3:
                fee_setting_3.fee_type = fee_type_3
                fee_setting_3.fee_amount = fee_amount_3
            else:
                fee_setting_3 = MembershipFee(
                    access_level=3,
                    fee_type=fee_type_3,
                    fee_amount=fee_amount_3
                )
                db.session.add(fee_setting_3)

            db.session.commit()
            flash('Membership fee settings updated', 'success')

        except Exception as e:
            db.session.rollback()
            flash(f'Update failed: {str(e)}', 'danger')
            print(f"MembershipFee update error: {str(e)}")

        # 无论是否成功，都返回到同一页面以显示结果
        return redirect(url_for('admin.manage_membership_fees'))

    # GET请求处理
    # 获取当前设置
    fee_settings = MembershipFee.query.all()

    # 创建一个字典，键为access_level，值为fee对象
    fees = {}
    for fee in fee_settings:
        fees[fee.access_level] = {
            'fee_type': fee.fee_type,
            'fee_amount': fee.fee_amount
        }

    # 确保这里有return语句
    return render_template('admin/membership_fees.html', fees=fees)


@admin_bp.route('/admin/view_logs')
def view_logs():
    if session.get('user_role') not in ['E-Admin', 'Senior-E-Admin', 'T-Admin']:
        flash('No access right', 'danger')
        return redirect(url_for('main.index'))

    # 过滤条件
    organization = request.args.get('organization')
    activity = request.args.get('activity')
    username = request.args.get('username')
    date = request.args.get('date')

    query = ActivityLog.query

    if organization:
        query = query.filter_by(organization_id=organization)
    if activity:
        if activity == 'login':
            query = query.filter(ActivityLog.service_accessed.is_(None))
        else:
            query = query.filter(ActivityLog.service_accessed.like(f'%{activity}%'))
    if username:
        query = query.join(User).filter(User.email.like(f'%{username}%'))
    if date:
        date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
        next_day = date_obj + datetime.timedelta(days=1)
        query = query.filter(ActivityLog.login_time >= date_obj, ActivityLog.login_time < next_day)

    logs = query.order_by(ActivityLog.login_time.desc()).all()
    organizations = Organization.query.all()

    return render_template('admin/logs.html',
                           logs=logs,
                           organizations=organizations,
                           organization=organization,
                           activity=activity,
                           username=username,
                           date=date)


# Senior E-Admin 相关路由
@admin_bp.route('/senior_eadmin/dashboard')
def senior_eadmin_dashboard():
    if session.get('user_role') != 'Senior-E-Admin':
        flash('No access right', 'danger')
        return redirect(url_for('main.index'))

    # 获取待最终审核的申请
    applications = Organization.query.filter_by(
        status='pending',
        approved_by_e_admin=True,
        approved_by_senior_e_admin=False
    ).all()

    return render_template('admin/senior_eadmin_dashboard.html', applications=applications)