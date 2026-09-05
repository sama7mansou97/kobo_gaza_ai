import os
import sys
from flask import Flask

# مسار الجذر للمشروع
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FLASK_APP_DIR = os.path.join(BASE_DIR, 'Dashboard Views', 'flask_app')

if FLASK_APP_DIR not in sys.path:
    sys.path.insert(0, FLASK_APP_DIR)

# إعداد التطبيق لاستخدام ملفات templates و static الموجودة داخل Dashboard Views/flask_app
app = Flask(
    __name__,
    template_folder=os.path.join(FLASK_APP_DIR, 'templates'),
    static_folder=os.path.join(FLASK_APP_DIR, 'static')
)

app.config['SECRET_KEY'] = 'kobo_gaza_four_experts_secret'

# تسجيل المسارات التابعة لـ Four Experts
from utils.routes import main_bp
app.register_blueprint(main_bp)

if __name__ == '__main__':
    print("🚀 Starting Kobo Gaza Relief AI (Four Experts Module) on http://127.0.0.1:5001")
    app.run(debug=True, port=5001)