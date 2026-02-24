import os
from datetime import datetime
from flask import render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.utils import secure_filename
from models import db, User, Role, Disparu, Contribution
from utils.geo import get_countries
from . import admin_bp, admin_required, log_activity

@admin_bp.route('/users')
@admin_required
def users():
    log_activity('Consultation utilisateurs', action_type='view', target_type='users')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    role_filter = request.args.get('role', '')
    search = request.args.get('search', '')

    query = User.query
    if role_filter:
        query = query.filter_by(role=role_filter)
    if search:
        query = query.filter(
            db.or_(
                User.email.ilike(f'%{search}%'),
                User.first_name.ilike(f'%{search}%'),
                User.last_name.ilike(f'%{search}%'),
                User.username.ilike(f'%{search}%')
            )
        )

    users = query.order_by(User.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    roles = Role.query.all()

    return render_template('admin_users.html',
                         users=users,
                         roles=roles,
                         role_filter=role_filter,
                         search=search)


@admin_bp.route('/users/add', methods=['GET', 'POST'])
@admin_required
def add_user():
    if request.method == 'POST':
        email = request.form.get('email')
        username = request.form.get('username')
        password = request.form.get('password')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        role = request.form.get('role', 'user')
        organization = request.form.get('organization')

        if User.query.filter_by(email=email).first():
            flash('Cet email existe deja', 'error')
            return redirect(url_for('admin.add_user'))

        user = User(
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            role=role,
            organization=organization,
            is_active=True
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        log_activity(f'Creation utilisateur', action_type='create', target_type='user', target_id=user.id, target_name=email)

        flash('Utilisateur cree avec succes', 'success')
        return redirect(url_for('admin.users'))

    roles = Role.query.all()
    return render_template('admin_user_form.html', user=None, roles=roles)


@admin_bp.route('/users/<int:user_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)

    if request.method == 'POST':
        user.email = request.form.get('email')
        user.username = request.form.get('username')
        user.first_name = request.form.get('first_name')
        user.last_name = request.form.get('last_name')
        user.role = request.form.get('role', 'user')
        user.organization = request.form.get('organization')
        user.is_active = request.form.get('is_active') == 'on'

        if request.form.get('password'):
            user.set_password(request.form.get('password'))

        log_activity(f'Modification utilisateur', action_type='update', target_type='user', target_id=user.id, target_name=user.email)
        db.session.commit()
        flash('Utilisateur mis a jour', 'success')
        return redirect(url_for('admin.users'))

    roles = Role.query.all()
    return render_template('admin_user_form.html', user=user, roles=roles)


@admin_bp.route('/users/<int:user_id>/delete', methods=['POST'])
@admin_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    log_activity(f'Suppression utilisateur', action_type='delete', target_type='user', target_id=user.id, target_name=user.email, severity='warning')
    db.session.delete(user)
    db.session.commit()
    flash('Utilisateur supprime', 'success')
    return redirect(url_for('admin.users'))


@admin_bp.route('/roles')
@admin_required
def roles():
    log_activity('Consultation roles', action_type='view', target_type='roles')
    roles = Role.query.order_by(Role.name).all()
    return render_template('admin_roles.html', roles=roles)


@admin_bp.route('/roles/add', methods=['GET', 'POST'])
@admin_required
def add_role():
    if request.method == 'POST':
        name = request.form.get('name')
        display_name = request.form.get('display_name')
        description = request.form.get('description')

        permissions = {}
        for key in request.form:
            if key.startswith('perm_'):
                permissions[key[5:]] = True

        menu_access = request.form.getlist('menu_access')

        role = Role(
            name=name,
            display_name=display_name,
            description=description,
            permissions=permissions,
            menu_access=menu_access,
            is_system=False
        )
        db.session.add(role)
        db.session.commit()
        log_activity(f'Creation role', action_type='create', target_type='role', target_id=role.id, target_name=name)

        flash('Role cree avec succes', 'success')
        return redirect(url_for('admin.roles'))

    return render_template('admin_role_form.html', role=None)


@admin_bp.route('/roles/<int:role_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_role(role_id):
    role = Role.query.get_or_404(role_id)

    if request.method == 'POST':
        if not role.is_system:
            role.name = request.form.get('name')
        role.display_name = request.form.get('display_name')
        role.description = request.form.get('description')

        permissions = {}
        for key in request.form:
            if key.startswith('perm_'):
                permissions[key[5:]] = True
        role.permissions = permissions

        role.menu_access = request.form.getlist('menu_access')

        log_activity(f'Modification role', action_type='update', target_type='role', target_id=role.id, target_name=role.name)
        db.session.commit()
        flash('Role mis a jour', 'success')
        return redirect(url_for('admin.roles'))

    return render_template('admin_role_form.html', role=role)


@admin_bp.route('/disparu/<int:disparu_id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_disparu(disparu_id):
    disparu = Disparu.query.get_or_404(disparu_id)
    if request.method == 'POST':
        try:
            old_status = disparu.status
            disparu.person_type = request.form.get('person_type')
            disparu.animal_type = request.form.get('animal_type')
            disparu.breed = request.form.get('breed')
            disparu.first_name = request.form.get('first_name')
            disparu.last_name = request.form.get('last_name') or "-"
            disparu.age = int(request.form.get('age')) if request.form.get('age') else -1
            disparu.sex = request.form.get('sex')
            disparu.country = request.form.get('country')
            disparu.city = request.form.get('city')
            disparu.physical_description = request.form.get('physical_description')
            disparu.clothing = request.form.get('clothing')
            disparu.objects = request.form.get('objects')
            disparu.circumstances = request.form.get('circumstances')
            disparu.status = request.form.get('status')

            if 'photo' in request.files:
                file = request.files['photo']
                if file and file.filename != '':
                    filename = secure_filename(f"{disparu.public_id}_{file.filename}")
                    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
                    file.save(file_path)
                    disparu.photo_url = filename

            if request.form.get('latitude') and request.form.get('latitude').strip():
                try:
                    disparu.latitude = float(request.form.get('latitude'))
                except ValueError:
                    disparu.latitude = None
            else:
                disparu.latitude = None

            if request.form.get('longitude') and request.form.get('longitude').strip():
                try:
                    disparu.longitude = float(request.form.get('longitude'))
                except ValueError:
                    disparu.longitude = None
            else:
                disparu.longitude = None

            # Contacts handling
            contacts = []
            for i in range(3):
                name = request.form.get(f'contact_name_{i}')
                phone = request.form.get(f'contact_phone_{i}')
                if name and phone:
                    contacts.append({
                        'name': name,
                        'phone': phone,
                        'email': request.form.get(f'contact_email_{i}', ''),
                        'relation': request.form.get(f'contact_relation_{i}', '')
                    })
            disparu.contacts = contacts

            if disparu.status != old_status:
                contribution = Contribution(
                    disparu_id=disparu.id,
                    contribution_type='status_change',
                    details=f"Statut modifié par l'administrateur : {old_status} -> {disparu.status}",
                    is_approved=True,
                    approved_by=session.get('admin_username', 'Admin'),
                    approved_at=datetime.utcnow(),
                    contributor_name=session.get('admin_username', 'Admin'),
                    created_at=datetime.utcnow()
                )
                db.session.add(contribution)

            db.session.commit()
            log_activity(f'Modification fiche disparu', action_type='update', target_type='disparu', target_id=disparu.id, target_name=f'{disparu.first_name} {disparu.last_name}')
            flash('Fiche mise a jour avec succes', 'success')
            return redirect(url_for('admin.all_reports'))
        except Exception as e:
            db.session.rollback()
            flash(f'Erreur lors de la modification: {str(e)}', 'error')

    from utils.geo import COUNTRIES_CITIES
    return render_template('admin_disparu_form.html', person=disparu, countries=get_countries(), countries_cities=COUNTRIES_CITIES)


@admin_bp.route('/disparu/<int:disparu_id>/status', methods=['POST'])
@admin_required
def update_status(disparu_id):
    disparu = Disparu.query.get_or_404(disparu_id)
    new_status = request.form.get('status')
    old_status = disparu.status
    if new_status in ['missing', 'found', 'deceased', 'found_alive', 'found_deceased']:
        disparu.status = new_status
        log_activity(f'Changement statut: {old_status} -> {new_status}', action_type='update', target_type='disparu', target_id=disparu.id, target_name=f'{disparu.first_name} {disparu.last_name}')

        # Create a contribution record for the status change
        contribution = Contribution(
            disparu_id=disparu.id,
            contribution_type='status_change',
            details=f"Statut modifié par l'administrateur : {old_status} -> {new_status}",
            is_approved=True,
            approved_by=session.get('admin_username', 'Admin'),
            approved_at=datetime.utcnow(),
            contributor_name=session.get('admin_username', 'Admin'),
            created_at=datetime.utcnow()
        )
        db.session.add(contribution)

        db.session.commit()
        flash(f'Statut mis à jour : {new_status}', 'success')
    return redirect(request.referrer or url_for('admin.dashboard'))


@admin_bp.route('/disparu/<int:disparu_id>/delete', methods=['POST'])
@admin_required
def delete_disparu(disparu_id):
    disparu = Disparu.query.get_or_404(disparu_id)
    name = f'{disparu.first_name} {disparu.last_name}'
    log_activity(f'Suppression fiche disparu', action_type='delete', target_type='disparu', target_id=disparu.id, target_name=name, severity='warning')
    db.session.delete(disparu)
    db.session.commit()
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/contributions')
@admin_required
def contributions():
    log_activity('Consultation contributions', action_type='view', target_type='contributions')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    contributions = Contribution.query.order_by(Contribution.created_at.desc()).paginate(page=page, per_page=per_page, error_out=False)
    return render_template('admin_contributions.html', contributions=contributions)


@admin_bp.route('/contributions/<int:contrib_id>/approve', methods=['POST'])
@admin_required
def approve_contribution(contrib_id):
    contribution = Contribution.query.get_or_404(contrib_id)
    contribution.is_approved = True
    contribution.approved_by = session.get('admin_username')
    contribution.approved_at = datetime.utcnow()

    # Apply proposed status if present
    if contribution.proposed_status:
        disparu = Disparu.query.get(contribution.disparu_id)
        if disparu:
            disparu.status = contribution.proposed_status
            log_activity(f'Mise a jour statut via contribution: {contribution.proposed_status}',
                        action_type='update', target_type='disparu', target_id=disparu.id,
                        target_name=f'{disparu.first_name} {disparu.last_name}')

    log_activity(f'Approbation contribution', action_type='update', target_type='contribution', target_id=contrib_id, target_name=contribution.contributor_name)
    db.session.commit()
    flash('Contribution approuvee', 'success')
    return redirect(url_for('admin.contributions'))


@admin_bp.route('/contributions/<int:contrib_id>/reject', methods=['POST'])
@admin_required
def reject_contribution(contrib_id):
    contribution = Contribution.query.get_or_404(contrib_id)
    log_activity(f'Rejet contribution', action_type='delete', target_type='contribution', target_id=contrib_id, target_name=contribution.contributor_name, severity='warning')
    db.session.delete(contribution)
    db.session.commit()
    flash('Contribution rejetee', 'success')
    return redirect(url_for('admin.contributions'))
