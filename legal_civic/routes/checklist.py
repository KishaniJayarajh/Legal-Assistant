from flask import Blueprint, render_template, request, jsonify
from flask_login import login_required
from models.user import GovService, RequiredDocument

checklist = Blueprint('checklist', __name__)


@checklist.route('/checklist')
@login_required
def checklist_page():
    all_services = GovService.query.filter_by(status='Active').all()
    return render_template('checklist.html', services=all_services)


@checklist.route('/checklist/<int:service_id>')
@login_required
def get_checklist(service_id):
    service = GovService.query.get_or_404(service_id)
    docs = RequiredDocument.query.filter_by(service_id=service_id).all()
    return render_template('checklist_detail.html', service=service, documents=docs)


@checklist.route('/checklist/api/<int:service_id>')
@login_required
def checklist_api(service_id):
    docs = RequiredDocument.query.filter_by(service_id=service_id).all()
    return jsonify([{
        'name': d.document_name,
        'mandatory': d.is_mandatory
    } for d in docs])
