"""
seed_data.py — Run this once after the app has created tables, to populate
sample Government Services matching the wireframe (NIC, Passport, Birth
Certificate, Marriage Certificate, Land Registration, Driving License,
Police Clearance, Visa Information) with steps and required documents.

IMPORTANT: The service "name" values below (e.g. "Passport Application",
"NIC Application") must exactly match the dictionary keys in
FORM_FIELD_DEFS inside routes/applications.py. If you rename a service
here, update FORM_FIELD_DEFS too, or the Form Assistant will silently
fall back to generic DEFAULT_FIELDS for that service.

Usage:
    python seed_data.py
"""
from app import create_app
from extensions import db
from models.user import GovService, ServiceStep, RequiredDocument, OfficialLink

app = create_app()

SERVICES = [
    {
        "name": "NIC Application", "category": "Identity Documents", "icon": "🪪",
        "description": "Apply for a new National Identity Card or replace a lost one.",
        "official_link": "https://www.drp.gov.lk",
        "steps": [
            "Obtain your Birth Certificate",
            "Get a Grama Niladhari (GN) Division letter",
            "Fill the NIC application form",
            "Submit the documents to the Divisional Secretariat (DS) office",
            "Collect your NIC after the processing period",
        ],
        "documents": [
            ("Birth Certificate (Original)", True),
            ("Grama Niladhari Letter", True),
            ("Completed Application Form", True),
            ("Passport Size Photo", True),
            ("Any other supporting documents (if required)", False),
        ],
    },
    {
        "name": "Passport Application", "category": "Travel Documents", "icon": "🛂",
        "description": "Apply for a new Sri Lankan passport or renew an existing one.",
        "official_link": "https://www.immigration.gov.lk",
        "steps": [
            "Obtain your Birth Certificate",
            "Get a Grama Niladhari (GN) letter",
            "Fill the passport application form online or in person",
            "Submit documents to the Department of Immigration & Emigration",
            "Pay the application fee and collect your passport",
        ],
        "documents": [
            ("Birth Certificate", True),
            ("NIC (Original + Copy)", True),
            ("Passport Size Photos", True),
            ("Previous Passport (for renewal)", False),
        ],
    },
    {
        "name": "Birth Certificate", "category": "Identity Documents", "icon": "📋",
        "description": "Obtain your official birth certificate from the Registrar General's Department.",
        "official_link": "https://www.rgd.gov.lk",
        "steps": [
            "Visit the Registrar General's Department or nearest Divisional Secretariat",
            "Submit the parent's NIC and hospital birth record",
            "Fill the request form",
            "Pay the certified copy fee",
            "Collect the certificate",
        ],
        "documents": [
            ("Parent's NIC", True),
            ("Hospital Birth Record", True),
            ("Marriage Certificate of Parents (if applicable)", False),
        ],
    },
    {
        "name": "Marriage Certificate", "category": "Civil Registration", "icon": "💍",
        "description": "Register your marriage and obtain an official marriage certificate.",
        "official_link": "https://www.rgd.gov.lk",
        "steps": [
            "Visit the Registrar of Marriages in your area",
            "Submit both parties' NICs and birth certificates",
            "Provide two witnesses",
            "Complete the registration",
            "Collect the marriage certificate",
        ],
        "documents": [
            ("NIC of both parties", True),
            ("Birth Certificates", True),
            ("Witness NICs", True),
            ("Divorce Certificate (if previously married)", False),
        ],
    },
    {
        "name": "Land Registration", "category": "Property", "icon": "🏠",
        "description": "Register or transfer land ownership at the Land Registry Department.",
        "official_link": "https://www.lrdepd.gov.lk",
        "steps": [
            "Obtain a certified survey plan",
            "Prepare the deed with a licensed notary",
            "Submit the deed and survey plan to the Land Registry",
            "Pay the registration/stamp duty fee",
            "Collect the registered deed",
        ],
        "documents": [
            ("Original Deed", True),
            ("Survey Plan", True),
            ("NIC of Owner", True),
            ("Previous Title Documents", False),
        ],
    },
    {
        "name": "Driving License", "category": "Transport", "icon": "🚗",
        "description": "Apply for a new driving license or renew your existing one.",
        "official_link": "https://www.motortraffic.gov.lk",
        "steps": [
            "Complete a medical examination",
            "Pass the written/eye test",
            "Pass the practical driving test",
            "Submit application with required documents",
            "Collect your driving license",
        ],
        "documents": [
            ("NIC", True),
            ("Medical Certificate", True),
            ("Eye Test Report", True),
            ("Passport Size Photos", True),
        ],
    },
    {
        "name": "Police Clearance", "category": "Legal Documents", "icon": "👮",
        "description": "Obtain a Police Clearance Certificate for employment, visa, or migration purposes.",
        "official_link": "https://www.police.lk",
        "steps": [
            "Visit your nearest Police Station or Criminal Records Division",
            "Submit your NIC and two passport photos",
            "Fill the clearance request form",
            "Pay the processing fee",
            "Collect the certificate",
        ],
        "documents": [
            ("NIC", True),
            ("Passport Size Photos", True),
            ("Passport (if for overseas use)", False),
        ],
    },
    {
        "name": "Visa Information", "category": "Immigration", "icon": "🌍",
        "description": "Get information about visa categories, requirements, and application process.",
        "official_link": "https://www.immigration.gov.lk",
        "steps": [
            "Identify the correct visa category for your purpose",
            "Check document requirements on the official website",
            "Complete the online or embassy application",
            "Submit supporting documents",
            "Track your visa application status",
        ],
        "documents": [
            ("Valid Passport", True),
            ("Passport Size Photos", True),
            ("Supporting Letter (invitation/employment/study)", True),
            ("Bank Statement (if required)", False),
        ],
    },
]

