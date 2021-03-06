"""
Initialize app
"""

import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask

from flask_mail import Mail
from flask_moment import Moment
from flask_bcrypt import Bcrypt
from flask_ckeditor import CKEditor
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from elasticsearch import Elasticsearch

from config import config


mail = Mail()
db = SQLAlchemy()
bcrypt = Bcrypt()
moment = Moment()
ckeditor = CKEditor()
login_manager = LoginManager()

login_manager.login_view = 'auth.loginPage'
login_manager.session_protection = "strong"
login_manager.login_message_category = 'info'


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    if app.config['ELASTICSEARCH_URL']:
        app.elasticsearch = Elasticsearch(
            [app.config['ELASTICSEARCH_URL']],
            http_compress=True
        )
    else:
        None

    mail.init_app(app)
    bcrypt.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    ckeditor.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from .main import main as main_blueprint
        app.register_blueprint(main_blueprint)

        from .auth import auth as auth_blueprint
        app.register_blueprint(auth_blueprint, url_prefix='/account/')

        from .blog import post as post_blueprint
        app.register_blueprint(post_blueprint,  url_prefix='/account/dashboard/')

        from .admin import admin as admin_blueprint
        app.register_blueprint(admin_blueprint, url_prefix='/admin/')

        return app
