from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from app.models import db, User, Organization, ActivityLog, Member
from werkzeug.utils import secure_filename
import os
import secrets
import datetime

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        code = request.form.get('code')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        # # Special case: T-Admin login
        # if email == 'tadmin@edba.example.com':
        #     if user and user.check_password(password):
        #         session['user_id'] = user.user_id
        #         session['user_email'] = user.email
        #         session['user_role'] = user.role
        #         return redirect(url_for('admin.tadmin_dashboard'))
        #     else:
        #         flash('Invalid credentials', 'danger')
        #         return render_template('auth/login.html')

        # If user doesn't exist, check if they match a wildcard member rule
        if not user and '@' in email:
            domain = email.split('@')[1]
            wildcard_email = f'*@{domain}'

            # Look for wildcard member
            wildcard_member = Member.query.filter_by(email=wildcard_email).first()

            if wildcard_member:
                # Create new user, inheriting access level from wildcard member
                user = User(
                    email=email,
                    organization_id=wildcard_member.organization_id,
                    access_level=wildcard_member.access_level,
                    role='user',
                    is_wildcard_user=True,
                    wildcard_source=wildcard_email  # Record source wildcard
                )
                db.session.add(user)
                db.session.commit()
                # Log wildcard user creation activity
                log_entry = ActivityLog(
                    user_id=user.user_id,
                    organization_id=wildcard_member.organization_id,
                    service_accessed="user_creation_via_wildcard",
                    details=f"User automatically created via wildcard {wildcard_email}, access level: {wildcard_member.access_level}"
                )
                db.session.add(log_entry)
                db.session.commit()

                # Update user ID in the log
                log_entry.user_id = user.user_id
                db.session.commit()

                print(f"User account created for {email} via wildcard {wildcard_email}, access level: {wildcard_member.access_level}")

        # Normal login using verification code
        if user and session.get('verification_code') == code and session.get('verification_email') == email:
            session['user_id'] = user.user_id
            session['user_email'] = user.email
            session['user_role'] = user.role
            session['user_access_level'] = user.access_level
            session['organization_id'] = user.organization_id if user.organization else None
            # Update last login time
            user.last_login = datetime.datetime.utcnow()

            # Log activity
            log = ActivityLog(
                user_id=user.user_id,
                organization_id=user.organization_id,
                details="Login via wildcard email rule" if user.is_wildcard_user else "Regular login"
            )
            db.session.add(log)
            db.session.commit()

            # Redirect based on role
            if user.role == 'T-Admin':
                return redirect(url_for('admin.tadmin_dashboard'))
            if user.role == 'O-Convener':
                return redirect(url_for('organization.workspace'))
            elif user.role == 'E-Admin':
                return redirect(url_for('admin.eadmin_dashboard'))
            elif user.role == 'Senior-E-Admin':
                return redirect(url_for('admin.senior_eadmin_dashboard'))
            else:
                return redirect(url_for('user.dashboard'))
        else:
            flash('Invalid verification code or email', 'danger')

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        org_full_name = request.form.get('org_full_name')
        org_short_name = request.form.get('org_short_name')
        email = request.form.get('email')
        verification_code = request.form.get('verification_code')

        # Check verification code
        if verification_code != session.get('verification_code') or email != session.get('verification_email'):
            flash('Invalid verification code', 'danger')
            return render_template('auth/register.html')

        # Check if organization already exists
        if Organization.query.filter_by(registration_email=email).first():
            flash('This email is already registered', 'danger')
            return render_template('auth/register.html')

        # Handle file upload
        if 'proof_document' not in request.files:
            flash('Proof document required', 'danger')
            return render_template('auth/register.html')

        proof_file = request.files['proof_document']
        if proof_file.filename == '':
            flash('No file selected', 'danger')
            return render_template('auth/register.html')

        # Save file and create organization
        filename = secure_filename(proof_file.filename)
        upload_folder = 'uploads/proof_documents'
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, filename)
        proof_file.save(file_path)

        # Create organization
        org = Organization(
            full_name=org_full_name,
            short_name=org_short_name,
            registration_email=email,
            proof_document=file_path,
            status='pending'
        )
        db.session.add(org)
        db.session.commit()

        flash('Organization registration submitted, an administrator will review your application', 'success')
        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


