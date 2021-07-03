from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail

from blogger.config import Config


mail = Mail()

db = SQLAlchemy()
bcrypt = Bcrypt()
loginmanager = LoginManager()
loginmanager.login_view = 'users.login'
loginmanager.login_message_category = 'info'


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    db.init_app(app)
    bcrypt.init_app(app)
    loginmanager.init_app(app)
    mail.init_app(app)

    from blogger.users.routes import users
    from blogger.posts.routes import posts
    from blogger.main.routes import main

    app.register_blueprint(users)
    app.register_blueprint(posts)
    app.register_blueprint(main)

    return app
