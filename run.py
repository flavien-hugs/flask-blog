"""
Application entry point.
"""

import os
import logging as lg

from core import create_app, db
from flask_migrate import Migrate
from core.models import Role, User, Post, Comment

from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.flaskeenv')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


app = create_app(os.getenv('FLASK_CONFIG') or 'dev')
migrate = Migrate(app, db)


@app.shell_context_processor
def make_shell_context():
    return dict(
        db=db, Role=Role,
        User=User, Post=Post, Comment=Comment
    )

@app.cli.command('test')
def test():
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


@app.cli.command('init_db')
def init_db():
    db.create_all()
    db.session.commit()
    lg.warning('Database initialized !')


if __name__ == "__main__":
    app.run()
