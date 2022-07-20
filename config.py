"""
Flask app configuration.
Set Flask configuration from environment variables
"""

from os import environ, path
from dotenv import load_dotenv

BASE_DIR = path.abspath(path.dirname(__file__))

load_dotenv(path.join(BASE_DIR, ".flaskeenv"))


class Config:

    SECRET_KEY = environ.get('SECRET_KEY')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    EMAIL_ADDRESS = "support@unsta.net"
    PHONE_NUMBER = "(225) 01 5157 1396"
    FLASKY_ADMIN = "unsta@pm.me"
    WTF_CSRF_SECRET_KEY = environ.get('SECRET_KEY')
    MAIL_POST = environ.get('MAIL_SERVER')
    MAIL_SERVER = environ.get('MAIL_SERVER')
    MAIL_USE_TLS = environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = environ.get('MAIL_USERNAME')
    MAIL_SUBJECT_PREFIX = '[Unsta Inc]'
    MAIL_SENDER = 'Unsta Admin <noreply@unsta.com>'
    MAIL_PASSWORD = environ.get('MAIL_PASSWORD')
    RESET_TOKEN_MINUTES = environ.get('RESET_TOKEN_MINUTES')

    @staticmethod
    def init_app(app):
        pass


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL") \
        or 'sqlite:///' + path.join(BASE_DIR, 'data-dev.sqlite')


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = environ.get('TEST_DATABASE_URL') \
        or 'sqlite://'


class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = environ.get('DATABASE_URL') \
        or 'sqlite:///' + path.join(BASE_DIR, 'data.sqlite')


config = {
    'testing': TestingConfig,
    'default': DevelopmentConfig,
    'production': ProductionConfig,
    'development': DevelopmentConfig,
}
