from flask import Flask, render_template, redirect, url_for, flash, request
from config import Config
from extensions import db, bcrypt, login_manager
from flask_login import login_user, logout_user, login_required, current_user
import os
from models import User, Post, Category, Comment, create_default_categories, Like
from datetime import datetime, timedelta
from sqlalchemy import func

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), '../frontend/templates'), static_folder=os.path.join(os.path.dirname(__file__), '../frontend/static'))
app.config.from_object(Config)

db.init_app(app)
bcrypt.init_app(app)
login_manager.init_app(app)

from auth import bp as auth_bp
from users import bp as users_bp
from forum import bp as forum_bp

app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)
app.register_blueprint(forum_bp)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def home():
    posts = Post.query.order_by(Post.created_at.desc()).limit(7).all()
    categories = Category.query.all()
    return render_template('index.html', posts=posts, user=current_user if current_user.is_authenticated else None, categories=categories)

@app.route('/tartismalar')
def topics():
    category_id = request.args.get('category_id', type=int)
    categories = Category.query.all()
    query = Post.query
    if category_id:
        query = query.filter_by(category_id=category_id)
    posts = query.order_by(Post.created_at.desc()).all()
    return render_template('konular.html', posts=posts, user=current_user if current_user.is_authenticated else None, categories=categories, selected_category=category_id)

@app.route('/uyeler')
def members():
    users = User.query.all()
    categories = Category.query.all()
    return render_template('uyeler.html', users=users, user=current_user if current_user.is_authenticated else None, categories=categories)

@app.route('/profil')
@login_required
def profile():
    categories = Category.query.all()
    # Kullanıcının açtığı tartışmalar
    user_posts = Post.query.filter_by(user_id=current_user.id).all()
    # Kullanıcının yaptığı yorumlar
    user_comments = Comment.query.filter_by(user_id=current_user.id).all()
    # Her tartışmanın beğeni sayısı
    post_likes = {post.id: len(post.likes) for post in user_posts}
    # Bu hafta en çok beğeni alan kendi tartışması
    week_ago = datetime.utcnow() - timedelta(days=7)
    weekly_posts = (
        Post.query
        .filter(Post.user_id == current_user.id)
        .join(Post.likes)
        .filter(Like.created_at >= week_ago)
        .group_by(Post.id)
        .with_entities(Post, func.count(Like.id).label('like_count'))
        .order_by(func.count(Like.id).desc())
        .all()
    )
    top_weekly_post = weekly_posts[0] if weekly_posts else None
    return render_template('profil.html', user=current_user, categories=categories, user_posts=user_posts, user_comments=user_comments, post_likes=post_likes, top_weekly_post=top_weekly_post)

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

@app.route('/tartisma/olustur', methods=['GET', 'POST'])
@login_required
def create_tartisma():
    categories = Category.query.all()
    title = request.form.get('title')
    content = request.form.get('content')
    category_id = request.form.get('category_id')
    print('DEBUG tartisma form:', title, content, category_id)
    try:
        category_id = int(category_id)
    except (TypeError, ValueError):
        flash('Kategori seçimi hatalı.', 'danger')
        return redirect(url_for('topics'))
    if not title or not content or not category_id:
        flash('Tüm alanlar zorunlu.', 'danger')
        return redirect(url_for('topics'))
    try:
        post = Post(title=title, content=content, category_id=category_id, user_id=current_user.id)
        db.session.add(post)
        db.session.commit()
        print('DEBUG: Tartışma başarıyla kaydedildi')
        flash('Tartışma başarıyla oluşturuldu.', 'success')
    except Exception as e:
        db.session.rollback()
        print('DEBUG: Exception:', e)
        flash('Bir hata oluştu, lütfen tekrar deneyin.', 'danger')
    return redirect(url_for('topics'))

@app.route('/konu/<int:post_id>', methods=['GET', 'POST'])
def post_detail(post_id):
    post = Post.query.get_or_404(post_id)
    if request.method == 'POST' and current_user.is_authenticated:
        content = request.form.get('comment_content')
        if content:
            comment = Comment(content=content, user_id=current_user.id, post_id=post.id)
            db.session.add(comment)
            db.session.commit()
            flash('Yorum eklendi.', 'success')
            return redirect(url_for('post_detail', post_id=post.id))
    return render_template('konu.html', post=post, user=current_user)

@app.route('/begen/<int:post_id>', methods=['POST'])
@login_required
def like_post(post_id):
    post = Post.query.get_or_404(post_id)
    existing_like = Like.query.filter_by(user_id=current_user.id, post_id=post_id).first()
    if existing_like:
        db.session.delete(existing_like)
        db.session.commit()
        flash('Beğeni geri alındı.', 'success')
    else:
        like = Like(user_id=current_user.id, post_id=post_id)
        db.session.add(like)
        db.session.commit()
        flash('Tartışma beğenildi.', 'success')
    return redirect(request.referrer or url_for('topics'))

# Blueprintler ve route'lar daha sonra eklenecek

if __name__ == '__main__':
    print('DB URI:', app.config['SQLALCHEMY_DATABASE_URI'])
    with app.app_context():
        db.create_all()
        create_default_categories()
    app.run(debug=True) 