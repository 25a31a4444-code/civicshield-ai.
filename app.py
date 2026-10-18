import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from flask import Flask, render_template, session, g
from config import Config
from database import init_db, get_db
from services.auth_service import get_current_user
from services.notification_service import get_unread_count
from services.i18n import get_text, SUPPORTED_LANGUAGES

# Import Blueprints
from routes.public import public_bp
from routes.auth import auth_bp
from routes.citizen import citizen_bp
from routes.authority import authority_bp
from routes.admin import admin_bp
from routes.api import api_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize database tables and folders
    with app.app_context():
        init_db()
        os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
        os.makedirs(os.path.join(app.root_path, 'static', 'img', 'demo'), exist_ok=True)

    # Register Blueprints
    app.register_blueprint(public_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(citizen_bp)
    app.register_blueprint(authority_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(api_bp)

    # Global Template Context Processor
    @app.context_processor
    def inject_global_vars():
        user = get_current_user()
        lang = session.get('lang', 'en')
        unread_count = get_unread_count(user['id']) if user else 0
        
        # Check active disaster mode
        disaster_mode = False
        try:
            db = get_db()
            cursor = db.cursor()
            cursor.execute("SELECT value FROM system_settings WHERE key = 'disaster_mode'")
            row = cursor.fetchone()
            if row and row['value'].lower() == 'true':
                disaster_mode = True
            db.close()
        except Exception:
            pass

        return {
            'current_user': user,
            'lang': lang,
            'supported_languages': SUPPORTED_LANGUAGES,
            't': lambda key: get_text(key, lang),
            'unread_notifications_count': unread_count,
            'disaster_mode_active': disaster_mode
        }

    # Custom Error Handlers
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('public/404.html'), 404

    @app.errorhandler(500)
    def internal_server_error(e):
        return render_template('public/500.html'), 500

    return app

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
