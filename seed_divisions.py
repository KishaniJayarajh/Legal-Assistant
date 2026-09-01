"""
seed_divisions.py — Run once to populate nearest office data.
Usage: python seed_divisions.py
"""
from app import create_app
from extensions import db
from models.user import Division

app = create_app()

DIVISIONS = [
    # ── POLICE CLEARANCE ─────────────────────────────────────
    ("Police Clearance", "Colombo",
     "Colombo Fort Police Station",
     "Olcott Mawatha, Colombo 01", "011-2421111",
     6.9344, 79.8428),
    ("Police Clearance", "Gampaha",
     "Gampaha Police Station",
     "Station Road, Gampaha", "033-2222222",
     7.0917, 80.0000),
    ("Police Clearance", "Kandy",
     "Kandy Police Station",
     "Dalada Veediya, Kandy", "081-2222222",
     7.2906, 80.6337),
    ("Police Clearance", "Galle",
     "Galle Police Station",
     "Church Cross Street, Galle Fort", "091-2222222",
     6.0328, 80.2168),
    ("Police Clearance", "Matara",
     "Matara Police Station",
     "Main Street, Matara", "041-2222222",
     5.9549, 80.5550),
    ("Police Clearance", "Jaffna",
     "Jaffna Police Station",
     "Stanley Road, Jaffna", "021-2222222",
     9.6615, 80.0255),
    ("Police Clearance", "Kurunegala",
     "Kurunegala Police Station",
     "Rajapihilla Mawatha, Kurunegala", "037-2222222",
     7.4818, 80.3609),
    ("Police Clearance", "Anuradhapura",
     "Anuradhapura Police Station",
     "Maithripala Senanayake Mawatha, Anuradhapura",
     "025-2222222", 8.3114, 80.4037),
    ("Police Clearance", "Ratnapura",
     "Ratnapura Police Station",
     "Main Street, Ratnapura", "045-2222222",
     6.6828, 80.3992),
    ("Police Clearance", "Badulla",
     "Badulla Police Station",
     "Bandarawela Road, Badulla", "055-2222222",
     6.9934, 81.0550),
    ("Police Clearance", "Trincomalee",
     "Trincomalee Police Station",
     "Dockyard Road, Trincomalee", "026-2222222",
     8.5711, 81.2335),
    ("Police Clearance", "Batticaloa",
     "Batticaloa Police Station",
     "Bar Road, Batticaloa", "065-2222222",
     7.7170, 81.7000),

    # ── PASSPORT ─────────────────────────────────────────────
    # NOTE: The Dept. of Immigration & Emigration only operates 6 real
    # locations island-wide (Head Office + 5 regional offices). Every
    # other district's applicants travel to their nearest one of these —
    # we no longer invent a fake local office for districts that don't
    # actually have one.
    ("Passport Application", "Colombo",
     "Dept. of Immigration & Emigration - Head Office",
     "Suhurupaya, Battaramulla", "011-5329000",
     6.9101, 79.9185),
    ("Passport Application", "Kandy",
     "Immigration Office - Kandy",
     "DS Senanayake Veediya, Kandy", "081-2222333",
     7.2906, 80.6337),
    ("Passport Application", "Matara",
     "Immigration Regional Office - Matara",
     "Anagarika Dharmapala Mawatha, Matara", "041-2222333",
     5.9549, 80.5550),
    ("Passport Application", "Vavuniya",
     "Immigration Regional Office - Vavuniya",
     "Station Road, Vavuniya", "024-2222333",
     8.7514, 80.4971),
    ("Passport Application", "Kurunegala",
     "Immigration Regional Office - Kurunegala",
     "Rajapihilla Mawatha, Kurunegala", "037-2222333",
     7.4818, 80.3609),
    ("Passport Application", "Jaffna",
     "Immigration Office - Jaffna",
     "Hospital Road, Jaffna", "021-2222333",
     9.6615, 80.0255),

    # ── NIC APPLICATION (Divisional Secretariats — present islandwide) ─
    ("NIC Application", "Colombo",
     "Dept. for Registration of Persons - Colombo",
     "369 Baudhaloka Mawatha, Colombo 07", "011-2690151",
     6.9166, 79.8674),
    ("NIC Application", "Gampaha",
     "Divisional Secretariat - Gampaha",
     "Station Road, Gampaha", "033-2222444",
     7.0917, 80.0000),
    ("NIC Application", "Kandy",
     "Divisional Secretariat - Kandy",
     "DS Senanayake Veediya, Kandy", "081-2222444",
     7.2906, 80.6337),
    ("NIC Application", "Galle",
     "Divisional Secretariat - Galle",
     "Gamini Mawatha, Galle", "091-2222444",
     6.0535, 80.2210),
    ("NIC Application", "Jaffna",
     "Divisional Secretariat - Jaffna",
     "Hospital Road, Jaffna", "021-2222444",
     9.6615, 80.0255),
    ("NIC Application", "Trincomalee",
     "Divisional Secretariat - Trincomalee",
     "Court Road, Trincomalee", "026-2222444",
     8.5711, 81.2335),
    ("NIC Application", "Batticaloa",
     "Divisional Secretariat - Batticaloa",
     "Bar Road, Batticaloa", "065-2222444",
     7.7170, 81.7000),

    # ── BIRTH CERTIFICATE ─────────────────────────────────────
    ("Birth Certificate", "Colombo",
     "Registrar General's Dept - Colombo",
     "234 Deans Road, Colombo 10", "011-2693591",
     6.9215, 79.8650),
    ("Birth Certificate", "Kandy",
     "Registrar Office - Kandy",
     "DS Senanayake Veediya, Kandy", "081-2222555",
     7.2906, 80.6337),
    ("Birth Certificate", "Galle",
     "Registrar Office - Galle",
     "Gamini Mawatha, Galle", "091-2222555",
     6.0535, 80.2210),
    ("Birth Certificate", "Trincomalee",
     "Registrar Office - Trincomalee",
     "Court Road, Trincomalee", "026-2222555",
     8.5711, 81.2335),

    # ── DRIVING LICENSE ───────────────────────────────────────
    ("Driving License", "Colombo",
     "Dept. of Motor Traffic - Colombo",
     "341 Elvitigala Mawatha, Colombo 05", "011-2694601",
     6.9016, 79.8737),
    ("Driving License", "Kandy",
     "Motor Traffic Office - Kandy",
     "Peradeniya Road, Kandy", "081-2222666",
     7.2906, 80.6337),
    ("Driving License", "Galle",
     "Motor Traffic Office - Galle",
     "Gamini Mawatha, Galle", "091-2222666",
     6.0535, 80.2210),
    ("Driving License", "Jaffna",
     "Motor Traffic Office - Jaffna",
     "Stanley Road, Jaffna", "021-2222666",
     9.6615, 80.0255),
    ("Driving License", "Trincomalee",
     "Motor Traffic Office - Trincomalee",
     "Dockyard Road, Trincomalee", "026-2222666",
     8.5711, 81.2335),
    ("Driving License", "Anuradhapura",
     "Motor Traffic Office - Anuradhapura",
     "Maithripala Senanayake Mawatha, Anuradhapura", "025-2222666",
     8.3114, 80.4037),

    # ── MARRIAGE CERTIFICATE ──────────────────────────────────
    ("Marriage Certificate", "Colombo",
     "Registrar of Marriages - Colombo",
     "234 Deans Road, Colombo 10", "011-2693591",
     6.9215, 79.8650),
    ("Marriage Certificate", "Kandy",
     "Registrar of Marriages - Kandy",
     "DS Senanayake Veediya, Kandy", "081-2222777",
     7.2906, 80.6337),
    ("Marriage Certificate", "Galle",
     "Registrar of Marriages - Galle",
     "Gamini Mawatha, Galle", "091-2222777",
     6.0535, 80.2210),
    ("Marriage Certificate", "Trincomalee",
     "Registrar of Marriages - Trincomalee",
     "Court Road, Trincomalee", "026-2222777",
     8.5711, 81.2335),

    # ── LAND REGISTRATION ────────────────────────────────────
    ("Land Registration", "Colombo",
     "Land Registry - Colombo",
     "Kings Court, Hulftsdorp Street, Colombo 12",
     "011-2433549", 6.9344, 79.8560),
    ("Land Registration", "Kandy",
     "Land Registry - Kandy",
     "DS Senanayake Veediya, Kandy", "081-2222888",
     7.2906, 80.6337),
    ("Land Registration", "Galle",
     "Land Registry - Galle",
     "Gamini Mawatha, Galle", "091-2222888",
     6.0535, 80.2210),
    ("Land Registration", "Trincomalee",
     "Land Registry - Trincomalee",
     "Court Road, Trincomalee", "026-2222888",
     8.5711, 81.2335),
]

ALL_DISTRICTS = [
    "Colombo", "Gampaha", "Kalutara", "Kandy", "Matale",
    "Nuwara Eliya", "Galle", "Matara", "Hambantota",
    "Jaffna", "Kilinochchi", "Mannar", "Vavuniya", "Mullaitivu",
    "Batticaloa", "Ampara", "Trincomalee", "Kurunegala",
    "Puttalam", "Anuradhapura", "Polonnaruwa", "Badulla",
    "Moneragala", "Ratnapura", "Kegalle"
]


def run():
    with app.app_context():
        db.create_all()
        existing = Division.query.count()
        if existing > 0:
            print(f"Found {existing} existing division rows — clearing and re-seeding with updated data...")
            Division.query.delete()
            db.session.commit()
        for svc, district, name, addr, phone, lat, lng in DIVISIONS:
            db.session.add(Division(
                service=svc, district=district,
                office_name=name, address=addr,
                phone=phone, lat=lat, lng=lng
            ))
        db.session.commit()
        print(f"Seeded {len(DIVISIONS)} division offices.")


if __name__ == "__main__":
    run()