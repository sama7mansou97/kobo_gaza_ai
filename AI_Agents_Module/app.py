from flask_app import create_app
from flask_app.config import Config

app = create_app()

if __name__ == "__main__":
    # يعمل التطبيق على المنفذ 5001 لمنع التعارض مع المجلد الأول (5000)
    app.run(host="0.0.0.0", port=Config.PORT, debug=Config.DEBUG)