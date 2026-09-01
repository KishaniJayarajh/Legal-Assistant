import os
from flask import Blueprint, render_template, request, jsonify, current_app, session
from flask_login import login_required, current_user
from extensions import db
from models.user import ChatHistory

chatbot = Blueprint('chatbot', __name__)

# ── TRILINGUAL FALLBACK KB ────────────────────────────────────────
# Each topic now has a "keywords" list covering English, Tamil, and
# Sinhala terms, since a citizen may type their question in any of the
# 3 languages. Previously only English keywords (e.g. "passport") were
# checked, so a Tamil/Sinhala question about the very same topic never
# matched and silently fell through to the generic default answer.
FALLBACK_KB = {
    "passport": {
        "keywords": ["passport", "பாஸ்போர்ட்", "விசா பத்திரம்", "விசா", "විදේශ ගමන් බලපත්‍ර", "පාස්පෝට්"],
        "English": "To apply for a passport: 1) Get Birth Certificate 2) Get GN letter 3) Fill application form 4) Submit to Immigration Department 5) Pay fee and collect. Official: https://www.immigration.gov.lk",
        "Tamil": "பாஸ்போர்ட் விண்ணப்பிக்க: 1) பிறப்பு சான்றிதழ் பெறுங்கள் 2) GN கடிதம் பெறுங்கள் 3) விண்ணப்பம் நிரப்புங்கள் 4) குடிவரவு திணைக்களத்தில் சமர்ப்பிக்கவும். இணையதளம்: https://www.immigration.gov.lk",
        "Sinhala": "විදේශ ගමන් බලපත්‍රය සඳහා: 1) උප්පැන්න සහතිකය 2) GN ලිපිය 3) අයදුම්පත පුරවන්න 4) ආගමන දෙපාර්තමේන්තුවට ඉදිරිපත් කරන්න. නිල: https://www.immigration.gov.lk",
    },
    "nic": {
        "keywords": ["nic", "national identity", "identity card", "அடையாள அட்டை", "தேசிய அடையாள", "හැඳුනුම්පත", "ජාතික හැඳුනුම්පත"],
        "English": "To apply for NIC: 1) Get Birth Certificate 2) Get GN Division letter 3) Fill NIC form 4) Submit to Divisional Secretariat. Official: https://www.drp.gov.lk",
        "Tamil": "NIC விண்ணப்பிக்க: 1) பிறப்பு சான்றிதழ் 2) GN பிரிவு கடிதம் 3) NIC படிவம் நிரப்புங்கள் 4) பிரிவு செயலகத்தில் சமர்ப்பிக்கவும். இணையதளம்: https://www.drp.gov.lk",
        "Sinhala": "NIC සඳහා: 1) උප්පැන්න සහතිකය 2) GN ලිපිය 3) NIC ෆෝරමය 4) ප්‍රාදේශීය ලේකම් කාර්යාලය. නිල: https://www.drp.gov.lk",
    },
    "birth certificate": {
        "keywords": ["birth certificate", "birth cert", "பிறப்பு சான்றிதழ்", "பிறப்பு சான்று", "උප්පැන්න සහතික"],
        "English": "For Birth Certificate: Visit Registrar General's Department or Divisional Secretariat with parent NIC and hospital birth record. Official: https://www.rgd.gov.lk",
        "Tamil": "பிறப்பு சான்றிதழுக்கு: பெற்றோர் NIC மற்றும் மருத்துவமனை பதிவுடன் பதிவாளர் திணைக்களம் செல்லவும். இணையதளம்: https://www.rgd.gov.lk",
        "Sinhala": "උප්පැන්න සහතිකය: දෙමාපියන්ගේ NIC සහ රෝහල් වාර්තාව සමඟ ලේඛනාරක්ෂක දෙපාර්තමේන්තුව. නිල: https://www.rgd.gov.lk",
    },
    "driving license": {
        "keywords": ["driving license", "driving licence", "driver's license", "ஓட்டுநர் உரிமம்", "ஓட்டுநர்", "රියදුරු බලපත්‍ර", "රියදුරු"],
        "English": "For Driving License: 1) Medical examination 2) Eye test 3) Written test 4) Practical test 5) Submit to Motor Traffic Department. Official: https://www.motortraffic.gov.lk",
        "Tamil": "ஓட்டுநர் உரிமத்திற்கு: 1) மருத்துவ பரிசோதனை 2) கண் பரிசோதனை 3) எழுத்துத் தேர்வு 4) நடைமுறை தேர்வு 5) மோட்டார் போக்குவரத்து திணைக்களம். இணையதளம்: https://www.motortraffic.gov.lk",
        "Sinhala": "රියදුරු බලපත්‍රය: 1) වෛද්‍ය පරීක්ෂණය 2) ඇස් පරීක්ෂණය 3) ලිඛිත පරීක්ෂණය 4) ප්‍රායෝගික පරීක්ෂණය 5) මෝටර් රථ දෙපාර්තමේන්තුව. නිල: https://www.motortraffic.gov.lk",
    },
    "marriage": {
        "keywords": ["marriage", "wedding", "திருமண சான்றிதழ்", "திருமணம்", "විවාහ සහතික", "විවාහ"],
        "English": "For Marriage Certificate: Visit Registrar of Marriages with both NICs, birth certificates and 2 witnesses. Official: https://www.rgd.gov.lk",
        "Tamil": "திருமண சான்றிதழுக்கு: இருவர் NIC, பிறப்பு சான்றிதழ் மற்றும் 2 சாட்சிகளுடன் திருமண பதிவாளரை சந்திக்கவும். இணையதளம்: https://www.rgd.gov.lk",
        "Sinhala": "විවාහ සහතිකය: NICs, උප්පැන්න සහතික සහ සාක්ෂිකරුවන් 2 සමඟ විවාහ ලේඛකාධිකාරී. නිල: https://www.rgd.gov.lk",
    },
    "land": {
        "keywords": ["land registration", "land registry", "land deed", "நில பதிவு", "பத்திரம்", "ඉඩම් ලියාපදිංචි", "ඔප්පු"],
        "English": "For Land Registration: Submit deed, survey plan and NIC to Land Registry Department. Official: https://www.lrdepd.gov.lk",
        "Tamil": "நில பதிவுக்கு: பத்திரம், நில அளவை திட்டம் மற்றும் NIC உடன் நில பதிவு திணைக்களம். இணையதளம்: https://www.lrdepd.gov.lk",
        "Sinhala": "ඉඩම් ලියාපදිංචිය: ඔප්පුව, මිනින්දෝරු සැලැස්ම සහ NIC සමඟ ඉඩම් ලේඛනාගාරය. නිල: https://www.lrdepd.gov.lk",
    },
    "police clearance": {
        "keywords": ["police clearance", "police report", "காவல்துறை அனுமதி", "பொலிஸ் சான்று", "පොලිස් නිරවුල්", "පොලිස්"],
        "English": "For Police Clearance: Visit nearest Police Station with NIC and 2 passport photos. Official: https://www.police.lk",
        "Tamil": "காவல்துறை அனுமதிக்கு: NIC மற்றும் 2 புகைப்படங்களுடன் காவல் நிலையம் செல்லவும். இணையதளம்: https://www.police.lk",
        "Sinhala": "පොලිස් නිරවුල් පත්‍රය: NIC සහ ඡායාරූප 2 සමඟ ආසන්නතම පොලිස් ස්ථානය. නිල: https://www.police.lk",
    },
    "legal aid": {
        "keywords": ["legal aid", "free legal", "lawyer", "சட்ட உதவி", "வழக்கறிஞர்", "නීති ආධාර", "නීතිඥ"],
        "English": "Legal Aid Commission provides free legal help. Visit: https://www.legalaid.gov.lk or call 011-2433618",
        "Tamil": "சட்ட உதவி ஆணையம் இலவச சட்ட உதவி வழங்குகிறது. இணையதளம்: https://www.legalaid.gov.lk அல்லது 011-2433618",
        "Sinhala": "නීති ආධාර කොමිසම නොමිලේ නීති සහාය. නිල: https://www.legalaid.gov.lk හෝ 011-2433618",
    },
    "default": {
        "English": "I am your Legal & Civic Assistant for Sri Lanka. I can help with NIC, Passport, Birth Certificate, Marriage Certificate, Land Registration, Driving License, Police Clearance and Legal Aid. Please ask your question.",
        "Tamil": "நான் உங்கள் இலங்கை சட்ட மற்றும் சிவில் உதவியாளர். NIC, பாஸ்போர்ட், பிறப்பு சான்றிதழ், திருமண சான்றிதழ், நில பதிவு, ஓட்டுநர் உரிமம், காவல்துறை அனுமதி பற்றி உதவ முடியும்.",
        "Sinhala": "මම ශ්‍රී ලංකාවේ ඔබේ නීති සහ සිවිල් සහායකයා. NIC, විදේශ ගමන් බලපත්‍රය, උප්පැන්න සහතිකය, ඉඩම් ලියාපදිංචිය, රියදුරු බලපත්‍රය ගැන සහාය දෙමි.",
    },
}