OFFICIAL_LINKS = [
    ("Department for Registration of Persons", "https://www.drp.gov.lk", "Identity Documents", "🪪"),
    ("Department of Immigration & Emigration", "https://www.immigration.gov.lk", "Travel & Visa", "🛂"),
    ("Registrar General's Department", "https://www.rgd.gov.lk", "Civil Registration", "📋"),
    ("Land Registry Department", "https://www.lrdepd.gov.lk", "Property", "🏠"),
    ("Department of Motor Traffic", "https://www.motortraffic.gov.lk", "Transport", "🚗"),
    ("Sri Lanka Police", "https://www.police.lk", "Law & Order", "👮"),
    ("Legal Aid Commission", "https://www.legalaid.gov.lk", "Legal Assistance", "⚖️"),
]


def run():
    with app.app_context():
        if GovService.query.count() > 0:
            print("⚠️  Services already exist — skipping seed to avoid duplicates.")
            print("   (Delete services from Admin Panel first if you want to re-seed.)")
            return

        for svc in SERVICES:
            service = GovService(
                name=svc["name"], category=svc["category"], icon=svc["icon"],
                description=svc["description"], official_link=svc["official_link"],
                status="Active"
            )
            db.session.add(service)
            db.session.flush()  # get service.id before commit

            for i, step_title in enumerate(svc["steps"], start=1):
                db.session.add(ServiceStep(
                    service_id=service.id, step_number=i, title=step_title
                ))

            for doc_name, mandatory in svc["documents"]:
                db.session.add(RequiredDocument(
                    service_id=service.id, document_name=doc_name, is_mandatory=mandatory
                ))

        for title, url, dept, icon in OFFICIAL_LINKS:
            db.session.add(OfficialLink(title=title, url=url, department=dept, icon=icon))

        db.session.commit()
        print(f"✅ Seeded {len(SERVICES)} government services with steps & documents")
        print(f"✅ Seeded {len(OFFICIAL_LINKS)} official government links")


if __name__ == "__main__":
    run()
