from flask import Blueprint, render_template, session
from flask_login import login_required, current_user
from extensions import db
from models.user import GovService, SavedGuide
from fees_data import get_fee_info

services = Blueprint('services', __name__)


@services.route('/services')
@login_required
def list_services():
    all_services = GovService.query.filter_by(status='Active').all()
    return render_template('services.html', services=all_services)


@services.route('/services/<int:service_id>')
@login_required
def service_detail(service_id):
    service = GovService.query.get_or_404(service_id)
    steps = sorted(service.steps, key=lambda s: s.step_number)
    is_saved = SavedGuide.query.filter_by(
        user_id=current_user.id, service_id=service_id
    ).first() is not None

    lang = session.get('language') or current_user.preferred_language or 'English'
    fee_info = get_fee_info(service.name, lang)

    return render_template('service_detail.html', service=service, steps=steps,
                            is_saved=is_saved, fee_info=fee_info)


@services.route('/services/<int:service_id>/save')
@login_required
def save_service(service_id):
    existing = SavedGuide.query.filter_by(
        user_id=current_user.id, service_id=service_id
    ).first()
    if not existing:
        db.session.add(SavedGuide(user_id=current_user.id, service_id=service_id))
        db.session.commit()
    from flask import redirect, url_for, flash
    flash('Guide saved to your dashboard!', 'success')
    return redirect(url_for('services.service_detail', service_id=service_id))
