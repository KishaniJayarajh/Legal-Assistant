"""
knowledge_base.py — Trilingual fallback knowledge base for the AI Chat
Assistant.

This is used automatically whenever the Groq API is unavailable (no key
configured, or the API call fails), so the chatbot must still be able to
give a genuinely useful, specific answer rather than a generic default.

Design:
  1. SERVICE_KB holds structured data (steps, documents, eligibility,
     official link) for every one of the 8 services actually listed in
     seed_data.py, translated into English / Tamil / Sinhala.
  2. Fee and processing-time figures are pulled directly from
     fees_data.py so the chatbot never contradicts the Fees & Processing
     Time card shown on the service detail page.
  3. INTENT_KEYWORDS lets the bot detect *what kind* of question is being
     asked (fee / documents / steps / eligibility / processing time /
     office) in any of the 3 languages, so "passport fee" and "பாஸ்போர்ட்
     கட்டணம்" both correctly return just the fee, not the whole guide.
  4. WEBSITE_FAQ answers meta-questions about how to use the site itself
     (Eligibility Checker, nearest-office locator, language switch, etc.)
  5. get_fallback_response() ties it all together: greeting/thanks check
     -> FAQ check -> service detection -> intent detection -> compose.
"""
import re
from fees_data import get_fee_info