def get_fallback_response(question, language="English"):
    q = question.lower()
    for topic, data in FALLBACK_KB.items():
        if topic == "default":
            continue
        if any(kw.lower() in q for kw in data["keywords"]):
            return data.get(language, data["English"])
    return FALLBACK_KB["default"].get(language, FALLBACK_KB["default"]["English"])


def get_groq_response(question, language="English"):
    """
    Calls Groq API (free, fast llama3).
    Falls back to KB if key missing or API fails.
    """
    api_key = os.getenv('GROQ_API_KEY', '')

    if not api_key or api_key == 'YOUR_GROQ_API_KEY_HERE':
        return get_fallback_response(question, language)

    try:
        from groq import Groq
        client = Groq(api_key=api_key)

        system_prompt = (
            f"You are a Legal and Civic Service Assistant for Sri Lankan citizens. "
            f"Answer clearly and step by step about Sri Lanka government services "
            f"(NIC, Passport, Birth Certificate, Marriage Certificate, Land Registration, "
            f"Driving License, Police Clearance, Legal Aid, Visa). "
            f"Always respond in {language} language. "
            f"Keep answers concise and practical. "
            f"If unsure, advise the user to visit the official government website."
        )

        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": question}
            ],
            model="llama3-8b-8192",
            max_tokens=500,
            temperature=0.3,
        )

        return chat_completion.choices[0].message.content

    except Exception as e:
        print(f"Groq API error: {e}")
        return get_fallback_response(question, language)


