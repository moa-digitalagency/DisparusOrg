import os
from flask import render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.utils import secure_filename
from models import db, SiteSetting
from models.settings import invalidate_settings_cache, get_all_settings_dict, DEFAULT_SETTINGS
from security.rate_limit import rate_limit
from services import stats_service
from . import admin_bp, admin_required, log_activity

@admin_bp.route('/login', methods=['GET', 'POST'])
@rate_limit(max_requests=5, window=60)
def login():
    if session.get('admin_logged_in'):
        return redirect(url_for('admin.dashboard'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')

        admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
        admin_password = os.environ.get('ADMIN_PASSWORD', '')

        if not admin_password:
            try:
                log_activity(f'Tentative connexion avec ADMIN_PASSWORD vide', action_type='auth', severity='error', is_security=True)
            except: pass
            error = 'Erreur configuration: Mot de passe admin non defini'
        elif username == admin_username and password == admin_password:
            session.permanent = True  # Enable session expiration
            session['admin_logged_in'] = True
            session['admin_username'] = username
            session['admin_role'] = 'admin'

            try:
                log_activity('Connexion admin reussie', action_type='auth', severity='info', is_security=True)
            except Exception as e:
                import logging
                logging.warning(f"Could not log activity: {e}")

            return redirect(url_for('admin.dashboard'))
        else:
            try:
                log_activity(f'Tentative de connexion echouee pour: {username}', action_type='auth', severity='warning', is_security=True)
            except Exception as e:
                import logging
                logging.warning(f"Could not log activity: {e}")
            error = 'Identifiants invalides'

    return render_template('admin_login.html', error=error)


@admin_bp.route('/logout')
def logout():
    try:
        log_activity('Deconnexion admin', action_type='auth', severity='info', is_security=True)
    except Exception as e:
        import logging
        logging.warning(f"Could not log activity: {e}")
    session.pop('admin_logged_in', None)
    session.pop('admin_username', None)
    return redirect(url_for('public.index'))


@admin_bp.route('/')
@admin_required
def dashboard():
    try:
        log_activity('Consultation tableau de bord', action_type='view', target_type='dashboard')
    except Exception as e:
        import logging
        logging.warning(f"Could not log activity: {e}")

    data = stats_service.get_dashboard_stats()

    return render_template('admin.html',
                         stats=data['stats'],
                         disparus=data['recent_disparus'],
                         disparus_list=data['map_list'])


@admin_bp.route('/map')
@admin_required
def map_view():
    log_activity('Consultation carte', action_type='view', target_type='map')

    data = stats_service.get_map_data()

    return render_template('admin_map.html', disparus=data['results'], disparus_list=data['disparus_list'])


@admin_bp.route('/settings', methods=['GET', 'POST'])
@admin_required
def settings():
    if request.method == 'GET':
        log_activity('Consultation parametres', action_type='view', target_type='settings')
    if request.method == 'POST':
        import os
        from werkzeug.utils import secure_filename

        # Optimization: Fetch all settings at once to avoid N+1 queries during update
        all_settings = {s.key: s for s in SiteSetting.query.all()}

        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'ico'}
        ALLOWED_MIMETYPES = {'image/png', 'image/jpeg', 'image/gif', 'image/webp', 'image/x-icon', 'image/vnd.microsoft.icon'}

        def allowed_file(filename, file_obj):
            if '.' not in filename:
                return False
            ext = filename.rsplit('.', 1)[1].lower()
            if ext not in ALLOWED_EXTENSIONS:
                return False
            if file_obj.content_type and file_obj.content_type not in ALLOWED_MIMETYPES:
                return False
            return True

        upload_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'static', 'uploads', 'settings')
        os.makedirs(upload_folder, exist_ok=True)

        image_fields = ['og_image', 'favicon', 'logo', 'placeholder_male', 'placeholder_female', 'pwa_icon']
        for field in image_fields:
            file_key = f'upload_{field}'
            if file_key in request.files:
                file = request.files[file_key]
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    if not allowed_file(filename, file):
                        continue
                    ext = filename.rsplit('.', 1)[-1].lower()
                    new_filename = f'{field}.{ext}'
                    file_path = os.path.join(upload_folder, new_filename)
                    file.save(file_path)

                    setting_key = f'seo_{field}' if field == 'og_image' else field
                    existing = all_settings.get(setting_key)
                    value = f'/static/uploads/settings/{new_filename}'
                    if existing:
                        existing.value = value
                        existing.updated_by = session.get('admin_username')
                    else:
                        category = 'seo' if field == 'og_image' else 'pwa' if field == 'pwa_icon' else 'general'
                        new_setting = SiteSetting(
                            key=setting_key,
                            value=value,
                            value_type='string',
                            category=category,
                            updated_by=session.get('admin_username')
                        )
                        db.session.add(new_setting)
                        all_settings[setting_key] = new_setting

        # Handle unchecked checkboxes (missing from request.form)
        # We need to check both existing settings and default boolean settings
        # to ensure even missing or wrong-typed settings are handled correctly
        boolean_keys = set()

        # 1. From Defaults
        for k, v in DEFAULT_SETTINGS.items():
             if v.get('type') == 'boolean':
                 boolean_keys.add(k)

        # 2. From fetched settings
        for s in all_settings.values():
            if s.value_type == 'boolean':
                boolean_keys.add(s.key)

        for key in boolean_keys:
            form_key = f'setting_{key}'
            if form_key not in request.form:
                # Unchecked: ensure it exists and is false
                existing = all_settings.get(key)
                if existing:
                    existing.value = 'false'
                    existing.value_type = 'boolean'  # Ensure correct type
                    existing.updated_by = session.get('admin_username')
                    db.session.add(existing)
                elif key in DEFAULT_SETTINGS:
                    # Create as false if it doesn't exist but is in defaults
                    new_setting = SiteSetting(
                        key=key,
                        value='false',
                        value_type='boolean',
                        category=DEFAULT_SETTINGS[key]['category'],
                        updated_by=session.get('admin_username')
                    )
                    db.session.add(new_setting)
                    all_settings[key] = new_setting

        for key in request.form:
            if key.startswith('setting_'):
                setting_key = key[8:]
                value = request.form[key]

                if isinstance(value, str):
                    value = value.strip()

                # Convert checkbox 'on' to 'true'
                if value == 'on':
                    value = 'true'

                existing = all_settings.get(setting_key)
                if existing:
                    existing.value = value
                    existing.updated_by = session.get('admin_username')
                    db.session.add(existing)
                else:
                    category = 'pwa' if setting_key.startswith('pwa_') else 'footer' if setting_key.startswith('footer_') else 'seo' if setting_key.startswith('seo_') else 'security' if setting_key in ['enable_rate_limiting', 'rate_limit_per_minute', 'blocked_ips', 'whitelisted_ips', 'enable_ip_logging', 'max_upload_size_mb'] else 'general'
                    value_type = 'boolean' if value in ['true', 'false'] else 'text' if setting_key.endswith('_scripts') or setting_key.endswith('_description') else 'string'
                    new_setting = SiteSetting(
                        key=setting_key,
                        value=value,
                        value_type=value_type,
                        category=category,
                        updated_by=session.get('admin_username')
                    )
                    db.session.add(new_setting)
                    all_settings[setting_key] = new_setting
        log_activity(f'Modification parametres', action_type='update', target_type='settings', severity='info')
        db.session.commit()
        invalidate_settings_cache()
        flash('Parametres sauvegardes', 'success')
        return redirect(url_for('admin.settings'))

    # Use standard fetch method that returns typed values
    settings_dict = get_all_settings_dict()

    # Still need list for structure iteration if needed, but the template uses settings_dict for values
    settings_list = SiteSetting.query.order_by(SiteSetting.category, SiteSetting.key).all()
    settings_by_category = {}
    for s in settings_list:
        if s.category not in settings_by_category:
            settings_by_category[s.category] = []
        settings_by_category[s.category].append(s)

    return render_template('admin_settings.html', settings_by_category=settings_by_category, settings=settings_dict)