# ─────────────────────────────────────────────────────────────────
# SERVICE KNOWLEDGE BASE
# Keys match GovService.name exactly, as seeded in seed_data.py.
# ─────────────────────────────────────────────────────────────────
SERVICE_KB = {

    "NIC Application": {
        "keywords": ["nic", "national identity", "identity card",
                     "அடையாள அட்டை", "தேசிய அடையாள", "என்ஐசி",
                     "හැඳුනුම්පත", "ජාතික හැඳුනුම්පත"],
        "official_link": "https://www.drp.gov.lk",
        "eligibility": {
            "English": "Sri Lankan citizens aged 16 or older, with a birth certificate, are generally eligible to apply for an NIC.",
            "Tamil": "இலங்கைக் குடியுரிமை பெற்ற 16 வயது அல்லது அதற்கு மேற்பட்டவர்கள், பிறப்புச் சான்றிதழுடன், பொதுவாக NIC-க்கு விண்ணப்பிக்கத் தகுதியுடையவர்கள்.",
            "Sinhala": "වයස අවුරුදු 16ට වැඩි ශ්‍රී ලාංකික පුරවැසියන්, උප්පැන්න සහතිකයක් සමඟ, සාමාන්‍යයෙන් NIC සඳහා අයදුම් කිරීමට සුදුසුකම් ලබයි.",
        },
        "steps": {
            "English": ["Obtain your Birth Certificate", "Get a Grama Niladhari (GN) Division letter",
                        "Fill the NIC application form", "Submit the documents to the Divisional Secretariat (DS) office",
                        "Collect your NIC after the processing period"],
            "Tamil": ["உங்கள் பிறப்புச் சான்றிதழைப் பெறுங்கள்", "கிராம சேவகர் (GN) பிரிவு கடிதம் பெறுங்கள்",
                       "NIC விண்ணப்பப் படிவத்தை நிரப்புங்கள்", "ஆவணங்களை பிரதேச செயலகத்தில் (DS) சமர்ப்பிக்கவும்",
                       "செயலாக்க காலத்திற்குப் பிறகு உங்கள் NIC-ஐ பெற்றுக்கொள்ளுங்கள்"],
            "Sinhala": ["ඔබේ උප්පැන්න සහතිකය ලබාගන්න", "ග්‍රාම නිලධාරී (GN) කොට්ඨාශ ලිපියක් ලබාගන්න",
                        "NIC අයදුම්පත පුරවන්න", "ලේඛන ප්‍රාදේශීය ලේකම් (DS) කාර්යාලයට ඉදිරිපත් කරන්න",
                        "සැකසුම් කාලයෙන් පසු ඔබේ NIC ලබාගන්න"],
        },
        "documents": {
            "English": [("Birth Certificate (Original)", True), ("Grama Niladhari Letter", True),
                        ("Completed Application Form", True), ("Passport Size Photo", True),
                        ("Any other supporting documents (if required)", False)],
            "Tamil": [("பிறப்புச் சான்றிதழ் (மூலப் பிரதி)", True), ("கிராம சேவகர் கடிதம்", True),
                      ("பூர்த்தி செய்யப்பட்ட விண்ணப்பப் படிவம்", True), ("பாஸ்போர்ட் அளவு புகைப்படம்", True),
                      ("தேவைப்பட்டால் பிற ஆதரவு ஆவணங்கள்", False)],
            "Sinhala": [("උප්පැන්න සහතිකය (මුල් පිටපත)", True), ("ග්‍රාම නිලධාරී ලිපිය", True),
                        ("සම්පූර්ණ කළ අයදුම්පත", True), ("විදේශ ගමන් බලපත්‍ර ප්‍රමාණයේ ඡායාරූපය", True),
                        ("අවශ්‍ය නම් වෙනත් අනුබද්ධ ලේඛන", False)],
        },
    },

    "Passport Application": {
        "keywords": ["passport", "பாஸ்போர்ட்", "பாஸ்போர்", "විදේශ ගමන් බලපත්‍ර", "පාස්පෝට්"],
        "official_link": "https://www.immigration.gov.lk",
        "eligibility": {
            "English": "Any Sri Lankan citizen holding a valid NIC and birth certificate can apply for a passport.",
            "Tamil": "செல்லுபடியாகும் NIC மற்றும் பிறப்புச் சான்றிதழ் வைத்திருக்கும் எந்த இலங்கைக் குடிமகனும் பாஸ்போர்ட்டுக்கு விண்ணப்பிக்கலாம்.",
            "Sinhala": "වලංගු NIC සහ උප්පැන්න සහතිකයක් ඇති ඕනෑම ශ්‍රී ලාංකික පුරවැසියෙකුට විදේශ ගමන් බලපත්‍රයක් සඳහා අයදුම් කළ හැක.",
        },
        "steps": {
            "English": ["Obtain your Birth Certificate", "Get a Grama Niladhari (GN) letter",
                        "Fill the passport application form online or in person",
                        "Submit documents to the Department of Immigration & Emigration",
                        "Pay the application fee and collect your passport"],
            "Tamil": ["உங்கள் பிறப்புச் சான்றிதழைப் பெறுங்கள்", "கிராம சேவகர் (GN) கடிதம் பெறுங்கள்",
                       "பாஸ்போர்ட் விண்ணப்பப் படிவத்தை ஆன்லைனில் அல்லது நேரடியாக நிரப்புங்கள்",
                       "குடிவரவு & குடியகல்வுத் திணைக்களத்தில் ஆவணங்களைச் சமர்ப்பிக்கவும்",
                       "விண்ணப்பக் கட்டணத்தைச் செலுத்தி உங்கள் பாஸ்போர்ட்டைப் பெற்றுக்கொள்ளுங்கள்"],
            "Sinhala": ["ඔබේ උප්පැන්න සහතිකය ලබාගන්න", "ග්‍රාම නිලධාරී (GN) ලිපියක් ලබාගන්න",
                        "විදේශ ගමන් බලපත්‍ර අයදුම්පත මාර්ගගතව හෝ පෞද්ගලිකව පුරවන්න",
                        "ආගමන හා විගමන දෙපාර්තමේන්තුවට ලේඛන ඉදිරිපත් කරන්න",
                        "අයදුම්පත් ගාස්තුව ගෙවා ඔබේ විදේශ ගමන් බලපත්‍රය ලබාගන්න"],
        },
        "documents": {
            "English": [("Birth Certificate", True), ("NIC (Original + Copy)", True),
                        ("Passport Size Photos", True), ("Previous Passport (for renewal)", False)],
            "Tamil": [("பிறப்புச் சான்றிதழ்", True), ("தேசிய அடையாள அட்டை (மூலம் + நகல்)", True),
                      ("பாஸ்போர்ட் அளவு புகைப்படங்கள்", True), ("முந்தைய பாஸ்போர்ட் (புதுப்பிப்புக்கு)", False)],
            "Sinhala": [("උප්පැන්න සහතිකය", True), ("ජාතික හැඳුනුම්පත (මුල් + පිටපත)", True),
                        ("විදේශ ගමන් බලපත්‍ර ප්‍රමාණයේ ඡායාරූප", True), ("පෙර විදේශ ගමන් බලපත්‍රය (අලුත් කිරීම සඳහා)", False)],
        },
    },

    "Birth Certificate": {
        "keywords": ["birth certificate", "birth cert", "பிறப்பு சான்றிதழ்", "பிறப்பு சான்று",
                     "பிறப்புச் சான்றிதழ்", "උප්පැන්න සහතික"],
        "official_link": "https://www.rgd.gov.lk",
        "eligibility": {
            "English": "Anyone born in Sri Lanka, or their parent/guardian on their behalf, can request a birth certificate.",
            "Tamil": "இலங்கையில் பிறந்த எவரும், அல்லது அவர்களின் சார்பாக பெற்றோர்/பாதுகாவலர், பிறப்புச் சான்றிதழைக் கோரலாம்.",
            "Sinhala": "ශ්‍රී ලංකාවේ උපත ලැබූ ඕනෑම අයෙකුට, හෝ ඔවුන් වෙනුවෙන් දෙමාපියෙකු/භාරකරුවෙකුට උප්පැන්න සහතිකයක් ඉල්ලීමට හැක.",
        },
        "steps": {
            "English": ["Visit the Registrar General's Department or nearest Divisional Secretariat",
                        "Submit the parent's NIC and hospital birth record", "Fill the request form",
                        "Pay the certified copy fee", "Collect the certificate"],
            "Tamil": ["பதிவாளர் நாயகம் திணைக்களம் அல்லது அருகிலுள்ள பிரதேச செயலகத்திற்குச் செல்லுங்கள்",
                       "பெற்றோரின் NIC மற்றும் மருத்துவமனை பிறப்புப் பதிவைச் சமர்ப்பிக்கவும்",
                       "கோரிக்கைப் படிவத்தை நிரப்புங்கள்", "சான்று நகல் கட்டணத்தைச் செலுத்துங்கள்",
                       "சான்றிதழைப் பெற்றுக்கொள்ளுங்கள்"],
            "Sinhala": ["රෙජිස්ට්‍රාර් ජනරාල් දෙපාර්තමේන්තුව හෝ ආසන්නතම ප්‍රාදේශීය ලේකම් කාර්යාලයට යන්න",
                        "දෙමාපියන්ගේ NIC සහ රෝහල් උප්පැන්න වාර්තාව ඉදිරිපත් කරන්න", "ඉල්ලුම් පත්‍රය පුරවන්න",
                        "සහතික කළ පිටපත් ගාස්තුව ගෙවන්න", "සහතිකය ලබාගන්න"],
        },
        "documents": {
            "English": [("Parent's NIC", True), ("Hospital Birth Record", True),
                        ("Marriage Certificate of Parents (if applicable)", False)],
            "Tamil": [("பெற்றோரின் தேசிய அடையாள அட்டை", True), ("மருத்துவமனை பிறப்புப் பதிவு", True),
                      ("பெற்றோரின் திருமணச் சான்றிதழ் (பொருந்தினால்)", False)],
            "Sinhala": [("දෙමාපියන්ගේ ජාතික හැඳුනුම්පත", True), ("රෝහල් උප්පැන්න වාර්තාව", True),
                        ("දෙමාපියන්ගේ විවාහ සහතිකය (අදාළ නම්)", False)],
        },
    },

    "Marriage Certificate": {
        "keywords": ["marriage", "wedding", "திருமண சான்றிதழ்", "திருமணச் சான்றிதழ்", "திருமணம்",
                     "විවාහ සහතික", "විවාහ"],
        "official_link": "https://www.rgd.gov.lk",
        "eligibility": {
            "English": "Both parties must be of legal marriageable age (18+, or 16+ with parental/court consent) and not already married.",
            "Tamil": "இரு தரப்பினரும் சட்டப்பூர்வ திருமண வயதை (18+, அல்லது பெற்றோர்/நீதிமன்ற ஒப்புதலுடன் 16+) அடைந்திருக்க வேண்டும், ஏற்கனவே திருமணமாகி இருக்கக்கூடாது.",
            "Sinhala": "දෙපාර්ශවයම නීතිමය විවාහ වයස (අවුරුදු 18+, හෝ දෙමාපිය/උසාවි කැමැත්තෙන් 16+) ළඟා වී තිබිය යුතුය, දැනටමත් විවාහ වී නොතිබිය යුතුය.",
        },
        "steps": {
            "English": ["Visit the Registrar of Marriages in your area", "Submit both parties' NICs and birth certificates",
                        "Provide two witnesses", "Complete the registration", "Collect the marriage certificate"],
            "Tamil": ["உங்கள் பகுதியில் உள்ள திருமணப் பதிவாளரைச் சந்திக்கவும்",
                       "இரு தரப்பினரின் NIC மற்றும் பிறப்புச் சான்றிதழ்களைச் சமர்ப்பிக்கவும்",
                       "இரு சாட்சிகளை வழங்குங்கள்", "பதிவை முடிக்கவும்", "திருமணச் சான்றிதழைப் பெற்றுக்கொள்ளுங்கள்"],
            "Sinhala": ["ඔබේ ප්‍රදේශයේ විවාහ ලේඛකාධිකාරී වෙත යන්න",
                        "දෙපාර්ශවයේම NIC සහ උප්පැන්න සහතික ඉදිරිපත් කරන්න",
                        "සාක්ෂිකරුවන් දෙදෙනෙකු ලබාදෙන්න", "ලියාපදිංචිය සම්පූර්ණ කරන්න", "විවාහ සහතිකය ලබාගන්න"],
        },
        "documents": {
            "English": [("NIC of both parties", True), ("Birth Certificates", True),
                        ("Witness NICs", True), ("Divorce Certificate (if previously married)", False)],
            "Tamil": [("இரு தரப்பினரின் தேசிய அடையாள அட்டை", True), ("பிறப்புச் சான்றிதழ்கள்", True),
                      ("சாட்சிகளின் அடையாள அட்டைகள்", True), ("விவாகரத்துச் சான்றிதழ் (முன்பு திருமணமானால்)", False)],
            "Sinhala": [("දෙපාර්ශවයේම ජාතික හැඳුනුම්පත්", True), ("උප්පැන්න සහතික", True),
                        ("සාක්ෂිකරුවන්ගේ හැඳුනුම්පත්", True), ("දික්කසාද සහතිකය (කලින් විවාහ වී ඇත්නම්)", False)],
        },
    },

    "Land Registration": {
        "keywords": ["land registration", "land registry", "land deed", "நில பதிவு", "பத்திரம்",
                     "நிலப் பதிவு", "ඉඩම් ලියාපදිංචි", "ඔප්පු"],
        "official_link": "https://www.lrdepd.gov.lk",
        "eligibility": {
            "English": "The registered owner, or their legal representative with proper authorization, can register or transfer land.",
            "Tamil": "பதிவு செய்யப்பட்ட உரிமையாளர், அல்லது சரியான அங்கீகாரம் பெற்ற அவரது சட்டப் பிரதிநிதி, நிலத்தைப் பதிவு செய்யலாம் அல்லது மாற்றலாம்.",
            "Sinhala": "ලියාපදිංචි හිමිකරු, හෝ නිසි බලය ලත් ඔවුන්ගේ නීතිමය නියෝජිතයාට, ඉඩම ලියාපදිංචි කිරීමට හෝ මාරු කිරීමට හැක.",
        },
        "steps": {
            "English": ["Obtain a certified survey plan", "Prepare the deed with a licensed notary",
                        "Submit the deed and survey plan to the Land Registry", "Pay the registration/stamp duty fee",
                        "Collect the registered deed"],
            "Tamil": ["சான்றளிக்கப்பட்ட அளவைத் திட்டத்தைப் பெறுங்கள்", "உரிமம் பெற்ற notary மூலம் பத்திரத்தைத் தயாரிக்கவும்",
                       "பத்திரம் மற்றும் அளவைத் திட்டத்தை நிலப் பதிவகத்தில் சமர்ப்பிக்கவும்",
                       "பதிவு/முத்திரைத் தீர்வைக் கட்டணத்தைச் செலுத்துங்கள்", "பதிவு செய்யப்பட்ட பத்திரத்தைப் பெற்றுக்கொள்ளுங்கள்"],
            "Sinhala": ["සහතික කළ මිනින්දෝරු සැලැස්මක් ලබාගන්න", "බලපත්‍රලාභී නොතාරිස්වරයෙකු මගින් ඔප්පුව සකස් කරන්න",
                        "ඔප්පුව සහ මිනින්දෝරු සැලැස්ම ඉඩම් ලේඛනාගාරයට ඉදිරිපත් කරන්න", "ලියාපදිංචි/මුද්දර ගාස්තුව ගෙවන්න",
                        "ලියාපදිංචි කළ ඔප්පුව ලබාගන්න"],
        },
        "documents": {
            "English": [("Original Deed", True), ("Survey Plan", True),
                        ("NIC of Owner", True), ("Previous Title Documents", False)],
            "Tamil": [("அசல் பத்திரம்", True), ("அளவை திட்டம்", True),
                      ("உரிமையாளரின் அடையாள அட்டை", True), ("முந்தைய உரிமை ஆவணங்கள்", False)],
            "Sinhala": [("මුල් ඔප්පුව", True), ("මිනින්දෝරු සැලැස්ම", True),
                        ("හිමිකරුගේ හැඳුනුම්පත", True), ("පෙර හිමිකම් ලේඛන", False)],
        },
    },

    "Driving License": {
        "keywords": ["driving license", "driving licence", "driver's license", "ஓட்டுநர் உரிமம்",
                     "ஓட்டுநர்", "රියදුරු බලපත්‍ර", "රියදුරු"],
        "official_link": "https://www.motortraffic.gov.lk",
        "eligibility": {
            "English": "Applicants must be at least 18 years old (16 for motorcycles under 100cc) and pass the medical, written and practical tests.",
            "Tamil": "விண்ணப்பதாரர்கள் குறைந்தது 18 வயது (100cc க்கும் குறைவான மோட்டார் சைக்கிள்களுக்கு 16 வயது) ஆக இருக்க வேண்டும், மருத்துவ, எழுத்து மற்றும் நடைமுறைத் தேர்வுகளில் தேர்ச்சி பெற வேண்டும்.",
            "Sinhala": "අයදුම්කරුවන් අවම වශයෙන් වයස අවුරුදු 18ක් විය යුතුය (100cc ට අඩු මෝටර් සයිකල් සඳහා 16), වෛද්‍ය, ලිඛිත සහ ප්‍රායෝගික පරීක්ෂණ සමත් විය යුතුය.",
        },
        "steps": {
            "English": ["Complete a medical examination", "Pass the written/eye test",
                        "Pass the practical driving test", "Submit application with required documents",
                        "Collect your driving license"],
            "Tamil": ["மருத்துவப் பரிசோதனையை முடிக்கவும்", "எழுத்து/கண் பரிசோதனையில் தேர்ச்சி பெறுங்கள்",
                       "நடைமுறை ஓட்டுதல் தேர்வில் தேர்ச்சி பெறுங்கள்", "தேவையான ஆவணங்களுடன் விண்ணப்பத்தைச் சமர்ப்பிக்கவும்",
                       "உங்கள் ஓட்டுநர் உரிமத்தைப் பெற்றுக்கொள்ளுங்கள்"],
            "Sinhala": ["වෛද්‍ය පරීක්ෂණයක් සම්පූර්ණ කරන්න", "ලිඛිත/ඇස් පරීක්ෂණය සමත් වන්න",
                        "ප්‍රායෝගික රිය පැදවීමේ පරීක්ෂණය සමත් වන්න", "අවශ්‍ය ලේඛන සමඟ අයදුම්පත ඉදිරිපත් කරන්න",
                        "ඔබේ රියදුරු බලපත්‍රය ලබාගන්න"],
        },
        "documents": {
            "English": [("NIC", True), ("Medical Certificate", True),
                        ("Eye Test Report", True), ("Passport Size Photos", True)],
            "Tamil": [("தேசிய அடையாள அட்டை", True), ("மருத்துவச் சான்றிதழ்", True),
                      ("கண் பரிசோதனை அறிக்கை", True), ("பாஸ்போர்ட் அளவு புகைப்படங்கள்", True)],
            "Sinhala": [("ජාතික හැඳුනුම්පත", True), ("වෛද්‍ය සහතිකය", True),
                        ("ඇස් පරීක්ෂණ වාර්තාව", True), ("විදේශ ගමන් බලපත්‍ර ප්‍රමාණයේ ඡායාරූප", True)],
        },
    },

    "Police Clearance": {
        "keywords": ["police clearance", "police report", "காவல்துறை அனுமதி", "பொலிஸ் சான்று",
                     "காவல் அனுமதி", "පොලිස් නිරවුල්", "පොලිස්"],
        "official_link": "https://www.police.lk",
        "eligibility": {
            "English": "Any Sri Lankan citizen or resident with a valid NIC can request a Police Clearance Certificate.",
            "Tamil": "செல்லுபடியாகும் NIC வைத்திருக்கும் எந்த இலங்கைக் குடிமகனும் அல்லது வதிவிடம் உள்ளவரும் காவல்துறை அனுமதிச் சான்றிதழைக் கோரலாம்.",
            "Sinhala": "වලංගු NIC එකක් ඇති ඕනෑම ශ්‍රී ලාංකික පුරවැසියෙකුට හෝ පදිංචිකරුවෙකුට පොලිස් නිරවුල් සහතිකයක් ඉල්ලීමට හැක.",
        },
        "steps": {
            "English": ["Visit your nearest Police Station or Criminal Records Division",
                        "Submit your NIC and two passport photos", "Fill the clearance request form",
                        "Pay the processing fee", "Collect the certificate"],
            "Tamil": ["அருகிலுள்ள காவல் நிலையம் அல்லது குற்றப் பதிவுப் பிரிவிற்குச் செல்லுங்கள்",
                       "உங்கள் NIC மற்றும் இரண்டு பாஸ்போர்ட் புகைப்படங்களைச் சமர்ப்பிக்கவும்",
                       "அனுமதிக் கோரிக்கைப் படிவத்தை நிரப்புங்கள்", "செயலாக்கக் கட்டணத்தைச் செலுத்துங்கள்",
                       "சான்றிதழைப் பெற்றுக்கொள்ளுங்கள்"],
            "Sinhala": ["ඔබේ ආසන්නතම පොලිස් ස්ථානය හෝ අපරාධ වාර්තා අංශයට යන්න",
                        "ඔබේ NIC සහ ඡායාරූප දෙකක් ඉදිරිපත් කරන්න", "නිරවුල් පත්‍ර ඉල්ලුම් පත්‍රය පුරවන්න",
                        "සැකසුම් ගාස්තුව ගෙවන්න", "සහතිකය ලබාගන්න"],
        },
        "documents": {
            "English": [("NIC", True), ("Passport Size Photos", True), ("Passport (if for overseas use)", False)],
            "Tamil": [("தேசிய அடையாள அட்டை", True), ("பாஸ்போர்ட் அளவு புகைப்படங்கள்", True),
                      ("பாஸ்போர்ட் (வெளிநாட்டு பயன்பாட்டுக்கு)", False)],
            "Sinhala": [("ජාතික හැඳුනුම්පත", True), ("විදේශ ගමන් බලපත්‍ර ප්‍රමාණයේ ඡායාරූප", True),
                        ("විදේශ ගමන් බලපත්‍රය (විදේශ භාවිතය සඳහා)", False)],
        },
    },

    "Visa Information": {
        "keywords": ["visa", "விசா", "வீசா", "වීසා"],
        "official_link": "https://www.immigration.gov.lk",
        "eligibility": {
            "English": "Eligibility depends on the specific visa category (tourist, work, student, etc.) - check the requirements for your intended purpose.",
            "Tamil": "தகுதி குறிப்பிட்ட விசா வகையைப் பொறுத்தது (சுற்றுலா, வேலை, மாணவர் போன்றவை) - உங்கள் நோக்கத்திற்கான தேவைகளைச் சரிபார்க்கவும்.",
            "Sinhala": "සුදුසුකම රඳා පවතින්නේ නිශ්චිත වීසා කාණ්ඩය මත ය (සංචාරක, රැකියා, ශිෂ්‍ය ආදිය) - ඔබේ අරමුණ සඳහා අවශ්‍යතා පරීක්ෂා කරන්න.",
        },
        "steps": {
            "English": ["Identify the correct visa category for your purpose", "Check document requirements on the official website",
                        "Complete the online or embassy application", "Submit supporting documents",
                        "Track your visa application status"],
            "Tamil": ["உங்கள் நோக்கத்திற்கான சரியான விசா வகையை அடையாளம் காணவும்",
                       "அதிகாரப்பூர்வ இணையதளத்தில் ஆவணத் தேவைகளைச் சரிபார்க்கவும்",
                       "ஆன்லைன் அல்லது தூதரக விண்ணப்பத்தை முடிக்கவும்", "ஆதரவு ஆவணங்களைச் சமர்ப்பிக்கவும்",
                       "உங்கள் விசா விண்ணப்ப நிலையைக் கண்காணிக்கவும்"],
            "Sinhala": ["ඔබේ අරමුණට නිවැරදි වීසා කාණ්ඩය හඳුනාගන්න", "නිල වෙබ් අඩවියේ ලේඛන අවශ්‍යතා පරීක්ෂා කරන්න",
                        "මාර්ගගත හෝ තානාපති කාර්යාල අයදුම්පත සම්පූර්ණ කරන්න", "අනුබද්ධ ලේඛන ඉදිරිපත් කරන්න",
                        "ඔබේ වීසා අයදුම්පත් තත්ත්වය නිරීක්ෂණය කරන්න"],
        },
        "documents": {
            "English": [("Valid Passport", True), ("Passport Size Photos", True),
                        ("Supporting Letter (invitation/employment/study)", True), ("Bank Statement (if required)", False)],
            "Tamil": [("செல்லுபடியாகும் பாஸ்போர்ட்", True), ("பாஸ்போர்ட் அளவு புகைப்படங்கள்", True),
                      ("ஆதரவுக் கடிதம் (அழைப்பு/வேலை/படிப்பு)", True), ("வங்கிக் கணக்கு அறிக்கை (தேவைப்பட்டால்)", False)],
            "Sinhala": [("වලංගු විදේශ ගමන් බලපත්‍රය", True), ("විදේශ ගමන් බලපත්‍ර ප්‍රමාණයේ ඡායාරූප", True),
                        ("අනුබද්ධ ලිපිය (ආරාධනාව/රැකියාව/අධ්‍යාපනය)", True), ("බැංකු ප්‍රකාශනය (අවශ්‍ය නම්)", False)],
        },
        # Visa fees vary by embassy/category and aren't in fees_data.py
        "custom_fee": {
            "English": "Varies by visa category and destination country/embassy - check with the relevant embassy or https://www.immigration.gov.lk for exact charges.",
            "Tamil": "விசா வகை மற்றும் இலக்கு நாடு/தூதரகத்தைப் பொறுத்து மாறுபடும் - சரியான கட்டணங்களுக்கு தொடர்புடைய தூதரகம் அல்லது https://www.immigration.gov.lk ஐப் பார்க்கவும்.",
            "Sinhala": "වීසා කාණ්ඩය සහ ගමනාන්ත රට/තානාපති කාර්යාලය අනුව වෙනස් වේ - නිවැරදි ගාස්තු සඳහා අදාළ තානාපති කාර්යාලය හෝ https://www.immigration.gov.lk බලන්න.",
        },
        "custom_time": {
            "English": "Varies by visa category and embassy - typically a few days to a few weeks.",
            "Tamil": "விசா வகை மற்றும் தூதரகத்தைப் பொறுத்து மாறுபடும் - பொதுவாக சில நாட்கள் முதல் சில வாரங்கள் வரை.",
            "Sinhala": "වීසා කාණ්ඩය සහ තානාපති කාර්යාලය අනුව වෙනස් වේ - සාමාන්‍යයෙන් දින කිහිපයක සිට සති කිහිපයක් දක්වා.",
        },
    },
}