@chatbot.route('/ai-chat')
@login_required
def chat_page():
    history = ChatHistory.query.filter_by(user_id=current_user.id)\
                  .order_by(ChatHistory.created_at.asc()).limit(30).all()
    api_key = os.getenv('GROQ_API_KEY', '')
    ai_active = bool(api_key) and api_key != 'YOUR_GROQ_API_KEY_HERE'
    return render_template('chatbot.html', history=history, ai_active=ai_active)


@chatbot.route('/ai-chat/ask', methods=['POST'])
@login_required
def ask():
    data = request.get_json()
    question = data.get('question', '').strip()
    language = session.get('language') or \
               current_user.preferred_language or 'English'

    if not question:
        return jsonify({'error': 'Empty question'}), 400

    answer = get_groq_response(question, language)

    chat = ChatHistory(
        user_id=current_user.id,
        question=question,
        response=answer,
        language=language
    )
    db.session.add(chat)
    db.session.commit()

    return jsonify({'response': answer})


@chatbot.route('/ai-chat/history')
@login_required
def get_history():
    history = ChatHistory.query.filter_by(user_id=current_user.id)\
                  .order_by(ChatHistory.created_at.desc()).all()
    return jsonify([{
        'question': c.question,
        'response': c.response,
        'created_at': c.created_at.strftime('%Y-%m-%d %H:%M')
    } for c in history])