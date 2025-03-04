from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models.user import User
from app.models.document import Document
from pdf2image import convert_from_path

auth = Blueprint('auth', __name__)

@auth.route('/', methods=['GET'])
def index():
    return render_template("home.html")

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['logged_in'] = True
            session['username'] = username
            if username == 'admin':
                session['is_admin'] = True
                flash('Đăng nhập thành công! Chào mừng admin!', 'success')
                return redirect(url_for('auth.dashboard'))
            else:
                session['is_admin'] = False
                flash('Đăng nhập thành công!', 'success')
                return redirect(url_for('auth.profile', username=username))
        else:
            flash('Tên người dùng hoặc mật khẩu không đúng!', 'error')
            return redirect(url_for('auth.login'))
    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if 'logged_in' in session:
        if session.get('is_admin', False):
            return redirect(url_for('auth.dashboard'))
        return redirect(url_for('auth.profile', username=session['username']))

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        import re
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            flash('Email không hợp lệ!', 'error')
            return redirect(url_for('auth.register'))

        if len(password) < 8:
            flash('Mật khẩu phải có ít nhất 8 ký tự!', 'error')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(username=username).first():
            flash('Tên người dùng đã tồn tại!', 'error')
            return redirect(url_for('auth.register'))
        if User.query.filter_by(email=email).first():
            flash('Email đã tồn tại!', 'error')
            return redirect(url_for('auth.register'))

        user = User(username=username, email=email, password=password)
        db.session.add(user)
        try:
            db.session.commit()
            flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
            return redirect(url_for('auth.login'))
        except Exception as e:
            db.session.rollback()
            flash('Đăng ký thất bại. Vui lòng thử lại!', 'error')
            return redirect(url_for('auth.register'))
    return render_template('login.html')

@auth.route('/profile/<username>')
def profile(username):
    if 'logged_in' not in session or session['username'] != username:
        flash('Vui lòng đăng nhập để xem trang cá nhân!', 'error')
        return redirect(url_for('auth.login'))

    if session.get('is_admin', False):  # Nếu là admin, chuyển hướng đến dashboard
        return redirect(url_for('auth.dashboard'))

    user = User.query.filter_by(username=username).first_or_404()
    
    # Lấy tham số tìm kiếm và danh mục từ query string
    search_query = request.args.get('search', '').strip()
    selected_category = request.args.get('category', '').strip()
    
    # Lấy danh sách tài liệu của người dùng
    query = Document.query.filter_by(user_id=user.id)
    
    if search_query:
        query = query.filter(Document.title.ilike(f'%{search_query}%'))
    
    if selected_category:
        query = query.filter(Document.category == selected_category)
    
    documents = query.all()
    
    # Nhóm tài liệu theo danh mục
    categories = {}
    for doc in documents:
        if doc.category not in categories:
            categories[doc.category] = []
        categories[doc.category].append(doc)

    # Lấy tất cả danh mục có sẵn
    all_categories = Document.query.with_entities(Document.category).distinct().all()
    all_categories = [cat[0] for cat in all_categories]

    # Nếu không có tài liệu, lấy gợi ý từ admin
    suggestions = []
    if not documents and not selected_category:
        admin_user = User.query.filter_by(username='admin').first()
        if admin_user:
            suggestions = Document.query.filter_by(user_id=admin_user.id).limit(5).all()

    return render_template('profile.html', user=user, categories=categories, suggestions=suggestions, all_categories=all_categories, selected_category=selected_category, is_admin=session.get('is_admin', False))

@auth.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('username', None)
    session.pop('is_admin', None)
    flash('Đăng xuất thành công!', 'success')
    return redirect(url_for('auth.index'))

@auth.route('/admin/users', defaults={'page': 1})
@auth.route('/admin/users/page/<int:page>')
def admin_users(page):
    if 'logged_in' not in session or not session.get('is_admin', False):
        flash('Bạn không có quyền truy cập trang này!', 'error')
        return redirect(url_for('auth.login'))

    per_page = 10
    users = User.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('admin_users.html', users=users)

@auth.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'logged_in' not in session or not session.get('is_admin', False):
        flash('Bạn không có quyền truy cập trang này!', 'error')
        return redirect(url_for('auth.login'))

    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        existing_user = User.query.filter_by(username=username).first()
        if existing_user and existing_user.id != user.id:
            flash('Tên người dùng đã tồn tại!', 'error')
            return redirect(url_for('auth.edit_user', user_id=user.id))

        existing_email = User.query.filter_by(email=email).first()
        if existing_email and existing_email.id != user.id:
            flash('Email đã tồn tại!', 'error')
            return redirect(url_for('auth.edit_user', user_id=user.id))

        user.username = username
        user.email = email
        if password:
            user.password = password

        try:
            db.session.commit()
            flash('Cập nhật thông tin người dùng thành công!', 'success')
            return redirect(url_for('auth.admin_users'))
        except Exception as e:
            db.session.rollback()
            flash('Cập nhật thất bại. Vui lòng thử lại!', 'error')
            return redirect(url_for('auth.edit_user', user_id=user.id))

    return render_template('edit_user.html', user=user)