# ─────────────────────────────────────────────────────────────────
# INTENT KEYWORDS — what KIND of question is being asked
# ─────────────────────────────────────────────────────────────────
INTENT_KEYWORDS = {
    "fee": {
        "English": [r"\bfee\b", r"\bfees\b", r"\bcost\b", r"\bprice\b", r"\bcharge\b", r"how much"],
        "Tamil": ["கட்டணம்", "விலை", "எவ்வளவு பணம்", "செலவு"],
        "Sinhala": ["ගාස්තු", "ගාස්තුව", "මිල", "කීයද"],
    },
    "documents": {
        "English": [r"\bdocument\b", r"\bdocuments\b", r"\brequired\b", r"\bneed\b", r"\bpapers\b", r"\bchecklist\b"],
        "Tamil": ["ஆவணங்கள்", "ஆவணம்", "தேவையான", "காகிதங்கள்"],
        "Sinhala": ["ලේඛන", "අවශ්‍ය", "ලියකියවිලි"],
    },
    "steps": {
        "English": [r"\bsteps?\b", r"how to apply", r"\bprocess\b", r"\bprocedure\b", r"how do i apply"],
        "Tamil": ["படிகள்", "எப்படி விண்ணப்பிக்க", "செயல்முறை", "விண்ணப்பிப்பது எப்படி"],
        "Sinhala": ["පියවර", "අයදුම් කරන්නේ කෙසේද", "ක්‍රියාවලිය"],
    },
    "eligibility": {
        "English": [r"eligib", r"\bqualify\b", r"can i apply", r"who can apply", r"am i allowed"],
        "Tamil": ["தகுதி", "விண்ணப்பிக்கலாமா", "தகுதியானவர்"],
        "Sinhala": ["සුදුසුකම", "අයදුම් කළ හැකිද", "සුදුසුකම්"],
    },
    "time": {
        "English": [r"how long", r"processing time", r"\bduration\b", r"how many days", r"how many weeks"],
        "Tamil": ["எவ்வளவு நாட்கள்", "செயலாக்க நேரம்", "எத்தனை நாள்", "காலம் எவ்வளவு"],
        "Sinhala": ["කොච්චර කාලයක්", "සැකසුම් කාලය", "දින කීයක්"],
    },
    "office": {
        "English": [r"\boffice\b", r"\bwhere\b", r"\blocation\b", r"nearest", r"\baddress\b"],
        "Tamil": ["அலுவலகம்", "எங்கே", "இருப்பிடம்", "அருகிலுள்ள"],
        "Sinhala": ["කාර්යාලය", "කොහෙද", "ස්ථානය", "ආසන්නතම"],
    },
}

