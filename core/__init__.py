"""
Initialize app
"""

import os
import logging
from logging.handlers import RotatingFileHandler

from flask import Flask, render_template

from flask_mail import Mail
from flask_moment import Moment
from flask_bcrypt import Bcrypt
from flask_ckeditor import CKEditor
from flask_wtf.csrf import CSRFError
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


        @app.errorhandler(404)
        def pageNotFound(error):
            page_title = f"{error.code} - page non trouvé"
            return render_template(
                'pages/error.html',
                page_title=page_title,
                error=error
            ), 404

        @app.errorhandler(500)
        def internalServerError(error):
            page_title = f"{error.code} - quelques choses à mal tourné"
            return render_template(
                'pages/error.html',
                page_title=page_title,
                error=error
            ), 500

        @app.errorhandler(400)
        def keyError(error):
            page_title = f"{error.code} - une demande invalide a entraîné une KeyError."
            return render_template(
                'pages/error.html',
                page_title=page_title,
                error=error
            ), 400

        @app.errorhandler(CSRFError)
        def handleCsrfError(error):
            page_title = f"{error.code} - une demande invalide a entraîné une KeyError."
            return render_template(
                'pages/error.html',
                page_title=page_title,
                error=error
            ), 400

        if not app.debug and not app.testing:
            if not os.path.exists('logs'):
                os.mkdir('logs')
            file_handler = RotatingFileHandler(
                'logs/logging.log', maxBytes=10240, backupCount=10)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
            file_handler.setLevel(logging.INFO)

            app.logger.addHandler(file_handler)
            app.logger.setLevel(logging.INFO)
            app.logger.info('running app')

        return app
