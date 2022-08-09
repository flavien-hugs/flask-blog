"""
Flask app configuration.
Set Flask configuration from environment variables
"""

import datetime
from os import urandom, environ, path

BASE_DIR = path.abspath(path.dirname(__file__))


class Config:

    DEBUG = False
    TESTING = False
    DEVELOPMENT = False

    SECRET_KEY = environ.get('SECRET_KEY', urandom(24))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    EMAIL_ADDRESS = "support@unsta.net"
    PHONE_NUMBER = "(225) 01 5157 1396"
    FLASKY_ADMIN = "unsta@pm.me"
    WTF_CSRF_SECRET_KEY = environ.get('SECRET_KEY')
    MAIL_POST = int(environ.get('MAIL_POST', '587'))
    MAIL_SERVER = environ.get('MAIL_SERVER')
    MAIL_USE_TLS = environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = environ.get('MAIL_USERNAME')
    MAIL_SUBJECT_PREFIX = '[Unsta Inc]'
    MAIL_SENDER = 'Unsta Admin <noreply@unsta.com>'
    MAIL_PASSWORD = environ.get('MAIL_PASSWORD')
    RESET_TOKEN_MINUTES = environ.get('RESET_TOKEN_MINUTES')
    ELASTICSEARCH_URL = environ.get('ELASTICSEARCH_URL')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    DEVELOPMENT = True
    SQLALCHEMY_DATABASE_URI = environ.get('DEV_DATABASE_URL') or \
        'sqlite:///' + path.join(BASE_DIR, 'dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = environ.get('TEST_DATABASE_URL') \
        or 'sqlite://'
    WTF_CSRF_ENABLED = False


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL') or \
        'sqlite:///' + path.join(BASE_DIR, 'prod.sqlite')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        import logging
        from logging.handlers import SMTPHandler

        credentials = None
        secure = None

        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()

        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.MAIL_SENDER,
            toaddrs=[cls.FLASKY_ADMIN],
            subject=cls.MAIL_SUBJECT_PREFIX + ' Application Error',
            credentials=credentials,
            secure=secure
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


config = {
    'test': TestingConfig,
    'prod': ProductionConfig,
    'dev': DevelopmentConfig,
}