SERVICE_LIST_TEXT = {
    "English": "NIC, Passport, Birth Certificate, Marriage Certificate, Land Registration, Driving License, Police Clearance, and Visa Information",
    "Tamil": "தேசிய அடையாள அட்டை, பாஸ்போர்ட், பிறப்புச் சான்றிதழ், திருமணச் சான்றிதழ், நில பதிவு, ஓட்டுநர் உரிமம், காவல்துறை அனுமதி, மற்றும் விசா தகவல்",
    "Sinhala": "ජාතික හැඳුනුම්පත, විදේශ ගමන් බලපත්‍රය, උප්පැන්න සහතිකය, විවාහ සහතිකය, ඉඩම් ලියාපදිංචිය, රියදුරු බලපත්‍රය, පොලිස් නිරවුල් සහතිකය, සහ වීසා තොරතුරු",
}

# ─────────────────────────────────────────────────────────────────
# WEBSITE FAQ — meta-questions about how to use THIS platform
# ─────────────────────────────────────────────────────────────────
WEBSITE_FAQ = [
    {
        "keywords": ["eligibility checker", "check eligibility", "am i eligible", "எலிஜிபிலிட்டி",
                     "தகுதி சரிபார்ப்பு", "தகுதியை சரிபார்", "සුදුසුකම් පරීක්ෂකය", "සුදුසුකම් පරීක්ෂා"],
        "answer": {
            "English": "Use the 'Eligibility Checker' tool in the sidebar under Tools. Select the service you want, answer a few short questions, and it will tell you immediately if you qualify - before you travel to any office.",
            "Tamil": "பக்கப்பட்டியில் உள்ள 'Tools' பிரிவின் கீழ் 'Eligibility Checker' கருவியைப் பயன்படுத்துங்கள். நீங்கள் விரும்பும் சேவையைத் தேர்ந்தெடுத்து, சில குறுகிய கேள்விகளுக்குப் பதிலளியுங்கள் - எந்த அலுவலகத்திற்கும் செல்வதற்கு முன் நீங்கள் தகுதியுடையவரா என்பதை உடனடியாகக் காண்பிக்கும்.",
            "Sinhala": "පැති තීරුවේ 'Tools' යටතේ ඇති 'Eligibility Checker' මෙවලම භාවිතා කරන්න. ඔබට අවශ්‍ය සේවාව තෝරා, කෙටි ප්‍රශ්න කිහිපයකට පිළිතුරු දෙන්න - ඕනෑම කාර්යාලයකට යාමට පෙර ඔබ සුදුසුකම් ලබනවාද යන්න එය වහාම පෙන්වයි.",
        },
    },
    {
        "keywords": ["nearest office", "find office", "office locator", "closest office",
                     "அருகிலுள்ள அலுவலகம்", "அலுவலகத்தைக் கண்டுபிடி", "ஆஃபீஸ்",
                     "ආසන්නතම කාර්යාලය", "කාර්යාලය සොයන්න"],
        "answer": {
            "English": "Open the 'Form Assistant' for your service, select your district, and the system automatically calculates the nearest government office offering that service using real geographic distance (the Haversine formula) - not just a default city.",
            "Tamil": "உங்கள் சேவைக்கான 'Form Assistant'-ஐத் திறந்து, உங்கள் மாவட்டத்தைத் தேர்ந்தெடுக்கவும் - அமைப்பு தானாகவே உண்மையான புவியியல் தூரத்தைப் பயன்படுத்தி (Haversine சூத்திரம்) அந்த சேவையை வழங்கும் அருகிலுள்ள அரசு அலுவலகத்தைக் கணக்கிடும் - வெறும் இயல்புநகரம் அல்ல.",
            "Sinhala": "ඔබේ සේවාව සඳහා 'Form Assistant' විවෘත කර, ඔබේ දිස්ත්‍රික්කය තෝරන්න - පද්ධතිය ස්වයංක්‍රීයව එම සේවාව සපයන ආසන්නතම රාජ්‍ය කාර්යාලය සැබෑ භූගෝලීය දුර (Haversine සූත්‍රය) භාවිතයෙන් ගණනය කරයි - හුදෙක් පෙරනිමි නගරයක් නොවේ.",
        },
    },
    {
        "keywords": ["change language", "switch language", "language dropdown",
                     "மொழியை மாற்ற", "மொழி மாற்றம்", "භාෂාව මාරු", "භාෂාව වෙනස්"],
        "answer": {
            "English": "Click the language dropdown at the top of the page and choose English, Tamil, or Sinhala - the entire interface updates immediately.",
            "Tamil": "பக்கத்தின் மேலே உள்ள மொழி dropdown-ஐ கிளிக் செய்து English, Tamil அல்லது Sinhala-ஐத் தேர்ந்தெடுக்கவும் - முழு இடைமுகமும் உடனடியாக புதுப்பிக்கப்படும்.",
            "Sinhala": "පිටුවේ ඉහළින් ඇති භාෂා dropdown එක ක්ලික් කර English, Tamil, හෝ Sinhala තෝරන්න - සම්පූර්ණ අතුරු මුහුණත වහාම යාවත්කාලීන වේ.",
        },
    },
    {
        "keywords": ["need nic to register", "nic required to register", "register without nic",
                     "first time nic applicant", "பதிவு செய்ய nic தேவையா", "nic இல்லாமல் பதிவு",
                     "ලියාපදිංචි වීමට nic අවශ්‍යද", "nic නැතුව ලියාපදිංචි"],
        "answer": {
            "English": "No - the NIC field is optional when registering. If you're applying for your first-ever NIC, simply leave it blank; you can add it to your profile later once issued.",
            "Tamil": "இல்லை - பதிவு செய்யும்போது NIC புலம் விருப்பமானது. உங்கள் முதல் NIC-க்கு விண்ணப்பிக்கிறீர்கள் என்றால், அதை வெறுமையாக விடுங்கள்; அது வழங்கப்பட்டதும் பின்னர் உங்கள் சுயவிவரத்தில் சேர்க்கலாம்.",
            "Sinhala": "නැත - ලියාපදිංචි වන විට NIC ක්ෂේත්‍රය විකල්පයි. ඔබ ඔබේ පළමු NIC සඳහා අයදුම් කරන්නේ නම්, එය හිස්ව තබන්න; එය නිකුත් වූ පසු ඔබට එය පසුව ඔබේ පැතිකඩට එකතු කළ හැක.",
        },
    },
    {
        "keywords": ["track application", "my application status", "application status",
                     "விண்ணப்ப நிலை", "விண்ணப்பத்தைக் கண்காணி", "අයදුම්පත් තත්ත්වය", "අයදුම්පත නිරීක්ෂණය"],
        "answer": {
            "English": "Go to 'My Applications' in the sidebar to see the status of every application you've submitted (In Progress, Completed, or Rejected).",
            "Tamil": "நீங்கள் சமர்ப்பித்த ஒவ்வொரு விண்ணப்பத்தின் நிலையையும் (In Progress, Completed, அல்லது Rejected) காண பக்கப்பட்டியில் உள்ள 'My Applications'-க்குச் செல்லுங்கள்.",
            "Sinhala": "ඔබ ඉදිරිපත් කළ සෑම අයදුම්පතක්ම (In Progress, Completed, හෝ Rejected) එහි තත්ත්වය බැලීමට පැති තීරුවේ ඇති 'My Applications' වෙත යන්න.",
        },
    },
]

