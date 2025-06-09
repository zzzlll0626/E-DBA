import requests
from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from app.models import db, Organization, Service, Member, BankAccount, ActivityLog, Course, User, Transaction, Payment
from werkzeug.utils import secure_filename
import os
import datetime
import csv
import io

from app.utils.bank_utils import load_bank_interface_info

org_bp = Blueprint('organization', __name__)


@org_bp.route('/workspace')
def workspace():
    if not session.get('user_id') or session.get('user_role') != 'O-Convener':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    organization_id = session.get('organization_id')
    organization = Organization.query.get_or_404(organization_id)

    # Get member count
    members_count = Member.query.filter_by(organization_id=organization_id).count()

    # Get service list
    services = Service.query.filter_by(organization_id=organization_id).all()

    # Get bank account information
    bank_account = BankAccount.query.filter_by(organization_id=organization_id).first()

    # Get recent activities
    recent_activities = ActivityLog.query.filter_by(organization_id=organization_id).order_by(
        ActivityLog.login_time.desc()).limit(5).all()

    return render_template('organization/workspace.html',
                           organization=organization,
                           members_count=members_count,
                           services=services,
                           bank_account=bank_account,
                           recent_activities=recent_activities)


@org_bp.route('/manage_members', methods=['GET', 'POST'])
def manage_members():
    if not session.get('user_id') or session.get('user_role') != 'O-Convener':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    organization_id = session.get('organization_id')
    from app.models import Payment
    # Process single member payment callback
    # if session.get('pending_single_member') and request.args.get('single_import_complete') == 'true':
    #     # Find the most recent payment record and verify status
    #     payment = Payment.query.filter_by(
    #         user_id=session.get('user_id'),
    #         payment_type='membership_fee',
    #         status='completed'
    #     ).order_by(Payment.completed_at.desc()).first()
    #     if payment:
    #         try:
    #             member_data = session.pop('pending_single_member')
    #
    #             # Create member
    #             member = Member(
    #                 organization_id=member_data['organization_id'],
    #                 name=member_data['name'],
    #                 email=member_data['email'],
    #                 access_level=member_data['access_level'],
    #                 quota=member_data['quota']
    #             )
    #             db.session.add(member)
    #
    #             # Create user account for non-wildcard emails
    #             if not member_data['email'].startswith('*@'):
    #                 existing_user = User.query.filter_by(email=member_data['email']).first()
    #                 if not existing_user:
    #                     user = User(
    #                         email=member_data['email'],
    #                         organization_id=member_data['organization_id'],
    #                         access_level=member_data['access_level'],
    #                         role='user'
    #                     )
    #                     db.session.add(user)
    #                     print(f"Created user account for member {member_data['email']}")
    #
    #             db.session.commit()
    #             flash('Member added successfully', 'success')
    #         except Exception as e:
    #             db.session.rollback()
    #             flash(f'Failed to add member: {str(e)}', 'danger')
    #             print(f"Single member import exception: {str(e)}")

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            try:
                name = request.form.get('name', '')
                email = request.form.get('email')
                access_right = int(request.form.get('access_right'))
                quota = float(request.form.get('quota', 0))

                # Handle empty name field
                if not name or name.strip() == '':
                    # Auto-generate name for wildcard emails
                    if email.startswith('*@'):
                        try:
                            domain = email.split('@')[1]
                            name = f"Wildcard User ({domain} domain)"
                        except IndexError:
                            name = "Wildcard User (format error)"
                    else:
                        # Provide default name for regular users
                        name = f"User-{email}"

                # Validate wildcard email format
                if email.startswith('*@'):
                    if '@' not in email or len(email.split('@')[1]) < 2:
                        flash('Incorrect wildcard email format, should be "*@domain.com"', 'danger')
                        return redirect(url_for('organization.manage_members'))

                    # Add information message
                    flash('Wildcard email added, all users matching this domain will automatically receive the corresponding access level and quota when logging in', 'info')
                    print(f"Adding wildcard email: {email}, access level: {access_right}, quota: {quota}")

                # Check if already exists
                existing = Member.query.filter_by(organization_id=organization_id, email=email).first()
                if existing:
                    flash('This email is already registered as a member', 'danger')
                    return redirect(url_for('organization.manage_members'))

                # Key change: Don't create member immediately, store info first
                member_data = {
                    'name': name,
                    'email': email,
                    'access_level': access_right,
                    'quota': quota,
                    'organization_id': organization_id
                }

                # Process membership payment logic
                from app.models import MembershipFee, Payment

                # Get membership fee settings
                fee_setting = MembershipFee.query.filter_by(access_level=access_right).first()

                if fee_setting:
                    fee_amount = 0

                    # Calculate fee based on fee type
                    if fee_setting.fee_type == 'flat_rate':
                        fee_amount = fee_setting.fee_amount
                    elif fee_setting.fee_type == 'per_person':
                        fee_amount = fee_setting.fee_amount
                    # Free type keeps fee_amount at 0

                    if fee_amount > 0:
                        # Check bank account
                        bank_account = BankAccount.query.filter_by(organization_id=organization_id).first()
                        if not bank_account:
                            flash('Please set up a bank account to pay membership fees', 'warning')
                            return redirect(url_for('organization.banking'))

                        # Query system bank account organization
                        system_account = BankAccount.query.filter_by(is_system_account=True).first()
                        if not system_account:
                            flash('System error: Cannot find system bank account', 'danger')
                            return redirect(url_for('organization.manage_members'))

                        # Create payment record
                        payment = Payment(
                            user_id=session.get('user_id'),
                            organization_id=organization_id,
                            amount=fee_amount,
                            payment_type='membership_fee',
                            payment_method='transfer',
                            receiver_organization_id=system_account.organization_id,
                            status='pending'
                        )
                        db.session.add(payment)

                        # Store member info in session
                        session['pending_single_member'] = member_data

                        db.session.commit()  # Only commit payment record

                        # Redirect to payment page
                        return redirect(url_for('payment.bank_transfer',
                                                payment_id=payment.payment_id,
                                                redirect_url=url_for('organization.manage_members',
                                                                     single_import_complete='true')))

                # If no payment needed, create member directly
                member = Member(
                    organization_id=organization_id,
                    name=name,
                    email=email,
                    access_level=access_right,
                    quota=quota
                )
                db.session.add(member)

                # Create user account for the member (if not a wildcard email)
                if not email.startswith('*@'):
                    existing_user = User.query.filter_by(email=email).first()
                    if not existing_user:
                        # Create new user account
                        user = User(
                            email=email,
                            organization_id=organization_id,
                            access_level=access_right,
                            role='user'  # Regular user role
                        )
                        db.session.add(user)
                        print(f"Created user account for member {email}")
                else:
                    print(f"Wildcard email {email} does not create a user account")

                db.session.commit()
                flash('Member added successfully', 'success')

            except Exception as e:
                db.session.rollback()  # Rollback transaction on exception
                flash(f'Failed to add member: {str(e)}', 'danger')
                print(f"Add member exception: {str(e)}")
                return redirect(url_for('organization.manage_members'))

        elif action == 'edit':
            try:
                member_id = request.form.get('member_id')
                name = request.form.get('name', '')
                email = request.form.get('email')
                access_right = int(request.form.get('access_right'))
                quota = float(request.form.get('quota', 0))

                # Handle empty name field
                if not name or name.strip() == '':
                    # Auto-generate name for wildcard emails
                    if email.startswith('*@'):
                        try:
                            domain = email.split('@')[1]
                            name = f"Wildcard User ({domain} domain)"
                        except IndexError:
                            name = "Wildcard User (format error)"
                    else:
                        # Provide default name for regular users
                        name = f"User-{email}"

                member = Member.query.get_or_404(member_id)
                if member.organization_id != organization_id:
                    flash('Not authorized to edit this member', 'danger')
                    return redirect(url_for('organization.manage_members'))

                # Check if membership upgrade needs to be processed
                old_access_level = member.access_level
                old_email = member.email

                # If email changed and not a wildcard email
                if email != old_email and not email.startswith('*@'):
                    # Check if user account exists
                    existing_user = User.query.filter_by(email=email).first()
                    if not existing_user:
                        # Create new user account
                        user = User(
                            email=email,
                            organization_id=organization_id,
                            access_level=access_right,
                            role='user'  # Regular user role
                        )
                        db.session.add(user)
                    else:
                        # Update existing user's access level
                        existing_user.access_level = access_right
                        existing_user.organization_id = organization_id

                    # If there was a previous user account and not wildcard, consider updating or deleting
                    old_user = User.query.filter_by(email=old_email).first()
                    if old_user and not old_email.startswith('*@'):
                        # Here you can choose to update email or delete old account, depending on requirements
                        pass
                elif not email.startswith('*@'):
                    # Email unchanged but access level might change, update user access level
                    user = User.query.filter_by(email=email).first()
                    if user:
                        user.access_level = access_right
                    else:
                        # If user doesn't exist, create new user
                        user = User(
                            email=email,
                            organization_id=organization_id,
                            access_level=access_right,
                            role='user'
                        )
                        db.session.add(user)

                # Process membership payment logic
                if access_right != old_access_level:  # Any level change triggers fee check
                    from app.models import MembershipFee, Payment

                    new_fee_setting = MembershipFee.query.filter_by(access_level=access_right).first()

                    if new_fee_setting:
                        fee_amount = 0

                        # Calculate fee based on fee type
                        if new_fee_setting.fee_type == 'flat_rate':
                            fee_amount = new_fee_setting.fee_amount
                        elif new_fee_setting.fee_type == 'per_person':
                            fee_amount = new_fee_setting.fee_amount
                        # Free type keeps fee_amount at 0

                        if fee_amount > 0:
                            # Check bank account
                            bank_account = BankAccount.query.filter_by(organization_id=organization_id).first()
                            if not bank_account:
                                flash('Please set up a bank account to pay membership fees', 'warning')
                                return redirect(url_for('organization.banking'))

                            # Query system bank account organization
                            system_account = BankAccount.query.filter_by(is_system_account=True).first()
                            if not system_account:
                                flash('System error: Cannot find system bank account', 'danger')
                                return redirect(url_for('organization.manage_members'))

                            # Create payment record
                            payment = Payment(
                                user_id=session.get('user_id'),
                                organization_id=organization_id,
                                amount=fee_amount,
                                payment_type='membership_upgrade',
                                payment_method='transfer',
                                receiver_organization_id=system_account.organization_id,
                                status='pending'
                            )
                            db.session.add(payment)

                            # Update member information first
                            member.name = name
                            member.email = email
                            member.access_level = access_right
                            member.quota = quota

                            db.session.commit()

                            # Redirect to payment page
                            return redirect(url_for('payment.bank_transfer',
                                                    payment_id=payment.payment_id,
                                                    redirect_url=url_for('organization.manage_members')))

                # If no payment needed, update member info directly
                member.name = name
                member.email = email
                member.access_level = access_right
                member.quota = quota

                db.session.commit()
                flash('Member updated successfully', 'success')

            except Exception as e:
                db.session.rollback()  # Rollback transaction on exception
                flash(f'Failed to edit member: {str(e)}', 'danger')
                print(f"Edit member exception: {str(e)}")
                return redirect(url_for('organization.manage_members'))


        elif action == 'delete':
            try:
                member_id = request.form.get('member_id')
                member = Member.query.get_or_404(member_id)

                if member.organization_id != organization_id:
                    flash('Not authorized to delete this member', 'danger')
                    return redirect(url_for('organization.manage_members'))

                if not member.email.startswith('*@'):
                    user = User.query.filter_by(email=member.email).first()
                    if user and user.organization_id == organization_id:
                        # Completely remove user account
                        db.session.delete(user)
                        print(f"User {member.email} completely removed from the system")

                db.session.delete(member)
                db.session.commit()
                flash('Member deleted successfully', 'success')

            except Exception as e:
                db.session.rollback()  # Rollback transaction on exception
                flash(f'Failed to delete member: {str(e)}', 'danger')
                print(f"Delete member exception: {str(e)}")
                return redirect(url_for('organization.manage_members'))


        # Modify members_file processing section
        elif action == 'upload':
            try:
                if 'members_file' not in request.files:
                    flash('Please select a file', 'danger')
                    return redirect(url_for('organization.manage_members'))

                file = request.files['members_file']

                if file.filename == '':
                    flash('No file selected', 'danger')
                    return redirect(url_for('organization.manage_members'))

                # Process Excel file
                import pandas as pd

                df = pd.read_excel(file)

                added = 0
                errors = 0
                total_fee = 0
                members_to_add = []

                from app.models import MembershipFee, Payment

                # Check bank account
                bank_account = BankAccount.query.filter_by(organization_id=organization_id).first()

                if not bank_account:
                    flash('Please set up a bank account to pay membership fees', 'warning')
                    return redirect(url_for('organization.banking'))

                processed_flat_rate_levels = set()

                # First calculate total fee and collect member data
                for index, row in df.iterrows():
                    try:
                        # Get and process name field
                        name = row.get('name', '')
                        email = row['email']

                        # Check if name is empty, nan or None
                        if pd.isna(name) or (isinstance(name, str) and name.strip() == ''):
                            # Auto-generate name for wildcard emails
                            if isinstance(email, str) and email.startswith('*@'):
                                try:
                                    domain = email.split('@')[1]
                                    name = f"Wildcard User ({domain} domain)"
                                except IndexError:
                                    name = "Wildcard User (format error)"
                            else:
                                # Provide default name for regular users
                                name = f"User-{email}"

                        access_level = int(row['access_right'])
                        quota = float(row.get('quota', 0))

                        # Validate wildcard email format
                        if isinstance(email, str) and email.startswith('*@'):
                            if email.count('*') > 1 or '@' not in email or len(email.split('@')[1]) < 2:
                                errors += 1
                                print(f"Wildcard email format error: {email}")
                                continue

                            print(f"Batch import wildcard email: {email}, access level: {access_level}, quota: {quota}")

                        # Check if already exists
                        existing = Member.query.filter_by(organization_id=organization_id, email=email).first()
                        if existing:
                            continue

                        # Collect member data, ensure name is not empty
                        members_to_add.append({
                            'name': name,  # Processed name, ensuring it's not empty
                            'email': email,
                            'access_level': access_level,
                            'quota': quota,
                            'organization_id': organization_id
                        })

                        # Get membership fee settings
                        fee_setting = MembershipFee.query.filter_by(access_level=access_level).first()

                        if fee_setting:
                            # Calculate fee based on fee type
                            if fee_setting.fee_type == 'flat_rate':
                                # For flat rate, add fee only once per level
                                if access_level not in processed_flat_rate_levels:
                                    total_fee += fee_setting.fee_amount
                                    processed_flat_rate_levels.add(access_level)
                            elif fee_setting.fee_type == 'per_person':
                                # For per-person fee, add for each person
                                total_fee += fee_setting.fee_amount
                            # If fee type is free, don't increase fee

                    except Exception as e:
                        errors += 1
                        print(f"Error processing row {index + 1}: {str(e)}")

                # If there's a fee, create a payment record
                if total_fee > 0:
                    # Query system bank account organization
                    system_account = BankAccount.query.filter_by(is_system_account=True).first()

                    if not system_account:
                        flash('System error: Cannot find system bank account', 'danger')
                        return redirect(url_for('organization.manage_members'))

                    # Create payment record
                    payment = Payment(
                        user_id=session.get('user_id'),
                        organization_id=organization_id,
                        amount=total_fee,
                        payment_type='membership_fee_batch',
                        payment_method='transfer',
                        receiver_organization_id=system_account.organization_id,
                        status='pending'
                    )

                    db.session.add(payment)
                    db.session.flush()

                    # Save batch member import info to session, use after payment complete
                    session['pending_members'] = members_to_add

                    # Commit transaction, save payment record
                    db.session.commit()

                    # Redirect to payment page
                    return redirect(url_for('payment.bank_transfer',
                                            payment_id=payment.payment_id,
                                            redirect_url=url_for('organization.manage_members',
                                                                 import_complete='true')))

                # If no payment needed, process member additions directly
                for member_data in members_to_add:
                    # Double-check name is not empty (just in case)
                    if not member_data['name'] or pd.isna(member_data['name']):
                        if isinstance(member_data['email'], str) and member_data['email'].startswith('*@'):
                            domain = member_data['email'].split('@')[1]
                            member_data['name'] = f"Wildcard User ({domain} domain)"
                        else:
                            member_data['name'] = f"User-{member_data['email']}"

                    member = Member(
                        organization_id=organization_id,
                        name=member_data['name'],
                        email=member_data['email'],
                        access_level=member_data['access_level'],
                        quota=member_data['quota']
                    )

                    db.session.add(member)

                    # Create user account for non-wildcard emails
                    if not member_data['email'].startswith('*@'):
                        existing_user = User.query.filter_by(email=member_data['email']).first()
                        if not existing_user:
                            user = User(
                                email=member_data['email'],
                                organization_id=organization_id,
                                access_level=member_data['access_level'],
                                role='user'
                            )
                            db.session.add(user)

                    added += 1

                db.session.commit()
                flash(f'Successfully imported {added} members. {errors} records failed to import.', 'success' if errors == 0 else 'warning')

            except Exception as e:
                db.session.rollback()  # Add rollback to prevent PendingRollbackError
                flash(f'File processing failed: {str(e)}', 'danger')
                print(f"Batch import exception: {str(e)}")
                return redirect(url_for('organization.manage_members'))

    # # Check if there's a pending batch import
    # if session.get('pending_members') and request.args.get('import_complete') == 'true':
    #     try:
    #         import pandas as pd
    #         members_to_add = session.pop('pending_members')
    #         added = 0
    #         user_added = 0
    #
    #         for member_data in members_to_add:
    #             # Ensure name is not empty
    #             if pd.isna(member_data['name']) or not member_data['name']:
    #                 if member_data['email'].startswith('*@'):
    #                     try:
    #                         domain = member_data['email'].split('@')[1]
    #                         member_data['name'] = f"Wildcard User ({domain} domain)"
    #                     except:
    #                         member_data['name'] = "Wildcard User"
    #                 else:
    #                     member_data['name'] = f"User-{member_data['email']}"
    #
    #             member = Member(
    #                 organization_id=organization_id,
    #                 name=member_data['name'],
    #                 email=member_data['email'],
    #                 access_level=member_data['access_level'],
    #                 quota=member_data['quota']
    #             )
    #             db.session.add(member)
    #             added += 1
    #
    #             # Create user account for non-wildcard emails
    #             if not member_data['email'].startswith('*@'):
    #                 existing_user = User.query.filter_by(email=member_data['email']).first()
    #                 if not existing_user:
    #                     user = User(
    #                         email=member_data['email'],
    #                         organization_id=organization_id,
    #                         access_level=member_data['access_level'],
    #                         role='user'
    #                     )
    #                     db.session.add(user)
    #                     user_added += 1
    #
    #         db.session.commit()
    #         flash(f'Successfully imported {added} members, created {user_added} user accounts.', 'success')
    #     except Exception as e:
    #         db.session.rollback()
    #         flash(f'Member import failed: {str(e)}', 'danger')
    #         print(f"Batch import processing exception: {str(e)}")

    # Get member list
    members = Member.query.filter_by(organization_id=organization_id).all()

    from app.models import MembershipFee
    fee_settings = MembershipFee.query.all()

    # Create a dictionary with access_level as key and fee object as value
    membership_fees = {}
    for fee in fee_settings:
        membership_fees[fee.access_level] = {
            'fee_type': fee.fee_type,
            'fee_amount': fee.fee_amount
        }

    # Pass membership_fees when returning template
    return render_template('organization/members.html',
                           members=members,
                           membership_fees=membership_fees)


