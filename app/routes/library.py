#app/routes/library.py
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from app import db
from app.models.user import User

# Tạo Blueprint cho library
library_bp = Blueprint('library', __name__)

# Route library
@library_bp.route('/library', methods=['GET'], endpoint='library')
def library():
    if 'logged_in' not in session or 'username' not in session:
        flash('Vui lòng đăng nhập trước!', 'error')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash('Người dùng không tồn tại!', 'error')
        return redirect(url_for('auth.logout'))

    return render_template('library.html', user=user)

# Route cho Lịch sử và Tài liệu gửi đi (đã có)
@library_bp.route('/sent-history', methods=['GET'], endpoint='sent_history')
def sent_history():
    if 'logged_in' not in session or 'username' not in session:
        flash('Vui lòng đăng nhập trước!', 'error')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash('Người dùng không tồn tại!', 'error')
        return redirect(url_for('auth.logout'))

    return render_template('sent_history.html', user=user)

# Route cho Tải tệp tải về
@library_bp.route('/download-files', methods=['GET'], endpoint='download_files')
def download_files():
    if 'logged_in' not in session or 'username' not in session:
        flash('Vui lòng đăng nhập trước!', 'error')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash('Người dùng không tồn tại!', 'error')
        return redirect(url_for('auth.logout'))

    flash('Chức năng "Tải tệp tải về" đang được phát triển!', 'success')
    return redirect(url_for('library.library'))

# Route cho Ghi chú
@library_bp.route('/notes', methods=['GET'], endpoint='notes')
def notes():
    if 'logged_in' not in session or 'username' not in session:
        flash('Vui lòng đăng nhập trước!', 'error')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash('Người dùng không tồn tại!', 'error')
        return redirect(url_for('auth.logout'))

    flash('Chức năng "Ghi chú" đang được phát triển!', 'success')
    return redirect(url_for('library.library'))



# Route cho Khóa học của tôi
@library_bp.route('/my-courses', methods=['GET'], endpoint='my_courses')
def my_courses():
    if 'logged_in' not in session or 'username' not in session:
        flash('Vui lòng đăng nhập trước!', 'error')
        return redirect(url_for('auth.login'))

    user = User.query.filter_by(username=session['username']).first()
    if not user:
        flash('Người dùng không tồn tại!', 'error')
        return redirect(url_for('auth.logout'))

    flash('Chức năng "Khóa học của tôi" đang được phát triển!', 'success')
    return redirect(url_for('library.library'))