GREETINGS = ["hi", "hello", "hey", "vanakkam", "வணக்கம்", "ஹலோ", "ஹாய்", "ayubowan", "ආයුබෝවන්", "හලෝ"]
THANKS = ["thank", "thanks", "நன்றி", "ස්තූතියි", "බොහොම ස්තූතියි"]

GREETING_RESPONSE = {
    "English": "Hello! I'm your Legal & Civic Assistant. Ask me about NIC, Passport, Birth/Marriage Certificate, Land Registration, Driving License, Police Clearance, or Visa Information - fees, documents, steps, eligibility, or office locations.",
    "Tamil": "வணக்கம்! நான் உங்கள் சட்ட மற்றும் சிவில் உதவியாளர். NIC, பாஸ்போர்ட், பிறப்பு/திருமண சான்றிதழ், நில பதிவு, ஓட்டுநர் உரிமம், காவல்துறை அனுமதி, அல்லது விசா தகவல் பற்றி என்னிடம் கேளுங்கள் - கட்டணங்கள், ஆவணங்கள், படிகள், தகுதி, அல்லது அலுவலக இருப்பிடங்கள்.",
    "Sinhala": "ආයුබෝවන්! මම ඔබේ නීති හා සිවිල් සහායකයා. NIC, විදේශ ගමන් බලපත්‍රය, උප්පැන්න/විවාහ සහතිකය, ඉඩම් ලියාපදිංචිය, රියදුරු බලපත්‍රය, පොලිස් නිරවුල් සහතිකය, හෝ වීසා තොරතුරු ගැන මගෙන් අසන්න - ගාස්තු, ලේඛන, පියවර, සුදුසුකම්, හෝ කාර්යාල ස්ථාන.",
}
THANKS_RESPONSE = {
    "English": "You're welcome! Let me know if you have any other questions about government services.",
    "Tamil": "பரவாயில்லை! அரசு சேவைகள் பற்றி வேறு ஏதேனும் கேள்விகள் இருந்தால் கேளுங்கள்.",
    "Sinhala": "සාදරයෙන් පිළිගනිමු! රාජ්‍ය සේවා ගැන වෙනත් ප්‍රශ්න තිබේ නම් අහන්න.",
}
DEFAULT_RESPONSE = {
    "English": "I am your Legal & Civic Assistant for Sri Lanka. I can help with {services}. Please ask about a specific service - for example, its fee, required documents, application steps, eligibility, or nearest office.",
    "Tamil": "நான் உங்கள் இலங்கை சட்ட மற்றும் சிவில் உதவியாளர். {services} பற்றி உதவ முடியும். ஒரு குறிப்பிட்ட சேவை பற்றி கேளுங்கள் - எடுத்துக்காட்டாக, அதன் கட்டணம், தேவையான ஆவணங்கள், விண்ணப்ப படிகள், தகுதி, அல்லது அருகிலுள்ள அலுவலகம்.",
    "Sinhala": "මම ශ්‍රී ලංකාවේ ඔබේ නීති සහ සිවිල් සහායකයා. {services} සම්බන්ධයෙන් උදව් කළ හැක. නිශ්චිත සේවාවක් ගැන අසන්න - උදාහරණයක් ලෙස, එහි ගාස්තුව, අවශ්‍ය ලේඛන, අයදුම් පියවර, සුදුසුකම්, හෝ ආසන්නතම කාර්යාලය.",
}
ASK_WHICH_SERVICE = {
    "English": "Which service would you like to know about? I can help with {services}.",
    "Tamil": "எந்த சேவையைப் பற்றி தெரிந்துகொள்ள விரும்புகிறீர்கள்? {services} பற்றி உதவ முடியும்.",
    "Sinhala": "ඔබට දැනගැනීමට අවශ්‍ය සේවාව කුමක්ද? {services} සම්බන්ධයෙන් උදව් කළ හැක.",
}

