import logging as lg

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_object('config')
db = SQLAlchemy(app)

from core import routes, models


db.init_app(app)

@app.cli.command('init_db')
def init_db():
    models.init_database()