@auth.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'logged_in' not in session or not session.get('is_admin', False):
        flash('Bạn không có quyền truy cập trang này!', 'error')
        return redirect(url_for('auth.login'))

    user = User.query.get_or_404(user_id)
    if user.username == 'admin':
        flash('Không thể xóa tài khoản admin!', 'error')
        return redirect(url_for('auth.admin_users'))

    try:
        db.session.delete(user)
        db.session.commit()
        flash('Xóa tài khoản thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Xóa tài khoản thất bại. Vui lòng thử lại!', 'error')

    return redirect(url_for('auth.admin_users'))

from pdf2image import convert_from_path
import os

@auth.route('/upload_document', methods=['GET', 'POST'])
def upload_document():
    if 'logged_in' not in session:
        flash('Vui lòng đăng nhập trước!', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        title = request.form.get('title')
        category = request.form.get('category')
        pages = request.form.get('pages', '0')
        file = request.files.get('file')
        user = User.query.filter_by(username=session['username']).first()

        if not title or not category:
            flash('Tiêu đề và danh mục không được để trống!', 'error')
            return redirect(url_for('auth.upload_document'))

        try:
            pages = int(pages)
        except ValueError:
            flash('Số trang phải là một số hợp lệ!', 'error')
            return redirect(url_for('auth.upload_document'))

        if file and (file.filename.endswith('.doc') or file.filename.endswith('.pdf')):
            file_type = 'DOC' if file.filename.endswith('.doc') else 'PDF'
            # Đường dẫn đến thư mục app/static/uploads
            upload_dir = os.path.join('app', 'static', 'uploads')
            if not os.path.exists(upload_dir):
                os.makedirs(upload_dir)

            thumbnail_dir = os.path.join('app', 'static', 'thumbnails')
            if not os.path.exists(thumbnail_dir):
                os.makedirs(thumbnail_dir)

            # Tạo tên file và kiểm tra trùng lặp
            file_path = f"uploads/{file.filename}"  # Đường dẫn tương đối để lưu vào cơ sở dữ liệu
            base, extension = os.path.splitext(file.filename)
            counter = 1
            saved_file_path = os.path.join('app', 'static', file_path)  # Đường dẫn đầy đủ để lưu file
            while os.path.exists(saved_file_path):
                file_path = f"uploads/{base}_{counter}{extension}"
                saved_file_path = os.path.join('app', 'static', file_path)
                counter += 1

            # Lưu file với tên đã được điều chỉnh
            file.save(saved_file_path)

            # Tạo thumbnail nếu là PDF
            thumbnail_path = None
            if file_type == 'PDF':
                try:
                    images = convert_from_path(saved_file_path, first_page=0, last_page=1)
                    if images:
                        thumbnail_filename = f"thumbnails/{base}_thumb.jpg"
                        counter = 1
                        saved_thumbnail_path = os.path.join('app', 'static', thumbnail_filename)
                        while os.path.exists(saved_thumbnail_path):
                            thumbnail_filename = f"thumbnails/{base}_thumb_{counter}.jpg"
                            saved_thumbnail_path = os.path.join('app', 'static', thumbnail_filename)
                            counter += 1
                        images[0].save(saved_thumbnail_path, 'JPEG')
                        thumbnail_path = thumbnail_filename
                except Exception as e:
                    print(f"Error creating thumbnail for PDF: {e}")

            # Lưu thông tin tài liệu vào cơ sở dữ liệu với file_path đã được điều chỉnh
            document = Document(
                title=title,
                category=category,
                file_type=file_type,
                user_id=user.id,
                file_path=file_path,  # Lưu đường dẫn tương đối (uploads/filename)
                thumbnail_path=thumbnail_path,
                pages=pages
            )
            db.session.add(document)
            try:
                db.session.commit()
                flash('Upload tài liệu thành công!', 'success')
            except Exception as e:
                db.session.rollback()
                flash('Upload tài liệu thất bại!', 'error')
        else:
            flash('Chỉ hỗ trợ file DOC hoặc PDF!', 'error')

        if session.get('is_admin', False):
            return redirect(url_for('auth.dashboard'))
        else:
            return redirect(url_for('auth.profile', username=user.username))

    return render_template('upload_document.html')

@auth.route('/document/<int:document_id>')
def view_document(document_id):
    if 'logged_in' not in session:
        flash('Vui lòng đăng nhập trước!', 'error')
        return redirect(url_for('auth.login'))

    document = Document.query.get_or_404(document_id)
    user = User.query.filter_by(username=session['username']).first()
    if session['username'] != document.user.username:
        flash('Bạn không có quyền xem tài liệu này!', 'error')
        return redirect(url_for('auth.login'))

    # Kiểm tra file tồn tại
    file_exists = os.path.exists(os.path.join('app', 'static', document.file_path))

    return render_template('profile_view.html', document=document, user=user, file_exists=file_exists)
def dashboard():
    if 'logged_in' not in session:
        flash('Vui lòng đăng nhập trước!', 'error')
        return redirect(url_for('auth.login'))
    if not session.get('is_admin', False):
        flash('Bạn không có quyền truy cập trang này!', 'error')
        return redirect(url_for('auth.profile', username=session['username']))

    user = User.query.filter_by(username=session['username']).first()
    
    documents = Document.query.filter_by(user_id=user.id).all()
    
    categories = {}
    for doc in documents:
        if doc.category not in categories:
            categories[doc.category] = []
        categories[doc.category].append(doc)

    return render_template('dashboard.html', username=session['username'], categories=categories, is_admin=session.get('is_admin', False))

@auth.route('/delete_document/<int:document_id>', methods=['POST'])
def delete_document(document_id):
    if 'logged_in' not in session:
        flash('Vui lòng đăng nhập trước!', 'error')
        return redirect(url_for('auth.login'))

    document = Document.query.get_or_404(document_id)
    user = User.query.filter_by(username=session['username']).first()
    if document.user_id != user.id:
        flash('Bạn không có quyền xóa tài liệu này!', 'error')
        if session.get('is_admin', False):
            return redirect(url_for('auth.dashboard'))
        else:
            return redirect(url_for('auth.profile', username=user.username))

    try:
        if document.file_path:
            import os
            file_path = os.path.join('static', document.file_path)
            if os.path.exists(file_path):
                os.remove(file_path)

        db.session.delete(document)
        db.session.commit()
        flash('Xóa tài liệu thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Xóa tài liệu thất bại!', 'error')

    if session.get('is_admin', False):
        return redirect(url_for('auth.dashboard'))
    else:
        return redirect(url_for('auth.profile', username=user.username))

@auth.route('/edit_document/<int:document_id>', methods=['GET', 'POST'])
def edit_document(document_id):
    if 'logged_in' not in session:
        flash('Vui lòng đăng nhập trước!', 'error')
        return redirect(url_for('auth.login'))

    document = Document.query.get_or_404(document_id)
    user = User.query.filter_by(username=session['username']).first()
    if document.user_id != user.id:
        flash('Bạn không có quyền chỉnh sửa tài liệu này!', 'error')
        if session.get('is_admin', False):
            return redirect(url_for('auth.dashboard'))
        else:
            return redirect(url_for('auth.profile', username=user.username))

    if request.method == 'POST':
        document.title = request.form['title']
        document.category = request.form['category']
        document.pages = int(request.form['pages'])
        try:
            db.session.commit()
            flash('Cập nhật tài liệu thành công!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Cập nhật tài liệu thất bại!', 'error')

        if session.get('is_admin', False):
            return redirect(url_for('auth.dashboard'))
        else:
            return redirect(url_for('auth.profile', username=user.username))

    return render_template('edit_document.html', document=document)

@auth.route('/save_document/<int:document_id>', methods=['POST'])
def save_document(document_id):
    if 'logged_in' not in session:
        flash('Vui lòng đăng nhập trước!', 'error')
        return redirect(url_for('auth.login'))

    document = Document.query.get_or_404(document_id)
    user = User.query.filter_by(username=session['username']).first()

    favorite = Favorite.query.filter_by(user_id=user.id, document_id=document.id).first()
    if favorite:
        flash('Tài liệu đã được lưu trong danh sách yêu thích!', 'error')
    else:
        favorite = Favorite(user_id=user.id, document_id=document.id)
        db.session.add(favorite)
        try:
            db.session.commit()
            flash('Đã lưu tài liệu vào danh sách yêu thích!', 'success')
        except Exception as e:
            db.session.rollback()
            flash('Lưu tài liệu thất bại!', 'error')

    if session.get('is_admin', False):
        return redirect(url_for('auth.dashboard'))
    else:
        return redirect(url_for('auth.profile', username=user.username))