LABELS = {
    "fee_title": {"English": "💰 Fee for {s}", "Tamil": "💰 {s} கட்டணம்", "Sinhala": "💰 {s} සඳහා ගාස්තුව"},
    "time_title": {"English": "⏱ Processing time for {s}", "Tamil": "⏱ {s} செயலாக்க நேரம்", "Sinhala": "⏱ {s} සැකසුම් කාලය"},
    "docs_title": {"English": "📋 Documents required for {s}:", "Tamil": "📋 {s}-க்குத் தேவையான ஆவணங்கள்:", "Sinhala": "📋 {s} සඳහා අවශ්‍ය ලේඛන:"},
    "steps_title": {"English": "📝 Steps to apply for {s}:", "Tamil": "📝 {s}-க்கு விண்ணப்பிக்கும் படிகள்:", "Sinhala": "📝 {s} සඳහා අයදුම් කිරීමේ පියවර:"},
    "elig_title": {"English": "✅ Eligibility for {s}:", "Tamil": "✅ {s}-க்கான தகுதி:", "Sinhala": "✅ {s} සඳහා සුදුසුකම්:"},
    "office_title": {"English": "🏢 Nearest office for {s}:", "Tamil": "🏢 {s}-க்கான அருகிலுள்ள அலுவலகம்:", "Sinhala": "🏢 {s} සඳහා ආසන්නතම කාර්යාලය:"},
    "office_body": {
        "English": "Open the Form Assistant for {s} and select your district - the system will calculate your nearest office automatically. Official department: {link}",
        "Tamil": "{s}-க்கான Form Assistant-ஐத் திறந்து உங்கள் மாவட்டத்தைத் தேர்ந்தெடுக்கவும் - அமைப்பு தானாகவே உங்கள் அருகிலுள்ள அலுவலகத்தைக் கணக்கிடும். அதிகாரப்பூர்வ திணைக்களம்: {link}",
        "Sinhala": "{s} සඳහා Form Assistant විවෘත කර ඔබේ දිස්ත්‍රික්කය තෝරන්න - පද්ධතිය ඔබේ ආසන්නතම කාර්යාලය ස්වයංක්‍රීයව ගණනය කරයි. නිල දෙපාර්තමේන්තුව: {link}",
    },
    "mandatory": {"English": "Mandatory", "Tamil": "கட்டாயம்", "Sinhala": "අනිවාර්ය"},
    "optional": {"English": "Optional", "Tamil": "விருப்பத்தேர்வு", "Sinhala": "විකල්ප"},
    "official_link": {"English": "Official website", "Tamil": "அதிகாரப்பூர்வ இணையதளம்", "Sinhala": "නිල වෙබ් අඩවිය"},
    "overview_lead": {
        "English": "Here's what you need for {s}:",
        "Tamil": "{s}-க்கு உங்களுக்குத் தேவையானவை இதோ:",
        "Sinhala": "{s} සඳහා ඔබට අවශ්‍ය දේ මෙන්න:",
    },
}


