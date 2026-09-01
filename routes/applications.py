import json
import random
from io import BytesIO
from datetime import datetime

from flask import Blueprint, render_template, request, jsonify, url_for, send_file, flash, redirect
from flask_login import login_required, current_user
from extensions import db
from models.user import Application, GovService

applications = Blueprint('applications', __name__)

# ── DISTRICT CENTROID COORDINATES (approx. town center of each district) ──
# Used to find the TRUE nearest office when a service has no office listed
# in the applicant's own district (instead of blindly picking the first
# office in the database, which used to always show Colombo).
DISTRICT_COORDS = {
    "Colombo": (6.9271, 79.8612), "Gampaha": (7.0917, 80.0000),
    "Kalutara": (6.5854, 79.9607), "Kandy": (7.2906, 80.6337),
    "Matale": (7.4675, 80.6234), "Nuwara Eliya": (6.9497, 80.7891),
    "Galle": (6.0535, 80.2210), "Matara": (5.9549, 80.5550),
    "Hambantota": (6.1241, 81.1185), "Jaffna": (9.6615, 80.0255),
    "Kilinochchi": (9.3961, 80.3982), "Mannar": (8.9810, 79.9044),
    "Vavuniya": (8.7514, 80.4971), "Mullaitivu": (9.2671, 80.8142),
    "Batticaloa": (7.7170, 81.7000), "Ampara": (7.2975, 81.6747),
    "Trincomalee": (8.5874, 81.2152), "Kurunegala": (7.4818, 80.3609),
    "Puttalam": (8.0362, 79.8283), "Anuradhapura": (8.3114, 80.4037),
    "Polonnaruwa": (7.9403, 81.0188), "Badulla": (6.9934, 81.0550),
    "Moneragala": (6.8712, 81.3507), "Ratnapura": (6.6828, 80.3992),
    "Kegalle": (7.2513, 80.3464),
}


def haversine_km(lat1, lng1, lat2, lng2):
    """Great-circle distance between two lat/lng points, in km."""
    import math
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def generate_application_no():
    """Generates a unique application number like APP12345, retrying on collision."""
    for _ in range(20):
        candidate = f"APP{random.randint(10000, 99999)}"
        if not Application.query.filter_by(application_no=candidate).first():
            return candidate
    return f"APP{int(datetime.utcnow().timestamp())}"

# ── FORM FIELD DEFINITIONS ────────────────────────────────────────────
FORM_FIELD_DEFS = {
    "Passport Application": [
        {"key": "full_name", "label": "Full Name (As in NIC)", "type": "text"},
        {"key": "nic_number", "label": "NIC Number", "type": "text"},
        {"key": "date_of_birth", "label": "Date of Birth", "type": "date"},
        {"key": "gender", "label": "Gender", "type": "select", "options": ["Male", "Female"]},
        {"key": "civil_status", "label": "Civil Status", "type": "select", "options": ["Single", "Married", "Divorced", "Widowed"]},
    ],
    "NIC Application": [
        {"key": "full_name", "label": "Full Name (As in old NIC, if any)", "type": "text"},
        {"key": "nic_number", "label": "NIC Number (leave blank if first-time applicant)", "type": "text"},
        {"key": "date_of_birth", "label": "Date of Birth", "type": "date"},
        {"key": "reason", "label": "Application Reason", "type": "select", "options": ["First Time", "Lost", "Damaged", "Details Changed", "Expired"]},
    ],
    "Birth Certificate": [
        {"key": "child_name", "label": "Child's Full Name", "type": "text"},
        {"key": "date_of_birth", "label": "Date of Birth", "type": "date"},
        {"key": "parent_nic", "label": "Parent's NIC Number", "type": "text"},
        {"key": "hospital_name", "label": "Hospital of Birth", "type": "text"},
    ],
    "Marriage Certificate": [
        {"key": "party_a_name", "label": "Full Name (Party A)", "type": "text"},
        {"key": "party_a_nic", "label": "NIC Number (Party A)", "type": "text"},
        {"key": "party_a_dob", "label": "Date of Birth (Party A)", "type": "date"},
        {"key": "party_b_name", "label": "Full Name (Party B)", "type": "text"},
        {"key": "party_b_nic", "label": "NIC Number (Party B)", "type": "text"},
        {"key": "party_b_dob", "label": "Date of Birth (Party B)", "type": "date"},
        {"key": "marriage_date", "label": "Date of Marriage", "type": "date"},
        {"key": "registrar_division", "label": "Registrar Division", "type": "text"},
        {"key": "witness_1_name", "label": "Witness 1 Full Name", "type": "text"},
        {"key": "witness_1_nic", "label": "Witness 1 NIC", "type": "text"},
        {"key": "witness_2_name", "label": "Witness 2 Full Name", "type": "text"},
        {"key": "witness_2_nic", "label": "Witness 2 NIC", "type": "text"},
        {"key": "address", "label": "Residential Address", "type": "text"},
        {"key": "contact_number", "label": "Contact Number", "type": "text"},
    ],
}

