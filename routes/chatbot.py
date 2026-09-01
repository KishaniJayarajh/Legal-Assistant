import os
from flask import Blueprint, render_template, request, jsonify, current_app, session
from flask_login import login_required, current_user
from extensions import db
from models.user import ChatHistory
from knowledge_base import get_fallback_response, SERVICE_LIST_TEXT

chatbot = Blueprint('chatbot', __name__)


def get_groq_response(question, language="English"):
    """
    Calls Groq API (free, fast llama3).
    Falls back to the trilingual knowledge base if the key is missing,
    unset, or the API call fails for any reason.
    """
    api_key = os.getenv('GROQ_API_KEY', '')

    if not api_key or api_key == 'YOUR_GROQ_API_KEY_HERE':
        return get_fallback_response(question, language)

    try:
        from groq import Groq
        client = Groq(api_key=api_key)

        services_text = SERVICE_LIST_TEXT.get(language, SERVICE_LIST_TEXT["English"])
        system_prompt = (
            f"You are the Legal and Civic Service Assistant for the AI-Powered Legal "
            f"& Civic Services Assistant website, built specifically for Sri Lankan "
            f"citizens. The site currently covers exactly these services: {services_text}. "
            f"When answering, be specific and practical: mention the required documents, "
            f"the typical fee (in LKR where known), the processing time, and the "
            f"responsible government department, formatted as short numbered steps where "
            f"appropriate. If the citizen asks about a service outside this list, politely "
            f"say this assistant focuses on the services above, then still give your best "
            f"general guidance. If you are unsure of an exact current fee or timeframe, say "
            f"the approximate range and advise the citizen to confirm on the official "
            f"government website before paying. Always respond entirely in {language}, "
            f"regardless of what language the question was asked in. Keep answers concise "
            f"(under 150 words) and avoid legal disclaimers or filler text."
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