def _detect_service(q_lower):
    best, best_score = None, 0
    for name, data in SERVICE_KB.items():
        score = 0
        for kw in data["keywords"]:
            kw_l = kw.lower()
            if len(kw_l) <= 4 and kw_l.isascii():
                # short English keywords (nic, visa) -> word boundary match
                if re.search(r"\b" + re.escape(kw_l) + r"\b", q_lower):
                    score += 1
            elif kw_l in q_lower:
                score += 1
        if score > best_score:
            best, best_score = name, score
    return best


def _detect_intent(q_lower):
    for intent, by_lang in INTENT_KEYWORDS.items():
        for lang_keywords in by_lang.values():
            for kw in lang_keywords:
                if kw.startswith(r"\b") or "\\" in kw:
                    if re.search(kw, q_lower):
                        return intent
                elif kw in q_lower:
                    return intent
    return None


def _get_fee_and_time(service_name, language):
    kb = SERVICE_KB[service_name]
    if "custom_fee" in kb:
        return kb["custom_fee"].get(language, kb["custom_fee"]["English"]), \
               kb["custom_time"].get(language, kb["custom_time"]["English"])
    info = get_fee_info(service_name, language)
    if info:
        return info.get("fee", "-"), info.get("processing_time", "-")
    return "-", "-"


