from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify, Response
from app.models import db, Service, APIConfig, Organization, User, Payment, Member, ActivityLog
import requests
import json
import datetime
import base64
from flask import current_app as app  # Add this line
from werkzeug.utils import secure_filename  # Ensure this line also exists # Or import correctly based on your project structure
from io import BytesIO
consumer_bp = Blueprint('consumer', __name__)

@consumer_bp.route('/thesis_search/<int:service_id>', methods=['GET', 'POST'])
def thesis_search(service_id):
    if not session.get('user_id'):
        flash('Please log in first', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.get(session.get('user_id'))
    if not user:
        flash('User does not exist', 'danger')
        return redirect(url_for('auth.login'))

    service = Service.query.get_or_404(service_id)
    if not service.is_configured:
        flash('Service not configured', 'danger')
        return redirect(url_for('user.view_organization', org_id=service.organization_id))

    # Check view permission - prioritize checking view_organizations
    has_view_access = True  # Thesis viewing is public data

    # If not a public service, check if user's organization has view permission

    # Check download permission - get download status early for display
    # Check download permission - special authorization required
    # has_download_access = service.is_public or user.organization_id == service.organization_id
    # has_download_access = user.organization_id == service.organization_id
    # if not has_download_access:
    #     if hasattr(service, 'download_organizations'):
    #         has_download_access = user.organization_id in [org.organization_id for org in
    #                                                        service.download_organizations]
    #     else:
    #         # Backward compatibility
    #         has_download_access = user.organization_id in [org.organization_id for org in service.access_organizations]
    has_download_access = user.organization_id == service.organization_id
    if not has_download_access:
        #     if hasattr(service, 'download_organizations'):
        # If download_organizations relationship is implemented
        has_download_access = user.organization_id in [org.organization_id for org in
                                                       service.download_organizations]

    # Get API configuration
    api_config = APIConfig.query.filter_by(service_id=service_id, is_active=True).first()
    if not api_config:
        flash('Service configuration error', 'danger')
        return redirect(url_for('user.view_organization', org_id=service.organization_id))

    # Get provider organization
    provider_organization = Organization.query.get(service.organization_id)

    # Find download service in the same organization
    download_service = Service.query.filter_by(
        organization_id=service.organization_id,
        type='thesis_sharing'  # Keep consistent with original type or use custom type
    ).filter(
        Service.service_id != service.service_id  # Exclude current search service
    ).first()

    # If no separate download service found, use current service
    download_service_id = download_service.service_id if download_service else service.service_id

    if request.method == 'POST':
        # Dynamically build request parameters
        payload = {}
        missing_fields = []

        # Build request data based on API config
        if api_config.input:
            for field_name, field_type in api_config.input.items():
                if isinstance(field_type, str) and field_type.lower() != 'file':  # Handle non-file fields
                    value = request.form.get(field_name)
                    if not value:
                        missing_fields.append(field_name)
                    payload[field_name] = value
                elif field_name in request.files and request.files[field_name].filename:
                    file = request.files[field_name]
                    if file.filename:
                        # Handle file...
                        pass

        # Validate required fields
        if missing_fields:
            flash(f'Please enter the following fields: {", ".join(missing_fields)}', 'danger')
            return redirect(url_for('consumer.thesis_search', service_id=service_id))

        # Call API
        try:
            url = f"{api_config.base_url.rstrip('/')}/{api_config.path.lstrip('/')}"

            # Pass all payload parameters to API
            if api_config.method.upper() == 'GET':
                response = requests.get(url, params=payload)
            else:
                response = requests.post(url, json=payload)

            # Record activity
            log = ActivityLog.query.filter_by(
                user_id=user.user_id,
                logout_time=None
            ).order_by(ActivityLog.login_time.desc()).first()

            if log:
                # Build activity description with search parameters
                activity_description = f'thesis_search: {service.name}'
                search_params = []
                if 'keywords' in payload and payload['keywords']:
                    search_params.append(f"Keyword: {payload['keywords']}")
                if 'code' in payload and payload['code']:
                    search_params.append(f"Code: {payload['code']}")

                if search_params:
                    activity_description += f" - {', '.join(search_params)}"

                log.service_accessed = activity_description
                log.provider_organization_id = service.organization_id
                db.session.commit()

            if response.status_code == 200:
                try:
                    results = response.json()
                    return render_template('consumer/thesis_results.html',
                                           service=service,
                                           provider_organization=provider_organization,
                                           results=results,
                                           keywords=payload.get('keywords', ''),
                                           code=payload.get('code', ''),
                                           download_price=service.price,
                                           has_download_access=has_download_access,
                                           download_service_id=download_service_id)
                except:
                    error = 'Response data format error'
                    return render_template('consumer/thesis_search.html',
                                           service=service,
                                           provider_organization=provider_organization,
                                           error=error,
                                           has_download_access=has_download_access,
                                           api_config=api_config)
            else:
                error = f'Request failed: HTTP {response.status_code}'
                return render_template('consumer/thesis_search.html',
                                       service=service,
                                       provider_organization=provider_organization,
                                       error=error,
                                       has_download_access=has_download_access,
                                       api_config=api_config)
        except Exception as e:
            error = f'Request error: {str(e)}'
            return render_template('consumer/thesis_search.html',
                                   service=service,
                                   provider_organization=provider_organization,
                                   error=error,
                                   has_download_access=has_download_access,
                                   api_config=api_config)

    return render_template('consumer/thesis_search.html',
                           service=service,
                           provider_organization=provider_organization,
                           has_download_access=has_download_access,
                           download_service_id=download_service_id,
                           api_config=api_config)  # Pass API config to template



@consumer_bp.route('/thesis_download/<int:service_id>', methods=['POST','GET'])
def thesis_download(service_id):
    if not session.get('user_id'):
        flash('Please log in first', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.get(session.get('user_id'))
    if not user:
        flash('User does not exist', 'danger')
        return redirect(url_for('auth.login'))

    service = Service.query.get_or_404(service_id)

    # Check download permissions
    #has_download_access = service.is_public or user.organization_id == service.organization_id
    has_download_access = user.organization_id == service.organization_id
    if not has_download_access:
    #     if hasattr(service, 'download_organizations'):
            # If download_organizations relationship is implemented
        has_download_access = user.organization_id in [org.organization_id for org in
                                                           service.download_organizations]
    #     else:
    #         # Backward compatibility - use traditional access_organizations
    #         has_download_access = user.organization_id in [org.organization_id for org in service.access_organizations]
    # print(f"Debug download permission: {has_download_access}")
    if not has_download_access:
        flash('You do not have permission to download this thesis. Please contact the service provider for access.', 'danger')
        return redirect(url_for('consumer.thesis_search', service_id=service_id))

    # Get API configuration
    api_config = APIConfig.query.filter_by(service_id=service_id, is_active=True).first()
    if not api_config:
        flash('Service configuration error', 'danger')
        return redirect(url_for('user.view_organization', org_id=service.organization_id))

    # Support GET request, get title from URL parameters
    if request.method == 'GET':
        title = request.args.get('title')
        if not title:
            flash('Missing thesis title', 'danger')
            return redirect(url_for('consumer.thesis_search', service_id=service_id))
    else:  # POST request
        title = request.form.get('title')
        if not title:
            flash('Missing thesis title', 'danger')
            return redirect(url_for('consumer.thesis_search', service_id=service_id))

    # Get thesis title
    title = request.form.get('title') or request.args.get('title')
    if title:
        # Save thesis title to session
        session['pending_thesis_title'] = title
        print(f"Thesis title saved to session: {title}")
    # title = request.form.get('title')
    # if not title:
    #     flash('Missing thesis title', 'danger')
    #     return redirect(url_for('consumer.thesis_search', service_id=service_id))

    # Handle payment - initialize payment variable
    payment = None  # Initialize as None

    if service.price > 0:
        # Check if there is already an unused payment record
        payment = Payment.query.filter_by(
            user_id=user.user_id,
            organization_id=user.organization_id,
            receiver_organization_id=service.organization_id,
            service_id=service.service_id,
            status='completed',
            payment_type='thesis_download'
        ).order_by(Payment.completed_at.desc()).first()

        if not payment:
            # Check if the user has sufficient quota
            member = Member.query.filter_by(
                organization_id=user.organization_id,
                email=user.email
            ).first()

            has_quota = False
            if member and member.quota >= service.price:
                # Allow user to choose quota payment
                has_quota = True

            # Redirect to payment page
            keywords = request.form.get('keywords', '')
            code = request.form.get('code', '')
            return redirect(url_for('payment.select_payment_method',
                                    org_id=service.organization_id,
                                    amount=service.price,
                                    payment_type='thesis_download',
                                    service_id=service.service_id,
                                    has_quota=has_quota,
                                    thesis_title=title,
                                    redirect_url=url_for('consumer.thesis_search',
                                                         service_id=service_id,
                                                         keywords=keywords,
                                                         code=code
                                                         )))

    # Call API to download thesis
    try:
        # url = f"{api_config.base_url.rstrip('/')}/{api_config.path.lstrip('/')}"
        base_url = api_config.base_url.rstrip('/')
        pdf_endpoint = "/hw/thesis/pdf"
        url = f"{base_url}{pdf_endpoint}"

        # if api_config.method.upper() == 'GET':
        #     response = requests.get(url, params={'title': title})
        # else:
        #     response = requests.post(url, json={'title': title})
        response = requests.get(url, params={'title': title})

        # Record activity
        log = ActivityLog.query.filter_by(
            user_id=user.user_id,
            logout_time=None
        ).order_by(ActivityLog.login_time.desc()).first()

        if log:
            log.service_accessed = f'thesis_download: {service.name} - {title}'
            log.provider_organization_id = service.organization_id
            db.session.commit()

        if response.status_code == 200:
            # Return PDF
            from flask import Response
            if payment:
                payment.status = 'used'
                db.session.commit()
                print(f"Payment record {payment.payment_id} marked as used")

            # Mark payment as used (if payment method was used)

            return Response(
                response.content,
                mimetype='application/pdf',
                headers={
                    "Content-Disposition": f"attachment; filename={title.replace(' ', '_')}.pdf"
                }
            )
        else:
            flash(f'Download failed: HTTP {response.status_code}', 'danger')
            return redirect(url_for('consumer.thesis_search', service_id=service_id))
    except Exception as e:
        flash(f'Download error: {str(e)}', 'danger')
        return redirect(url_for('consumer.thesis_search', service_id=service_id))



@consumer_bp.route('/thesis_download_after_payment/<int:service_id>', methods=['GET'])
def thesis_download_after_payment(service_id):
    """Handle thesis download request after successful payment"""
    if not session.get('user_id'):
        flash('Please log in first', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.get(session.get('user_id'))
    if not user:
        flash('User does not exist', 'danger')
        return redirect(url_for('auth.login'))

    # Get thesis title from session
    title = session.get('pending_thesis_title')
    print(f"Debug: Thesis title retrieved from session in thesis_download_after_payment: {title}")

    if not title:
        flash('Failed to retrieve thesis information. Please return to the search page and select again.', 'danger')
        return redirect(url_for('consumer.thesis_search', service_id=service_id))

    service = Service.query.get_or_404(service_id)
    api_config = APIConfig.query.filter_by(service_id=service_id, is_active=True).first()

    if not api_config:
        flash('Service configuration error', 'danger')
        return redirect(url_for('user.view_organization', org_id=service.organization_id))

    # Find payment record and verify
    payment = Payment.query.filter_by(
        user_id=user.user_id,
        organization_id=user.organization_id,
        receiver_organization_id=service.organization_id,
        service_id=service.service_id,
        status='completed',
        payment_type='thesis_download'
    ).order_by(Payment.completed_at.desc()).first()

    if not payment:
        flash('No valid payment record found. Please complete payment first.', 'danger')
        return redirect(url_for('consumer.thesis_search', service_id=service_id))

    # Call API to download thesis - add more validation and debugging
    try:
        # Construct the correct PDF endpoint URL
        base_url = api_config.base_url.rstrip('/')
        pdf_endpoint = "/hw/thesis/pdf"
        url = f"{base_url}{pdf_endpoint}"
        print(f"Debug: API endpoint used for download after payment: {url}")

        # Use GET request to get PDF
        request_data = {'title': title}
        print(f"Debug: Request parameters: {request_data}")

        response = requests.get(url, params=request_data)
        print(f"Debug: API response status code: {response.status_code}")
        print(f"Debug: Response headers: {dict(response.headers)}")
        print(f"Debug: First 50 bytes of response content: {response.content[:50]}")

        # Check if the returned content is actually a PDF (check PDF header %PDF-)
        is_pdf = response.content.startswith(b'%PDF-')
        print(f"Debug: Is the response content in PDF format: {is_pdf}")

        # Check content length
        content_length = len(response.content)
        print(f"Debug: Response content length: {content_length} bytes")

        if response.status_code == 200 and is_pdf and content_length > 100:
            # Mark payment record as used
            payment.status = 'used'
            db.session.commit()

            # Use HTML page to implement download + redirect
            from flask import make_response

            # Create an HTML response that automatically downloads PDF and redirects
            safe_filename = title.replace(' ', '_').replace('"', '').replace("'", '')
            search_url = url_for('consumer.thesis_search', service_id=service_id)

            html_content = f"""
                        <!DOCTYPE html>
                        <html>
                        <head>
                            <meta charset="utf-8">
                            <title>Thesis Download</title>
                            <script>
                                function downloadAndRedirect() {{
                                    // Create an invisible 'a' tag to trigger download
                                    var a = document.createElement('a');
                                    var blob = new Blob([new Uint8Array({list(response.content)})], {{type: 'application/pdf'}});
                                    a.href = window.URL.createObjectURL(blob);
                                    a.download = '{safe_filename}.pdf';
                                    document.body.appendChild(a);
                                    a.click();

                                    // Redirect after download
                                    setTimeout(function() {{
                                        window.location.href = "{search_url}";
                                    }}, 500);
                                }}

                                // Execute after page loads
                                window.onload = downloadAndRedirect;
                            </script>
                        </head>
                        <body>
                            <div style="text-align:center; margin-top:50px;">
                                <h2>Downloading thesis...</h2>
                                <p>You will be redirected to the search page after the download completes.</p>
                            </div>
                        </body>
                        </html>
                        """

            # Clear thesis title from session
            session.pop('pending_thesis_title', None)

            return make_response(html_content)
        else:
            # Problematic response
            error_message = "Download failed: "
            if response.status_code != 200:
                error_message += f"HTTP error code {response.status_code}"
            elif not is_pdf:
                error_message += "Returned content is not in PDF format"
            elif content_length <= 100:
                error_message += "Returned PDF content is too small and might be corrupted"

            try:
                error_details = response.json()
                print(f"Debug: API error details: {error_details}")
                if 'detail' in error_details:
                    error_message += f" - {error_details['detail']}"
            except:
                if not is_pdf:
                    print(f"Debug: Error response content: {response.text[:200]}")
                    error_message += f" - {response.text[:100]}"

            flash(error_message, 'danger')
            return redirect(url_for('consumer.thesis_search', service_id=service_id))
    except Exception as e:
        print(f"Debug: Download exception: {str(e)}")
        flash(f'Download error: {str(e)}', 'danger')
        return redirect(url_for('consumer.thesis_search', service_id=service_id))


@consumer_bp.route('/thesis_view/<int:service_id>', methods=['GET'])
def thesis_view(service_id):
    print(f"Debug: thesis_view function called, service_id={service_id}")
    print(f"Debug: Request parameters: {request.args}")
    if not session.get('user_id'):
        flash('Please log in first', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.get(session.get('user_id'))
    if not user:
        flash('User does not exist', 'danger')
        return redirect(url_for('auth.login'))

    # Get thesis title
    title = request.args.get('title')
    print(f"Debug: Extracted title: {title}")
    if not title:
        flash('Missing thesis title', 'danger')
        return redirect(url_for('consumer.thesis_search', service_id=service_id))

    service = Service.query.get_or_404(service_id)

    # Check view permission
    has_view_access = service.is_public
    if not has_view_access:
        if hasattr(service, 'view_organizations'):
            has_view_access = user.organization_id in [org.organization_id for org in service.view_organizations]
        else:
            has_view_access = user.organization_id in [org.organization_id for org in service.access_organizations]
    print(f"Debug: User has view access: {has_view_access}")
    if not has_view_access:
        flash('No permission to view the thesis, please contact the service provider for access', 'danger')
        return redirect(url_for('consumer.thesis_search', service_id=service_id))

    has_download_access = user.organization_id == service.organization_id
    if not has_download_access:
        # If the download_organizations relationship is implemented
        has_download_access = user.organization_id in [org.organization_id for org in
                                                       service.download_organizations]

    # Get API configuration
    api_config = APIConfig.query.filter_by(service_id=service_id, is_active=True).first()
    if not api_config:
        flash('Service configuration error', 'danger')
        return redirect(url_for('user.view_organization', org_id=service.organization_id))

    # Get service provider
    provider_organization = Organization.query.get(service.organization_id)

    # Log activity
    log = ActivityLog.query.filter_by(
        user_id=user.user_id,
        logout_time=None
    ).order_by(ActivityLog.login_time.desc()).first()

    if log:
        log.service_accessed = f'thesis_view: {service.name} - {title}'
        log.provider_organization_id = service.organization_id
        db.session.commit()

    # Call API to get thesis content - key change
    try:
        # Build PDF endpoint URL - use thesis/pdf instead of thesis/search
        base_url = api_config.base_url.rstrip('/')

        # Manually construct PDF endpoint, instead of using api_config.path
        pdf_endpoint = "/hw/thesis/pdf"
        url = f"{base_url}{pdf_endpoint}"

        print(f"Debug: API URL to be called: {url}")
        print(f"Debug: Request method: {api_config.method.upper()}")

        # Keep using title parameter
        request_data = {'title': title}
        print(f"Debug: Request data: {request_data}")

        # Always use GET request
        response = requests.get(url, params=request_data)

        print(f"Debug: API response status: {response.status_code}")
        print(f"Debug: API response headers: {response.headers}")

        if response.status_code == 200:
            print(f"Debug: API response content (partial): {response.text[:500]}")
            # Base64 encode PDF content for embedding in HTML
            try:
                pdf_data = base64.b64encode(response.content).decode('utf-8')
                return render_template('consumer/thesis_view.html',
                                       title=title,
                                       service=service,
                                       provider_organization=provider_organization,
                                       pdf_data=pdf_data,
                                       has_download_access=has_download_access)
            except Exception as e:
                flash(f'PDF processing error: {str(e)}', 'danger')
                return redirect(url_for('consumer.thesis_search', service_id=service_id))
        else:
            # Enhanced error handling
            error_message = f'View failed: HTTP {response.status_code}'
            try:
                error_details = response.json()
                print(f"Debug: API error details: {error_details}")
                if 'detail' in error_details:
                    error_message += f" - {error_details['detail']}"
            except:
                print(f"Debug: Unable to parse error response: {response.text}")

            flash(error_message, 'danger')
            return redirect(url_for('consumer.thesis_search', service_id=service_id))
    except Exception as e:
        flash(f'View error: {str(e)}', 'danger')
        return redirect(url_for('consumer.thesis_search', service_id=service_id))


# Add a helper route to get the list of available students (for testing environment only)
@consumer_bp.route('/get_available_students/<int:service_id>', methods=['GET'])
def get_available_students(service_id):
    if not session.get('user_id'):
        return jsonify({'error': 'Please log in first'}), 401

    service = Service.query.get_or_404(service_id)
    api_config = APIConfig.query.filter_by(service_id=service_id, is_active=True).first()

    if not api_config:
        return jsonify({'error': 'Service configuration error'}), 404

    try:
        # Try to fetch student list from mock server
        student_list_url = f"{api_config.base_url.rstrip('/')}/hw/students/list"
        response = requests.get(student_list_url)

        if response.status_code == 200:
            students = response.json()
            return jsonify(students)
        else:
            return jsonify({'error': f'Failed to get student list: {response.status_code}'}), response.status_code
    except Exception as e:
        return jsonify({'error': f'Request error: {str(e)}'}), 500

@consumer_bp.route('/student_services/<int:service_id>', methods=['GET'])
def student_services(service_id):
    if not session.get('user_id'):
        flash('Please log in first', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.get(session.get('user_id'))
    if not user:
        flash('User does not exist', 'danger')
        return redirect(url_for('auth.login'))

    service = Service.query.get_or_404(service_id)

    # Redirect to corresponding page according to service type
    if service.type == 'student_identity':
        return redirect(url_for('consumer.student_auth', service_id=service_id))
    elif service.type == 'student_record':
        return redirect(url_for('consumer.student_record', service_id=service_id))
    else:
        flash('Unknown service type', 'danger')
        return redirect(url_for('user.view_organization', org_id=service.organization_id))


# Add these new routes to consumer_controller.py



# from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify, Response
# from app.models import db, Service, APIConfig, Organization, User, Payment, Member, ActivityLog
# import requests
# import json
# import datetime
# import base64
import os
# from flask import current_app as app
# from werkzeug.utils import secure_filename

# consumer_bp = Blueprint('consumer', __name__)


def cleanup_temp_files():
    """Clean up expired temporary files"""
    try:
        import os
        import datetime

        temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp')
        if not os.path.exists(temp_dir):
            return

        # Get current time
        now = datetime.datetime.now()

        # Clean up temporary files older than 24 hours
        for filename in os.listdir(temp_dir):
            file_path = os.path.join(temp_dir, filename)
            if os.path.isfile(file_path):
                # Get file modification time
                file_time = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
                # If file is older than 24 hours
                if (now - file_time).total_seconds() > 24 * 3600:
                    try:
                        os.remove(file_path)
                        print(f"Cleaned temporary file: {file_path}")
                    except:
                        pass
    except Exception as e:
        print(f"Error cleaning temporary files: {str(e)}")


# Student Identity Verification Service - Identity only
@consumer_bp.route('/student_auth/<int:service_id>', methods=['GET', 'POST'])
def student_auth(service_id):
    # Clean up expired temporary files
    cleanup_temp_files()

    if not session.get('user_id'):
        flash('Please log in first', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.get(session.get('user_id'))
    if not user or user.access_level < 2:  # Requires consumer permission
        flash('Access denied, requires private data consumer permission', 'danger')
        return redirect(url_for('main.index'))

    service = Service.query.get_or_404(service_id)
    if not service.is_configured:
        flash('Service not configured', 'danger')
        return redirect(url_for('user.view_organization', org_id=service.organization_id))

    # Check service access permission - prioritize checking view_organizations
    has_view_access = service.is_public
    if not has_view_access:
        if hasattr(service, 'view_organizations'):
            has_view_access = user.organization_id in [org.organization_id for org in service.view_organizations]
        else:
            has_view_access = user.organization_id in [org.organization_id for org in service.access_organizations]

    if not has_view_access:
        flash('No permission to access this service', 'danger')
        return redirect(url_for('user.view_organization', org_id=service.organization_id))

    # Get API configuration
    api_config = APIConfig.query.filter_by(service_id=service_id, is_active=True).first()
    if not api_config:
        flash('Service configuration error', 'danger')
        return redirect(url_for('user.view_organization', org_id=service.organization_id))

    # Get service provider organization
    provider_organization = Organization.query.get(service.organization_id)

    if request.method == 'POST':
        # Handle payment
        if service.price > 0:
            member = Member.query.filter_by(
                organization_id=user.organization_id,
                email=user.email
            ).first()

            if member and member.quota < service.price:
                flash('Your consumption quota is insufficient, please contact the organization admin to increase quota or use bank transfer payment', 'warning')
        if service.price > 0:
            # Get form data
            form_data = {}
            for key, value in request.form.items():
                if key not in ['csrf_token']:
                    form_data[key] = value

            # Save form data to session
            session['pending_auth_form_data'] = form_data
            print(f"Saved form data to session: {form_data}")

            # Handle file upload
            if request.files:
                # Create temporary directory to save files
                temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp')
                os.makedirs(temp_dir, exist_ok=True)

                file_info = {}
                for key, file in request.files.items():
                    if file.filename:
                        # Generate secure filename
                        secure_name = secure_filename(file.filename)
                        temp_path = os.path.join(temp_dir, f"{user.user_id}_{secure_name}")
                        file.save(temp_path)
                        file_info[key] = {
                            'filename': file.filename,
                            'path': temp_path
                        }

                # Save file info to session
                if file_info:
                    session['pending_auth_files'] = file_info
                    print(f"Saved file info to session: {file_info}")

            # Check if user has enough quota
            member = Member.query.filter_by(
                organization_id=user.organization_id,
                email=user.email
            ).first()

            has_quota = False
            if member and member.quota >= service.price:
                has_quota = True

            # Redirect to payment page - use simple redirect URL
            return redirect(url_for('payment.select_payment_method',
                                    org_id=service.organization_id,
                                    amount=service.price,
                                    payment_type='student_identity',
                                    service_id=service.service_id,
                                    has_quota=has_quota,
                                    redirect_url=url_for('consumer.student_auth_result', service_id=service_id)))

        # Get form data
        form_data = {}
        for key, value in request.form.items():
            if key not in ['csrf_token']:
                form_data[key] = value

        # Handle file upload
        files = {}
        for key, file in request.files.items():
            if file.filename:
                files[key] = file

        # Call API
        try:
            url = f"{api_config.base_url.rstrip('/')}/hw/student/authenticate"
            print(f"API endpoint for single authentication: {url}")
            print(f"Request data: {form_data}")

            if files:
                # Send request as FormData
                response = requests.post(
                    url,
                    data=form_data,
                    files={key: (f.filename, f.read(), f.content_type) for key, f in files.items()}
                )
            else:
                # Send as form-data
                response = requests.post(url, data=form_data)

            # Log activity
            log = ActivityLog.query.filter_by(
                user_id=user.user_id,
                logout_time=None
            ).order_by(ActivityLog.login_time.desc()).first()

            if log:
                # Add more details to activity record
                activity_description = f'student_auth: {service.name}'

                # Log verified student info
                if 'name' in form_data and 'id' in form_data:
                    activity_description += f" - Student: {form_data['name']} (ID: {form_data['id']})"

                log.service_accessed = activity_description
                log.provider_organization_id = service.organization_id
                db.session.commit()

            if response.status_code == 200:
                try:
                    api_result = response.json()

                    # Format conversion
                    if 'status' in api_result and api_result['status'] == 'y':
                        result = {
                            'status': 'success',
                            'message': 'Student identity verification successful',
                            'student_name': form_data.get('name', ''),
                            'student_id': form_data.get('id', '')
                        }
                    else:
                        result = {
                            'status': 'fail',
                            'message': 'Student identity verification failed',
                            'student_name': form_data.get('name', ''),
                            'student_id': form_data.get('id', '')
                        }

                    # Add more context to result
                    if 'name' in form_data:
                        result['student_name'] = form_data['name']
                    if 'id' in form_data:
                        result['student_id'] = form_data['id']
                    if 'photo' in files:
                        result['photo_uploaded'] = True
                        result['photo_name'] = files['photo'].filename

                    return render_template('consumer/student_auth_result.html',
                                           service=service,
                                           provider_organization=provider_organization,
                                           result=result)
                except Exception as e:
                    result = {'error': f'Invalid response format: {str(e)}',
                              'status': 'fail',
                              'student_name': form_data.get('name', ''),
                              'student_id': form_data.get('id', '')}
                    return render_template('consumer/student_auth_result.html',
                                           service=service,
                                           provider_organization=provider_organization,
                                           result=result)
            else:
                result = {'error': f'Request failed: HTTP {response.status_code}',
                          'status': 'fail',
                          'student_name': form_data.get('name', ''),
                          'student_id': form_data.get('id', '')}
                if response.text:
                    try:
                        error_json = response.json()
                        result['details'] = error_json
                    except:
                        result['details'] = response.text

                return render_template('consumer/student_auth_result.html',
                                       service=service,
                                       provider_organization=provider_organization,
                                       result=result)
        except Exception as e:
            result = {'error': f'Request error: {str(e)}',
                      'status': 'fail',
                      'student_name': form_data.get('name', ''),
                      'student_id': form_data.get('id', '')}
            return render_template('consumer/student_auth_result.html',
                                   service=service,
                                   provider_organization=provider_organization,
                                   result=result)

    # Get API input format
    input_fields = api_config.input if api_config else {}

    # Get available student list (for development/testing environment only)
    available_students = []
    try:
        # Use only in development/testing mode
        student_list_url = f"{api_config.base_url.rstrip('/')}/hw/students/list"
        student_response = requests.get(student_list_url)
        if student_response.status_code == 200:
            available_students = student_response.json()
    except:
        # If failed, ignore error, keep list empty
        pass

    return render_template('consumer/student_auth.html',
                           service=service,
                           provider_organization=provider_organization,
                           input_fields=input_fields,
                           available_students=available_students)


@consumer_bp.route('/student_auth_after_payment/<int:service_id>', methods=['GET'])
def student_auth_after_payment(service_id):
    """Handle single authentication request after payment"""
    if not session.get('user_id'):
        flash('Please log in first', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.get(session.get('user_id'))
    service = Service.query.get_or_404(service_id)
    provider_organization = Organization.query.get(service.organization_id)
    api_config = APIConfig.query.filter_by(service_id=service_id, is_active=True).first()

    # Get request parameters
    form_data = {}
    for key, value in request.args.items():
        if key not in ['csrf_token']:
            form_data[key] = value

    # If parameters are empty, try to get from session
    if not form_data and session.get('pending_auth_form_data'):
        form_data = session.get('pending_auth_form_data')
        session.pop('pending_auth_form_data', None)

    if not form_data:
        flash('Authentication data lost, please re-enter', 'danger')
        return redirect(url_for('consumer.student_auth', service_id=service_id))

    # Get file info
    files = {}
    if session.get('pending_auth_files'):
        file_info = session.get('pending_auth_files')
        for key, info in file_info.items():
            if os.path.exists(info['path']):
                with open(info['path'], 'rb') as f:
                    files[key] = (info['filename'], f.read(), 'application/octet-stream')

        # Clear file info from session
        session.pop('pending_auth_files', None)

    # Call API for authentication
    try:
        url = f"{api_config.base_url.rstrip('/')}/hw/student/authenticate"
        print(f"API endpoint used after payment: {url}")
        print(f"Request data: {form_data}")

        # Choose request method based on whether files exist
        if files:
            response = requests.post(url, data=form_data, files=files)
        else:
            response = requests.post(url, data=form_data)

        # Log activity
        log = ActivityLog.query.filter_by(
            user_id=user.user_id,
            logout_time=None
        ).order_by(ActivityLog.login_time.desc()).first()

        if log:
            activity_description = f'student_auth: {service.name}'
            if 'name' in form_data and 'id' in form_data:
                activity_description += f" - Student: {form_data['name']} (ID: {form_data['id']})"
            log.service_accessed = activity_description
            log.provider_organization_id = service.organization_id
            db.session.commit()

        # Mark payment record as used
        payment = Payment.query.filter_by(
            user_id=user.user_id,
            organization_id=user.organization_id,
            receiver_organization_id=service.organization_id,
            service_id=service.service_id,
            status='completed',
            payment_type='student_identity'
        ).order_by(Payment.completed_at.desc()).first()

        if payment:
            payment.status = 'used'
            db.session.commit()
            print(f"Marked payment record {payment.payment_id} as used")

        # Process response
        if response.status_code == 200:
            try:
                api_result = response.json()
                print(f"API response: {api_result}")

                # Convert API response format
                if 'status' in api_result and api_result['status'] == 'y':
                    result = {
                        'status': 'success',
                        'message': 'Student identity verification succeeded',
                        'student_name': form_data.get('name', ''),
                        'student_id': form_data.get('id', '')
                    }
                else:
                    result = {
                        'status': 'fail',
                        'message': 'Student identity verification failed',
                        'student_name': form_data.get('name', ''),
                        'student_id': form_data.get('id', '')
                    }

                # Add file info
                if files:
                    for key in files:
                        if key == 'photo':
                            result['photo_uploaded'] = True
                            result['photo_name'] = files[key][0]  # filename

                return render_template('consumer/student_auth_result.html',
                                       service=service,
                                       provider_organization=provider_organization,
                                       result=result)
            except Exception as e:
                print(f"JSON parsing error: {str(e)}")
                result = {
                    'error': f'Invalid response format: {str(e)}',
                    'status': 'fail',
                    'student_name': form_data.get('name', ''),
                    'student_id': form_data.get('id', '')
                }
                return render_template('consumer/student_auth_result.html',
                                       service=service,
                                       provider_organization=provider_organization,
                                       result=result)
        else:
            print(f"API request failed: HTTP {response.status_code}, {response.text}")
            result = {
                'error': f'Request failed: HTTP {response.status_code}',
                'status': 'fail',
                'student_name': form_data.get('name', ''),
                'student_id': form_data.get('id', '')
            }
            return render_template('consumer/student_auth_result.html',
                                   service=service,
                                   provider_organization=provider_organization,
                                   result=result)
    except Exception as e:
        print(f"Request exception: {str(e)}")
        result = {
            'error': f'Request error: {str(e)}',
            'status': 'fail',
            'student_name': form_data.get('name', ''),
            'student_id': form_data.get('id', '')
        }
        return render_template('consumer/student_auth_result.html',
                               service=service,
                               provider_organization=provider_organization,
                               result=result)


@consumer_bp.route('/student_auth_result/<int:service_id>', methods=['GET'])
def student_auth_result(service_id):
    # Get form data
    form_data = {}
    if session.get('pending_auth_form_data'):
        form_data = session.get('pending_auth_form_data')
        session.pop('pending_auth_form_data', None)
    else:
        for key, value in request.args.items():
            if key not in ['csrf_token']:
                form_data[key] = value

    print(f"Student identity verification result request parameters: {form_data}")

    # Get service and API config
    service = Service.query.get_or_404(service_id)
    api_config = APIConfig.query.filter_by(service_id=service_id, is_active=True).first()
    if not api_config:
        flash('Service configuration error', 'danger')
        return redirect(url_for('user.view_organization', org_id=service.organization_id))

    provider_organization = Organization.query.get(service.organization_id)

    # Mark related payment record as used
    user = User.query.get(session.get('user_id'))
    if user:
        payment = Payment.query.filter_by(
            user_id=user.user_id,
            organization_id=user.organization_id,
            receiver_organization_id=service.organization_id,
            service_id=service.service_id,
            status='completed',
            payment_type='student_identity'
        ).order_by(Payment.completed_at.desc()).first()

        if payment:
            payment.status = 'used'
            db.session.commit()
            print(f"Marked payment record {payment.payment_id} as used")

    # If there is form data, perform verification; otherwise return to form page
    if not form_data:
        # If GET request and no form data, probably direct access to result page, redirect to auth form
        return redirect(url_for('consumer.student_auth', service_id=service_id))

    # Get file info (if any)
    files = {}
    if session.get('pending_auth_files'):
        file_info = session.get('pending_auth_files')
        for key, info in file_info.items():
            if os.path.exists(info['path']):
                with open(info['path'], 'rb') as f:
                    files[key] = (info['filename'], f.read(), 'application/octet-stream')

        # Clear file info from session
        session.pop('pending_auth_files', None)

    # Construct correct URL
    url = f"{api_config.base_url.rstrip('/')}/hw/student/authenticate"
    print(f"Result page API request URL: {url}")
    print(f"API request data: {form_data}")

    # Call API
    try:
        # Choose request method based on whether files exist
        if files:
            response = requests.post(url, data=form_data, files=files)
        else:
            response = requests.post(url, data=form_data)

        print(f"API response status code: {response.status_code}")
        print(f"API response content: {response.text}")

        if response.status_code == 200:
            try:
                api_result = response.json()
                print(f"Parsed JSON result: {api_result}")

                # Key part: check API response format and convert to expected template format
                if 'status' in api_result and api_result['status'] == 'y':
                    result = {
                        'status': 'success',
                        'message': 'Student identity verification succeeded',
                        'student_name': form_data.get('name', ''),
                        'student_id': form_data.get('id', '')
                    }
                else:
                    result = {
                        'status': 'fail',
                        'message': 'Student identity verification failed',
                        'student_name': form_data.get('name', ''),
                        'student_id': form_data.get('id', '')
                    }

                # Add file info
                if files:
                    for key in files:
                        if key == 'photo':
                            result['photo_uploaded'] = True
                            result['photo_name'] = files[key][0]  # filename

                return render_template('consumer/student_auth_result.html',
                                       service=service,
                                       provider_organization=provider_organization,
                                       result=result)
            except Exception as e:
                print(f"JSON parsing error: {str(e)}")
                result = {
                    'error': f'Invalid response format: {str(e)}',
                    'message': f'Data processing error: {str(e)}',
                    'status': 'fail',
                    'student_name': form_data.get('name', ''),
                    'student_id': form_data.get('id', '')
                }
                return render_template('consumer/student_auth_result.html',
                                       service=service,
                                       provider_organization=provider_organization,
                                       result=result)
        else:
            print(f"API request failed: HTTP {response.status_code}")
            result = {
                'error': f'Request failed: HTTP {response.status_code}',
                'message': f'API request returned error: {response.status_code}',
                'status': 'fail',
                'student_name': form_data.get('name', ''),
                'student_id': form_data.get('id', '')
            }

            return render_template('consumer/student_auth_result.html',
                                   service=service,
                                   provider_organization=provider_organization,
                                   result=result)
    except Exception as e:
        print(f"Request exception: {str(e)}")
        result = {
            'error': f'Request error: {str(e)}',
            'message': f'Exception occurred: {str(e)}',
            'status': 'fail',
            'student_name': form_data.get('name', ''),
            'student_id': form_data.get('id', '')
        }

        return render_template('consumer/student_auth_result.html',
                               service=service,
                               provider_organization=provider_organization,
                               result=result)



# Batch Student Identity Verification Service
@consumer_bp.route('/student_auth_batch/<int:service_id>', methods=['POST'])
def student_auth_batch(service_id):
    # Clean up expired temporary files
    cleanup_temp_files()

    if not session.get('user_id'):
        flash('Please log in first', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.get(session.get('user_id'))
    if not user or user.access_level < 2:  # Requires consumer permission
        flash('Access denied, consumer permission required', 'danger')
        return redirect(url_for('main.index'))

    service = Service.query.get_or_404(service_id)
    if not service.is_configured:
        flash('Service not configured', 'danger')
        return redirect(url_for('user.view_organization', org_id=service.organization_id))

    # Check service access permission
    has_view_access = service.is_public
    if not has_view_access:
        if hasattr(service, 'view_organizations'):
            has_view_access = user.organization_id in [org.organization_id for org in service.view_organizations]
        else:
            has_view_access = user.organization_id in [org.organization_id for org in service.access_organizations]

    if not has_view_access:
        flash('No access to this service', 'danger')
        return redirect(url_for('user.view_organization', org_id=service.organization_id))

    # Get API configuration
    api_config = APIConfig.query.filter_by(service_id=service_id, is_active=True).first()
    if not api_config:
        flash('Service configuration error', 'danger')
        return redirect(url_for('user.view_organization', org_id=service.organization_id))

    # Get service provider
    provider_organization = Organization.query.get(service.organization_id)
    if service.price > 0:
        member = Member.query.filter_by(
            organization_id=user.organization_id,
            email=user.email
        ).first()

        if member and member.quota < service.price:
            flash('Your consumption quota is insufficient, please contact your organization administrator to increase the quota or use bank transfer payment', 'warning')
    # Handle payment - calculate batch processing fee
    if service.price > 0:
        # Check if file is uploaded
        if 'batch_file' not in request.files:
            flash('Please select an Excel file', 'danger')
            return redirect(url_for('consumer.student_auth', service_id=service_id))

        file = request.files['batch_file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('consumer.student_auth', service_id=service_id))

        # Read Excel file to count records and save temporary file
        try:
            import pandas as pd

            # Create temporary directory
            temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp')
            os.makedirs(temp_dir, exist_ok=True)

            # Use secure filename with user ID prefix
            secure_name = f"{user.user_id}_{secure_filename(file.filename)}"
            temp_file = os.path.join(temp_dir, secure_name)

            # Save file
            file.save(temp_file)
            print(f"Batch verification file saved at: {temp_file}")

            # Read Excel to count records
            df = pd.read_excel(temp_file)
            batch_size = len(df)

            # Calculate total fee
            total_fee = service.price * batch_size

            # Save info to session
            session['temp_batch_file'] = temp_file
            session['batch_size'] = batch_size
            print(f"Batch verification info saved to session: file={temp_file}, size={batch_size}")

            # Check if payment already made
            payment = Payment.query.filter_by(
                user_id=user.user_id,
                organization_id=user.organization_id,
                receiver_organization_id=service.organization_id,
                service_id=service.service_id,
                status='completed',
                payment_type='student_identity_batch'
            ).order_by(Payment.completed_at.desc()).first()

            if not payment:
                # Check if user has enough quota
                member = Member.query.filter_by(
                    organization_id=user.organization_id,
                    email=user.email
                ).first()

                has_quota = False
                if member and member.quota >= total_fee:
                    has_quota = True

                # Redirect to payment page
                return redirect(url_for('payment.select_payment_method',
                                        org_id=service.organization_id,
                                        amount=total_fee,
                                        payment_type='student_identity_batch',
                                        service_id=service.service_id,
                                        has_quota=has_quota,
                                        redirect_url=url_for('consumer.student_auth', service_id=service_id)))
        except Exception as e:
            flash(f'File processing failed: {str(e)}', 'danger')
            return redirect(url_for('consumer.student_auth', service_id=service_id))

    # If service is free or payment done, process batch verification
    try:
        # Get temporary file or uploaded file
        temp_file = session.get('temp_batch_file')

        if temp_file and os.path.exists(temp_file):
            # Use previously saved temporary file
            print(f"Using temporary file from session: {temp_file}")
            file_path = temp_file
        elif 'batch_file' in request.files:
            # Use newly uploaded file
            file = request.files['batch_file']
            if file.filename == '':
                flash('No file selected', 'danger')
                return redirect(url_for('consumer.student_auth', service_id=service_id))

            # Create temporary directory
            temp_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'temp')
            os.makedirs(temp_dir, exist_ok=True)

            # Save uploaded file
            file_path = os.path.join(temp_dir, f"{user.user_id}_{secure_filename(file.filename)}")
            file.save(file_path)
            print(f"Saved new uploaded file: {file_path}")
        else:
            flash('Please select an Excel file', 'danger')
            return redirect(url_for('consumer.student_auth', service_id=service_id))

        # Read Excel file
        import pandas as pd
        df = pd.read_excel(file_path)

        # Prepare result list
        results = []
        success_count = 0
        fail_count = 0

        # Specify API endpoint clearly
        url = f"{api_config.base_url.rstrip('/')}/hw/student/authenticate"
        print(f"Batch verification API endpoint: {url}")

        # Print Excel columns to help debugging
        print(f"Excel columns: {df.columns.tolist()}")

        # Call API for each row of data
        for index, row in df.iterrows():
            # Ensure data format is correct
            data = {}
            print(f"Processing row {index + 1}: {dict(row)}")

            # Flexible handling of different column name variants
            for name_variant in ['name', 'Name', 'NAME', '姓名']:
                if name_variant in row:
                    data['name'] = str(row[name_variant])
                    break

            for id_variant in ['id', 'Id', 'ID', '学号', 'student_id']:
                if id_variant in row:
                    data['id'] = str(row[id_variant])
                    break

            # Check if required fields exist
            if 'name' not in data or 'id' not in data:
                print(f"Row {index + 1} missing required fields 'name' or 'id'")
                fail_count += 1
                results.append({
                    "student_name": data.get("name", f"Unknown_Name_{index + 1}"),
                    "student_id": data.get("id", f"Unknown_ID_{index + 1}"),
                    "status": "fail",
                    "message": "Missing required fields (name or id)"
                })
                continue

            # Print request data
            print(f"Request data sent: {data}")

            # Call API - use form-data format
            try:
                response = requests.post(url, data=data)
                print(f"API response: {response.status_code}, {response.text}")

                if response.status_code == 200:
                    try:
                        result = response.json()
                        # Key modification: more accurate response result handling
                        if 'status' in result:
                            if result['status'] == 'y':
                                success_count += 1
                                processed_result = {
                                    "status": "success",
                                    "message": "Verification successful",
                                    "student_name": data.get("name", ""),
                                    "student_id": data.get("id", "")
                                }
                            else:
                                fail_count += 1
                                processed_result = {
                                    "status": "fail",
                                    "message": "Verification failed",
                                    "student_name": data.get("name", ""),
                                    "student_id": data.get("id", "")
                                }
                        else:
                            # Missing status field in response
                            fail_count += 1
                            processed_result = {
                                "status": "fail",
                                "message": "API response missing status field",
                                "student_name": data.get("name", ""),
                                "student_id": data.get("id", "")
                            }
                        results.append(processed_result)
                    except Exception as e:
                        print(f"JSON parsing error: {str(e)}")
                        fail_count += 1
                        results.append({
                            "student_name": data.get("name", ""),
                            "student_id": data.get("id", ""),
                            "status": "fail",
                            "message": f"Response data format error: {str(e)}"
                        })
                else:
                    # Handle non-200 response
                    error_message = f"API request failed: HTTP {response.status_code}"
                    try:
                        # Try to extract detailed error info from response
                        error_json = response.json()
                        if 'detail' in error_json:
                            error_message = f"{error_message} - {error_json['detail']}"
                        elif 'message' in error_json:
                            error_message = f"{error_message} - {error_json['message']}"
                    except:
                        if response.text:
                            error_message = f"{error_message} - {response.text[:100]}"

                    print(f"API request failed: {error_message}")
                    fail_count += 1
                    results.append({
                        "student_name": data.get("name", ""),
                        "student_id": data.get("id", ""),
                        "status": "fail",
                        "message": error_message
                    })
            except Exception as e:
                print(f"Request exception: {str(e)}")
                fail_count += 1
                results.append({
                    "student_name": data.get("name", ""),
                    "student_id": data.get("id", ""),
                    "status": "fail",
                    "message": f"Request exception: {str(e)}"
                })

        # Log activity
        log = ActivityLog.query.filter_by(
            user_id=user.user_id,
            logout_time=None
        ).order_by(ActivityLog.login_time.desc()).first()

        if log:
            log.service_accessed = f'student_auth_batch: {service.name} - batch verification {len(df)} records'
            log.provider_organization_id = service.organization_id
            db.session.commit()
        if service.price > 0:
            member = Member.query.filter_by(
                organization_id=user.organization_id,
                email=user.email
            ).first()

            if member and member.quota < service.price:
                flash('Your consumption quota is insufficient, please contact your organization administrator to increase the quota or use bank transfer payment', 'warning')
        # Mark any related payment records as used
        if service.price > 0:
            payment = Payment.query.filter_by(
                user_id=user.user_id,
                organization_id=user.organization_id,
                receiver_organization_id=service.organization_id,
                service_id=service.service_id,
                status='completed',
                payment_type='student_identity_batch'
            ).order_by(Payment.completed_at.desc()).first()

            if payment:
                payment.status = 'used'
                db.session.commit()
                print(f"Marked batch verification payment record {payment.payment_id} as used")

        # Clean up temporary files and session data
        try:
            # Delete temporary file
            if os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted temporary file: {file_path}")
        except Exception as e:
            print(f"Failed to delete temporary file: {str(e)}")

        # Clear session data
        session.pop('temp_batch_file', None)
        session.pop('batch_size', None)
        session.pop('pending_auth_form_data', None)

        # Return batch verification results
        return render_template('consumer/student_auth_batch_result.html',
                               service=service,
                               provider_organization=provider_organization,
                               results=results,
                               total=len(df),
                               success_count=success_count,
                               fail_count=fail_count)

    except Exception as e:
        # Clear session data to avoid leftover data
        if 'pending_auth_form_data' in session:
            session.pop('pending_auth_form_data', None)
        if 'pending_auth_files' in session:
            session.pop('pending_auth_files', None)
        if 'temp_batch_file' in session:
            session.pop('temp_batch_file', None)
        if 'batch_size' in session:
            session.pop('batch_size', None)

        flash(f'Batch processing failed: {str(e)}', 'danger')
        return redirect(url_for('consumer.student_auth', service_id=service_id))


@consumer_bp.route('/process_batch_after_payment/<int:service_id>', methods=['GET'])
def process_batch_after_payment(service_id):
    """Handle batch verification request after payment"""
    if not session.get('user_id'):
        flash('Please log in first', 'danger')
        return redirect(url_for('auth.login'))

    # Get temporary file path
    temp_file = request.args.get('temp_file')
    if not temp_file or not os.path.exists(temp_file):
        temp_file = session.get('temp_batch_file')
        if not temp_file or not os.path.exists(temp_file):
            flash('Temporary file does not exist or has expired, please upload again', 'danger')
            return redirect(url_for('consumer.student_auth', service_id=service_id))

    user = User.query.get(session.get('user_id'))
    service = Service.query.get_or_404(service_id)
    provider_organization = Organization.query.get(service.organization_id)
    api_config = APIConfig.query.filter_by(service_id=service_id, is_active=True).first()

    try:
        # Read temporary Excel file
        import pandas as pd
        df = pd.read_excel(temp_file)

        # Prepare results list
        results = []
        success_count = 0
        fail_count = 0

        # Explicitly specify API endpoint
        url = f"{api_config.base_url.rstrip('/')}/hw/student/authenticate"
        print(f"API endpoint used for batch verification after payment: {url}")

        # Process each row of data
        for index, row in df.iterrows():
            data = {}

            # Flexible handling of column names
            for name_variant in ['name', 'Name', 'NAME', '姓名']:
                if name_variant in row:
                    data['name'] = str(row[name_variant])
                    break

            for id_variant in ['id', 'Id', 'ID', '学号', 'student_id']:
                if id_variant in row:
                    data['id'] = str(row[id_variant])
                    break

            # Check required fields
            if 'name' not in data or 'id' not in data:
                fail_count += 1
                results.append({
                    "student_name": data.get("name", f"Unknown Name_{index + 1}"),
                    "student_id": data.get("id", f"Unknown ID_{index + 1}"),
                    "status": "fail",
                    "message": "Missing required field (name or ID)"
                })
                continue

            # Call API
            try:
                response = requests.post(url, data=data)

                if response.status_code == 200:
                    try:
                        result = response.json()
                        if 'status' in result and result['status'] == 'y':
                            success_count += 1
                            processed_result = {
                                "status": "success",
                                "message": "Identity verification succeeded",
                                "student_name": data.get("name", ""),
                                "student_id": data.get("id", "")
                            }
                        else:
                            fail_count += 1
                            processed_result = {
                                "status": "fail",
                                "message": "Identity verification failed",
                                "student_name": data.get("name", ""),
                                "student_id": data.get("id", "")
                            }
                        results.append(processed_result)
                    except Exception as e:
                        fail_count += 1
                        results.append({
                            "student_name": data.get("name", ""),
                            "student_id": data.get("id", ""),
                            "status": "fail",
                            "message": f"Response data format error: {str(e)}"
                        })
                else:
                    fail_count += 1
                    results.append({
                        "student_name": data.get("name", ""),
                        "student_id": data.get("id", ""),
                        "status": "fail",
                        "message": f"API request failed: HTTP {response.status_code}"
                    })
            except Exception as e:
                fail_count += 1
                results.append({
                    "student_name": data.get("name", ""),
                    "student_id": data.get("id", ""),
                    "status": "fail",
                    "message": f"Request exception: {str(e)}"
                })

        # Log activity
        log = ActivityLog.query.filter_by(
            user_id=user.user_id,
            logout_time=None
        ).order_by(ActivityLog.login_time.desc()).first()

        if log:
            log.service_accessed = f'student_auth_batch: {service.name} - batch verification {len(df)} records'
            log.provider_organization_id = service.organization_id
            db.session.commit()

        # Mark payment record as used
        payment = Payment.query.filter_by(
            user_id=user.user_id,
            organization_id=user.organization_id,
            receiver_organization_id=service.organization_id,
            service_id=service.service_id,
            status='completed',
            payment_type='student_identity_batch'
        ).order_by(Payment.completed_at.desc()).first()

        if payment:
            payment.status = 'used'
            db.session.commit()

        # Clean up temporary file
        try:
            os.remove(temp_file)
            print(f"Temporary file deleted: {temp_file}")
        except Exception as e:
            print(f"Failed to delete temporary file: {str(e)}")

        # Clear session data
        session.pop('temp_batch_file', None)
        session.pop('batch_size', None)

        # Return results
        return render_template('consumer/student_auth_batch_result.html',
                               service=service,
                               provider_organization=provider_organization,
                               results=results,
                               total=len(df),
                               success_count=success_count,
                               fail_count=fail_count)

    except Exception as e:
        # Clear session data
        session.pop('temp_batch_file', None)
        session.pop('batch_size', None)

        flash(f'Batch processing failed: {str(e)}', 'danger')
        return redirect(url_for('consumer.student_auth', service_id=service_id))

# Student Record Query Service - New Function
@consumer_bp.route('/student_record/<int:service_id>', methods=['GET', 'POST'])
def student_record(service_id):
    if not session.get('user_id'):
        flash('Please log in first', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.get(session.get('user_id'))
    if not user or user.access_level < 2:  # Requires consumer permission
        flash('Access denied, private data consumption permission required', 'danger')
        return redirect(url_for('main.index'))

    service = Service.query.get_or_404(service_id)
    if not service.is_configured:
        flash('Service not configured', 'danger')
        return redirect(url_for('user.view_organization', org_id=service.organization_id))

    # Check service access permission - prioritize checking view_organizations
    has_view_access = service.is_public
    if not has_view_access:
        if hasattr(service, 'view_organizations'):
            has_view_access = user.organization_id in [org.organization_id for org in service.view_organizations]
        else:
            has_view_access = user.organization_id in [org.organization_id for org in service.access_organizations]

    if not has_view_access:
        flash('No permission to access this service', 'danger')
        return redirect(url_for('user.view_organization', org_id=service.organization_id))

    # Get API configuration
    api_config = APIConfig.query.filter_by(service_id=service_id, is_active=True).first()
    if not api_config:
        flash('Service configuration error', 'danger')
        return redirect(url_for('user.view_organization', org_id=service.organization_id))

    # Get service provider organization
    provider_organization = Organization.query.get(service.organization_id)

    if request.method == 'POST':
        # Handle payment
        # In payment handling section
        if service.price > 0:
            member = Member.query.filter_by(
                organization_id=user.organization_id,
                email=user.email
            ).first()
            if service.type== thesis_download:
                if member and member.quota < service.price:
                    flash('Your consumption quota is insufficient, please contact your organization admin to increase quota or use bank transfer payment', 'warning')
        if service.price > 0:
            # Get form data
            form_data = {}
            for key, value in request.form.items():
                if key not in ['csrf_token']:
                    form_data[key] = value

            # Each query requires new payment, do not check existing payment records
            # Directly save form data to session
            session['pending_record_form_data'] = form_data

            # Check if user has enough quota
            member = Member.query.filter_by(
                organization_id=user.organization_id,
                email=user.email
            ).first()

            has_quota = False
            if member and member.quota >= service.price:
                # Allow user to choose quota payment
                has_quota = True

            # Redirect to payment page
            return redirect(url_for('payment.select_payment_method',
                                    org_id=service.organization_id,
                                    amount=service.price,
                                    payment_type='student_record',
                                    service_id=service.service_id,
                                    has_quota=has_quota,
                                    redirect_url=url_for('consumer.process_record_batch_after_payment', service_id=service_id)))

        # Get form data
        form_data = {}
        for key, value in request.form.items():
            if key not in ['csrf_token']:
                form_data[key] = value

        # Call API
        try:
            url = f"{api_config.base_url.rstrip('/')}/{api_config.path.lstrip('/')}"

            # Use json
            if api_config.method.upper() == 'GET':
                response = requests.get(url, params=form_data)
            else:
                response = requests.post(url, json=form_data)

            # Log activity
            log = ActivityLog.query.filter_by(
                user_id=user.user_id,
                logout_time=None
            ).order_by(ActivityLog.login_time.desc()).first()

            if log:
                # Add more details to activity record
                activity_description = f'student_record: {service.name}'

                # Log queried student info
                if 'name' in form_data and 'id' in form_data:
                    activity_description += f" - Student: {form_data['name']} (ID: {form_data['id']})"

                log.service_accessed = activity_description
                log.provider_organization_id = service.organization_id
                db.session.commit()

            if response.status_code == 200:
                try:
                    result = response.json()

                    # Add more context to result for displaying on result page
                    if 'name' in form_data:
                        result['student_name'] = form_data['name']
                    if 'id' in form_data:
                        result['student_id'] = form_data['id']

                    return render_template('consumer/student_record_result.html',
                                           service=service,
                                           provider_organization=provider_organization,
                                           result=result)
                except Exception as e:
                    result = {'error': f'Return data format error: {str(e)}'}
                    return render_template('consumer/student_record_result.html',
                                           service=service,
                                           provider_organization=provider_organization,
                                           result=result)
                else:
                    # Set different error messages based on status code
                    error_message = ""
                    if response.status_code == 404:
                        error_message = "Student not found"
                    else:
                        error_message = f"Request failed: HTTP {response.status_code}"

                    result = {'error': error_message}

                    if response.text:
                        try:
                            error_json = response.json()
                            result['details'] = error_json
                        except:
                            result['details'] = response.text

                    return render_template('consumer/student_record_result.html',
                                           service=service,
                                           provider_organization=provider_organization,
                                           result=result)
        except Exception as e:
            result = {'error': f'Request error: {str(e)}'}
            return render_template('consumer/student_record_result.html',
                                   service=service,
                                   provider_organization=provider_organization,
                                   result=result)

    # Get API input format
    input_fields = api_config.input if api_config else {}

    # Get available student list (only for dev/testing)
    available_students = []
    try:
        # Use only in development mode for testing
        student_list_url = f"{api_config.base_url.rstrip('/')}/hw/students/list"
        student_response = requests.get(student_list_url)
        if student_response.status_code == 200:
            available_students = student_response.json()
    except:
        # Ignore errors if failed, keep list empty
        pass

    return render_template('consumer/student_record.html',
                           service=service,
                           provider_organization=provider_organization,
                           input_fields=input_fields,
                           available_students=available_students)


@consumer_bp.route('/student_record_result/<int:service_id>', methods=['GET'])
def student_record_result(service_id):
    """Handle the student record query result after payment"""
    if not session.get('user_id'):
        flash('Please log in first', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.get(session.get('user_id'))
    if not user or user.access_level < 2:  # Requires consumer permission
        flash('Access denied, consumer permission required', 'danger')
        return redirect(url_for('main.index'))

    service = Service.query.get_or_404(service_id)
    provider_organization = Organization.query.get(service.organization_id)
    api_config = APIConfig.query.filter_by(service_id=service_id, is_active=True).first()

    # Get query parameters
    form_data = {}
    for key, value in request.args.items():
        if key not in ['csrf_token']:
            form_data[key] = value

    # If request parameters are empty, try to get from session
    if not form_data and session.get('pending_record_form_data'):
        form_data = session.get('pending_record_form_data', {})
        # Clear session data after use
        session.pop('pending_record_form_data', None)

    if not form_data:
        flash('Query parameters lost, please try again', 'danger')
        return redirect(url_for('consumer.student_record', service_id=service_id))

    # Key change: Check if this query has been paid for
    # Find the most recent completed but unused payment record
    payment = Payment.query.filter_by(
        user_id=user.user_id,
        organization_id=user.organization_id,
        receiver_organization_id=service.organization_id,
        service_id=service.service_id,
        status='completed',  # Payment completed
        payment_type='student_record'
    ).order_by(Payment.completed_at.desc()).first()

    # If no valid payment record found or payment already used
    if not payment or payment.status == 'used':
        # Save query parameters to session
        session['pending_record_form_data'] = form_data

        # Prompt user to pay and redirect to query page
        flash('Payment is required for each query', 'warning')
        return redirect(url_for('consumer.student_record', service_id=service_id))

    # Mark payment record as used to prevent reuse
    payment.status = 'used'
    db.session.commit()

    # Call the API
    try:
        url = f"{api_config.base_url.rstrip('/')}/{api_config.path.lstrip('/')}"

        # Use the method specified in API config
        if api_config.method.upper() == 'GET':
            response = requests.get(url, params=form_data)
        else:
            response = requests.post(url, json=form_data)

        # Log activity
        log = ActivityLog.query.filter_by(
            user_id=user.user_id,
            logout_time=None
        ).order_by(ActivityLog.login_time.desc()).first()

        if log:
            # Add detailed info to activity log
            activity_description = f'student_record_result: {service.name}'
            if 'name' in form_data and 'id' in form_data:
                activity_description += f" - Student: {form_data['name']} (ID: {form_data['id']})"
            log.service_accessed = activity_description
            log.provider_organization_id = service.organization_id
            db.session.commit()

        # Handle API response
        if response.status_code == 200:
            try:
                result = response.json()

                # Add more context for displaying on result page
                if 'name' in form_data:
                    result['student_name'] = form_data['name']
                if 'id' in form_data:
                    result['student_id'] = form_data['id']

                return render_template('consumer/student_record_result.html',
                                       service=service,
                                       provider_organization=provider_organization,
                                       result=result)
            except Exception as e:
                result = {'error': f'Response data format error: {str(e)}'}
                return render_template('consumer/student_record_result.html',
                                       service=service,
                                       provider_organization=provider_organization,
                                       result=result)
        else:
            error_message = ""
            if response.status_code == 404:
                error_message = "Student information not found"
            elif response.status_code == 400:
                error_message = "Bad request parameters"
            else:
                error_message = f"Request failed: HTTP {response.status_code}"

            result = {'error': error_message}

            if response.text:
                try:
                    error_json = response.json()
                    result['details'] = error_json
                except:
                    result['details'] = response.text

            return render_template('consumer/student_record_result.html',
                                   service=service,
                                   provider_organization=provider_organization,
                                   result=result)
    except Exception as e:
        result = {'error': f'Request error: {str(e)}'}
        return render_template('consumer/student_record_result.html',
                               service=service,
                               provider_organization=provider_organization,
                               result=result)

@consumer_bp.route('/process_record_batch_after_payment/<int:service_id>', methods=['GET'])
def process_record_batch_after_payment(service_id):
    """Handle batch student record query requests after payment"""
    if not session.get('user_id'):
        flash('Please log in first', 'danger')
        return redirect(url_for('auth.login'))

    # Get temporary file path
    temp_file = request.args.get('temp_file')
    if not temp_file or not os.path.exists(temp_file):
        temp_file = session.get('temp_batch_file')
        if not temp_file or not os.path.exists(temp_file):
            flash('Temporary file does not exist or has expired, please re-upload', 'danger')
            return redirect(url_for('consumer.student_record', service_id=service_id))

    user = User.query.get(session.get('user_id'))
    service = Service.query.get_or_404(service_id)
    provider_organization = Organization.query.get(service.organization_id)
    api_config = APIConfig.query.filter_by(service_id=service_id, is_active=True).first()

    try:
        # Read Excel file
        import pandas as pd
        df = pd.read_excel(temp_file)

        # Prepare result list
        results = []
        success_count = 0
        fail_count = 0

        # Call API for each row
        url = f"{api_config.base_url.rstrip('/')}/{api_config.path.lstrip('/')}"
        for index, row in df.iterrows():
            data = {}
            for key in api_config.input.keys():
                data[key] = str(row.get(key, '')) if key in row else ''

            # Call API
            if api_config.method.upper() == 'GET':
                response = requests.get(url, params=data)
            else:
                response = requests.post(url, json=data)

            if response.status_code == 200:
                try:
                    result = response.json()
                    success_count += 1

                    # Add source data to result
                    if 'name' not in result and 'name' in data:
                        result['name'] = data['name']
                    if 'student_id' not in result and 'id' in data:
                        result['student_id'] = data['id']

                    results.append(result)
                except Exception as e:
                    fail_count += 1
                    results.append({
                        "name": data.get("name", ""),
                        "student_id": data.get("id", ""),
                        "error": f"Response data format error: {str(e)}"
                    })
            else:
                # Set different error messages according to status code
                fail_count += 1
                error_message = ""
                if response.status_code == 404:
                    error_message = "Student information not found"
                else:
                    error_message = f"Request failed: HTTP {response.status_code}"

                results.append({
                    "name": data.get("name", ""),
                    "student_id": data.get("id", ""),
                    "error": error_message
                })
                fail_count += 1

        # Log activity
        log = ActivityLog.query.filter_by(
            user_id=user.user_id,
            logout_time=None
        ).order_by(ActivityLog.login_time.desc()).first()

        if log:
            log.service_accessed = f'student_record_batch: {service.name} - batch query of {len(df)} records'
            log.provider_organization_id = service.organization_id
            db.session.commit()

        # Mark payment record as used
        payment = Payment.query.filter_by(
            user_id=user.user_id,
            organization_id=user.organization_id,
            receiver_organization_id=service.organization_id,
            service_id=service.service_id,
            status='completed',
            payment_type='student_record_batch'
        ).order_by(Payment.completed_at.desc()).first()

        if payment:
            payment.status = 'used'
            db.session.commit()

        # Clean up temporary file
        try:
            os.remove(temp_file)
            print(f"Deleted temporary file: {temp_file}")
        except Exception as e:
            print(f"Failed to delete temporary file: {str(e)}")

        # Clear session data
        session.pop('temp_batch_file', None)
        session.pop('batch_size', None)

        # Return batch query results
        return render_template('consumer/student_record_batch_result.html',
                               service=service,
                               provider_organization=provider_organization,
                               results=results,
                               total=len(df),
                               success_count=success_count,
                               fail_count=fail_count)

    except Exception as e:
        # Clear session data
        session.pop('temp_batch_file', None)
        session.pop('batch_size', None)

        flash(f'Batch processing failed: {str(e)}', 'danger')
        return redirect(url_for('consumer.student_record', service_id=service_id))

# Batch Student Record Query Service
@consumer_bp.route('/student_record_batch/<int:service_id>', methods=['POST'])
def student_record_batch(service_id):
    if not session.get('user_id'):
        flash('Please log in first', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.get(session.get('user_id'))
    if not user or user.access_level < 2:  # Requires consumer permission
        flash('Access denied, requires private data consumer permission', 'danger')
        return redirect(url_for('main.index'))

    service = Service.query.get_or_404(service_id)
    if not service.is_configured:
        flash('Service not configured', 'danger')
        return redirect(url_for('user.view_organization', org_id=service.organization_id))

    # Check service access permission
    has_view_access = service.is_public
    if not has_view_access:
        if hasattr(service, 'view_organizations'):
            has_view_access = user.organization_id in [org.organization_id for org in service.view_organizations]
        else:
            has_view_access = user.organization_id in [org.organization_id for org in service.access_organizations]

    if not has_view_access:
        flash('No access to this service', 'danger')
        return redirect(url_for('user.view_organization', org_id=service.organization_id))

    # Get API configuration
    api_config = APIConfig.query.filter_by(service_id=service_id, is_active=True).first()
    if not api_config:
        flash('Service configuration error', 'danger')
        return redirect(url_for('user.view_organization', org_id=service.organization_id))

    # Get service provider
    provider_organization = Organization.query.get(service.organization_id)

    # Handle payment - calculate batch processing fee
    if service.price > 0:
        # Check if file is uploaded
        if 'batch_file' not in request.files:
            flash('Please select an Excel file', 'danger')
            return redirect(url_for('consumer.student_record', service_id=service_id))

        file = request.files['batch_file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('consumer.student_record', service_id=service_id))

        # Read Excel file to calculate record count
        try:
            import pandas as pd
            from io import BytesIO  # Correct import of BytesIO

            # Read file content
            file_content = file.read()
            df = pd.read_excel(BytesIO(file_content))
            batch_size = len(df)

            # Calculate total fee
            total_fee = service.price * batch_size

            # Key modification here: no longer check existing payment records
            # Directly save file to temporary directory
            from flask import current_app
            import os
            from werkzeug.utils import secure_filename

            temp_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], 'temp')
            os.makedirs(temp_dir, exist_ok=True)
            temp_file = os.path.join(temp_dir, secure_filename(file.filename))

            # Save file content
            with open(temp_file, 'wb') as f:
                f.write(file_content)

            # Save temporary file path to session
            session['temp_batch_file'] = temp_file
            session['batch_size'] = batch_size

            # Check if user has enough quota
            member = Member.query.filter_by(
                organization_id=user.organization_id,
                email=user.email
            ).first()

            has_quota = False
            if member and member.quota >= total_fee:
                has_quota = True

            # Redirect to payment page
            return redirect(url_for('payment.select_payment_method',
                                    org_id=service.organization_id,
                                    amount=total_fee,
                                    payment_type='student_record_batch',
                                    service_id=service.service_id,
                                    has_quota=has_quota,
                                    redirect_url=url_for('consumer.student_record', service_id=service_id)))


        except Exception as e:
            import traceback
            print(f"Batch processing error: {str(e)}")
            print(traceback.format_exc())  # Print full stack trace
            flash(f'File processing failed: {str(e)}', 'danger')
            return redirect(url_for('consumer.student_record', service_id=service_id))

    # If service is free or payment already made, process batch query
    try:
        # Get uploaded Excel file
        if 'batch_file' not in request.files:
            flash('Please select an Excel file', 'danger')
            return redirect(url_for('consumer.student_record', service_id=service_id))

        file = request.files['batch_file']
        if file.filename == '':
            flash('No file selected', 'danger')
            return redirect(url_for('consumer.student_record', service_id=service_id))

        # Read Excel file
        import pandas as pd
        df = pd.read_excel(file)

        # Prepare result list
        results = []
        success_count = 0
        fail_count = 0

        # Call API to process each row
        url = f"{api_config.base_url.rstrip('/')}/{api_config.path.lstrip('/')}"
        for index, row in df.iterrows():
            data = {}
            for key in api_config.input.keys():
                data[key] = str(row.get(key, '')) if key in row else ''

            # Call API
            if api_config.method.upper() == 'GET':
                response = requests.get(url, params=data)
            else:
                response = requests.post(url, json=data)

            if response.status_code == 200:
                try:
                    result = response.json()
                    success_count += 1

                    # Add source data to result
                    if 'name' not in result and 'name' in data:
                        result['name'] = data['name']
                    if 'student_id' not in result and 'id' in data:
                        result['student_id'] = data['id']

                    results.append(result)
                except Exception as e:
                    results.append({
                        "name": data.get("name", ""),
                        "student_id": data.get("id", ""),
                        "error": f"Response data format error: {str(e)}"
                    })
                    fail_count += 1
            else:
                # Set different error messages based on status code
                error_message = ""
                if response.status_code == 404:
                    error_message = "Student information not found"
                else:
                    error_message = f"Request failed: HTTP {response.status_code}"

                results.append({
                    "name": data.get("name", ""),
                    "student_id": data.get("id", ""),
                    "error": error_message
                })
                fail_count += 1

        # Log activity
        log = ActivityLog.query.filter_by(
            user_id=user.user_id,
            logout_time=None
        ).order_by(ActivityLog.login_time.desc()).first()

        if log:
            log.service_accessed = f'student_record_batch: {service.name} - batch query of {len(df)} records'
            log.provider_organization_id = service.organization_id
            db.session.commit()

        # Return batch query results
        return render_template('consumer/student_record_batch_result.html',
                               service=service,
                               provider_organization=provider_organization,
                               results=results,
                               total=len(df),
                               success_count=success_count,
                               fail_count=fail_count)

    except Exception as e:
        flash(f'Batch processing failed: {str(e)}', 'danger')
        return redirect(url_for('consumer.student_record', service_id=service_id))