DEFAULT_FIELDS = [
    {"key": "full_name", "label": "Full Name", "type": "text"},
    {"key": "nic_number", "label": "NIC Number", "type": "text"},
    {"key": "date_of_birth", "label": "Date of Birth", "type": "date"},
]

# ── FORM ASSISTANT - FIXED ────────────────────────────────────────────
@applications.route('/applications/form/<int:service_id>')
@login_required
def form_assistant(service_id):
    service = GovService.query.get_or_404(service_id)
    fields = FORM_FIELD_DEFS.get(service.name, DEFAULT_FIELDS)
    prefill = {
        "full_name": current_user.fullname,
        "nic_number": current_user.nic or "",
    }
    districts = [
        "Colombo", "Gampaha", "Kalutara", "Kandy",
        "Matale", "Nuwara Eliya", "Galle", "Matara",
        "Hambantota", "Jaffna", "Kilinochchi", "Mannar",
        "Vavuniya", "Mullaitivu", "Batticaloa", "Ampara",
        "Trincomalee", "Kurunegala", "Puttalam",
        "Anuradhapura", "Polonnaruwa", "Badulla",
        "Moneragala", "Ratnapura", "Kegalle"
    ]
    return render_template(
        'form_assistant.html',
        service=service,
        fields=fields,
        prefill=prefill, 
        districts=districts
    )

    # Pre-fill from user profile
    prefill = {
        "full_name": current_user.fullname,
        "nic_number": current_user.nic or "",
    }

    # Form submit aana
    if request.method == 'POST':
        form_data = request.form.to_dict()
        
        app_record = Application(
            application_no=generate_application_no(),
            user_id=current_user.id,
            service_id=service.id,
            application_type=service.name,
            form_data=json.dumps(form_data),
            status='In Progress'
        )
        db.session.add(app_record)
        db.session.commit()
        flash('Application submitted successfully!', 'success')
        return redirect(url_for('applications.my_applications'))

    # GET request na form kaatu
    return render_template(
        'form_assistant.html',
        service=service,
        fields=fields,
        prefill=prefill
    )

# ── SUBMIT API - For AJAX ─────────────────────────────────────────────
@applications.route('/applications/form/<int:service_id>/submit', methods=['POST'])
@login_required
def submit_form(service_id):
    service = GovService.query.get_or_404(service_id)
    data = request.get_json()
    form_data = data.get('form_data', {})

    app_record = Application(
        application_no=generate_application_no(),
        user_id=current_user.id,
        service_id=service.id,
        application_type=service.name,
        form_data=json.dumps(form_data),
        status='In Progress'
    )
    db.session.add(app_record)
    db.session.commit()

    return jsonify({
        'success': True,
        'application_no': app_record.application_no,
        'app_id': app_record.id,
        'redirect': url_for('applications.my_applications')
    })

