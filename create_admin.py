# create_admin.py
from app import create_app, db
from app.models.user import User

app = create_app()
with app.app_context():
    admin = User(username='admin', email='admin@example.com', password='admin123')
    db.session.add(admin)
    db.session.commit()
    print("Admin user created!")