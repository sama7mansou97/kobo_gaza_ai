import os
from flask import Flask
from flask_cors import CORS
from flask_app.config import Config

def create_app():
    # تحديد مسار المجلد الأول (Dashboard Views) بالنسبة للمجلد الحالي
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    dashboard_path = os.path.join(base_dir, 'Dashboard Views', 'flask_app')
    
    template_folder = os.path.join(dashboard_path, 'templates')
    static_folder = os.path.join(dashboard_path, 'static')

    app = Flask(__name__, template_folder=template_folder, static_folder=static_folder)
    app.config.from_object(Config)
    
    CORS(app)

    # تسجيل المسارات
    from flask_app.routes import agents_bp
    app.register_blueprint(agents_bp)

    return app