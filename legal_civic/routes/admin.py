from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from functools import wraps
from extensions import db
from models.user import User, GovService, ServiceStep, RequiredDocument, ChatHistory, OfficialLink, Application

admin = Blueprint('admin', __name__, url_prefix='/admin')


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated


@admin.route('/dashboard')
@login_required
@admin_required
def admin_dashboard():
    total_users    = User.query.filter_by(role='user').count()
    total_services = GovService.query.count()
    total_chats    = ChatHistory.query.count()
    total_docs     = RequiredDocument.query.count()
    recent_services = GovService.query.order_by(GovService.created_at.desc()).limit(5).all()
    return render_template(
        'admin_dashboard.html',
        total_users=total_users,
        total_services=total_services,
        total_chats=total_chats,
        total_docs=total_docs,
        recent_services=recent_services
    )


@admin.route('/services')
@login_required
@admin_required
def manage_services():
    all_services = GovService.query.order_by(GovService.created_at.desc()).all()
    return render_template('admin_services.html', services=all_services)


@admin.route('/services/add', methods=['GET', 'POST'])
@login_required
@admin_required
def add_service():
    if request.method == 'POST':
        s = GovService(
            name=request.form.get('name'),
            category=request.form.get('category'),
            icon=request.form.get('icon', '📄'),
            description=request.form.get('description'),
            official_link=request.form.get('official_link'),
        )
        db.session.add(s)
        db.session.commit()
        flash('Service added successfully!', 'success')
        return redirect(url_for('admin.manage_services'))
    return render_template('admin_service_form.html', service=None)


@admin.route('/services/edit/<int:sid>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_service(sid):
    s = GovService.query.get_or_404(sid)
    if request.method == 'POST':
        s.name = request.form.get('name')
        s.category = request.form.get('category')
        s.icon = request.form.get('icon')
        s.description = request.form.get('description')
        s.official_link = request.form.get('official_link')
        s.status = request.form.get('status')
        db.session.commit()
        flash('Service updated!', 'success')
        return redirect(url_for('admin.manage_services'))
    return render_template('admin_service_form.html', service=s)


@admin.route('/services/delete/<int:sid>')
@login_required
@admin_required
def delete_service(sid):
    s = GovService.query.get_or_404(sid)
    existing_apps = Application.query.filter_by(service_id=sid).count()
    if existing_apps > 0:
        flash(f'Cannot delete "{s.name}" — {existing_apps} citizen application(s) reference this service. '
              f'Set status to Inactive instead to hide it from new applicants.', 'danger')
        return redirect(url_for('admin.manage_services'))
    db.session.delete(s)
    db.session.commit()
    flash('Service deleted', 'success')
    return redirect(url_for('admin.manage_services'))


@admin.route('/users')
@login_required
@admin_required
def manage_users():
    all_users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=all_users)


@admin.route('/links')
@login_required
@admin_required
def manage_links():
    all_links = OfficialLink.query.all()
    return render_template('admin_links.html', links=all_links)


@admin.route('/links/add', methods=['POST'])
@login_required
@admin_required
def add_link():
    link = OfficialLink(
        title=request.form.get('title'),
        url=request.form.get('url'),
        department=request.form.get('department'),
        icon=request.form.get('icon', '🔗')
    )
    db.session.add(link)
    db.session.commit()
    flash('Official link added!', 'success')
    return redirect(url_for('admin.manage_links'))

@admin.route('/applications')
@login_required
@admin_required
def manage_applications():
    apps = Application.query.order_by(Application.submitted_at.desc()).all()
    return render_template('admin_applications.html', applications=apps)


@admin.route('/applications/update/<int:app_id>', methods=['POST'])
@login_required
@admin_required
def update_application(app_id):
    app_record = Application.query.get_or_404(app_id)
    app_record.status = request.form.get('status')
    db.session.commit()
    flash(f'Application {app_record.application_no} updated to {app_record.status}', 'success')
    return redirect(url_for('admin.manage_applications'))

@admin.route('/chats')
@login_required
@admin_required
def manage_chats():
    from models.user import ChatHistory
    chats = ChatHistory.query.order_by(
        ChatHistory.created_at.desc()
    ).all()
    return render_template('admin_chats.html', chats=chats)


@admin.route('/documents')
@login_required
@admin_required
def manage_documents():
    from models.user import Application  # ← RequiredDocument ah Application maathu
    docs = Application.query.order_by(
        Application.submitted_at.desc()
    ).all()  # ← RequiredDocument.query ah Application.query maathu
    return render_template('admin_documents.html', documents=docs)