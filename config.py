"""
Flask app configuration.
Set Flask configuration from environment variables
"""

from os import environ, path
from dotenv import load_dotenv

BASE_DIR = path.abspath(path.dirname(__file__))

load_dotenv(path.join(BASE_DIR, ".flaskeenv"))


SECRET_KEY = environ.get('SECRET_KEY')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_ECHO = False

if environ.get('DATABASE_URL'):
   SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL")
else:
   SQLALCHEMY_DATABASE_URI = "sqlite:///" + path.join(BASE_DIR, 'site.db')


EMAIL_ADDRESS = "support@unsta.net"
PHONE_NUMBER = "(225) 01 5157 1396"

# https://flask-wtf.readthedocs.io/en/1.0.x/form/#secure-form

WTF_CSRF_SECRET_KEY = environ.get('SECRET_KEY')

# Configuration MAIL SERVER

MAIL_POST = environ.get('MAIL_SERVER')
MAIL_SERVER = environ.get('MAIL_SERVER')
MAIL_USE_TLS = environ.get('MAIL_USE_TLS')
MAIL_USERNAME = environ.get('MAIL_USERNAME')
MAIL_PASSWORD = environ.get('MAIL_PASSWORD')
