from flask import Flask, render_template, redirect, url_for, flash, request
from config import Config
from extensions import db, bcrypt, login_manager
from flask_login import login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)

from auth import bp as auth_bp
from users import bp as users_bp
from forum import bp as forum_bp
from models import User, Post, Category, create_default_categories

app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)
app.register_blueprint(forum_bp)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    posts = Post.query.order_by(Post.created_at.desc()).limit(7).all()
    return render_template('index.html', posts=posts, user=current_user if current_user.is_authenticated else None)

@app.route('/konular')
def topics():
    posts = Post.query.order_by(Post.created_at.desc()).all()
    return render_template('konular.html', posts=posts, user=current_user if current_user.is_authenticated else None)

@app.route('/uyeler')
def members():
    users = User.query.all()
    return render_template('uyeler.html', users=users, user=current_user if current_user.is_authenticated else None)

@app.route('/profil')
@login_required
def profile():
    return render_template('profil.html', user=current_user)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if not username or not email or not password:
            flash('Eksik alanlar', 'danger')
            return redirect(url_for('signup'))
        if User.query.filter((User.username == username) | (User.email == email)).first():
            flash('Kullanıcı zaten mevcut', 'danger')
            return redirect(url_for('signup'))
        password_hash = bcrypt.generate_password_hash(password).decode('utf-8')
        user = User(username=username, email=email, password_hash=password_hash)
        db.session.add(user)
        db.session.commit()
        flash('Kayıt başarılı, giriş yapabilirsiniz.', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', user=current_user if current_user.is_authenticated else None)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and bcrypt.check_password_hash(user.password_hash, password):
            login_user(user)
            flash('Giriş başarılı', 'success')
            return redirect(url_for('home'))
        else:
            flash('Kullanıcı adı veya parola hatalı', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html', user=current_user if current_user.is_authenticated else None)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Çıkış yapıldı', 'success')
    return redirect(url_for('home'))

# Blueprintler ve route'lar daha sonra eklenecek

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_default_categories()
    app.run(debug=True) 