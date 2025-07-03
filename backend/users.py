from flask import Blueprint, jsonify, request, render_template, redirect, url_for, flash
from models import User
from flask_login import login_required, current_user
from extensions import db

bp = Blueprint('users', __name__, url_prefix='/users')

@bp.route('/', methods=['GET'])
def list_users():
    users = User.query.all()
    return jsonify([
        {
            'id': user.id,
            'username': user.username,
            'email': user.email
        } for user in users
    ])

@bp.route('/<int:user_id>', methods=['DELETE'])
@login_required
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.role == 1 or current_user.id == user.id:
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'Kullanıcı silindi'}), 200
    return jsonify({'error': 'Yetkisiz işlem'}), 403

@bp.route('/<int:user_id>', methods=['PUT'])
@login_required
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.role == 1 or current_user.id == user.id:
        data = request.get_json()
        user.username = data.get('username', user.username)
        user.email = data.get('email', user.email)
        # Şifre güncelleme opsiyonel
        if 'password' in data:
            from extensions import bcrypt
            user.password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        db.session.commit()
        return jsonify({'message': 'Kullanıcı güncellendi'}), 200
    return jsonify({'error': 'Yetkisiz işlem'}), 403

@bp.route('/<int:user_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_user(user_id):
    user = User.query.get_or_404(user_id)
    if current_user.role != 1 and current_user.id != user.id:
        flash('Yetkisiz işlem', 'danger')
        return redirect(url_for('users.list_users'))
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if username:
            user.username = username
        if email:
            user.email = email
        if password:
            from extensions import bcrypt
            user.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        db.session.commit()
        flash('Kullanıcı güncellendi', 'success')
        return redirect(url_for('users.list_users'))
    return render_template('edit_user.html', user=user) 