def _compose_service_answer(service_name, intent, language):
    kb = SERVICE_KB[service_name]
    L = lambda d: d.get(language, d.get("English"))

    if intent == "fee":
        fee, _ = _get_fee_and_time(service_name, language)
        return f"{L(LABELS['fee_title']).format(s=service_name)}\n{fee}"

    if intent == "time":
        _, proc_time = _get_fee_and_time(service_name, language)
        return f"{L(LABELS['time_title']).format(s=service_name)}\n{proc_time}"

    if intent == "documents":
        docs = kb["documents"].get(language, kb["documents"]["English"])
        mand = L(LABELS["mandatory"]); opt = L(LABELS["optional"])
        lines = [f"- {name} ({mand if is_m else opt})" for name, is_m in docs]
        return f"{L(LABELS['docs_title']).format(s=service_name)}\n" + "\n".join(lines)

    if intent == "steps":
        steps = kb["steps"].get(language, kb["steps"]["English"])
        lines = [f"{i+1}. {s}" for i, s in enumerate(steps)]
        return f"{L(LABELS['steps_title']).format(s=service_name)}\n" + "\n".join(lines)

    if intent == "eligibility":
        elig = kb["eligibility"].get(language, kb["eligibility"]["English"])
        return f"{L(LABELS['elig_title']).format(s=service_name)}\n{elig}"

    if intent == "office":
        body = L(LABELS["office_body"]).format(s=service_name, link=kb["official_link"])
        return f"{L(LABELS['office_title']).format(s=service_name)}\n{body}"

    # No specific intent -> full overview
    fee, proc_time = _get_fee_and_time(service_name, language)
    steps = kb["steps"].get(language, kb["steps"]["English"])
    docs = kb["documents"].get(language, kb["documents"]["English"])
    mand = L(LABELS["mandatory"]); opt = L(LABELS["optional"])
    doc_lines = [f"- {name} ({mand if is_m else opt})" for name, is_m in docs]
    step_lines = [f"{i+1}. {s}" for i, s in enumerate(steps)]

    parts = [
        L(LABELS["overview_lead"]).format(s=service_name),
        "",
        L(LABELS["steps_title"]).format(s=service_name),
        "\n".join(step_lines),
        "",
        L(LABELS["docs_title"]).format(s=service_name),
        "\n".join(doc_lines),
        "",
        f"{L(LABELS['fee_title']).format(s=service_name)}: {fee}",
        f"{L(LABELS['time_title']).format(s=service_name)}: {proc_time}",
        "",
        f"{L(LABELS['official_link'])}: {kb['official_link']}",
    ]
    return "\n".join(parts)


def get_fallback_response(question, language="English"):
    q_lower = question.lower().strip()

    # Greetings / thanks first (short-circuit before any keyword matching)
    if any(re.search(r"\b" + re.escape(g) + r"\b", q_lower) if g.isascii() else g in q_lower for g in GREETINGS):
        return GREETING_RESPONSE.get(language, GREETING_RESPONSE["English"])
    if any(t in q_lower for t in THANKS):
        return THANKS_RESPONSE.get(language, THANKS_RESPONSE["English"])

    # Detect service + intent BEFORE checking website FAQ, so a specific
    # question like "am I eligible for a driving license" gets the actual
    # Driving Licence eligibility answer, rather than being swallowed by
    # the generic "how does the Eligibility Checker tool work" FAQ entry.
    service = _detect_service(q_lower)
    intent = _detect_intent(q_lower)

    if service:
        return _compose_service_answer(service, intent, language)

    # No specific service mentioned -> check if this is a general
    # "how do I use this website feature" question instead.
    for faq in WEBSITE_FAQ:
        for kw in faq["keywords"]:
            kw_l = kw.lower()
            matched = re.search(r"\b" + re.escape(kw_l) + r"\b", q_lower) if kw_l.isascii() else kw_l in q_lower
            if matched:
                return faq["answer"].get(language, faq["answer"]["English"])

    if intent:
        services_text = SERVICE_LIST_TEXT.get(language, SERVICE_LIST_TEXT["English"])
        return ASK_WHICH_SERVICE.get(language, ASK_WHICH_SERVICE["English"]).format(services=services_text)

    services_text = SERVICE_LIST_TEXT.get(language, SERVICE_LIST_TEXT["English"])
    return DEFAULT_RESPONSE.get(language, DEFAULT_RESPONSE["English"]).format(services=services_text)
