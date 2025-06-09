import os

from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from app.models import db, User, Organization, Payment, Transaction, BankAccount, Member
import datetime
import requests
import json

from app.utils.bank_utils import load_bank_interface_info

payment_bp = Blueprint('payment', __name__)


@payment_bp.route('/select_method', methods=['GET', 'POST'])
def select_payment_method():
    if not session.get('user_id'):
        flash('Please login first', 'danger')
        return redirect(url_for('auth.login'))

    org_id = request.args.get('org_id') or request.form.get('org_id')
    amount = float(request.args.get('amount') or request.form.get('amount', 0))
    payment_type = request.args.get('payment_type') or request.form.get('payment_type')
    service_id = request.args.get('service_id') or request.form.get('service_id')
    redirect_url = request.args.get('redirect_url') or request.form.get('redirect_url')
    thesis_title = request.args.get('thesis_title') or request.form.get('thesis_title')

    if not all([org_id, amount, payment_type]):
        flash('Missing payment parameters', 'danger')
        return redirect(redirect_url or url_for('user.dashboard'))

    user = User.query.get(session.get('user_id'))
    organization = Organization.query.get_or_404(org_id)
    # Only check quota for thesis download service
    quota_available = 0
    quota_sufficient = False
    member = None

    if payment_type == 'thesis_download':
        member = Member.query.filter_by(
            organization_id=user.organization_id,
            email=user.email
        ).first()

        if member:
            quota_available = member.quota
            quota_sufficient = (quota_available >= amount)

    # Prepare payment description information
    payment_desc = ""
    if payment_type == 'thesis_download' and thesis_title:
        payment_desc = f"thesis download: {thesis_title}"
    elif payment_type == 'student_identity':
        payment_desc = "Student identity verification"
    elif payment_type == 'student_record':
        payment_desc = "Student record query"
    elif payment_type == 'student_identity_batch':
        payment_desc = "Batch student identity verification"
    elif payment_type == 'student_record_batch':
        payment_desc = "Batch student record query"

    return render_template('payment/select_method.html',
                           org_id=org_id,
                           organization=organization,
                           amount=amount,
                           payment_type=payment_type,
                           payment_desc=payment_desc,
                           service_id=service_id,
                           redirect_url=redirect_url,
                           thesis_title=thesis_title,
                           quota_available=quota_available,
                           quota_sufficient=quota_sufficient)


@payment_bp.route('/process_payment', methods=['POST'])
def process_payment():
    if not session.get('user_id'):
        flash('Please login first', 'danger')
        return redirect(url_for('auth.login'))

    org_id = request.form.get('org_id')
    amount = float(request.form.get('amount', 0))
    payment_type = request.form.get('payment_type')
    service_id = request.form.get('service_id')
    redirect_url = request.form.get('redirect_url')
    payment_method = request.form.get('payment_method')

    if not all([org_id, amount, payment_type, payment_method]):
        flash('Missing payment parameters', 'danger')
        return redirect(redirect_url or url_for('user.dashboard'))

    user_id = session.get('user_id')
    user = User.query.get(user_id)

    # Check user quota limit (as consumption limit, not payment method)
    member = Member.query.filter_by(
        organization_id=user.organization_id,
        email=user.email
    ).first()
    # Only check quota limit for thesis download service
    if payment_type == 'thesis_download':
        member = Member.query.filter_by(
            organization_id=user.organization_id,
            email=user.email
        ).first()
        # Check if exceeding quota limit
        if member and member.quota < amount:
            flash('Your consumption quota is insufficient, please contact your organization administrator', 'danger')
            return redirect(url_for('payment.select_payment_method',
                                org_id=org_id,
                                amount=amount,
                                payment_type=payment_type,
                                service_id=service_id,
                                redirect_url=redirect_url))

    # Create payment record
    thesis_title = request.form.get('thesis_title')
    payment = Payment(
        user_id=user_id,
        organization_id=user.organization_id,
        amount=amount,
        payment_type=payment_type,
        payment_method=payment_method,
        service_id=service_id,
        receiver_organization_id=org_id,
        status='pending',
    )
    db.session.add(payment)
    db.session.commit()

    # Process based on payment method
    if payment_method == 'transfer':
        # Bank transfer payment
        return redirect(url_for('payment.bank_transfer',
                                payment_id=payment.payment_id,
                                redirect_url=redirect_url))
    else:
        flash('Unsupported payment method', 'danger')
        return redirect(redirect_url or url_for('user.dashboard'))

