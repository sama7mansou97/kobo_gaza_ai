import os
import sys
from flask import Flask

# إضافة المسار لضمان قراءة المجلدات بشكل صحيحة
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.routes import main_bp

app = Flask(__name__, template_folder="templates", static_folder="static")
app.register_blueprint(main_bp)

if __name__ == "__main__":
    app.run(debug=True, port=5000)