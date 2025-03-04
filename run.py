from app import create_app, db
from app.models.document import Document
from pdf2image import convert_from_path
import os

app = create_app()
with app.app_context():
    documents = Document.query.all()
    for doc in documents:
        if not doc.thumbnail_path and doc.file_path and doc.file_type == 'PDF':
            try:
                images = convert_from_path(os.path.join('static', doc.file_path), first_page=0, last_page=1)
                if images:
                    base = os.path.splitext(doc.file_path)[0]
                    thumbnail_filename = f"thumbnails/{os.path.basename(base)}_thumb.jpg"
                    counter = 1
                    while os.path.exists(os.path.join('static', thumbnail_filename)):
                        thumbnail_filename = f"thumbnails/{os.path.basename(base)}_thumb_{counter}.jpg"
                        counter += 1
                    images[0].save(os.path.join('static', thumbnail_filename), 'JPEG')
                    doc.thumbnail_path = thumbnail_filename
                    db.session.commit()
                    print(f"Created thumbnail for {doc.title}: {thumbnail_filename}")
            except Exception as e:
                print(f"Error creating thumbnail for {doc.title}: {e}")
if __name__ == '__main__':
    app.run(debug=True)