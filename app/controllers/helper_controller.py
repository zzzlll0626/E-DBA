from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify, send_file
from app.models import db, User, Organization, ActivityLog
import pandas as pd
import io
import datetime

helper_bp = Blueprint('helper', __name__)


@helper_bp.route('/check_email')
def check_email():
    email = request.args.get('email')

    if not email:
        return jsonify({'registered': False})

    user = User.query.filter_by(email=email).first()
    organization = Organization.query.filter_by(registration_email=email).first()

    return jsonify({'registered': bool(user or organization)})


@helper_bp.route('/export_logs')
def export_logs():
    if not session.get('user_id'):
        flash('Please login first', 'danger')
        return redirect(url_for('main.index'))

    # Check permissions
    user = User.query.get(session.get('user_id'))
    if not user:
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    # Process request parameters
    organization_id = request.args.get('organization_id') or user.organization_id
    type = request.args.get('type', 'activity')  # 'activity' or 'transaction'
    activity = request.args.get('activity')
    username = request.args.get('username')
    date = request.args.get('date')

    # Verify permissions
    is_admin = user.role in ['T-Admin', 'E-Admin', 'Senior-E-Admin']
    is_convener = user.role == 'O-Convener' and str(user.organization_id) == str(organization_id)

    if not (is_admin or is_convener):
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    # Query data
    if type == 'activity':
        # Activity logs
        query = ActivityLog.query

        if not is_admin:
            # Non-admins can only view logs from their own organization
            query = query.filter(
                (ActivityLog.organization_id == organization_id) |
                (ActivityLog.provider_organization_id == organization_id)
            )
        elif organization_id and is_admin:
            # Admins viewing logs for a specific organization
            query = query.filter(
                (ActivityLog.organization_id == organization_id) |
                (ActivityLog.provider_organization_id == organization_id)
            )

        if activity:
            if activity == 'login':
                query = query.filter(ActivityLog.service_accessed.is_(None))
            else:
                query = query.filter(ActivityLog.service_accessed.like(f'%{activity}%'))
        if username:
            query = query.join(ActivityLog.user).filter(User.email.like(f'%{username}%'))
        if date:
            date_obj = datetime.datetime.strptime(date, '%Y-%m-%d')
            next_day = date_obj + datetime.timedelta(days=1)
            query = query.filter(ActivityLog.login_time >= date_obj, ActivityLog.login_time < next_day)

        logs = query.order_by(ActivityLog.login_time.desc()).all()

        # Create DataFrame
        data = []
        for log in logs:
            user_email = log.user.email if log.user else None
            organization_name = log.organization.short_name if log.organization else None
            provider_organization_name = log.provider_organization.short_name if log.provider_organization else None

            data.append({
                'ID': log.log_id,
                'User': user_email,
                'Organization': organization_name,
                'Login Time': log.login_time.strftime('%Y-%m-%d %H:%M:%S') if log.login_time else None,
                'Logout Time': log.logout_time.strftime('%Y-%m-%d %H:%M:%S') if log.logout_time else None,
                'Service Accessed': log.service_accessed,
                'Provider Organization': provider_organization_name
            })

        df = pd.DataFrame(data)

    else:
        # Transaction records
        from app.models import Transaction

        query = Transaction.query

        if not is_admin:
            # Non-admins can only view transactions from their own organization
            query = query.filter(
                (Transaction.from_organization_id == organization_id) |
                (Transaction.to_organization_id == organization_id)
            )
        elif organization_id and is_admin:
            # Admins viewing transactions for a specific organization
            query = query.filter(
                (Transaction.from_organization_id == organization_id) |
                (Transaction.to_organization_id == organization_id)
            )

        transactions = query.order_by(Transaction.transaction_time.desc()).all()

        # Get organization information
        organizations = {
            org.organization_id: org.short_name
            for org in Organization.query.all()
        }

        # Create DataFrame
        data = []
        for transaction in transactions:
            from_org = organizations.get(transaction.from_organization_id, 'Unknown')
            to_org = organizations.get(transaction.to_organization_id, 'Unknown')

            data.append({
                'ID': transaction.transaction_id,
                'Amount': transaction.amount,
                'Sender': from_org,
                'Receiver': to_org,
                'Status': transaction.status,
                'Reason': transaction.reason,
                'Transaction Time': transaction.transaction_time.strftime(
                    '%Y-%m-%d %H:%M:%S') if transaction.transaction_time else None
            })

        df = pd.DataFrame(data)

    # Export to Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Data', index=False)

    output.seek(0)

    # Generate filename
    filename = f"{'Activity_Logs' if type == 'activity' else 'Transaction_Records'}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"

    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )


