# config.py

import os

SECRET_KEY = os.environ.get('SECRET_KEY')
SQLALCHEMY_TRACK_MODIFICATIONS = False

if os.getenv('DATABASE_URL'):
   SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
else:
   BASE_DIR = os.path.abspath(os.path.dirname(__file__))
   SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, 'core.db')

EMAIL_ADDRESS = "support@unsta.net"
PHONE_NUMBER = "(225) 01 5157 1396"

# https://flask-wtf.readthedocs.io/en/1.0.x/form/#secure-form

WTF_CSRF_SECRET_KEY = os.environ.get('SECRET_KEY')
