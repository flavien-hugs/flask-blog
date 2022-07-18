"""
Initialize app
"""

import logging as lg

from flask import Flask

from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
ckeditor = CKEditor(app)
mail = Mail(app)


login_manager = LoginManager(app)
login_manager.login_view = 'auth.loginPage'
login_manager.session_protection = "strong"
login_manager.login_message_category = 'info'


from core import models
from .auth import auth as auth_blueprint
from .main import main as main_blueprint
from .post import post as post_blueprint

db.init_app(app)

# blueprint for auth routes in our app

app.register_blueprint(auth_blueprint)
app.register_blueprint(main_blueprint)
app.register_blueprint(post_blueprint)


@app.cli.command('init_db')
def init_db():
    models.init_database()