# @helper_bp.route('/export_template/<type>')
# def export_template(type):
#     if not session.get('user_id'):
#         flash('Please login first', 'danger')
#         return redirect(url_for('main.index'))
#
#     if type == 'members':
#         # Create member template
#         data = {
#             'name': ['Zhang San', 'Li Si', 'Wang Wu'],
#             'email': ['zhangsan@example.com', 'lisi@example.com', '*@example.com'],
#             'access_right': [1, 2, 3],
#             'quota': [0, 100, 500]
#         }
#
#         df = pd.DataFrame(data)
#         filename = 'Member_Import_Template.xlsx'
#     else:
#         flash('Unknown template type', 'danger')
#         return redirect(url_for('main.index'))
#
#     # Export to Excel
#     output = io.BytesIO()
#     with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
#         df.to_excel(writer, sheet_name='Import Data', index=False)
#
#         # Add explanation sheet
#         workbook = writer.book
#         worksheet = workbook.add_worksheet('Instructions')
#
#         if type == 'members':
#             worksheet.write(0, 0, 'Field Descriptions:')
#             worksheet.write(1, 0, 'name: Member name')
#             worksheet.write(2, 0, 'email: Member email, use *@domain.com format for wildcards')
#             worksheet.write(3, 0, 'access_right: Access level, 1=Public data access, 2=Private data consumption, 3=Private data provision')
#             worksheet.write(4, 0, 'quota: Paper download quota (RMB)')
#
#     output.seek(0)
#
#     return send_file(
#         output,
#         as_attachment=True,
#         download_name=filename,
#         mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
#     )

# Add to the export_template function in helper_controller.py

@helper_bp.route('/export_template/<type>')
def export_template(type):
    if not session.get('user_id'):
        flash('Please login first', 'danger')
        return redirect(url_for('main.index'))

    if type == 'members':
        # Create member template
        data = {
            'name': ['Zhang San', 'Li Si', 'Wang Wu'],
            'email': ['zhangsan@example.com', 'lisi@example.com', '*@example.com'],
            'access_right': [1, 2, 3],
            'quota': [0, 100, 500]
        }
        df = pd.DataFrame(data)
        filename = 'Member_Import_Template.xlsx'
    elif type == 'student_auth':
        # Create student authentication template
        data = {
            'name': ['Zhang San', 'Li Si', 'Wang Wu'],
            'id': ['S20230001', 'S20230002', 'S20230003']
            # Photo field needs to be handled separately in batch verification
        }
        df = pd.DataFrame(data)
        filename = 'Student_Authentication_Template.xlsx'
    elif type == 'student_record':
        # Create student record query template
        data = {
            'name': ['Zhang San', 'Li Si', 'Wang Wu'],
            'id': ['S20230001', 'S20230002', 'S20230003']
        }
        df = pd.DataFrame(data)
        filename = 'Student_Record_Query_Template.xlsx'
    else:
        flash('Unknown template type', 'danger')
        return redirect(url_for('main.index'))

    # Export to Excel
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Import Data', index=False)

        # Add explanation sheet
        workbook = writer.book
        worksheet = workbook.add_worksheet('Instructions')

        if type == 'members':
            worksheet.write(0, 0, 'Field Descriptions:')
            worksheet.write(1, 0, 'name: Member name')
            worksheet.write(2, 0, 'email: Member email, use *@domain.com format for wildcards')
            worksheet.write(3, 0, 'access_right: Access level, 1=Public data access, 2=Private data consumption, 3=Private data provision')
            worksheet.write(4, 0, 'quota: Paper download quota (RMB)')
        elif type == 'student_auth':
            worksheet.write(0, 0, 'Field Descriptions:')
            worksheet.write(1, 0, 'name: Student name')
            worksheet.write(2, 0, 'id: Student ID')
            worksheet.write(3, 0, 'Note: Batch verification does not support photo uploads. For photo verification, please use the individual verification feature')
            worksheet.write(4, 0, 'Batch verification costs will be calculated based on the number of records')
        elif type == 'student_record':
            worksheet.write(0, 0, 'Field Descriptions:')
            worksheet.write(1, 0, 'name: Student name')
            worksheet.write(2, 0, 'id: Student ID')
            worksheet.write(3, 0, 'Batch query costs will be calculated based on the number of records')

    output.seek(0)

    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )