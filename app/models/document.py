# app/models/document.py
from app import db
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    file_type = db.Column(db.String(10), nullable=False)
    file_path = db.Column(db.String(200))
    thumbnail_path = db.Column(db.String(200))  # Thêm trường thumbnail_path
    pages = db.Column(db.Integer, default=0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User', backref=db.backref('documents', lazy=True))

    def __init__(self, title, category, file_type, user_id, file_path=None, thumbnail_path=None, pages=0):
        self.title = title
        self.category = category
        self.file_type = file_type
        self.user_id = user_id
        self.file_path = file_path
        self.thumbnail_path = thumbnail_path
        self.pages = pages

    def __repr__(self):
        return f'<Document {self.title}>'