# @auth_bp.route('/send_verification', methods=['POST'])
# def send_verification():
#     email = request.form.get('email')
#     if not email:
#         return {'status': 'error', 'message': 'Please provide an email address'}
#
#     # Generate verification code
#     verification_code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
#     session['verification_code'] = verification_code
#     session['verification_email'] = email
#
#     # TODO: Actually send email
#     # send_email(email, 'Your verification code', f'Your verification code is: {verification_code}')
#
#     # For demonstration purposes, print the code
#     print(f"Verification code: {verification_code} sent to {email}")
#
#     return {'status': 'success', 'message': 'Verification code sent'}
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import secrets
import os
import logging



def send_verification_email(recipient_email):
    """
    Send verification code to a fixed test email regardless of the input email
    :param recipient_email: Email input from frontend (not actually used)
    :return: Generated verification code or None
    """
    # Fixed test recipient email
    test_email = '3278789436@qq.com'

    # QQ Mail SMTP server configuration
    smtp_server = 'smtp.qq.com'
    smtp_port = 587  # TLS port

    # System email configuration
    SYSTEM_EMAIL = {
        'email': '1943565996@qq.com',  # Sender QQ email
        'password': 'yjmrubwshwlzbefg'  # SMTP authorization code
    }

    # Generate 6-digit verification code
    verification_code = ''.join([str(secrets.randbelow(10)) for _ in range(6)])
    # Create email
    msg = MIMEMultipart()
    msg['From'] = SYSTEM_EMAIL['email']
    msg['To'] = test_email
    msg['Subject'] = 'E-DBA System Login Verification Code'

    # Email body
    body = f'''
    <html>
    <body>
        <p>Hello,</p>
        <p>Your E-DBA system login verification code:</p>
        <p style="font-size: 24px; font-weight: bold; color: #007bff;">{verification_code}</p>
        <p>This code will expire in 10 minutes, please use it promptly.</p>
        <p>Best regards,<br>E-DBA Management Team</p>
    </body>
    </html>
    '''
    msg.attach(MIMEText(body, 'html', 'utf-8'))

    try:
        # Establish secure connection
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Enable TLS encryption
        server.login(SYSTEM_EMAIL['email'], SYSTEM_EMAIL['password'])

        # Send email to test address
        server.sendmail(SYSTEM_EMAIL['email'], test_email, msg.as_string())
        server.quit()

        print(f"Verification code: {verification_code}, sent to test email {test_email}, original request email: {recipient_email}")
        return verification_code

    except Exception as e:
        print(f"Failed to send email: {e}")
        return None

@auth_bp.route('/send_verification', methods=['POST'])
def send_verification():
    """
    Route handler function for sending verification code
    """
    email = request.form.get('email')
    if not email:
        return {'status': 'error', 'message': 'Please provide an email address'}

    # Generate and send verification code
    verification_code = send_verification_email(email)

    if verification_code:
        # Store verification code in session (using original input email)
        session['verification_code'] = verification_code
        session['verification_email'] = email
        return {'status': 'success', 'message': 'Verification code sent to test email'}
    else:
        return {'status': 'error', 'message': 'Failed to send verification code, please try again later'}


def test_email_sending():
    """
    Test email sending functionality
    """
    test_email = '3278789436@qq.com'  # Replace with test email
    result = send_verification_email(test_email)
    if result:
        print(f"Test email sent successfully, verification code: {result}")
    else:
        print("Test email sending failed")

@auth_bp.route('/logout')
def logout():
    # Record logout time
    if session.get('user_id'):
        log = ActivityLog.query.filter_by(
            user_id=session['user_id'],
            logout_time=None
        ).order_by(ActivityLog.login_time.desc()).first()

        if log:
            log.logout_time = datetime.datetime.utcnow()
            db.session.commit()

    # Completely clear session - modify this part
    session.clear()
    # Set flash message
    flash('You have successfully logged out', 'success')
    return redirect(url_for('main.index'))