# app/routes/auth.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models.user import User
from app.models.document import Document
import os
from app.models.favorite_document import FavoriteDocument
from app.models.downloaded_document import DownloadedDocument

auth = Blueprint('auth', __name__)

@auth.route('/', methods=['GET'])
def index():
    return render_template("home.html")
@auth.route('/privacy_policy')
def privacy_policy():
    """
    Route cho trang Chính sách bảo mật.
    """
    return render_template('privacy_policy.html')
@auth.route('/feedback')
def feedback():
    """
    Route cho trang Phản hồi người dùng.
    """
    return render_template('feedback.html')
@auth.route('/search')
def search():
    query = request.args.get('query', '')  # Lấy query từ URL
    # Logic giả lập để tạo kết quả (thay bằng truy vấn cơ sở dữ liệu thực tế)
    if query:
        results = [f"Kết quả {i} cho '{query}'" for i in range(1, 6)]  # 5 kết quả mẫu
    else:
        results = []
    return render_template('search_results.html', query=query, results=results)
@auth.route('/books')
def books():
    return render_template('books.html')

# Các route khác giữ nguyên
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

    if session.get('is_admin', False):
        return redirect(url_for('auth.dashboard'))

    user = User.query.filter_by(username=username).first_or_404()
    
    # Lấy tham số tìm kiếm và danh mục từ query string
    search_query = request.args.get('search', '').strip()
    selected_category = request.args.get('category', '').strip()

    # Lấy tài liệu của user
    query = Document.query.filter_by(user_id=user.id)
    if search_query:
        query = query.filter(Document.title.ilike(f'%{search_query}%'))
    if selected_category:
        query = query.filter(Document.category == selected_category)
    documents = query.all()

    # Lấy tài liệu của admin (luôn hiển thị cho tất cả người dùng)
    admin_user = User.query.filter_by(username='admin').first()
    admin_documents = []
    if admin_user:
        admin_query = Document.query.filter_by(user_id=admin_user.id)
        if search_query:
            admin_query = admin_query.filter(Document.title.ilike(f'%{search_query}%'))
        if selected_category:
            admin_query = admin_query.filter(Document.category == selected_category)
        admin_documents = admin_query.all()

    # Nhóm tài liệu của user
    categories = {}
    for doc in documents:
        category = doc.category if doc.category else 'Khác'
        if category not in categories:
            categories[category] = []
        categories[category].append(doc)

    # Thêm tài liệu của admin vào danh mục "Tài liệu từ Admin"
    if admin_documents:
        categories['Tài liệu từ Admin'] = admin_documents

    # Lấy danh sách tất cả các danh mục để hiển thị nút
    all_categories = Document.query.with_entities(Document.category).distinct().all()
    all_categories = [cat[0] for cat in all_categories if cat[0]]  # Loại bỏ None
    all_categories.append('Tài liệu từ Admin')  # Thêm danh mục của admin

    return render_template(
        'profile.html',
        user=user,
        categories=categories,
        all_categories=all_categories,
        selected_category=selected_category,
        is_admin=session.get('is_admin', False)
    )

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

@auth.route('/dashboard', methods=['GET', 'POST'])
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


@auth.route('/favorite-and-downloaded', methods=['GET'])
def favorite_and_downloaded():
    if 'logged_in' not in session or 'username' not in session:
        flash('Vui lòng đăng nhập trước!', 'error')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash('Người dùng không tồn tại!', 'error')
        return redirect(url_for('auth.logout'))

    # Lấy danh sách tài liệu yêu thích
    favorite_docs = FavoriteDocument.query.filter_by(user_id=user.id).all()
    # Lấy danh sách tài liệu đã tải về
    downloaded_docs = DownloadedDocument.query.filter_by(user_id=user.id).all()

    # Lấy danh sách document_id yêu thích để kiểm tra trạng thái nút "Thêm vào yêu thích"
    favorite_doc_ids = [fav.document_id for fav in favorite_docs]

    return render_template(
        'favorite_and_downloaded.html',
        user=user,
        favorite_docs=favorite_docs,  # Danh sách FavoriteDocument
        downloaded_docs=downloaded_docs,  # Danh sách DownloadedDocument
        favorite_doc_ids=favorite_doc_ids
    )

@auth.route('/toggle-favorite/<int:document_id>', methods=['POST'])
def toggle_favorite(document_id):
    if 'logged_in' not in session or 'username' not in session:
        flash('Vui lòng đăng nhập trước!', 'error')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash('Người dùng không tồn tại!', 'error')
        return redirect(url_for('auth.logout'))

    document = Document.query.get_or_404(document_id)
    favorite = FavoriteDocument.query.filter_by(user_id=user.id, document_id=document_id).first()

    if favorite:
        # Xóa khỏi danh sách yêu thích
        db.session.delete(favorite)
        flash('Đã xóa khỏi tài liệu yêu thích!', 'success')
    else:
        # Thêm vào danh sách yêu thích
        favorite = FavoriteDocument(user_id=user.id, document_id=document_id)
        db.session.add(favorite)
        flash('Đã thêm vào tài liệu yêu thích!', 'success')

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash('Có lỗi xảy ra, vui lòng thử lại!', 'error')

    # Chuyển hướng về trang trước đó
    return redirect(request.referrer or url_for('auth.profile', username=user.username))