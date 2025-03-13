from flask import Flask, session
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta
import os

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # Cấu hình ứng dụng
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1111@localhost:5432/docflow_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["SECRET_KEY"] = "BEST"  # Nên thay bằng một chuỗi phức tạp hơn trong production
    app.permanent_session_lifetime = timedelta(minutes=60)

    # Khởi tạo các extension
    db.init_app(app)

    # Đăng ký blueprints
    from app.routes.auth import auth
    from app.routes.document import document
    from app.routes.ai_assistant import ai_assistant_bp
    from app.routes.chat import chat
    from app.routes.library import library_bp

    app.register_blueprint(auth)
    app.register_blueprint(document)
    app.register_blueprint(ai_assistant_bp)
    app.register_blueprint(chat)
    app.register_blueprint(library_bp)

    # Thêm bộ lọc file_exists vào Jinja
    def file_exists(filename):
        return os.path.exists(os.path.join(app.static_folder, filename))
    app.jinja_env.filters['file_exists'] = file_exists

    # Tạo database tables (chỉ chạy lần đầu hoặc khi cần)
    # with app.app_context():
    #     db.create_all()
    #     print("Created database!")

    return app