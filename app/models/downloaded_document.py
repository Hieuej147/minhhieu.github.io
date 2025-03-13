from app import db

class DownloadedDocument(db.Model):
    __tablename__ = 'downloaded_documents'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    document_id = db.Column(db.Integer, db.ForeignKey('documents.id'), nullable=False)
    downloaded_at = db.Column(db.DateTime, nullable=False, default=db.func.current_timestamp())

    user = db.relationship('User', backref=db.backref('downloaded_documents', lazy=True))
    document = db.relationship('Document', backref=db.backref('downloaded_by', lazy=True))

    def __repr__(self):
        return f"<DownloadedDocument(user_id={self.user_id}, document_id={self.document_id})>"