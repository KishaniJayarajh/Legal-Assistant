"""
fees_data.py — Multi-language Fee & Processing Time reference data.

Figures reflect officially published 2026 government fee schedules
(Dept. of Immigration & Emigration, DRP, RGD, DMT, Police). Shown as a
helpful reference in each service's step-by-step guide, in the user's
selected language (English / Tamil / Sinhala) — always subject to
change, so the UI links back to the official source as well.
"""

FEES_INFO = {

    "Passport Application": {
        "English": {
            "fee": "Rs. 10,000 (Normal, adult) · Rs. 3,000 (child) · Rs. 20,000 (Urgent/1-day, adult)",
            "processing_time": "Normal: ~8–12 weeks · Urgent (1-day): same day (Head Office/Jaffna only)",
            "validity": "10 years (adults) · 3 or 10 years (children, parent's choice)",
            "note": "Fee is the same for new applications and renewals. A lost-passport replacement adds a Rs. 15,000–20,000 penalty on top of the normal fee.",
        },
        "Tamil": {
            "fee": "ரூ. 10,000 (சாதாரண, பெரியவர்) · ரூ. 3,000 (குழந்தை) · ரூ. 20,000 (அவசர/ஒரு நாள் சேவை, பெரியவர்)",
            "processing_time": "சாதாரணம்: ~8–12 வாரங்கள் · அவசரம் (ஒரு நாள்): அதே நாளில் (தலைமை அலுவலகம்/யாழ்ப்பாணம் மட்டும்)",
            "validity": "10 ஆண்டுகள் (பெரியவர்கள்) · 3 அல்லது 10 ஆண்டுகள் (குழந்தைகள், பெற்றோர் தேர்வு)",
            "note": "புதிய விண்ணப்பத்திற்கும் புதுப்பித்தலுக்கும் கட்டணம் ஒன்றுதான். தொலைந்த பாஸ்போர்ட்டுக்கு பதிலீடு பெற ரூ. 15,000–20,000 அபராதம் கூடுதலாக சேரும்.",
        },
        "Sinhala": {
            "fee": "රු. 10,000 (සාමාන්‍ය, වැඩිහිටි) · රු. 3,000 (දරුවා) · රු. 20,000 (හදිසි/එක් දින සේවාව, වැඩිහිටි)",
            "processing_time": "සාමාන්‍ය: සති 8–12ක් පමණ · හදිසි (එක් දින): එදිනම (ප්‍රධාන කාර්යාලය/යාපනය පමණි)",
            "validity": "වසර 10 (වැඩිහිටියන්) · වසර 3 හෝ 10 (දරුවන්, දෙමාපිය තේරීම)",
            "note": "නව අයදුම්පත් සහ අලුත් කිරීම් සඳහා ගාස්තුව සමානයි. නැති වූ විදේශ ගමන් බලපත්‍රයක් වෙනුවට ලබා ගැනීමට රු. 15,000–20,000ක දඩයක් අමතරව එකතු වේ.",
        },
    },

    "NIC Application": {
        "English": {
            "fee": "Free (first-time application) · Rs. 100 (damaged-card replacement) · higher fee for lost-card replacement",
            "processing_time": "Approx. 2–4 weeks (may extend during peak periods)",
            "validity": "Valid until details change (no fixed expiry)",
            "note": "Your very first NIC is completely free of charge — never pay any 'agent' to speed this up.",
        },
        "Tamil": {
            "fee": "இலவசம் (முதல் முறை விண்ணப்பம்) · ரூ. 100 (சேதமான அட்டை மாற்றம்) · தொலைந்த அட்டைக்கு அதிக கட்டணம்",
            "processing_time": "தோராயமாக 2–4 வாரங்கள் (அதிக நெரிசல் காலங்களில் தாமதமாகலாம்)",
            "validity": "விவரங்கள் மாறும் வரை செல்லுபடியாகும் (நிலையான காலாவதி இல்லை)",
            "note": "உங்கள் முதல் தேசிய அடையாள அட்டை முற்றிலும் இலவசம் — இதை விரைவுபடுத்த எந்த 'ஏஜென்ட்'டுக்கும் பணம் கொடுக்க வேண்டாம்.",
        },
        "Sinhala": {
            "fee": "නොමිලේ (පළමු වර අයදුම්පත) · රු. 100 (හානි වූ කාඩ්පත මාරු කිරීම) · නැති වූ කාඩ්පතකට වැඩි ගාස්තුවක්",
            "processing_time": "සති 2–4ක් පමණ (කාර්යබහුල කාලවලදී වඩාත් කාලය ගත විය හැක)",
            "validity": "විස්තර වෙනස් වන තුරු වළංගුයි (නියමිත කල් ඉකුත්වීමක් නැත)",
            "note": "ඔබේ පළමු ජාතික හැඳුනුම්පත සම්පූර්ණයෙන්ම නොමිලේයි — එය ඉක්මන් කිරීමට කිසිදු 'නියෝජිතයෙකුට' මුදල් ගෙවන්න එපා.",
        },
    },

    "Birth Certificate": {
        "English": {
            "fee": "Nominal certified-copy fee (typically under Rs. 500, varies by Divisional Secretariat)",
            "processing_time": "Same day at DS office (if record exists in system) · longer for older/manual records",
            "validity": "Permanent record",
            "note": "Online copies (via eBMD) may carry a small additional service fee.",
        },
        "Tamil": {
            "fee": "சிறிய சான்று நகல் கட்டணம் (பொதுவாக ரூ. 500க்கும் குறைவு, பிரதேச செயலகத்தைப் பொறுத்தது)",
            "processing_time": "பிரதேச செயலக அலுவலகத்தில் அதே நாளில் (பதிவு கணினியில் இருந்தால்) · பழைய/கையால் எழுதிய பதிவுகளுக்கு அதிக நேரம்",
            "validity": "நிரந்தர பதிவு",
            "note": "ஆன்லைன் நகல்கள் (eBMD மூலம்) சிறிய கூடுதல் சேவைக் கட்டணம் இருக்கலாம்.",
        },
        "Sinhala": {
            "fee": "සුළු සහතික කළ පිටපත් ගාස්තුවක් (සාමාන්‍යයෙන් රු. 500ට වඩා අඩු, ප්‍රාදේශීය ලේකම් කාර්යාලය අනුව වෙනස් වේ)",
            "processing_time": "පද්ධතියේ වාර්තාව තිබේ නම් ප්‍රාදේශීය ලේකම් කාර්යාලයේ එදිනම · පැරණි/අතින් ලියන ලද වාර්තා සඳහා වැඩි කාලයක්",
            "validity": "ස්ථිර වාර්තාවක්",
            "note": "අන්තර්ජාල පිටපත් (eBMD මගින්) සඳහා සුළු අතිරේක සේවා ගාස්තුවක් අය විය හැක.",
        },
    },

    "Marriage Certificate": {
        "English": {
            "fee": "Nominal certified-copy fee (typically under Rs. 500)",
            "processing_time": "14 working days for a marriage clearance report · same day for certified copies (if digitised)",
            "validity": "Permanent record",
            "note": "Registration itself (Notice of Marriage) must be lodged at least 14 days before the ceremony.",
        },
        "Tamil": {
            "fee": "சிறிய சான்று நகல் கட்டணம் (பொதுவாக ரூ. 500க்கும் குறைவு)",
            "processing_time": "திருமண அனுமதிச் சான்றுக்கு 14 வேலை நாட்கள் · டிஜிட்டல் பதிவு இருந்தால் சான்று நகலுக்கு அதே நாள்",
            "validity": "நிரந்தர பதிவு",
            "note": "திருமண நோட்டீஸ் பதிவு விழாவுக்கு குறைந்தது 14 நாட்களுக்கு முன் சமர்ப்பிக்கப்பட வேண்டும்.",
        },
        "Sinhala": {
            "fee": "සුළු සහතික කළ පිටපත් ගාස්තුවක් (සාමාන්‍යයෙන් රු. 500ට වඩා අඩු)",
            "processing_time": "විවාහ නිදහස් කිරීමේ වාර්තාවක් සඳහා වැඩකරන දින 14ක් · ඩිජිටල්කරණය කර ඇත්නම් සහතික කළ පිටපත් සඳහා එදිනම",
            "validity": "ස්ථිර වාර්තාවක්",
            "note": "විවාහ දැනුම්දීම උත්සවයට දින 14කට පෙර ඉදිරිපත් කළ යුතුය.",
        },
    },

    "Driving License": {
        "English": {
            "fee": "Varies by vehicle class — approx. Rs. 2,500–6,000 total (medical certificate + written/trial test + license issue fee)",
            "processing_time": "Varies by DMT centre — written test, then trial run, then card issue (several weeks typical)",
            "validity": "Valid until age 60 (medical re-certification required after)",
            "note": "Fees are set by the Dept. of Motor Traffic and revised periodically — confirm the exact class-wise rate at your DMT office.",
        },
        "Tamil": {
            "fee": "வாகன வகையைப் பொறுத்து மாறுபடும் — தோராயமாக ரூ. 2,500–6,000 (மருத்துவ சான்று + எழுத்து/ஓட்டுத் தேர்வு + அட்டை வெளியீட்டுக் கட்டணம்)",
            "processing_time": "DMT மையத்தைப் பொறுத்து மாறுபடும் — எழுத்துத் தேர்வு, பின் ஓட்டுத் தேர்வு, பின் அட்டை வெளியீடு (பொதுவாக பல வாரங்கள்)",
            "validity": "60 வயது வரை செல்லுபடியாகும் (பின்பு மருத்துவ மறுசான்று தேவை)",
            "note": "கட்டணங்களை மோட்டார் போக்குவரத்துத் திணைக்களம் நிர்ணயித்து அவ்வப்போது மாற்றுகிறது — உங்கள் DMT அலுவலகத்தில் வகைவாரியான சரியான கட்டணத்தை உறுதிப்படுத்திக் கொள்ளுங்கள்.",
        },
        "Sinhala": {
            "fee": "වාහන පංතිය අනුව වෙනස් වේ — රු. 2,500–6,000 පමණ (වෛද්‍ය සහතිකය + ලිඛිත/අත්හදා බැලීමේ පරීක්ෂණය + බලපත්‍ර නිකුත් කිරීමේ ගාස්තුව)",
            "processing_time": "DMT මධ්‍යස්ථානය අනුව වෙනස් වේ — ලිඛිත පරීක්ෂණය, පසුව අත්හදා බැලීම, පසුව කාඩ්පත නිකුත් කිරීම (සාමාන්‍යයෙන් සති කීපයක්)",
            "validity": "වයස 60 දක්වා වළංගුයි (ඉන් පසු වෛද්‍ය නැවත සහතික කිරීම අවශ්‍යයි)",
            "note": "ගාස්තු මෝටර් රථ ප්‍රවාහන දෙපාර්තමේන්තුව විසින් නියම කර වරින් වර සංශෝධනය කරයි — ඔබේ DMT කාර්යාලයේදී පංති අනුව නිවැරදි ගාස්තුව තහවුරු කරගන්න.",
        },
    },

    "Police Clearance": {
        "English": {
            "fee": "Rs. 5,000 (online application, single certificate)",
            "processing_time": "Approx. 2–3 weeks after document verification",
            "validity": "Typically accepted for 6 months from issue date by most embassies/employers",
            "note": "Pay only through the official eservices.police.lk portal — avoid third-party 'agents'.",
        },
        "Tamil": {
            "fee": "ரூ. 5,000 (ஆன்லைன் விண்ணப்பம், ஒரு சான்றிதழுக்கு)",
            "processing_time": "ஆவணச் சரிபார்ப்புக்குப் பின் தோராயமாக 2–3 வாரங்கள்",
            "validity": "பொதுவாக பெரும்பாலான தூதரகங்கள்/முதலாளிகளால் வெளியிட்ட தேதியிலிருந்து 6 மாதங்களுக்கு ஏற்கப்படும்",
            "note": "அதிகாரப்பூர்வ eservices.police.lk போர்ட்டல் மூலம் மட்டும் பணம் செலுத்துங்கள் — மூன்றாம் தரப்பு 'ஏஜென்ட்'களை தவிர்க்கவும்.",
        },
        "Sinhala": {
            "fee": "රු. 5,000 (අන්තර්ජාල අයදුම්පත, එක් සහතිකයක් සඳහා)",
            "processing_time": "ලේඛන සත්‍යාපනයෙන් පසු සති 2–3ක් පමණ",
            "validity": "සාමාන්‍යයෙන් නිකුත් කළ දින සිට මාස 6ක් දක්වා බොහෝ තානාපති කාර්යාල/සේවායෝජකයන් විසින් පිළිගනී",
            "note": "නිල eservices.police.lk වෙබ් අඩවිය මගින් පමණක් මුදල් ගෙවන්න — තෙවන පාර්ශව 'නියෝජිතයින්' වළක්වා ගන්න.",
        },
    },

    "Land Registration": {
        "English": {
            "fee": "Varies by property value (registration fee + stamp duty, calculated per transaction)",
            "processing_time": "Varies by Land Registry workload — typically several weeks",
            "validity": "Permanent record",
            "note": "Consult the Land Registry or a licensed conveyancer for an exact fee calculation for your property.",
        },
        "Tamil": {
            "fee": "சொத்தின் மதிப்பைப் பொறுத்து மாறுபடும் (பதிவுக் கட்டணம் + முத்திரைத் தீர்வை, ஒப்பந்தத்திற்கேற்ப கணக்கிடப்படும்)",
            "processing_time": "நிலப் பதிவு அலுவலகத்தின் பணிச்சுமையைப் பொறுத்து மாறுபடும் — பொதுவாக பல வாரங்கள்",
            "validity": "நிரந்தர பதிவு",
            "note": "உங்கள் சொத்துக்கான சரியான கட்டணக் கணக்கீட்டுக்கு நிலப் பதிவு அலுவலகம் அல்லது உரிமம் பெற்ற contract எழுத்தாளரை அணுகவும்.",
        },
        "Sinhala": {
            "fee": "දේපළ වටිනාකම අනුව වෙනස් වේ (ලියාපදිංචි ගාස්තුව + මුද්දර ගාස්තුව, ගනුදෙනුව අනුව ගණනය කරයි)",
            "processing_time": "ඉඩම් ලේකම් කාර්යාලයේ වැඩ බහුල්කම අනුව වෙනස් වේ — සාමාන්‍යයෙන් සති කීපයක්",
            "validity": "ස්ථිර වාර්තාවක්",
            "note": "ඔබේ දේපළ සඳහා නිවැරදි ගාස්තු ගණනය සඳහා ඉඩම් ලේකම් කාර්යාලය හෝ බලපත්‍රලාභී conveyancer අමතන්න.",
        },
    },
}


def get_fee_info(service_name: str, language: str):
    """Returns the fee dict for a service in the given language, falling
    back to English if the language or service isn't found."""
    entry = FEES_INFO.get(service_name)
    if not entry:
        return None
    return entry.get(language, entry.get("English"))
