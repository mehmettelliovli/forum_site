from flask import Flask
from config import Config
from extensions import db, bcrypt, login_manager

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

# Blueprintler ve route'lar daha sonra eklenecek

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        create_default_categories()
    app.run(debug=True) 