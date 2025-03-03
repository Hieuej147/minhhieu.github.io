from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models.user import User

auth = Blueprint('auth', __name__)

@auth.route('/', methods=['GET'])
def index():
    return render_template("home.html")

@auth.route('/create_admin')
def create_admin():
    existing_admin = User.query.filter_by(username='admin').first()
    if existing_admin:
        flash('Tài khoản admin đã tồn tại!', 'info')
        return redirect(url_for('auth.login'))

    admin_user = User(
        username='admin',
        email='admin@docflow.com',
        password='admin123456'
    )
    db.session.add(admin_user)
    try:
        db.session.commit()
        flash('Tạo tài khoản admin thành công! Vui lòng đăng nhập.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Tạo tài khoản admin thất bại. Vui lòng thử lại!', 'error')
    return redirect(url_for('auth.login'))

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
            else:
                session['is_admin'] = False
            flash('Đăng nhập thành công!', 'success')
            # Chuyển hướng đến trang cá nhân của người dùng
            return redirect(url_for('auth.profile', username=username))
        else:
            flash('Tên người dùng hoặc mật khẩu không đúng!', 'error')
            return redirect(url_for('auth.login'))
    return render_template('login.html')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if 'logged_in' in session:
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

# Route cho trang cá nhân
@auth.route('/profile/<username>')
def profile(username):
    if 'logged_in' not in session or session['username'] != username:
        flash('Vui lòng đăng nhập để xem trang cá nhân!', 'error')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(username=username).first_or_404()
    return render_template('profile.html', user=user, is_admin=session.get('is_admin', False))

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
        return redirect(url_for('auth.login'))  # Chuyển hướng về login thay vì profile

    per_page = 10
    users = User.query.paginate(page=page, per_page=per_page, error_out=False)
    return render_template('admin_users.html', users=users)

@auth.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'logged_in' not in session or not session.get('is_admin', False):
        flash('Bạn không có quyền truy cập trang này!', 'error')
        return redirect(url_for('auth.login'))  # Chuyển hướng về login

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
        return redirect(url_for('auth.login'))  # Chuyển hướng về login

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