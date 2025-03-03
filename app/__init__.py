from flask import Flask,session
from flask_sqlalchemy import SQLAlchemy
from datetime import timedelta

# Khởi tạo SQLAlchemy
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)

    # Cấu hình database PostgreSQL (hard-coded tạm thời)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1111@localhost:5432/docflow_db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config["SECRET_KEY"] = "BEST"
    app.permanent_session_lifetime = timedelta(minutes=1)
    

    # Khởi tạo database
    db.init_app(app)
    from app.routes.auth import auth
    from app.models.user import User
    # Đăng ký blueprints
    app.register_blueprint(auth)

    # Tạo bảng nếu chưa tồn tại
    with app.app_context():
        db.create_all()
        print("Created database!")

    return app