## Original transfer version
@payment_bp.route('/bank_transfer/<int:payment_id>', methods=['GET', 'POST'])
def bank_transfer(payment_id):
    if not session.get('user_id'):
        flash('Please login first', 'danger')
        return redirect(url_for('auth.login'))

    payment = Payment.query.get_or_404(payment_id)
    user_id = session.get('user_id')

    if payment.user_id != user_id:
        flash('Access denied', 'danger')
        return redirect(url_for('user.dashboard'))

    redirect_url = request.args.get('redirect_url')

    # Get payee information
    receiver_organization = Organization.query.get(payment.receiver_organization_id)
    receiver_account = BankAccount.query.filter_by(organization_id=payment.receiver_organization_id).first()

    if not receiver_account:
        flash('Payee has not set up a bank account', 'danger')
        return redirect(redirect_url or url_for('user.dashboard'))

    # Get payer information
    sender_organization = Organization.query.get(payment.organization_id)
    sender_account = BankAccount.query.filter_by(organization_id=payment.organization_id).first()

    try:
        # Get bank interface information (including input fields)
        bank_config = load_bank_interface_info()
        transfer_input_fields = bank_config["transfer"]["input"]
        print(f"Bank interface configuration loaded successfully: URL={bank_config['url']}, Transfer path={bank_config['transfer']['path']}")
    except Exception as e:
        flash(f'Unable to load bank interface information: {str(e)}', 'danger')
        print(f"Unable to load bank interface information: {str(e)}")
        return redirect(redirect_url or url_for('user.dashboard'))

    if request.method == 'POST':
        print("\n======== POST request received ========")

        # Dynamically get form data
        form_data = {}
        for key, value in request.form.items():
            if key not in ['csrf_token', 'use_org_account', 'confirm_payment']:
                form_data[key] = value

        # Get operation type
        action = request.form.get('action', 'confirm_payment')

        print(f"Operation type: {action}")

        # If using organization account, supplement account information including password
        if 'use_org_account' in request.form and request.form['use_org_account'] == '1' and sender_account:
            print("\nUsing organization account information")
            # 添加银行账户信息
            for field_name in transfer_input_fields.keys():
                if field_name.startswith('from_') and field_name not in form_data:
                    base_field = field_name.replace('from_', '')
                    if base_field == 'bank':
                        form_data[field_name] = sender_account.bank_name
                        print(f"  Adding {field_name}: {sender_account.bank_name}")
                    elif base_field == 'name':
                        form_data[field_name] = sender_account.account_name
                        print(f"  Adding {field_name}: {sender_account.account_name}")
                    elif base_field == 'account':
                        form_data[field_name] = sender_account.account_no
                        print(f"  Adding {field_name}: {sender_account.account_no}")

            # 自动添加密码
            if 'password' not in form_data and hasattr(sender_account, 'password') and sender_account.password:
                form_data['password'] = sender_account.password
                print("  Auto-filling password from database")

        # Add payee information
        print("\nAdding payee information")
        for field_name in transfer_input_fields.keys():
            if field_name.startswith('to_') and field_name not in form_data:
                base_field = field_name.replace('to_', '')
                if base_field == 'bank':
                    form_data[field_name] = receiver_account.bank_name
                    print(f"  Adding {field_name}: {receiver_account.bank_name}")
                elif base_field == 'name':
                    form_data[field_name] = receiver_account.account_name
                    print(f"  Adding {field_name}: {receiver_account.account_name}")
                elif base_field == 'account':
                    form_data[field_name] = receiver_account.account_no
                    print(f"  Adding {field_name}: {receiver_account.account_no}")

        # Ensure amount field exists and is numeric
        if 'amount' in transfer_input_fields and 'amount' not in form_data:
            form_data['amount'] = float(payment.amount)
            print(f"  Adding amount: {payment.amount}")
        elif 'amount' in form_data:
            # Ensure amount is a float
            try:
                form_data['amount'] = float(form_data['amount'])
                print(f"  Converting amount to float: {form_data['amount']}")
            except (ValueError, TypeError) as e:
                print(f"  Unable to convert amount to float: {str(e)}")

        # If checking balance operation
        if action == 'check_balance':
            # Query balance
            from app.utils.bank_utils import check_bank_balance

            print("\n======== Checking balance ========")
            print(
                f"Checking account: {form_data.get('from_bank')} - {form_data.get('from_name')} - {form_data.get('from_account')}")

            balance_info = check_bank_balance(
                form_data.get('from_bank', ''),
                form_data.get('from_name', ''),
                form_data.get('from_account', ''),
                form_data.get('password', '')
            )

            print(f"Balance check result: {balance_info}")

            # Render balance page
            return render_template('payment/bank_balance.html',
                                   payment=payment,
                                   balance_info=balance_info,
                                   from_bank=form_data.get('from_bank', ''),
                                   from_name=form_data.get('from_name', ''),
                                   from_account=form_data.get('from_account', ''),
                                   password=form_data.get('password', ''),
                                   to_bank=form_data.get('to_bank', ''),
                                   to_name=form_data.get('to_name', ''),
                                   to_account=form_data.get('to_account', ''),
                                   thesis_title=session.get('pending_thesis_title'))

        # If confirming payment operation
        else:  # action == 'confirm_payment'
            print("\n======== Confirming payment ========")

            # Create transaction record
            transaction = Transaction(
                payment_id=payment.payment_id,
                from_organization_id=payment.organization_id,
                to_organization_id=payment.receiver_organization_id,
                amount=payment.amount
            )
            db.session.add(transaction)

            # Prepare payment request data - ensure correct format
            transfer_data = {
                "from_bank": form_data.get('from_bank', ''),
                "from_name": form_data.get('from_name', ''),
                "from_account": form_data.get('from_account', ''),
                "to_bank": form_data.get('to_bank', ''),
                "to_name": form_data.get('to_name', ''),
                "to_account": form_data.get('to_account', ''),
                "amount": float(form_data.get('amount', 0)),  # Ensure it's a number
                "password": form_data.get('password', '')
            }

            # Log the data being sent (hide password)
            log_data = {k: (v if k != 'password' else '******') for k, v in transfer_data.items()}
            print(f"Data sent to bank API: {log_data}")

            # Call bank interface for transfer
            try:
                url = f"{bank_config['url']}{bank_config['transfer']['path']}"
                print(f"Sending request to URL: {url}")

                # Set correct Content-Type
                headers = {'Content-Type': 'application/json'}

                # Send request
                print("Starting to send request...")
                start_time = datetime.datetime.now()

                if bank_config['transfer']['method'].upper() == 'POST':
                    response = requests.post(url, json=transfer_data, headers=headers, timeout=30)
                    print("Using POST method with json parameter")
                else:
                    response = requests.get(url, params=transfer_data, timeout=30)
                    print("Using GET method with params parameter")

                end_time = datetime.datetime.now()
                print(f"Request time: {(end_time - start_time).total_seconds():.2f} seconds")

                # Log response
                print(f"Response status code: {response.status_code}")
                print(f"Response headers: {dict(response.headers)}")
                print(f"Response content: {response.text}")

                # Safely parse JSON
                try:
                    if response.text.strip():
                        bank_response = response.json()
                        print(f"Parsed JSON response: {bank_response}")
                    else:
                        print("Empty response received, using default success response")
                        bank_response = {"status": "success"}
                except ValueError as e:
                    print(f"JSON parsing error: {str(e)}")
                    print(f"Using default success response")
                    bank_response = {"status": "success"}

                # Handle bank response
                if bank_response.get("status") == "success":
                    try:
                        from app.utils.bank_utils import check_bank_balance

                        # Query balance using the same account info
                        updated_balance_info = check_bank_balance(
                            form_data.get('from_bank', ''),
                            form_data.get('from_name', ''),
                            form_data.get('from_account', ''),
                            form_data.get('password', '')
                        )

                        # If query successful, save balance to session and display in flash message
                        if updated_balance_info.get('status') == 'success':
                            session['last_balance'] = updated_balance_info.get('balance')
                            flash(f'Payment successful! Current account balance: {updated_balance_info.get("balance")} RMB', 'success')
                        else:
                            # If balance query fails, still show payment success but without balance
                            flash('Payment successful!', 'success')
                    except Exception as e:
                        print(f"Balance query failed: {str(e)}")
                        flash('Payment successful!', 'success')

                    payment.status = 'completed'

                    # Find the user's member record
                    if payment.payment_type == 'thesis_download':
                        user = User.query.get(payment.user_id)
                        if user:
                            member = Member.query.filter_by(
                                organization_id=user.organization_id,
                                email=user.email
                            ).first()

                            # If member record found and has quota, reduce quota
                            if member and member.quota >= payment.amount:
                                member.quota -= payment.amount
                                db.session.commit()
                                print(f"Deducted {payment.amount} RMB from user {user.email}'s quota")

                    payment.completed_at = datetime.datetime.utcnow()
                    transaction.status = 'success'
                    db.session.commit()

                    # Set flash message and redirect based on payment type
                    if payment.payment_type == 'membership_fee_batch' and session.get('pending_members'):
                        flash('Payment successful, processing member import', 'success')
                        return redirect(
                            url_for('organization.process_batch_members_after_payment', payment_id=payment.payment_id))
                    elif payment.payment_type == 'membership_fee':
                        flash('Membership fee payment successful', 'success')
                        return redirect(url_for('organization.process_member_after_payment', payment_id=payment.payment_id))
                    elif payment.payment_type == 'membership_upgrade':
                        flash('Membership level upgrade fee payment successful', 'success')
                        return redirect(url_for('organization.manage_members'))
                    elif payment.payment_type == 'thesis_download':
                        flash('Thesis download fee payment successful', 'success')

                        # Simplified: Get thesis title directly from session, no longer from form or URL
                        thesis_title = session.get('pending_thesis_title')
                        print(f"Thesis title from session: {thesis_title}")

                        # Jump directly to thesis download processing function, only passing service_id parameter
                        # No longer pass thesis_title in URL, all through session
                        if payment.service_id:
                            return redirect(url_for('consumer.thesis_download_after_payment',
                                                    service_id=payment.service_id))
                        else:
                            # If service_id doesn't exist, return to dashboard
                            flash('Missing service ID, cannot complete download', 'danger')
                            return redirect(url_for('user.dashboard'))

                    elif payment.payment_type == 'student_identity':
                        flash('Student identity verification fee payment successful', 'success')
                        # Changed to use student_auth_after_payment for verification
                        return redirect(url_for('consumer.student_auth_after_payment', service_id=payment.service_id))
                    elif payment.payment_type == 'student_identity_batch':
                        flash('Batch student identity verification fee payment successful', 'success')
                        # Use temporary file for batch verification
                        temp_file = session.get('temp_batch_file')
                        if temp_file and os.path.exists(temp_file):
                            return redirect(url_for('consumer.process_batch_after_payment',
                                                    service_id=payment.service_id,
                                                    temp_file=temp_file))
                        else:
                            flash('Temporary file lost, please upload again', 'danger')
                            return redirect(url_for('consumer.student_auth', service_id=payment.service_id))
                    elif payment.payment_type == 'student_record':
                        flash('Student record query fee payment successful', 'success')
                        # Get original query parameters
                        query_params = session.get('pending_record_form_data', {})
                        # Redirect back to query processing page
                        return redirect(
                            url_for('consumer.student_record_result', service_id=payment.service_id, **query_params))
                    elif payment.payment_type == 'student_record_batch':
                        flash('Student record batch query fee payment successful', 'success')
                        # Add code below to implement redirect
                        temp_file = session.get('temp_batch_file')
                        if temp_file and os.path.exists(temp_file):
                            return redirect(url_for('consumer.process_record_batch_after_payment',
                                                    service_id=payment.service_id,
                                                    temp_file=temp_file))
                        else:
                            flash('Temporary file lost, please upload again', 'danger')
                            return redirect(url_for('consumer.student_record', service_id=payment.service_id))
                    else:
                        flash('Payment successful', 'success')

                    return redirect(redirect_url or url_for('user.dashboard'))
                else:
                    # Transfer failed
                    reason = bank_response.get("reason", "Unknown reason")
                    print(f"Transfer failed, reason: {reason}")
                    payment.status = 'failed'
                    transaction.status = 'failed'
                    transaction.reason = reason
                    db.session.commit()
                    if payment.payment_type == 'membership_fee':
                        session.pop('pending_single_member', None)
                    # If batch member import payment fails, clear pending members
                    if payment.payment_type == 'membership_fee_batch':
                        session.pop('pending_members', None)
                        print("Cleared pending member imports")

                    flash(f'Payment failed: {reason}', 'danger')
                    return redirect(redirect_url or url_for('user.dashboard'))
            except requests.exceptions.RequestException as e:
                # Network request exception
                print(f"Network request exception: {type(e).__name__} - {str(e)}")
                payment.status = 'failed'
                transaction.status = 'failed'
                transaction.reason = f"Network request exception: {str(e)}"
                db.session.commit()

                # If batch member import payment exception, clear pending members
                if payment.payment_type == 'membership_fee_batch':
                    session.pop('pending_members', None)

                flash(f'Network request exception: {str(e)}', 'danger')
                return redirect(redirect_url or url_for('user.dashboard'))
            except Exception as e:
                # Other exceptions
                print(f"Other exception: {type(e).__name__} - {str(e)}")
                payment.status = 'failed'
                transaction.status = 'failed'
                transaction.reason = str(e)
                db.session.commit()

                # If batch member import payment exception, clear pending members
                if payment.payment_type == 'membership_fee_batch':
                    session.pop('pending_members', None)

                flash(f'Payment exception: {str(e)}', 'danger')
                return redirect(redirect_url or url_for('user.dashboard'))
        # 传递是否有银行账户信息的标志给模板
    has_sender_account = sender_account is not None
    return render_template('payment/bank_transfer.html',
                           payment=payment,
                           receiver_organization=receiver_organization,
                           receiver_account=receiver_account,
                           sender_account=sender_account,
                           has_sender_account=has_sender_account,
                           redirect_url=redirect_url,
                           transfer_input_fields=transfer_input_fields)


@payment_bp.route('/payment_history')
def payment_history():
    if not session.get('user_id'):
        flash('Please login first', 'danger')
        return redirect(url_for('auth.login'))

    user_id = session.get('user_id')
    user = User.query.get(user_id)

    # Get payment records
    payments = Payment.query.filter_by(user_id=user_id).order_by(Payment.created_at.desc()).all()

    # Get organization information
    organizations = {
        org.organization_id: org.short_name
        for org in Organization.query.all()
    }

    # Add organization names
    for payment in payments:
        payment.receiver_organization_name = organizations.get(payment.receiver_organization_id, 'Unknown')

        # If user is organization convener, show organization transactions
        transactions = None
        if user.role == 'O-Convener':
            organization_id = user.organization_id
            transactions = Transaction.query.filter(
                (Transaction.from_organization_id == organization_id) |
                (Transaction.to_organization_id == organization_id)
            ).order_by(Transaction.transaction_time.desc()).limit(10).all()

            # Add organization names
            for transaction in transactions:
                transaction.from_organization_name = organizations.get(transaction.from_organization_id, 'Unknown')
                transaction.to_organization_name = organizations.get(transaction.to_organization_id, 'Unknown')