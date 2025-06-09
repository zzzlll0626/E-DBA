from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from app.models import db, Service, APIConfig, Course, Organization, User
import requests
import json
import datetime

provider_bp = Blueprint('provider', __name__)

from flask import Blueprint, render_template, redirect, url_for, request, flash, session, jsonify
from app.models import db, Service, APIConfig, Course, Organization, User
import requests
import json
import datetime

provider_bp = Blueprint('provider', __name__)


@provider_bp.route('/configure_api/<int:service_id>', methods=['GET'])
def configure_api(service_id):
    if not session.get('user_id'):
        flash('Please login first', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.get(session.get('user_id'))
    if not user or user.access_level < 3:  # Provider permission required
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    service = Service.query.get_or_404(service_id)
    if service.organization_id != user.organization_id:
        flash('No permission to configure this service', 'danger')
        return redirect(url_for('main.index'))

    # Get all configurations for this service
    configs = APIConfig.query.filter_by(service_id=service_id).all()

    return render_template('provider/api_configs.html', service=service, configs=configs)


@provider_bp.route('/configure_api/<int:service_id>/add', methods=['GET', 'POST'])
def add_api_config(service_id):
    if not session.get('user_id'):
        flash('Please login first', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.get(session.get('user_id'))
    if not user or user.access_level < 3:  # Provider permission required
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    service = Service.query.get_or_404(service_id)
    if service.organization_id != user.organization_id:
        flash('No permission to configure this service', 'danger')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        config_name = request.form.get('config_name')
        base_url = request.form.get('base_url')
        path = request.form.get('path')
        method = request.form.get('method')
        input_format = request.form.get('input_format')
        output_format = request.form.get('output_format')
        is_active = 'is_active' in request.form

        try:
            input_json = json.loads(input_format)
            output_json = json.loads(output_format)
        except json.JSONDecodeError:
            flash('Input or output format is not valid JSON', 'danger')
            return redirect(url_for('provider.add_api_config', service_id=service_id))

        # Create new configuration
        config = APIConfig(
            service_id=service_id,
            config_name=config_name,
            base_url=base_url,
            path=path,
            method=method,
            input=input_json,
            output=output_json,
            is_active=is_active
        )
        db.session.add(config)

        # If this is the first configuration, update service status to configured
        if not service.is_configured:
            service.is_configured = True

        db.session.commit()
        flash('API configuration successfully added', 'success')
        return redirect(url_for('provider.configure_api', service_id=service_id))

    return render_template('provider/add_edit_config.html', service=service, config=None)


@provider_bp.route('/configure_api/<int:service_id>/edit/<int:config_id>', methods=['GET', 'POST'])
def edit_api_config(service_id, config_id):
    if not session.get('user_id'):
        flash('Please login first', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.get(session.get('user_id'))
    if not user or user.access_level < 3:  # Provider permission required
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    service = Service.query.get_or_404(service_id)
    if service.organization_id != user.organization_id:
        flash('No permission to configure this service', 'danger')
        return redirect(url_for('main.index'))

    config = APIConfig.query.get_or_404(config_id)
    if config.service_id != service_id:
        flash('Configuration does not match service', 'danger')
        return redirect(url_for('provider.configure_api', service_id=service_id))

    if request.method == 'POST':
        config_name = request.form.get('config_name')
        base_url = request.form.get('base_url')
        path = request.form.get('path')
        method = request.form.get('method')
        input_format = request.form.get('input_format')
        output_format = request.form.get('output_format')
        is_active = 'is_active' in request.form

        try:
            input_json = json.loads(input_format)
            output_json = json.loads(output_format)
        except json.JSONDecodeError:
            flash('Input or output format is not valid JSON', 'danger')
            return redirect(url_for('provider.edit_api_config', service_id=service_id, config_id=config_id))

        # Update configuration
        config.config_name = config_name
        config.base_url = base_url
        config.path = path
        config.method = method
        config.input = input_json
        config.output = output_json
        config.is_active = is_active
        config.updated_at = datetime.datetime.utcnow()

        db.session.commit()
        flash('API configuration has been updated', 'success')
        return redirect(url_for('provider.configure_api', service_id=service_id))

    return render_template('provider/add_edit_config.html', service=service, config=config)


@provider_bp.route('/configure_api/<int:service_id>/delete/<int:config_id>', methods=['POST'])
def delete_api_config(service_id, config_id):
    if not session.get('user_id'):
        flash('Please login first', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.get(session.get('user_id'))
    if not user or user.access_level < 3:  # Provider permission required
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    service = Service.query.get_or_404(service_id)
    if service.organization_id != user.organization_id:
        flash('No permission to delete this service configuration', 'danger')
        return redirect(url_for('main.index'))

    config = APIConfig.query.get_or_404(config_id)
    if config.service_id != service_id:
        flash('Configuration does not match service', 'danger')
        return redirect(url_for('provider.configure_api', service_id=service_id))

    db.session.delete(config)

    # Check if there are other configurations, if not, update service status to unconfigured
    remaining_configs = APIConfig.query.filter_by(service_id=service_id).count()
    if remaining_configs == 0:
        service.is_configured = False

    db.session.commit()
    flash('API configuration has been deleted', 'success')
    return redirect(url_for('provider.configure_api', service_id=service_id))


@provider_bp.route('/test_api', methods=['POST'])
def test_api():
    if not session.get('user_id'):
        return jsonify({'success': False, 'message': 'Please login first'})

    data = request.json
    base_url = data.get('base_url')
    path = data.get('path')
    method = data.get('method')
    test_data = data.get('data')

    if not all([base_url, path, method, test_data]):
        return jsonify({'success': False, 'message': 'Missing required parameters'})

    try:
        url = f"{base_url.rstrip('/')}/{path.lstrip('/')}"

        if method.upper() == 'GET':
            response = requests.get(url, params=test_data)
        else:  # POST
            response = requests.post(url, json=test_data)

        if response.status_code == 200:
            try:
                result = response.json()
                return jsonify({'success': True, 'result': result})
            except:
                return jsonify({'success': True, 'result': response.text})
        else:
            return jsonify({
                'success': False,
                'message': f'Request failed: HTTP {response.status_code} - {response.text}'
            })
    except Exception as e:
        return jsonify({'success': False, 'message': f'Request error: {str(e)}'})




@provider_bp.route('/manage_courses', methods=['GET', 'POST'])
def manage_courses():
    if not session.get('user_id'):
        flash('Please login first', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.get(session.get('user_id'))
    if not user or user.access_level < 3:  # Provider permission required
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    organization_id = user.organization_id

    if request.method == 'POST':
        action = request.form.get('action')

        if action == 'add':
            title = request.form.get('title')
            units = float(request.form.get('units'))
            description = request.form.get('description')

            course = Course(
                organization_id=organization_id,
                title=title,
                units=units,
                description=description
            )
            db.session.add(course)
            db.session.commit()
            flash('Course added successfully', 'success')

        elif action == 'edit':
            course_id = request.form.get('course_id')
            title = request.form.get('title')
            units = float(request.form.get('units'))
            description = request.form.get('description')

            course = Course.query.get_or_404(course_id)
            if course.organization_id != organization_id:
                flash('No permission to edit this course', 'danger')
                return redirect(url_for('provider.manage_courses'))

            course.title = title
            course.units = units
            course.description = description
            db.session.commit()
            flash('Course updated successfully', 'success')

        elif action == 'delete':
            course_id = request.form.get('course_id')

            course = Course.query.get_or_404(course_id)
            if course.organization_id != organization_id:
                flash('No permission to delete this course', 'danger')
                return redirect(url_for('provider.manage_courses'))

            db.session.delete(course)
            db.session.commit()
            flash('Course deleted successfully', 'success')

        elif action == 'upload':
            if 'courses_file' not in request.files:
                flash('Please select a file', 'danger')
                return redirect(url_for('provider.manage_courses'))

            file = request.files['courses_file']
            if file.filename == '':
                flash('No file selected', 'danger')
                return redirect(url_for('provider.manage_courses'))

            # Process Excel file
            try:
                import pandas as pd
                df = pd.read_excel(file)

                added = 0
                errors = 0

                for _, row in df.iterrows():
                    try:
                        title = row['title']
                        units = float(row['units'])
                        description = row.get('description', '')

                        # Check if course with same name already exists
                        existing = Course.query.filter_by(
                            organization_id=organization_id,
                            title=title
                        ).first()

                        if existing:
                            # Update existing course
                            existing.units = units
                            existing.description = description
                        else:
                            # Create new course
                            course = Course(
                                organization_id=organization_id,
                                title=title,
                                units=units,
                                description=description
                            )
                            db.session.add(course)

                        added += 1
                    except Exception as e:
                        errors += 1
                        print(f"Error processing course row: {e}")

                db.session.commit()
                flash(f'Successfully imported {added} courses. {errors} records failed to import.',
                      'success' if errors == 0 else 'warning')
            except Exception as e:
                flash(f'File processing failed: {str(e)}', 'danger')

    # Get course list
    courses = Course.query.filter_by(organization_id=organization_id).all()

    return render_template('provider/courses.html', courses=courses, user=user)


@provider_bp.route('/dashboard')
def dashboard():
    if not session.get('user_id'):
        flash('Please login first', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.get(session.get('user_id'))
    if not user or user.access_level < 3:  # Provider permission required
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    organization_id = user.organization_id
    organization = Organization.query.get_or_404(organization_id)

    return render_template('provider/dashboard.html',
                           user=user,
                           organization=organization)


@provider_bp.route('/services_to_configure')
def services_to_configure():
    if not session.get('user_id'):
        flash('Please login first', 'danger')
        return redirect(url_for('auth.login'))

    user = User.query.get(session.get('user_id'))
    if not user or user.access_level < 3:  # Provider permission required
        flash('Access denied', 'danger')
        return redirect(url_for('main.index'))

    organization_id = user.organization_id

    # Get unconfigured services
    unconfigured_services = Service.query.filter_by(
        organization_id=organization_id,
        is_configured=False
    ).all()

    # Get configured services
    configured_services = Service.query.filter_by(
        organization_id=organization_id,
        is_configured=True
    ).all()

    return render_template('provider/services_to_configure.html',
                           unconfigured_services=unconfigured_services,
                           configured_services=configured_services)