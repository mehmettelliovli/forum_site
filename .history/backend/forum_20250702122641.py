from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from app import db
from models import Post, Category

bp = Blueprint('forum', __name__, url_prefix='/forum')

@bp.route('/posts', methods=['GET'])
def list_posts():
    posts = Post.query.all()
    return jsonify([
        {
            'id': post.id,
            'title': post.title,
            'content': post.content,
            'author': post.author.username,
            'category': post.category.name if post.category else None,
            'created_at': post.created_at.isoformat(timespec='seconds')
        } for post in posts
    ])

@bp.route('/posts', methods=['POST'])
@login_required
def create_post():
    data = request.get_json()
    title = data.get('title')
    content = data.get('content')
    category_id = data.get('category_id')
    if not title or not content or not category_id:
        return jsonify({'error': 'Eksik alanlar'}), 400
    category = Category.query.get(category_id)
    if not category:
        return jsonify({'error': 'Kategori bulunamadı'}), 400
    post = Post(title=title, content=content, category_id=category_id, user_id=current_user.id)
    db.session.add(post)
    db.session.commit()
    return jsonify({'message': 'Gönderi oluşturuldu'}) 