@applications.route('/applications/nearest-office')
@login_required
def nearest_office():
    from models.user import Division

    service  = request.args.get('service', '')
    district = request.args.get('district', '')

    # Step 1: Exact service + district match — best case, office is right there.
    office = Division.query.filter(
        Division.service == service,
        Division.district == district
    ).first()

    if office:
        return jsonify({
            'office_name': office.office_name,
            'address':     office.address,
            'phone':       office.phone or 'Not available',
            'lat':         office.lat,
            'lng':         office.lng,
            'district':    office.district,
            'matched':     True,
            'distance_km': 0
        })

    # Step 2: No office for this service in the applicant's own district —
    # find the TRUE geographically nearest office for this service using
    # real distance, instead of just grabbing the first row in the table.
    all_offices = Division.query.filter_by(service=service).all()
    user_coords = DISTRICT_COORDS.get(district)

    if all_offices and user_coords:
        best_office = None
        best_distance = None
        for o in all_offices:
            dist = haversine_km(user_coords[0], user_coords[1], o.lat, o.lng)
            if best_distance is None or dist < best_distance:
                best_distance = dist
                best_office = o
        office = best_office
        distance_km = round(best_distance, 1) if best_distance is not None else None
    elif all_offices:
        # District not recognised — fall back to first office as last resort.
        office = all_offices[0]
        distance_km = None
    else:
        distance_km = None

    # Step 3: Still nothing for this service anywhere — try any office
    # at least located in the applicant's district (different service).
    if not office:
        office = Division.query.filter_by(district=district).first()
        distance_km = 0 if office else None

    if not office:
        return jsonify({
            'error': 'No office found. Please contact your nearest Divisional Secretariat.'
        })

    return jsonify({
        'office_name': office.office_name,
        'address':     office.address,
        'phone':       office.phone or 'Not available',
        'lat':         office.lat,
        'lng':         office.lng,
        'district':    office.district,
        'matched':     office.district == district,
        'distance_km': distance_km
    })
