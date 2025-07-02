from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from config import Config
from auth import bp as auth_bp
from users import bp as users_bp
from forum import bp as forum_bp

app = Flask(__name__)
app.config.from_object(Config)

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

from models import User, Post, Category

app.register_blueprint(auth_bp)
app.register_blueprint(users_bp)
app.register_blueprint(forum_bp)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Blueprintler ve route'lar daha sonra eklenecek

if __name__ == '__main__':
    app.run(debug=True) 