@org_bp.route('/process_member_after_payment/<int:payment_id>')
def process_member_after_payment(payment_id):
    # Check user permissions
    if not session.get('user_id') or session.get('user_role') != 'O-Convener':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    organization_id = session.get('organization_id')

    # Verify payment record
    payment = Payment.query.get_or_404(payment_id)

    # Verify payment record belongs to current user
    if payment.user_id != session.get('user_id'):
        flash('Not authorized to access this payment record', 'danger')
        return redirect(url_for('organization.manage_members'))

    # Verify payment status
    if payment.status != 'completed':
        flash('Payment not completed, cannot add member', 'danger')
        return redirect(url_for('organization.manage_members'))

    # Verify payment type
    if payment.payment_type != 'membership_fee':
        flash('Incorrect payment type', 'danger')
        return redirect(url_for('organization.manage_members'))

    # Check if there's pending member data
    if not session.get('pending_single_member'):
        flash('No pending member data', 'warning')
        return redirect(url_for('organization.manage_members'))

    try:
        # Get member data from session
        member_data = session.pop('pending_single_member')

        # Verify member organization ID matches current organization
        if member_data['organization_id'] != organization_id:
            flash('Member data does not match current organization', 'danger')
            return redirect(url_for('organization.manage_members'))

        # Create member
        member = Member(
            organization_id=member_data['organization_id'],
            name=member_data['name'],
            email=member_data['email'],
            access_level=member_data['access_level'],
            quota=member_data['quota']
        )
        db.session.add(member)

        # Create user account for non-wildcard emails
        if not member_data['email'].startswith('*@'):
            existing_user = User.query.filter_by(email=member_data['email']).first()
            if not existing_user:
                user = User(
                    email=member_data['email'],
                    organization_id=member_data['organization_id'],
                    access_level=member_data['access_level'],
                    role='user'
                )
                db.session.add(user)
                print(f"Created user account for member {member_data['email']}")

        # Commit to database
        db.session.commit()

        # Show success message
        flash('Member added successfully', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Failed to add member: {str(e)}', 'danger')
        print(f"Single member import exception: {str(e)}")

    # Redirect to member management page when done
    return redirect(url_for('organization.manage_members'))


@org_bp.route('/process_batch_members_after_payment/<int:payment_id>')
def process_batch_members_after_payment(payment_id):
    # Check user permissions
    if not session.get('user_id') or session.get('user_role') != 'O-Convener':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    organization_id = session.get('organization_id')

    # Verify payment record
    payment = Payment.query.get_or_404(payment_id)

    # Verify payment record belongs to current user
    if payment.user_id != session.get('user_id'):
        flash('Not authorized to access this payment record', 'danger')
        return redirect(url_for('organization.manage_members'))

    # Verify payment status
    if payment.status != 'completed':
        flash('Payment not completed, cannot import members', 'danger')
        return redirect(url_for('organization.manage_members'))

    # Verify payment type
    if payment.payment_type != 'membership_fee_batch':
        flash('Incorrect payment type', 'danger')
        return redirect(url_for('organization.manage_members'))

    # Check if there's pending member data
    if not session.get('pending_members'):
        flash('No pending member data', 'warning')
        return redirect(url_for('organization.manage_members'))

    try:
        import pandas as pd
        members_to_add = session.pop('pending_members')
        added = 0
        user_added = 0

        for member_data in members_to_add:
            # Ensure name is not empty
            if pd.isna(member_data['name']) or not member_data['name']:
                if member_data['email'].startswith('*@'):
                    try:
                        domain = member_data['email'].split('@')[1]
                        member_data['name'] = f"Wildcard User ({domain} domain)"
                    except:
                        member_data['name'] = "Wildcard User"
                else:
                    member_data['name'] = f"User-{member_data['email']}"

            # Verify member organization ID matches current organization
            if member_data['organization_id'] != organization_id:
                continue

            member = Member(
                organization_id=organization_id,
                name=member_data['name'],
                email=member_data['email'],
                access_level=member_data['access_level'],
                quota=member_data['quota']
            )
            db.session.add(member)
            added += 1

            # Create user account for non-wildcard emails
            if not member_data['email'].startswith('*@'):
                existing_user = User.query.filter_by(email=member_data['email']).first()
                if not existing_user:
                    user = User(
                        email=member_data['email'],
                        organization_id=organization_id,
                        access_level=member_data['access_level'],
                        role='user'
                    )
                    db.session.add(user)
                    user_added += 1

        db.session.commit()
        flash(f'Successfully imported {added} members, created {user_added} user accounts.', 'success')

    except Exception as e:
        db.session.rollback()
        flash(f'Batch member import failed: {str(e)}', 'danger')
        print(f"Batch member import exception: {str(e)}")

    # Redirect to member management page when done
    return redirect(url_for('organization.manage_members'))

@org_bp.route('/manage_services', methods=['GET', 'POST'])
def manage_services():
    if not session.get('user_id') or session.get('user_role') != 'O-Convener':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    organization_id = session.get('organization_id')

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            service_type = request.form.get('service_type')
            service_name = request.form.get('service_name')
            description = request.form.get('description')
            price = float(request.form.get('price', 0))
            is_public = request.form.get('is_public') == 'on'
            # For course info service, force set as free and public
            if service_type == 'course_info':
                price = 0  # Ensure price is 0
                is_public = True  # Ensure it's public
            # Create service
            service = Service(
                organization_id=organization_id,
                type=service_type,
                name=service_name,
                description=description,
                price=price,  # For thesis sharing service, this is the download price per paper
                is_public=is_public
            )

            # Course info service is set as configured by default
            if service_type == 'course_info':
                service.is_configured = True

            db.session.add(service)
            db.session.commit()
            flash('Service added successfully', 'success')

        elif action == 'edit':
            service_id = request.form.get('service_id')
            service_name = request.form.get('service_name')
            description = request.form.get('description')
            price = float(request.form.get('price', 0))
            is_public = request.form.get('is_public') == 'on'

            service = Service.query.get_or_404(service_id)
            if service.organization_id != organization_id:
                flash('Not authorized to edit this service', 'danger')
                return redirect(url_for('organization.manage_services'))
                # For course info service, force set as free and public
            if service.type == 'course_info':
                price = 0
                is_public = True
            service.name = service_name
            service.description = description
            service.price = price
            service.is_public = is_public

            db.session.commit()
            flash('Service updated successfully', 'success')

        elif action == 'remove':
            service_id = request.form.get('service_id')

            service = Service.query.get_or_404(service_id)
            if service.organization_id != organization_id:
                flash('Not authorized to delete this service', 'danger')
                return redirect(url_for('organization.manage_services'))

            db.session.delete(service)
            db.session.commit()
            flash('Service deleted successfully', 'success')


        elif action == 'access':

            service_id = request.form.get('service_id')
            # Get organizations with download permissions

            download_organizations = request.form.getlist('download_organizations')

            service = Service.query.get_or_404(service_id)

            if service.organization_id != organization_id:
                flash('Not authorized to configure this service', 'danger')

                return redirect(url_for('organization.manage_services'))

            # Clear existing download permissions
            service.download_organizations = []

            # When handling thesis service, all organizations have view permission
            # Clear existing view permissions (will be reset below for all organizations)
            service.view_organizations = []

            # Add view permissions (all organizations)
            all_organizations = Organization.query.filter(
                Organization.organization_id != organization_id
            ).all()

            for org in all_organizations:
                # All organizations have view permission
                service.view_organizations.append(org)

            # Add download permissions
            for org_id in download_organizations:
                org = Organization.query.get(org_id)
                if org:
                    service.download_organizations.append(org)

            db.session.commit()
            flash('Access permissions configured successfully', 'success')

    # Get service list
    services = Service.query.filter_by(organization_id=organization_id).all()

    # Get service types
    service_types = [
        {'id': 'course_info', 'name': 'Course Information Sharing'},
        {'id': 'student_identity', 'name': 'Student Identity Verification'},
        {'id': 'student_record', 'name': 'Student Record Query'},  # New service type
        {'id': 'thesis_sharing', 'name': 'Thesis Sharing'}
    ]

    # Get all organizations (for setting access permissions)
    organizations = Organization.query.filter(Organization.organization_id != organization_id).all()

    return render_template('organization/services.html',
                           services=services,
                           service_types=service_types,
                           organizations=organizations)


@org_bp.route('/banking', methods=['GET', 'POST'])
def banking():
    if not session.get('user_id') or session.get('user_role') != 'O-Convener':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    organization_id = session.get('organization_id')

    # Get bank interface information, including input fields
    bank_config = load_bank_interface_info()
    auth_input_fields = bank_config["authenticate"]["input"]

    if request.method == 'POST':
        # Dynamically get form data
        form_data = {}
        for field in auth_input_fields.keys():
            if field in request.form:
                form_data[field] = request.form.get(field)

        # Verify bank account information
        try:
            url = f"{bank_config['url']}{bank_config['authenticate']['path']}"

            # Send request
            if bank_config['authenticate']['method'].upper() == 'POST':
                response = requests.post(url, json=form_data)
            else:
                response = requests.get(url, params=form_data)

            auth_response = response.json()

            if auth_response.get('status') != 'success':
                flash('Bank account verification failed, please check information', 'danger')
                return redirect(url_for('organization.banking'))

            # Field mapping to fit BankAccount model
            field_mapping = {
                'bank': 'bank_name',
                'account_name': 'account_name',
                'account_number': 'account_no',
                'password': 'password'  # 直接映射到password字段，而不是password_hash
            }

            # Get existing account or create new account
            account = BankAccount.query.filter_by(organization_id=organization_id).first()

            if account:
                # Update account information
                for api_field, model_field in field_mapping.items():
                    if api_field in form_data:
                        setattr(account, model_field, form_data[api_field])

                # 为兼容性保留密码哈希设置
                # if 'password' in form_data:
                #     account.password_hash = generate_password_hash(form_data['password'])
            else:
                # Create new account
                account_data = {}
                for api_field, model_field in field_mapping.items():
                    if api_field in form_data:
                        account_data[model_field] = form_data[api_field]

                account_data['organization_id'] = organization_id
                account = BankAccount(**account_data)

                # 为兼容性设置密码哈希
                # if 'password' in form_data:
                #     account.password_hash = generate_password_hash(form_data['password'])

                db.session.add(account)

            db.session.commit()
            flash('Bank account information saved', 'success')
        except Exception as e:
            flash(f'Failed to save bank account information: {str(e)}', 'danger')
            return redirect(url_for('organization.banking'))

    # Get current account information
    account = BankAccount.query.filter_by(organization_id=organization_id).first()

    return render_template('organization/banking.html',
                           account=account,
                           auth_input_fields=auth_input_fields)

@org_bp.route('/view_logs')
def view_logs():
    if not session.get('user_id') or session.get('user_role') != 'O-Convener':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    organization_id = session.get('organization_id')

    # Filter conditions
    activity = request.args.get('activity')
    username = request.args.get('username')
    date = request.args.get('date')
    page = int(request.args.get('page', 1))
    per_page = 20

    query = ActivityLog.query.filter(ActivityLog.organization_id == organization_id)

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

    # Calculate total pages
    total_count = query.count()
    total_pages = (total_count + per_page - 1) // per_page

    # Paginated query
    logs = query.order_by(ActivityLog.login_time.desc()).offset((page - 1) * per_page).limit(per_page).all()

    return render_template('organization/logs.html',
                           logs=logs,
                           organization_id=organization_id,
                           activity=activity,
                           username=username,
                           date=date,
                           page=page,
                           total_pages=total_pages)


@org_bp.route('/view_transactions')
def view_transactions():
    if not session.get('user_id') or session.get('user_role') != 'O-Convener':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    organization_id = session.get('organization_id')

    # Get transaction list
    transactions = Transaction.query.filter(
        (Transaction.from_organization_id == organization_id) |
        (Transaction.to_organization_id == organization_id)
    ).order_by(Transaction.transaction_time.desc()).all()

    # Get organization information for displaying transaction counterparty names
    organizations = {
        org.organization_id: org.short_name
        for org in Organization.query.all()
    }

    # Add organization name information
    for transaction in transactions:
        transaction.from_organization_name = organizations.get(transaction.from_organization_id, 'Unknown')
        transaction.to_organization_name = organizations.get(transaction.to_organization_id, 'Unknown')

    return render_template('organization/transactions.html', transactions=transactions)


# Add the following method to organization_controller.py

@org_bp.route('/get_service_permissions/<int:service_id>')
def get_service_permissions(service_id):
    if not session.get('user_id') or session.get('user_role') != 'O-Convener':
        return jsonify({'error': 'Access denied'}), 403

    organization_id = session.get('organization_id')
    service = Service.query.get_or_404(service_id)

    if service.organization_id != organization_id:
        return jsonify({'error': 'Not authorized to access this service'}), 403

    # Get current permission settings
    view_organizations = []
    download_organizations = []

    # Check if new permission relationships are implemented
    if hasattr(service, 'view_organizations'):
        view_organizations = [org.organization_id for org in service.view_organizations]

    if hasattr(service, 'download_organizations'):
        download_organizations = [org.organization_id for org in service.download_organizations]
    else:
        # Backward compatibility - use traditional access_organizations
        view_organizations = [org.organization_id for org in service.access_organizations]
        download_organizations = view_organizations.copy()

    return jsonify({
        'view_organizations': view_organizations,
        'download_organizations': download_organizations
    })


@org_bp.route('/update_quota/<int:member_id>', methods=['POST'])
def update_quota(member_id):
    if not session.get('user_id') or session.get('user_role') != 'O-Convener':
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    organization_id = session.get('organization_id')

    # Get member information
    member = Member.query.get_or_404(member_id)

    if member.organization_id != organization_id:
        flash('Not authorized to modify this member', 'danger')
        return redirect(url_for('organization.manage_members'))

    # Get new quota
    try:
        new_quota = float(request.form.get('quota', 0))
        if new_quota < 0:
            flash('Quota cannot be negative', 'danger')
            return redirect(url_for('organization.manage_members'))

        # Update quota
        member.quota = new_quota
        db.session.commit()
        flash('Member quota updated successfully', 'success')
    except ValueError:
        flash('Quota must be a number', 'danger')
    except Exception as e:
        db.session.rollback()
        flash(f'Quota update failed: {str(e)}', 'danger')

    return redirect(url_for('organization.manage_members'))