# ── PDF PREVIEW ───────────────────────────────────────────────────────
@applications.route('/applications/<int:app_id>/preview-pdf')
@login_required
def preview_pdf(app_id):
    app_record = Application.query.filter_by(
        id=app_id, user_id=current_user.id
    ).first_or_404()
    form_data = json.loads(app_record.form_data or '{}')

    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.pdfgen import canvas
    from reportlab.lib.colors import (
        HexColor, black, white, Color
    )

    buf = BytesIO()
    c = canvas.Canvas(buf, pagesize=A4)
    w, h = A4

    # ── COLORS ─────────────────────────────
    NAVY  = HexColor("#0f4c81")
    GOLD  = HexColor("#e8a020")
    LIGHT = HexColor("#eef2f7")
    GRAY  = HexColor("#64748b")
    BORD  = HexColor("#dde3ed")
    GREEN = HexColor("#0d9488")

    # ── SERVICE-SPECIFIC FORM NUMBERS ───────
    form_numbers = {
        "Passport Application":  "PP-1 (Rev. 2024)",
        "NIC Application":       "NIC-1 (Rev. 2024)",
        "Birth Certificate":     "RGD-BC-1 (Rev. 2024)",
        "Marriage Certificate":  "RGD-MC-1 (Rev. 2024)",
        "Land Registration":     "LR-1 (Rev. 2024)",
        "Driving License":       "DMT-1 (Rev. 2024)",
        "Police Clearance":      "POL-CC-1 (Rev. 2024)",
        "Visa Information":      "IMM-V-1 (Rev. 2024)",
    }
    form_no = form_numbers.get(
        app_record.application_type, "LC-1 (Rev. 2024)"
    )

    # ── PAGE BORDER ─────────────────────────
    c.setStrokeColor(NAVY)
    c.setLineWidth(3)
    c.rect(6*mm, 6*mm, w - 12*mm, h - 12*mm)
    c.setLineWidth(0.5)
    c.setStrokeColor(GOLD)
    c.rect(8*mm, 8*mm, w - 16*mm, h - 16*mm)

    # ── HEADER BACKGROUND ───────────────────
    c.setFillColor(NAVY)
    c.rect(6*mm, h - 48*mm, w - 12*mm, 42*mm,
           fill=True, stroke=False)

    # Left emblem
    c.setFillColor(GOLD)
    c.circle(22*mm, h - 26*mm, 14*mm,
             fill=True, stroke=False)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 6)
    c.drawCentredString(22*mm, h - 21*mm, "GOVERNMENT")
    c.drawCentredString(22*mm, h - 26*mm, "OF")
    c.drawCentredString(22*mm, h - 31*mm, "SRI LANKA")

    # Right ministry emblem
    c.setFillColor(GOLD)
    c.circle(w - 22*mm, h - 26*mm, 14*mm,
             fill=True, stroke=False)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 5.5)
    c.drawCentredString(w - 22*mm, h - 21*mm, "DEPT OF")
    c.drawCentredString(w - 22*mm, h - 26*mm, "LEGAL &")
    c.drawCentredString(w - 22*mm, h - 31*mm, "CIVIC SVC")

    # Header text
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 13)
    c.drawCentredString(
        w/2, h - 18*mm,
        "DEMOCRATIC SOCIALIST REPUBLIC OF SRI LANKA"
    )
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(
        w/2, h - 25*mm,
        "LEGAL & CIVIC SERVICE ASSISTANT"
    )
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(
        w/2, h - 33*mm,
        app_record.application_type.upper() + " APPLICATION"
    )
    c.setFillColor(white)
    c.setFont("Helvetica", 8)
    c.drawCentredString(
        w/2, h - 39*mm,
        "Form No: " + form_no
    )

    # Gold bottom bar of header
    c.setFillColor(GOLD)
    c.rect(6*mm, h - 50*mm, w - 12*mm, 2*mm,
           fill=True, stroke=False)

    # ── APPLICATION INFO ROW ────────────────
    c.setFillColor(LIGHT)
    c.rect(6*mm, h - 61*mm, w - 12*mm, 11*mm,
           fill=True, stroke=False)
    c.setFillColor(NAVY)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(
        10*mm, h - 55*mm,
        "Application No: " + app_record.application_no
    )
    c.drawString(
        80*mm, h - 55*mm,
        "Status: " + app_record.status
    )
    c.drawString(
        140*mm, h - 55*mm,
        "Date: " + app_record.submitted_at.strftime('%d/%m/%Y')
    )
    c.setFont("Helvetica", 8)
    c.setFillColor(GRAY)
    c.drawString(
        10*mm, h - 59*mm,
        "Submitted via Legal & Civic Service Assistant | "
        "www.legalcivic.lk"
    )

    # ── FOR OFFICIAL USE BOX ────────────────
    c.setStrokeColor(NAVY)
    c.setLineWidth(0.7)
    c.rect(w - 58*mm, h - 85*mm, 50*mm, 22*mm)
    c.setFillColor(NAVY)
    c.rect(w - 58*mm, h - 67*mm, 50*mm, 4*mm,
           fill=True, stroke=False)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(
        w - 33*mm, h - 64*mm,
        "FOR OFFICIAL USE ONLY"
    )
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 7)
    c.drawString(w - 56*mm, h - 70*mm,
                 "Received by: _______________")
    c.drawString(w - 56*mm, h - 75*mm,
                 "Received date: _____________")
    c.drawString(w - 56*mm, h - 80*mm,
                 "Reference No: _____________")
    c.drawString(w - 56*mm, h - 85*mm,
                 "Stamp: ____________________")

    # ── SECTION A: APPLICANT DETAILS ────────
    y = h - 72*mm

    # Section Header
    c.setFillColor(NAVY)
    c.rect(10*mm, y, w - 78*mm, 7*mm,
           fill=True, stroke=False)
    c.setFillColor(GOLD)
    c.rect(10*mm, y, 3*mm, 7*mm,
           fill=True, stroke=False)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(16*mm, y + 2*mm,
                 "SECTION A — APPLICANT INFORMATION")

    y -= 2*mm
    row = 0

    for key, value in form_data.items():
        if y < 65*mm:
            # Page break
            c.showPage()
            c.setFillColor(NAVY)
            c.rect(6*mm, h - 20*mm,
                   w - 12*mm, 14*mm,
                   fill=True, stroke=False)
            c.setFillColor(white)
            c.setFont("Helvetica-Bold", 10)
            c.drawCentredString(
                w/2, h - 11*mm,
                app_record.application_type.upper() +
                " — Page 2"
            )
            y = h - 28*mm
            row = 0

        label = key.replace('_', ' ').title()

        # Alternating rows
        c.setFillColor(LIGHT if row % 2 == 0 else white)
        c.rect(10*mm, y - 7.5*mm, w - 20*mm, 7.5*mm,
               fill=True, stroke=False)

        # Row border
        c.setStrokeColor(BORD)
        c.setLineWidth(0.3)
        c.rect(10*mm, y - 7.5*mm, w - 20*mm, 7.5*mm,
               fill=False, stroke=True)

        # Divider line between label and value
        c.setStrokeColor(BORD)
        c.line(75*mm, y - 7.5*mm, 75*mm, y)

        # Number column
        c.setFillColor(NAVY)
        c.setFont("Helvetica-Bold", 7)
        c.drawString(11*mm, y - 5*mm, str(row + 1) + ".")

        # Label
        c.setFillColor(GRAY)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(16*mm, y - 5*mm, label)

        # Value
        c.setFillColor(black)
        c.setFont("Helvetica", 8)
        val = str(value) if value else "— Not provided —"
        c.drawString(77*mm, y - 5*mm, val)

        y -= 7.5*mm
        row += 1

    # ── SECTION B: DECLARATION ──────────────
    y -= 6*mm
    if y < 70*mm:
        c.showPage()
        y = h - 25*mm

    c.setFillColor(NAVY)
    c.rect(10*mm, y, w - 20*mm, 7*mm,
           fill=True, stroke=False)
    c.setFillColor(GOLD)
    c.rect(10*mm, y, 3*mm, 7*mm,
           fill=True, stroke=False)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(16*mm, y + 2*mm,
                 "SECTION B — DECLARATION BY APPLICANT")

    y -= 3*mm
    c.setStrokeColor(BORD)
    c.setLineWidth(0.5)
    c.rect(10*mm, y - 24*mm, w - 20*mm, 24*mm)

    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 8.5)
    c.drawString(13*mm, y - 6*mm,
                 "I, the undersigned, hereby solemnly declare that:")
    c.setFont("Helvetica", 8)
    c.drawString(13*mm, y - 11*mm,
        "1.  All information furnished in this application "
        "is true, complete and accurate to the best of my knowledge.")
    c.drawString(13*mm, y - 16*mm,
        "2.  I understand that any false statement will "
        "result in rejection of this application and/or legal action.")
    c.drawString(13*mm, y - 21*mm,
        "3.  I consent to verification of the above "
        "information with relevant government authorities of Sri Lanka.")

    # ── SECTION C: SIGNATURES ───────────────
    y -= 32*mm
    if y < 60*mm:
        c.showPage()
        y = h - 25*mm

    c.setFillColor(NAVY)
    c.rect(10*mm, y, w - 20*mm, 7*mm,
           fill=True, stroke=False)
    c.setFillColor(GOLD)
    c.rect(10*mm, y, 3*mm, 7*mm,
           fill=True, stroke=False)
    c.setFillColor(white)
    c.setFont("Helvetica-Bold", 9)
    c.drawString(16*mm, y + 2*mm,
                 "SECTION C — SIGNATURES & CERTIFICATION")

    y -= 15*mm

    # Applicant signature box
    c.setStrokeColor(NAVY)
    c.setLineWidth(0.7)
    c.rect(10*mm, y - 25*mm, 80*mm, 25*mm)
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 8)
    c.drawString(12*mm, y - 5*mm,  "Applicant Signature:")
    c.drawString(12*mm, y - 20*mm, "Date: ______ / ______ / __________")

    # Photo box
    c.setStrokeColor(NAVY)
    c.setLineWidth(1)
    c.rect(w - 50*mm, y - 35*mm, 38*mm, 35*mm)
    c.setFillColor(LIGHT)
    c.rect(w - 50*mm, y - 35*mm, 38*mm, 35*mm,
           fill=True, stroke=True)
    c.setFillColor(GRAY)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(w - 31*mm, y - 14*mm,
                        "Passport Size")
    c.drawCentredString(w - 31*mm, y - 19*mm,
                        "Photograph")
    c.drawCentredString(w - 31*mm, y - 24*mm,
                        "35mm × 45mm")
    c.setFont("Helvetica", 6)
    c.drawCentredString(w - 31*mm, y - 29*mm,
                        "(White background)")

    # Officer box
    c.setStrokeColor(NAVY)
    c.setLineWidth(0.7)
    c.rect(10*mm, y - 50*mm, 80*mm, 20*mm)
    c.setFillColor(GRAY)
    c.setFont("Helvetica", 8)
    c.drawString(12*mm, y - 32*mm,
                 "Authorized Officer Signature:")
    c.drawString(12*mm, y - 38*mm,
                 "Name: _______________________________")
    c.drawString(12*mm, y - 44*mm,
                 "Designation: ________________________")
    c.drawString(12*mm, y - 49*mm,
                 "Official Stamp:                Date: ____________")

    # ── WATERMARK ───────────────────────────
    c.saveState()
    c.setFillColor(Color(0.85, 0.88, 0.95, alpha=0.12))
    c.setFont("Helvetica-Bold", 55)
    c.translate(w/2, h/2)
    c.rotate(42)
    c.drawCentredString(0, 0, "OFFICIAL COPY")
    c.restoreState()

    # ── FOOTER ──────────────────────────────
    c.setFillColor(GOLD)
    c.rect(6*mm, 14*mm, w - 12*mm, 1*mm,
           fill=True, stroke=False)
    c.setFillColor(NAVY)
    c.rect(6*mm, 6*mm, w - 12*mm, 8*mm,
           fill=True, stroke=False)
    c.setFillColor(white)
    c.setFont("Helvetica", 6.5)
    c.drawString(10*mm, 10*mm,
        "Legal & Civic Service Assistant | "
        "AI-Powered Government Services | Sri Lanka")
    c.setFillColor(GOLD)
    c.setFont("Helvetica-Bold", 6.5)
    c.drawRightString(
        w - 10*mm, 10*mm,
        "Form: " + form_no + " | Ref: " + app_record.application_no
    )

    c.showPage()
    c.save()
    buf.seek(0)

    filename = (
        app_record.application_no + "_" +
        app_record.application_type.replace(' ', '_') +
        ".pdf"
    )

    return send_file(
        buf,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=filename
    )
@applications.route('/applications')
@login_required
def my_applications():
    apps = Application.query.filter_by(user_id=current_user.id)\
               .order_by(Application.submitted_at.desc()).all()
    return render_template('my_applications.html', applications=apps)

@applications.route('/applications/<int:app_id>')
@login_required
def view_application(app_id):
    app_record = Application.query.filter_by(
        id=app_id, user_id=current_user.id
    ).first_or_404()
    form_data = json.loads(app_record.form_data or '{}')
    return render_template(
        'application_detail.html',
        application=app_record,
        form_data=form_data
    )