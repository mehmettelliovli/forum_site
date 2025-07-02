from flask import Blueprint, jsonify
from models import User

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