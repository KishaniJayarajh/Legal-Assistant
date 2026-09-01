from flask import Blueprint, render_template, request, jsonify, session
from flask_login import login_required, current_user
from models.user import GovService
from translations import get_translator

tools = Blueprint('tools', __name__)

# ── ELIGIBILITY RULES ──────────────────────────────────────────────
ELIGIBILITY_RULES = {
    "new_passport": {
        "name_key": "new_passport",
        "questions": [
            {"key": "has_nic", "label_key": "q_has_nic", "type": "yesno"},
            {"key": "has_birth_cert", "label_key": "q_has_birth_cert", "type": "yesno"},
            {"key": "age", "label_key": "q_age", "type": "number"},
        ],
        "evaluate": lambda a: (
            a.get("has_nic") == "yes" and
            a.get("has_birth_cert") == "yes" and
            int(a.get("age", 0) or 0) >= 0
        ),
        "eligible_msg": "You are eligible to apply for a New Passport.",
        "ineligible_msg": "You need a valid NIC and Birth Certificate.",
    },
    "passport_renewal": {
        "name_key": "passport_renewal",
        "questions": [
            {"key": "has_old_passport", "label_key": "q_has_old_passport", "type": "yesno"},
            {"key": "has_nic", "label_key": "q_has_nic", "type": "yesno"},
        ],
        "evaluate": lambda a: (
            a.get("has_old_passport") == "yes" and
            a.get("has_nic") == "yes"
        ),
        "eligible_msg": "You are eligible for Passport Renewal.",
        "ineligible_msg": "You need your previous passport and a valid NIC.",
    },
    "nic_new": {
        "name_key": "nic_new",
        "questions": [
            {"key": "has_birth_cert", "label_key": "q_has_birth_cert", "type": "yesno"},
            {"key": "has_gn_letter", "label_key": "q_has_gn_letter", "type": "yesno"},
            {"key": "age", "label_key": "q_age", "type": "number"},
        ],
        "evaluate": lambda a: (
            a.get("has_birth_cert") == "yes" and
            int(a.get("age", 0) or 0) >= 15
        ),
        "eligible_msg": "You are eligible to apply for a new NIC.",
        "ineligible_msg": "You must be at least 15 years old with a Birth Certificate.",
    },
    "nic_renewal": {
        "name_key": "nic_renewal",
        "questions": [
            {"key": "has_old_nic", "label_key": "q_has_old_nic", "type": "yesno"},
        ],
        "evaluate": lambda a: a.get("has_old_nic") == "yes",
        "eligible_msg": "You are eligible for NIC Renewal.",
        "ineligible_msg": "You need your previous NIC to apply for renewal.",
    },
    "birth_certificate": {
        "name_key": "birth_certificate_elig",
        "questions": [
            {"key": "has_parent_nic", "label_key": "q_has_parent_nic", "type": "yesno"},
            {"key": "has_hospital_record", "label_key": "q_has_hospital_record", "type": "yesno"},
        ],
        "evaluate": lambda a: (
            a.get("has_parent_nic") == "yes" and
            a.get("has_hospital_record") == "yes"
        ),
        "eligible_msg": "You are eligible to obtain a Birth Certificate.",
        "ineligible_msg": "You need a parent NIC and hospital birth record.",
    },
    "marriage_certificate": {
        "name_key": "marriage_certificate_elig",
        "questions": [
            {"key": "both_nic", "label_key": "q_both_nic", "type": "yesno"},
            {"key": "has_witnesses", "label_key": "q_has_witnesses", "type": "yesno"},
        ],
        "evaluate": lambda a: (
            a.get("both_nic") == "yes" and
            a.get("has_witnesses") == "yes"
        ),
        "eligible_msg": "You are eligible to register your marriage.",
        "ineligible_msg": "Both parties need valid NICs and two witnesses.",
    },
}

@tools.route('/tools/eligibility-checker')
@login_required
def eligibility_checker():
    service_types = list(ELIGIBILITY_RULES.keys())
    return render_template('eligibility_checker.html', service_types=service_types)


from flask import session
from translations import get_translator

@tools.route('/tools/eligibility-checker/questions/<service_type>')
@login_required
def get_eligibility_questions(service_type):
    rule = ELIGIBILITY_RULES.get(service_type)
    if not rule:
        return jsonify({'error': 'Unknown service type'}), 404

    # Current language session-ல இருந்து எடு
    lang = session.get('language') or \
           current_user.preferred_language or 'English'
    t = get_translator(lang)

    # label_key → translated label-ஆ மாத்து
    translated_questions = []
    for q in rule['questions']:
        translated_questions.append({
            "key": q["key"],
            "label": t(q["label_key"]),
            "type": q["type"]
        })

    return jsonify({'questions': translated_questions})

@tools.route('/tools/eligibility-checker/check', methods=['POST'])
@login_required
def check_eligibility():
    data = request.get_json()
    service_type = data.get('service_type')
    answers = data.get('answers', {})

    rule = ELIGIBILITY_RULES.get(service_type)
    if not rule:
        return jsonify({'error': 'Unknown service type'}), 404

    try:
        is_eligible = bool(rule['evaluate'](answers))
    except (ValueError, TypeError):
        is_eligible = False

    message = rule['eligible_msg'] if is_eligible else rule['ineligible_msg']
    return jsonify({'eligible': is_eligible, 'message': message})


# ── SERVICE FINDER ───────────────────────────────────────────────────
SERVICE_FINDER_MAP = {
    "sf_travel":     ["Travel Documents", "Immigration"],
    "sf_identity":   ["Identity Documents"],
    "sf_life_event": ["Civil Registration"],
    "sf_property":   ["Property"],
    "sf_drive":      ["Transport"],
    "sf_legal_doc":  ["Legal Documents", "Law & Order"],
}

@tools.route('/tools/service-finder')
@login_required
def service_finder():
    from flask import session
    from translations import get_translator
    lang = session.get('language') or \
           current_user.preferred_language or 'English'
    t = get_translator(lang)
    situations = [
        {"key": k, "label": t(k)}
        for k in SERVICE_FINDER_MAP.keys()
    ]
    return render_template('service_finder.html',
                           questions=situations)

@tools.route('/tools/service-finder/find', methods=['POST'])
@login_required
def find_service():
    data = request.get_json()
    situation_key = data.get('situation', '')
    categories = SERVICE_FINDER_MAP.get(situation_key, [])

    if not categories:
        keyword = situation_key.lower()
        matches = GovService.query.filter(
            GovService.status == 'Active'
        ).all()
        matches = [s for s in matches if
                   keyword in (s.name or '').lower()
                   or keyword in (s.category or '').lower()]
    else:
        matches = GovService.query.filter(
            GovService.category.in_(categories),
            GovService.status == 'Active'
        ).all()

    return jsonify([{
        'id': s.id, 'name': s.name, 'icon': s.icon,
        'category': s.category, 'description': s.description
    } for s in matches])