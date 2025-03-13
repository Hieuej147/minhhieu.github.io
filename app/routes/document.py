#app/routes/document.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models.user import User
from app.models.document import Document
import os
import shutil
from werkzeug.utils import secure_filename
from app.models.downloaded_document import DownloadedDocument

document = Blueprint('document', __name__)

@document.route('/upload_document', methods=['GET', 'POST'])
def upload_document():
    if 'logged_in' not in session or 'username' not in session:
        flash('Vui lòng đăng nhập trước!', 'error')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash('Người dùng không tồn tại!', 'error')
        return redirect(url_for('auth.logout'))

    if request.method == 'POST':
        file = request.files.get('file')

        if not file:
            flash('Vui lòng chọn một file để upload!', 'error')
            return render_template('upload_document.html', user=user)

        if file and (file.filename.lower().endswith('.doc') or file.filename.lower().endswith('.pdf') or file.filename.lower().endswith('.docx')):
            file_type = 'DOC' if file.filename.lower().endswith(('.doc', '.docx')) else 'PDF'

            temp_upload_dir = os.path.join('app', 'static', 'temp_uploads')
            os.makedirs(temp_upload_dir, exist_ok=True)

            temp_file_path = os.path.join(temp_upload_dir, secure_filename(file.filename))
            counter = 1
            base, extension = os.path.splitext(file.filename)
            while os.path.exists(temp_file_path):
                temp_file_path = os.path.join(temp_upload_dir, f"{base}_{counter}{extension}")
                counter += 1

            file.save(temp_file_path)

            thumbnail_path = None

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return render_template('upload_details_content.html', user=user, temp_file_path=os.path.relpath(temp_file_path, 'app/static'), file_type=file_type, temp_thumbnail_path=thumbnail_path)

            return render_template('upload_details.html', user=user, temp_file_path=os.path.relpath(temp_file_path, 'app/static'), file_type=file_type, temp_thumbnail_path=thumbnail_path)

        else:
            flash('Chỉ hỗ trợ file DOC hoặc PDF!', 'error')
            return render_template('upload_document.html', user=user)

    return render_template('upload_document.html', user=user)

@document.route('/upload_document_details', methods=['POST'])
def upload_document_details():
    if 'logged_in' not in session or 'username' not in session:
        flash('Vui lòng đăng nhập trước!', 'error')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash('Người dùng không tồn tại!', 'error')
        return redirect(url_for('auth.logout'))

    temp_file_path = request.form.get('temp_file_path')
    file_type = request.form.get('file_type')
    temp_thumbnail_path = request.form.get('temp_thumbnail_path')
    title = request.form.get('title')
    category = request.form.get('category')
    pages = request.form.get('pages')

    if not title or not category:
        flash('Tiêu đề và danh mục không được để trống!', 'error')
        return render_template('upload_details.html', user=user, temp_file_path=temp_file_path, file_type=file_type, temp_thumbnail_path=temp_thumbnail_path, title=title, category=category, pages=pages)

    upload_dir = os.path.join('app', 'static', 'uploads')
    os.makedirs(upload_dir, exist_ok=True)

    base, extension = os.path.splitext(os.path.basename(temp_file_path))
    file_path = f"uploads/{base}{extension}"
    counter = 1
    saved_file_path = os.path.join('app', 'static', file_path)
    while os.path.exists(saved_file_path):
        file_path = f"uploads/{base}_{counter}{extension}"
        saved_file_path = os.path.join('app', 'static', file_path)
        counter += 1

    shutil.move(os.path.join('app', 'static', temp_file_path), saved_file_path)

    thumbnail_path = None

    document = Document(
        title=title,
        category=category,
        file_type=file_type,
        user_id=user.id,
        file_path=file_path,
        thumbnail_path=thumbnail_path,
        pages=0
    )
    db.session.add(document)
    try:
        db.session.commit()
        flash('Upload tài liệu thành công!', 'success')
        return redirect(url_for('auth.profile', username=user.username))
    except Exception as e:
        db.session.rollback()
        flash('Upload tài liệu thất bại!', 'error')
        if os.path.exists(saved_file_path):
            os.remove(saved_file_path)
        return render_template('upload_details.html', user=user, temp_file_path=temp_file_path, file_type=file_type, temp_thumbnail_path=temp_thumbnail_path, title=title, category=category, pages=pages)

@document.route('/document/<int:document_id>')
def view_document(document_id):
    if 'logged_in' not in session or 'username' not in session:
        flash('Vui lòng đăng nhập trước!', 'error')
        return redirect(url_for('auth.login'))

    document = Document.query.get_or_404(document_id)
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash('Người dùng không tồn tại!', 'error')
        return redirect(url_for('auth.logout'))

    # Cho phép tất cả người dùng xem tài liệu của admin
    if document.user.username != 'admin' and session['username'] != document.user.username:
        flash('Bạn không có quyền xem tài liệu này!', 'error')
        return redirect(url_for('auth.profile', username=session['username']))

    # Thêm vào danh sách đã tải về nếu chưa có
    downloaded_doc = DownloadedDocument.query.filter_by(user_id=user.id, document_id=document.id).first()
    if not downloaded_doc:
        downloaded_doc = DownloadedDocument(user_id=user.id, document_id=document.id)
        db.session.add(downloaded_doc)
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            flash('Có lỗi xảy ra khi lưu lịch sử tải về!', 'error')

    file_exists = os.path.exists(os.path.join('app', 'static', document.file_path))

    return render_template('profile_view.html', document=document, user=user, file_exists=file_exists)