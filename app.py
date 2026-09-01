from flask import Flask, session, request, redirect, url_for
from extensions import db, bcrypt, login_manager
from dotenv import load_dotenv
from translations import get_translator
import os

load_dotenv()

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'legal-civic-secret-key-2024')

    db_user = os.getenv('DB_USER', 'root')
    db_pass = os.getenv('DB_PASSWORD', '')
    db_host = os.getenv('DB_HOST', 'localhost')
    db_name = os.getenv('DB_NAME', 'legal_civic_db')
    app.config['SQLALCHEMY_DATABASE_URI'] = (
        f'mysql+pymysql://{db_user}:{db_pass}@{db_host}/{db_name}'
    )
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'uploads')
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    db.init_app(app)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    from routes.auth        import auth
    from routes.dashboard   import dashboard
    from routes.chatbot     import chatbot
    from routes.services    import services
    from routes.checklist   import checklist
    from routes.profile     import profile
    from routes.admin       import admin
    from routes.tools       import tools
    from routes.applications import applications

    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    app.register_blueprint(chatbot)
    app.register_blueprint(services)
    app.register_blueprint(checklist)
    app.register_blueprint(profile)
    app.register_blueprint(admin)
    app.register_blueprint(tools)
    app.register_blueprint(applications)

    # ── LANGUAGE SWITCHING ────────────────────────────────────────
    # current_language() checks session override first (set by the
    # topbar dropdown), then falls back to the logged-in user's saved
    # preferred_language, then defaults to English for guests.
    @app.context_processor
    def inject_translator():
        from flask_login import current_user
        lang = session.get('language')
        if not lang and current_user.is_authenticated:
            lang = current_user.preferred_language
        lang = lang or 'English'
        return {
            't': get_translator(lang),
            'current_language': lang,
            'available_languages': ['English', 'Tamil', 'Sinhala']
        }

    @app.route('/set-language/<lang>')
    def set_language(lang):
        if lang in ('English', 'Tamil', 'Sinhala'):
            session['language'] = lang
        # Redirect back to whichever page the user was on
        return redirect(request.referrer or url_for('auth.index'))

    with app.app_context():
        db.create_all()
        from models.user import User
        if not User.query.filter_by(email='admin@legalcivic.lk').first():
            admin_user = User(
                fullname='Admin User',
                email='admin@legalcivic.lk',
                mobile='0112345678',
                nic='199012345678',
                preferred_language='English',
                role='admin',
                password=bcrypt.generate_password_hash('admin123').decode('utf-8')
            )
            db.session.add(admin_user)
            db.session.commit()
            print('✅ Admin created: admin@legalcivic.lk / admin123')
        else:
            print('✅ System Ready!')

    return app


if __name__ == '__main__':
    app = create_app()
    print('\n🚀 Legal & Civic Assistant: http://localhost:5000')
    print('👤 Admin: admin@legalcivic.lk / admin123\n')
    if os.getenv('GROQ_API_KEY', '') in ('', 'PASTE_YOUR_GROQ_API_KEY_HERE'):
        print('⚠️  WARNING: Groq API key not set yet! AI chat will use fallback responses.')
        print('   Get your free key: https://console.groq.com/keys')
        print('   Then update GROQ_API_KEY in the .env file.\n')
    app.run(debug=True, port=5000)
